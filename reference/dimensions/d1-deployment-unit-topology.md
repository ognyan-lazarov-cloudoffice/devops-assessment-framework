# D1: Deployment Unit Topology

## Core Question

**What constitutes a single deployable unit?**

Assesses process cardinality, deployment atomicity, and image-to-unit mapping to determine how well the application's deployment boundaries align with the container model.

---

## Classifications

| Code | Name | Score | Description |
|------|------|-------|-------------|
| T1 | True Microservices | 3 | Independently deployable services. Each service owns its build, release, and runtime lifecycle. One image = one service = one deployable unit. |
| T2 | Modular Monolith | 3 | Single deployable unit with well-defined internal module boundaries. Modules share process but maintain clear separation of concerns. One image = one application. |
| T3 | Traditional Monolith | 2 | Single deployable unit without clear internal boundaries. Tightly coupled internals. Containerizable but gains fewer orchestration benefits. |
| T4 | Distributed Monolith | 0 | **DISQUALIFYING.** Multiple services that MUST deploy together. Worst of both worlds: distributed complexity without deployment independence. |

### Scoring Notes

- T1 and T2 both score 3 — modular monolith is NOT penalized if boundaries are genuine.
- T3 scores 2 — containerizable but limited benefit from orchestration features (independent scaling, canary per-service, etc.).
- T4 scores 0 — triggers BLOCKED. This is an architectural problem, not a deployment problem. Containers amplify this dysfunction.

---

## Decision Tree

```
START
│
├─ Q: Can each service/component be deployed independently
│  without requiring simultaneous deployment of other components?
│
├─ YES ──► Q: Does each deployable unit run as its own process
│          with its own lifecycle (start/stop/crash independently)?
│          │
│          ├─ YES ──► Classification: T1 (True Microservices)
│          │
│          └─ NO ───► INVESTIGATE: Multiple images that must
│                     deploy together = likely T4, not T1.
│                     Go to T4 validation below.
│
└─ NO ───► Q: Is the application a single process?
           │
           ├─ YES ──► Q: Are there well-defined module boundaries
           │          (separate packages/modules with explicit interfaces,
           │          no circular dependencies between modules)?
           │          │
           │          ├─ YES ──► Classification: T2 (Modular Monolith)
           │          │
           │          └─ NO ───► Classification: T3 (Traditional Monolith)
           │
           └─ NO ───► Multiple processes that cannot deploy independently.
                      Classification: T4 (Distributed Monolith)
```

### T4 Validation Gate

If initial indicators suggest T1 but ANY of the following are true, **reclassify as T4**:

- Services share a database schema with cross-service writes
- Deployment of Service A routinely breaks Service B
- There is a required deployment ORDER across services
- Services communicate via shared filesystem or shared memory
- A single CI pipeline builds and deploys multiple services atomically
- Release notes bundle multiple services as a single "release"

---

## Static Analysis Indicators

Evidence the agent gathers from code/configuration without human input.

### Strong Indicators (high confidence)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Multiple Dockerfiles in separate directories with independent build contexts | T1 | Repo root, `/services/*/Dockerfile` |
| Single Dockerfile at repo root | T2 or T3 | Repo root |
| `docker-compose.yml` with multiple services sharing volumes or networks with `depends_on` + healthchecks suggesting ordering | T4 risk | Repo root |
| Separate CI pipelines per service (e.g., `.github/workflows/service-*.yml`) | T1 | CI config directory |
| Single CI pipeline building multiple images with sequential deployment steps | T4 risk | CI config |
| Monorepo with independent `package.json` / `go.mod` / `pom.xml` per directory | T1 if independent builds, T4 if shared build | Service directories |
| Monorepo with single build file at root | T2 or T3 | Build config |

### Moderate Indicators (needs confirmation)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Shared database migration directory across services | T4 risk | `/migrations/`, `/db/` |
| Inter-service imports (e.g., `import { UserModel } from '../user-service/models'`) | T4 risk | Source code |
| Shared library/package referenced by multiple services | Neutral if versioned, T4 risk if direct path reference | `package.json`, `go.mod`, `pom.xml` |
| API gateway or BFF pattern in repo | T1 if services behind it are independent | Source/config |
| K8s manifests with `initContainers` waiting for other services | T4 risk | K8s manifests |

