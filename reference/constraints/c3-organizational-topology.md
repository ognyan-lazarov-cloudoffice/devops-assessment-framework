# C3: Organizational Topology

## Core Question

**Who builds, deploys, and operates the application, and how are they organized?**

Applied THIRD (softest constraint). Primarily adds operational requirements to the chosen path. Rarely eliminates paths outright. Conway's Law operates in full force: team structure shapes system boundaries.

---

## Classifications

| Code | Name | Description |
|------|------|-------------|
| O1 | Single Team | One team owns build, deploy, and operate. Full autonomy over tooling and release cadence. |
| O2 | Multi-Team Shared | Multiple teams contribute to the same deployable(s). Shared pipeline, coordinated releases. |
| O3 | Multi-Team Distributed | Multiple teams own independent services. Independent pipelines per team. Service catalog and contract testing. |
| O4 | Cross-Organizational | Teams span organizational boundaries. Contractual interfaces (SLAs), federated identity, independent environments per organization. |

---

## Decision Tree

```
START
│
├─ Q: How many teams are involved in building,
│  deploying, or operating this application?
│
├─ 1 team ──► Classification: O1 (Single Team)
│
└─ Multiple ──► Q: Do teams span organizational
               (legal/contractual) boundaries?
               │
               ├─ YES ──► Classification: O4 (Cross-Organizational)
               │
               └─ NO ───► Q: Can each team deploy its
                          components independently without
                          coordinating with other teams?
                          │
                          ├─ YES ──► Classification: O3 (Multi-Team Distributed)
                          │
                          └─ NO ───► Classification: O2 (Multi-Team Shared)
```

---

## Accumulated Requirements by Classification

Requirements are CUMULATIVE — each level adds to the previous.

### O1 (Single Team)
No mandatory requirements added. Team has full autonomy.

### O2 (Multi-Team Shared)
Adds:
- Merge coordination strategy (trunk-based with feature flags, or gitflow with merge queue)
- Deployment queue or deployment lock to prevent concurrent deployments
- Shared environment management (who provisions, who has access)
- Integration testing gates before shared deployment
- Breaking change communication protocol
- Shared on-call rotation or clear escalation paths

### O3 (Multi-Team Distributed)
Adds:
- Pipeline-per-team (each team owns its CI/CD)
- GitOps per-team namespaces (isolation at deployment target level)
- Contract testing between services (Pact, Protolock, or equivalent)
- Service catalog with ownership metadata
- Distributed tracing (correlation IDs across service boundaries)
- API versioning strategy (semver, URL versioning, header versioning)
- Independent release cadences per team

### O4 (Cross-Organizational)
Adds to O3:
- API versioning as contractual obligation (breaking changes = contract breach)
- Cross-organization authentication (federated identity, mutual TLS, API keys with rotation)
- Independent environments per organization (no shared staging/production)
- Data sharing agreements (what data crosses organizational boundaries)
- SLA definitions at service boundaries
- Incident response protocols spanning organizations
- Potentially: separate registries, separate clusters, network segmentation

---

## Team Capability Sub-Assessment

Not a separate classification — flags capability gaps within any O-level that may require mitigation.

| Capability Area | Gap Indicator | Mitigation |
|---|---|---|
| Kubernetes operations | Team has no K8s production experience | Training plan, managed K8s (GKE Autopilot), or platform team overlay |
| GitOps workflows | Team unfamiliar with Argo CD / Flux / declarative deployment | Start with CI/CD push model, migrate to GitOps incrementally |
| Contract testing | Teams have no API contract testing practice | Introduce Pact or equivalent; critical for O3/O4 |
| Observability | No distributed tracing or centralized logging experience | Instrument incrementally; critical for O3/O4 |
| On-call / incident response | No production operations experience | Shadow existing ops team, establish runbooks before launch |

---

## Path Influence (Not Elimination)

O-level almost never eliminates deployment paths — it shapes operational requirements.

| Scenario | Impact |
|---|---|
| O3 + Container-Native path | Requires namespace isolation, per-team RBAC, service mesh consideration |
| O4 + Any path | Requires network segmentation, cross-org auth, SLA monitoring |
| O2 + Container-Native + HIGH fitness | Deployment coordination becomes the bottleneck; consider O3 migration |
| O1 + LOW fitness | Team autonomy means refactoring decisions are fast — least constrained scenario |

**Exception:** O4 with air-gap requirements (from C2 CP4) CAN eliminate shared infrastructure paths. This is a C2×C3 compound effect, not O-level alone.

---

## Collection Method

**Question:**
> How is the team organized around this application? Is it one team owning everything, or multiple teams? If multiple, do they deploy independently or coordinate releases?

**Follow-up probes:**
> Do any teams sit in a different organization (separate company, contractor, external vendor)?
> What is the team's experience level with Kubernetes and GitOps workflows?
> How are breaking changes communicated across teams today?

---

## Conway's Law Checkpoint

At classification lock, surface this observation when D1 and O-level create a Conway's Law tension:

| D1 Classification | O Classification | Tension |
|---|---|---|
| T1 (Microservices) | O1 (Single Team) | One team owning many microservices may create operational overhead without organizational benefit. Are all services necessary? |
| T3 (Traditional Monolith) | O3 (Distributed) | Multiple independent teams working on a monolith creates coordination bottleneck. Team structure and architecture are misaligned. |
| T2 (Modular Monolith) | O4 (Cross-Org) | Modular monolith across organizational boundaries creates contractual complexity around a single deployable. Consider service extraction at org boundaries. |