### Weak Indicators (context-dependent)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Multiple `Makefile` targets for different components | Could be T1 or T2 with sub-modules | `Makefile` |
| Env var references to other services (e.g., `USER_SERVICE_URL`) | Normal for T1, suspicious if hardcoded to localhost | `.env`, config files |
| Shared protobuf/OpenAPI definitions | Normal for T1 (contract-first), concerning if tightly coupled | `/proto/`, `/api/` |

### Static Analysis Ceiling: ~60-70%

**CAN detect:** Build topology, dependency graphs, CI pipeline structure, image definitions, deployment manifests.

**CANNOT verify:** Actual runtime deployment independence, whether "independent" services truly function when deployed alone, real-world deployment ordering requirements.

---

## Question Bank

Gap-resolution questions for Phase 2 dialogue. Max 3 per dimension.

**Q-D1-1: Deployment Independence Verification**
> Static analysis shows [N] separate build targets/Dockerfiles. In practice, can you deploy Service A without simultaneously deploying Service B? Has this actually been done in the last 3 months?

- *Purpose:* Distinguishes T1 from T4.
- *Triggers when:* Multiple images detected but deployment ordering signals also present.
- *Maps to:* T1 vs T4 boundary.

**Q-D1-2: Module Boundary Reality Check**
> The codebase appears to be a single deployable unit with [observed structure]. Are these module boundaries enforced (compilation boundaries, linting rules, architectural fitness functions) or conventions that get violated under pressure?

- *Purpose:* Distinguishes T2 from T3.
- *Triggers when:* Single process detected with apparent but unverified internal structure.
- *Maps to:* T2 vs T3 boundary.

**Q-D1-3: Deployment Coupling Probe**
> When a change is made to [component/service], what other components must also be redeployed? Is there a required deployment sequence?

- *Purpose:* Detects hidden T4 patterns even when architecture appears to be T1.
- *Triggers when:* T1 indicators present but cross-service dependency signals also detected.
- *Maps to:* T1 vs T4 boundary.

---

## Dialectical Triggers

### Category 1: Evidence-Statement Contradictions

Fire when human claims conflict with static evidence. Max 2 rounds per trigger.

| Human Claims | Evidence Shows | Challenge |
|---|---|---|
| "Services are independently deployable" | Single CI pipeline deploys all services together | "The CI pipeline at `[path]` appears to build and deploy all services in a single run. Can you explain how independent deployment works in practice?" |
| "It's a monolith, single deploy" | Multiple Dockerfiles with separate build contexts found | "I found separate Dockerfiles in `[paths]`. Are these actively used or legacy artifacts?" |
| "Well-structured modular monolith" | Circular dependency chains detected between modules | "Dependency analysis shows circular references between `[moduleA]` and `[moduleB]`. How are module boundaries maintained with these cycles?" |

### Category 3: Downstream Implication Surfacing

Surfaced at classification lock time. Max 1 round.

| Classification | Implication | Surface |
|---|---|---|
| T4 = 0 | **BLOCKED.** Must address before proceeding. Remediation: consolidate into true monolith OR decouple into genuine services. | Always when T4 is locked. |
| T3 = 2 | Caps practical benefit of container orchestration. HPA scales entire monolith. Canary deploys entire monolith. Confirm trade-off is understood. | When total might be borderline HIGH (other dims scoring 3). |
| T1 + many services | Multi-repo or monorepo strategy affects Phase 1 scan scope. Confirm repo boundary map. | When T1 locked and >5 services identified. |

---

## Common Misclassifications

| Looks Like | Actually Is | How to Detect |
|---|---|---|
| "Microservices" with shared DB schema | T4 (Distributed Monolith) | Check migration dirs, DB connection strings, cross-service data access |
| Monolith with multiple Docker images (app + worker + scheduler) | T2/T3 — NOT T1 (single logical unit, multiple process types) | Check if processes share codebase and must deploy together |
| Modular monolith with one eroded boundary | T3 (one violation = boundaries are conventions, not contracts) | Cross-module imports violating declared boundaries |
| Service mesh with sidecar | T1 with infra concern — sidecar is NOT a separate service for D1 | Ignore infrastructure sidecars in topology assessment |
