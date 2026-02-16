# Containerization & Deployment Decision Framework
## Practitioner's Quick-Reference

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 1: PRIMARY DECISION AXIS                                              │
│  Application Architecture + Intrinsic Technical Properties                  │
│  Model: SCORING (0–3 per dimension → fitness classification)                │
│  Answers: What are we deploying? How well does it fit containers?           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                              fitness class
                            + path candidates
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 2: EXTRINSIC CONSTRAINTS                                              │
│  Organizational Topology + Compliance Posture + Available Infrastructure    │
│  Model: FILTERING & ACCUMULATION (eliminate paths, add requirements)        │
│  Answers: What are we allowed/able to do? What must we add?                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                             viable path(s)
                          + mandatory requirements
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TIER 3: STRATEGIC CHOICES                                                  │
│  Lifecycle Stage + Deployment Velocity Target + Risk Tolerance              │
│  Model: SELECTION & COMPOSITION (human decisions → execution profile)       │
│  Answers: How do we get from here to there?                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                          EXECUTION PROFILE
                    (path + requirements + strategy)
```

---

## Failure Modes at a Glance

Each tier has a characteristic failure mode, progressively softer:

| Tier | Failure Mode | Severity | Meaning |
|------|-------------|----------|---------|
| 1 | **BLOCKED** | Hard stop | Intrinsic property is disqualifying; cannot containerize as-is |
| 2 | **CONSTRAINT DEADLOCK** | Hard stop | No viable path survives all external constraints |
| 3 | **STRATEGY TENSION** | Soft conflict | Selected choices conflict; requires adjustment, not redesign |

Resolution escalation is always upward: Tension → revisit Tier 3 selections → if unresolvable, escalate to Tier 2 → if still stuck, revisit Tier 1.

---

# Tier 1: Primary Decision Axis

Assess each of the four dimensions independently, then aggregate.

---

## D1 — Deployment Unit Topology (T)

```
Q1: Can each service/component be deployed without coordinating
    with other services/components?
    │
    ├─── YES ──▶ Q2: Does each deployable unit run as a single
    │                primary process?
    │                │
    │                ├─── YES ──▶ T1 (True Microservices) or T2 (Modular Monolith)
    │                │            depending on number of units
    │                │
    │                └─── NO ───▶ Can it be refactored to single-process?
    │                             │
    │                             ├─── Easily ──▶ T2 with remediation
    │                             └─── No ──────▶ T3 with constraints
    │
    └─── NO ───▶ Q3: Is there a single deployable unit, or multiple
                     tightly-coupled units?
                     │
                     ├─── Single ────▶ T3 (Traditional Monolith)
                     │
                     └─── Multiple ──▶ T4 (Distributed Monolith)
                                       ⚠️ WARNING: Worst-case scenario
```

| Classification | Score | Key Indicator |
|---------------|-------|---------------|
| T1 — True Microservices | 3 | Independent deploy, single process per unit, many units |
| T2 — Modular Monolith | 3 | Independent deploy (or single unit), single process |
| T3 — Traditional Monolith | 2 | Single deployable unit, may have multi-process concerns |
| T4 — Distributed Monolith | **0** | Multiple units that *must* deploy together (**BLOCKER**) |

> **T4 Remediation:** Consolidate into true monolith (T3), or decouple into independent services (T1/T2). There is no container-friendly middle ground for distributed monoliths.

---

## D2 — State & Data Model (S)

```
Q1: Does the application write to local filesystem or maintain
    in-memory state that must survive restarts?
    │
    ├─── NO ───▶ Q2: Is all persistent data externalized to
    │                managed services (DB, cache, object storage)?
    │                │
    │                ├─── YES ──▶ S1 (Cloud-Native Stateless)
    │                │
    │                └─── NO ───▶ What prevents externalization?
    │                             │
    │                             └─── [Requires case-by-case analysis]
    │
    └─── YES ──▶ Q3: Can multiple instances safely run concurrently?
                     │
                     ├─── YES ──▶ S2 (Managed Statefulness)
                     │            Requires: PVCs, StatefulSets,
                     │            or careful volume management
                     │
                     └─── NO ───▶ Q4: Is this a single service or multiple?
                                      │
                                      ├─── Single ──▶ S3 (Embedded State)
                                      │
                                      └─── Multiple with shared DB ──▶ S4
                                           ⚠️ Architectural issue
```

| Classification | Score | Key Indicator |
|---------------|-------|---------------|
| S1 — Cloud-Native Stateless | 3 | All state externalized to managed services |
| S2 — Managed Statefulness | 2 | Local state, but concurrency-safe (StatefulSets viable) |
| S3 — Embedded State | **1** | Local state, single-instance only (**caps fitness at MEDIUM**) |
| S4 — Distributed State Coupling | **0** | Multiple services sharing mutable state (**BLOCKER**) |

> **S4 Remediation:** Fix data ownership boundaries first — this is an architectural issue, not a deployment issue. **S3 Note:** Workable in containers but severely limits scaling and resilience; forces replica count = 1.

---

## D3 — Independence Profile (I)

```
Q1: Can any single component fail without causing other components to fail?
    │
    ├─── YES ──▶ Q2: Can any single component be restarted/redeployed
    │                without affecting others?
    │                │
    │                ├─── YES ──▶ Q3: Can components scale independently?
    │                │                │
    │                │                ├─── YES ──▶ I1 (Fully Independent)
    │                │                │
    │                │                └─── NO ───▶ I2 (Bounded Independence)
    │                │
    │                └─── NO ───▶ I3 (Coordinated Dependence)
    │
    └─── NO ───▶ Q4: Is the coupling explicit and documented,
                     or discovered under load?
                     │
                     ├─── Explicit ──▶ I3 (Coordinated Dependence)
                     │
                     └─── Hidden ────▶ I4 (Hidden Coupling)
                                       ⚠️ Requires architectural work
```

| Classification | Score | Key Indicator |
|---------------|-------|---------------|
| I1 — Fully Independent | 3 | Fail, restart, and scale independently |
| I2 — Bounded Independence | 2 | Fail and restart independently, scaling is coupled |
| I3 — Coordinated Dependence | 2 | Explicit, documented coupling; managed operationally |
| I4 — Hidden Coupling | **0** | Undocumented dependencies discovered in production (**BLOCKER**) |

> **I4 Remediation:** Perform dependency analysis under realistic load *before* containerizing. Hidden coupling in containers manifests as cascading failures that are harder to diagnose than in monolithic deployments.

---

## D4 — Lifecycle Compliance (L)

```
Q1: Does the application start and become ready in under 2 minutes?
    │
    ├─── YES ──▶ Q2: Does it handle SIGTERM and shut down gracefully?
    │                │
    │                ├─── YES ──▶ Q3: Is all configuration injectable
    │                │                at runtime (env vars, mounted files)?
    │                │                │
    │                │                ├─── YES ──▶ Q4: Does it expose
    │                │                │                health endpoints?
    │                │                │                │
    │                │                │                ├─── YES ──▶ L1
    │                │                │                └─── NO ───▶ L2
    │                │                │
    │                │                └─── NO ───▶ L2 (config remediation needed)
    │                │
    │                └─── NO ───▶ L3 (shutdown remediation needed)
    │
    └─── NO ───▶ Q5: Is slow startup inherent to the technology
                     or fixable?
                     │
                     ├─── Fixable ──▶ L3 with remediation path
                     │
                     └─── Inherent ──▶ L4
                          (Consider: init containers, extended
                           startup probes, or non-container deployment)
```

| Classification | Score | Key Indicator |
|---------------|-------|---------------|
| L1 — Cloud-Native Lifecycle | 3 | Fast startup, graceful shutdown, injectable config, health endpoints |
| L2 — Compliant with Gaps | 2 | Mostly compliant, missing health endpoints or needs config work |
| L3 — Legacy Lifecycle | **1** | Slow startup or no graceful shutdown (**caps fitness at MEDIUM**) |
| L4 — Incompatible Lifecycle | **0** | Inherently incompatible with container lifecycle (**BLOCKER**) |

> **L4 Remediation:** Evaluate whether the lifecycle incompatibility can be modified. If inherent to the technology stack, consider non-container deployment (VM/IaaS, PaaS with long-running process support).

---

## Tier 1 Aggregation: How to Use These Results

### Step 1 — Check for Blockers

If **any** dimension scored **0**, the overall fitness is **BLOCKED**.

| Blocker | Resolution |
|---------|------------|
| T4 (Distributed Monolith) | Consolidate into monolith or decouple into independent services |
| S4 (Distributed State Coupling) | Resolve data ownership boundaries |
| I4 (Hidden Coupling) | Dependency analysis under realistic load |
| L4 (Incompatible Lifecycle) | Evaluate modifiability; consider non-container path |

**Do not proceed to Tier 2 until all blockers are resolved or an alternative deployment path is chosen.**

### Step 2 — Check for Caps

If **any** dimension scored **1** (S3 or L3), the overall fitness is **capped at MEDIUM** regardless of the total score.

This is because single-instance-only state (S3) or legacy lifecycle behavior (L3) fundamentally limits what containers can offer you — you lose scaling, rolling updates, and self-healing, which are the primary reasons to containerize.

### Step 3 — Sum and Classify

| Total Score | Additional Condition | Fitness | Path Candidates |
|-------------|---------------------|---------|----------------|
| 10–12 | No dimension below 2 | **HIGH** | Container-Native |
| 6–9 | — | **MEDIUM** | Container-with-Constraints, PaaS Abstraction, Hybrid |
| Any | Any dimension = 1 | **MEDIUM** (capped) | Container-with-Constraints, PaaS Abstraction, Hybrid |
| 0–5 | — | **LOW** | VM/IaaS, PaaS with heavy abstraction, Refactor First |
| Any | Any dimension = 0 | **BLOCKED** | Resolve blocker before proceeding |

### Step 4 — Record Structured Output

Carry forward to Tier 2:

```
Tier 1 Result:
  D1 Topology:     [classification] = [score]
  D2 State:        [classification] = [score]
  D3 Independence: [classification] = [score]
  D4 Lifecycle:    [classification] = [score]
  ─────────────────────────────────────
  Total:           [sum] / 12
  Fitness:         [HIGH | MEDIUM | LOW | BLOCKED]
  Path Candidates: [list from table above]
  Flagged Concerns: [any dimension-specific notes]
```

---

# Tier 2: Extrinsic Constraints

Apply constraints **in order** (hardest filter first). Each constraint either **eliminates** candidate paths or **accumulates** mandatory requirements onto surviving paths.

**Application order: C1 → C2 → C3** (Infrastructure → Compliance → Organization)

---

## C1 — Infrastructure Availability (IA)

```
Does the environment have container orchestration (Kubernetes)?
├── Yes, managed (GKE/EKS/AKS)
│   └── Is the supporting ecosystem operational?
│       ├── Yes (registry, GitOps, observability, secrets) → IA1
│       └── Partial or immature → IA2
├── Yes, self-managed
│   └── IA2
└── No
    └── Is a container runtime (Docker/Podman) available?
        ├── Yes, but no orchestration → IA2
        └── No
            └── Is a managed PaaS available?
                ├── Yes → IA3
                └── No → IA4

Additionally: Must deploy to multiple infra types?
├── Yes → Add IA5 overlay
└── No → Primary classification only
```

| Classification | What's Available |
|---------------|-----------------|
| IA1 — Full Cloud-Native Platform | Managed K8s + registry + GitOps + observability + secrets management |
| IA2 — Container-Capable | Container runtime exists but ecosystem is partial or self-managed |
| IA3 — PaaS-Constrained | Cloud Run, App Engine, Heroku — managed but opinionated |
| IA4 — Traditional Infrastructure | VMs and/or bare metal only |
| IA5 — Multi-Target (overlay) | Must deploy to more than one infrastructure type simultaneously |

### C1 Path Viability Filter

| Candidate Path | IA1 | IA2 | IA3 | IA4 |
|---------------|-----|-----|-----|-----|
| Container-Native | ✅ | ⚠️ gaps | ❌ | ❌ |
| Container-with-Constraints | ✅ | ✅ | ⚠️ partial | ❌ |
| PaaS Abstraction | ✅ | ⚠️ | ✅ | ❌ |
| VM/IaaS | ✅ | ✅ | ❌ | ✅ |

> **Key deadlock:** HIGH fitness (Tier 1) + IA4 = **CONSTRAINT DEADLOCK** — the application is container-fit but containers are unavailable. Resolution: invest in infrastructure, or accept VM/IaaS path despite fitness.

> **IA5 overlay:** When active, the deployment architecture must produce artifacts portable across all target infrastructure types, or maintain parallel pipelines. Adds complexity to any path.

**After C1:** Eliminate any path candidates marked ❌ for your IA classification. Carry surviving paths forward.

---

## C2 — Compliance Posture (CP)

```
Does the application handle externally regulated data?
├── No
│   └── Does organizational policy mandate security practices?
│       ├── No formal policy → CP1
│       └── Yes (internal standards, SOC2 aspirational) → CP2
└── Yes
    └── How many regulatory frameworks apply?
        ├── Single framework (e.g., only HIPAA, only PCI-DSS)
        │   └── Does it require air-gapped or classified handling?
        │       ├── No → CP3
        │       └── Yes → CP4
        └── Multiple overlapping frameworks
            └── CP4
```

| Classification | Accumulated Requirements |
|---------------|------------------------|
| CP1 — Unrestricted | Team discretion; no mandated security practices |
| CP2 — Standard | + image scanning, RBAC, audit logging, environment isolation, encrypted secrets, dependency scanning |
| CP3 — Regulated | + (all CP2) + segregation of duties, formal approval gates, data residency controls, signed images, immutable artifacts |
| CP4 — Highly Regulated | + (all CP3) + air-gap capability, FIPS-validated cryptography, SBOM generation, multi-party authorization, tamper-evident audit trails, dedicated infrastructure per regulatory boundary |

> **CP4 can eliminate paths:** Cloud PaaS eliminated if air-gap required. Shared Kubernetes clusters eliminated if dedicated infrastructure per regulatory boundary is mandated.

**After C2:** Add all accumulated requirements for your CP level onto every surviving path. Eliminate any paths incompatible with CP4-specific hard requirements.

---

## C3 — Organizational Topology (O)

```
How many teams contribute to this application's code and deployment?
├── One team → O1
└── Multiple teams
    └── Do they cross organizational/company boundaries?
        ├── Yes → O4
        └── No (same org)
            └── Do teams deploy their components independently?
                ├── Yes (each team has its own pipeline and release cadence) → O3
                └── No (shared pipeline, coordinated releases) → O2
```

| Classification | Accumulated Requirements |
|---------------|------------------------|
| O1 — Single Team | Full autonomy; no additional coordination requirements |
| O2 — Multi-Team Shared | + merge coordination, deployment queue, shared environment management, integration testing gates, breaking change protocols |
| O3 — Multi-Team Distributed | + pipeline-per-team, GitOps per-team namespaces, contract testing, service catalog, distributed tracing, API versioning |
| O4 — Cross-Organizational | + (all O3) + API versioning as contractual obligation, cross-org authentication/federation, independent environments per org, formal data sharing agreements, SLAs |

> **Capability gap flags:** At O2+, assess whether teams have Kubernetes experience, GitOps proficiency, and contract testing skills. Gaps don't eliminate paths but must be addressed in execution planning.

**After C3:** Add all accumulated requirements for your O level onto surviving paths.

---

## Tier 2 Aggregation: How to Use These Results

### Constraint Compounding

Constraints compound — they don't just add linearly. Watch for these amplifying combinations:

| Combination | Compounding Effect |
|------------|-------------------|
| IA2 + CP3 + O3 | Need orchestration features the infrastructure doesn't fully provide, while compliance demands managed-platform capabilities and teams need independent pipelines |
| IA1 + CP4 + O4 | Full cloud-native but: dedicated clusters per org, separate registries, air-gapped image promotion, multi-party cross-org approval chains |
| IA3 + CP2 + O2 | PaaS simplifies deployment but may lack fine-grained RBAC and audit logging; shared pipeline creates bottleneck |

### CONSTRAINT DEADLOCK

If no candidate path survives all three constraint filters, you have a **CONSTRAINT DEADLOCK**.

**Resolution order:**

1. **Invest to change the hardest constraint** — typically IA (build/acquire infrastructure capability)
2. **Accept a suboptimal path** — document the trade-offs explicitly and get stakeholder sign-off
3. **Return to Tier 1** — reassess whether the application's architecture should change to fit available constraints

### Record Structured Output

Carry forward to Tier 3:

```
Tier 2 Result:
  C1 Infrastructure: [classification]
  C2 Compliance:     [classification]
  C3 Organization:   [classification]
  ─────────────────────────────────────
  Surviving Path(s):      [from viability filter]
  Accumulated Requirements: [union of all constraint requirements]
  Capability Gaps:         [flagged skill/tooling gaps]
  Status:                  [VIABLE | CONSTRAINT DEADLOCK]
```

---

# Tier 3: Strategic Choices

These are genuine human decisions — not assessments. Select one option per choice area, in order.

**Selection order: S1 → S2 → S3** (Lifecycle Stage → Velocity Target → Risk Tolerance)

---

## S1 — Lifecycle Stage (LS)

```
Is this a new application with no existing deployment?
├─ YES → LS1: Greenfield
└─ NO → Is there an active decision to decommission or replace this application?
    ├─ YES → LS4: Sunset
    └─ NO → Is the application under active feature development?
        ├─ YES → LS2: Active Evolution
        └─ NO → LS3: Stable/Maintenance
```

| Classification | Implication for Deployment |
|---------------|--------------------------|
| LS1 — Greenfield | Maximum freedom; design deployment architecture from scratch |
| LS2 — Active Evolution | Must support frequent changes without disruption |
| LS3 — Stable/Maintenance | Minimize operational overhead; changes are rare |
| LS4 — Sunset | Minimize investment; focus on reliability until decommission |

---

## S2 — Velocity Target (VT)

```
Must multiple services/teams release together for business reasons?
├─ YES (business requirement, not technical coupling) → VT4: Coordinated
└─ NO → Is there a mandated or preferred release schedule?
    ├─ YES (sprint-aligned, weekly, change windows) → VT3: Cadenced
    └─ NO → Should deployment happen automatically when code passes all checks?
        ├─ YES → VT1: Continuous
        └─ NO (deployment is a deliberate decision) → VT2: On-Demand
```

| Classification | Implication for Deployment |
|---------------|--------------------------|
| VT1 — Continuous | Fully automated pipeline; deploy on every successful merge |
| VT2 — On-Demand | Automated pipeline but deployment is a deliberate human trigger |
| VT3 — Cadenced | Deploy on a schedule (sprint boundary, weekly, change window) |
| VT4 — Coordinated | Multiple services/teams release together for business reasons |

> ⚠️ **VT4 Validation:** If coordinated releases are forced by *technical coupling* rather than genuine business need, this signals an unresolved Tier 1 issue (D1 Topology or D3 Independence). Revisit before proceeding.

---

## S3 — Risk Tolerance (RT)

```
What is the business impact of a failed deployment?
├─ CRITICAL (revenue loss, safety impact, SLA breach)
│   └─ Does the platform support traffic splitting + automated rollback?
│       ├─ YES → RT1: Progressive
│       └─ NO → Can you run parallel environments?
│           ├─ YES → RT2: Parallel
│           └─ NO → ⚠️ STRATEGY TENSION
│
├─ SIGNIFICANT (user-facing disruption, reputational impact)
│   └─ Is deployment frequency high enough to justify automated risk management?
│       ├─ YES (multiple times per week) → RT1: Progressive or RT3: Rolling with enhanced monitoring
│       └─ NO (less frequently) → RT2: Parallel or RT3: Rolling
│
└─ LOW (internal tools, non-critical services, minimal user impact)
    └─ RT3: Rolling or RT4: Direct
```

| Classification | Mechanism | Infrastructure Requirement |
|---------------|-----------|--------------------------|
| RT1 — Progressive | Canary / traffic splitting with automated rollback | Service mesh or advanced ingress + observability |
| RT2 — Parallel | Blue-green / parallel environments | 2× environment capacity during deployment |
| RT3 — Rolling | Rolling update with health checks | Standard orchestrator capability |
| RT4 — Direct | Replace in place | Minimal (accepts downtime risk) |

---

## Tier 3 Composition: How to Use These Results

### Execution Archetypes

Common selection combinations that form recognizable patterns:

| Archetype | Lifecycle | Velocity | Risk | Typical Context |
|-----------|-----------|----------|------|----------------|
| **Cloud-Native Ideal** | LS1 or LS2 | VT1 | RT1 | Greenfield or actively evolving product with mature platform |
| **Enterprise Standard** | LS2 | VT3 | RT2 or RT3 | Established product with sprint-aligned releases |
| **Controlled Evolution** | LS2 | VT2 | RT2 | Product evolving carefully with deliberate deployments |
| **Regulated Continuous** | LS2 | VT1 | RT1 | High-velocity delivery under compliance constraints (CP3/CP4) |
| **Pragmatic Maintenance** | LS3 | VT2 or VT3 | RT3 | Stable product, minimal change, low operational overhead |
| **Sunset Minimal** | LS4 | VT2 | RT4 | Winding down; deploy only for critical fixes |

These are reference patterns, not prescriptions. Your actual combination may not match any archetype exactly.

### STRATEGY TENSION

A strategy tension occurs when your selections conflict with each other or with the surviving path from Tier 2. Common tensions:

| Tension | Signal | Resolution |
|---------|--------|------------|
| VT1 + RT2 | Continuous delivery with blue-green is expensive and operationally heavy | Consider RT1 (progressive) or accept the cost |
| VT4 + LS1 | Coordinated releases on a greenfield — why? | Verify this is truly a business need, not premature coupling |
| LS4 + RT1 | Investing in progressive rollout for a sunsetting app | Drop to RT3 or RT4; minimize investment |
| RT1 + IA2 | Progressive rollout requires service mesh / advanced ingress not available | Invest in platform, drop to RT2/RT3, or escalate to Tier 2 |
| VT1 + CP4 | Continuous delivery under heavy regulation needs automated compliance gates | Feasible but requires significant pipeline investment |

**Resolution order:**

1. **Adjust selection** — pick a different option within Tier 3
2. **Invest in capability** — build what's missing to support the desired selection
3. **Accept with documented trade-offs** — proceed with the tension acknowledged
4. **Escalate to Tier 2** — the tension may indicate a constraint that should be reclassified

### Record Structured Output

```
Tier 3 Result:
  S1 Lifecycle Stage:  [classification]
  S2 Velocity Target:  [classification]
  S3 Risk Tolerance:   [classification]
  ─────────────────────────────────────
  Archetype Match:     [closest archetype or "custom"]
  Strategy Tensions:   [any conflicts identified]
  Status:              [RESOLVED | TENSION — with resolution]
```

---

# Final Execution Profile

Combine all three tier outputs into a single execution profile:

```
═══════════════════════════════════════════════════════════════
EXECUTION PROFILE: [Application Name]
═══════════════════════════════════════════════════════════════

TIER 1 — FITNESS
  D1 Topology:       [class] = [score]
  D2 State:          [class] = [score]
  D3 Independence:   [class] = [score]
  D4 Lifecycle:      [class] = [score]
  Total: [sum]/12    Fitness: [HIGH|MEDIUM|LOW|BLOCKED]

TIER 2 — CONSTRAINTS
  C1 Infrastructure: [class]
  C2 Compliance:     [class]
  C3 Organization:   [class]
  Surviving Path:    [path name]

TIER 3 — STRATEGY
  S1 Lifecycle:      [class]
  S2 Velocity:       [class]
  S3 Risk:           [class]
  Archetype:         [match or custom]

DEPLOYMENT PATH:     [final path]
MANDATORY REQS:      [accumulated from Tier 2]
CAPABILITY GAPS:     [flagged items]
OPEN TENSIONS:       [any unresolved, with accepted trade-offs]

═══════════════════════════════════════════════════════════════
```

---

## Failure Mode Summary & Resolution

```
BLOCKED (Tier 1)
  │   Any dimension = 0
  │   Resolution: fix architecture, choose alternative path
  │   Cannot proceed to Tier 2
  │
  ▼
CONSTRAINT DEADLOCK (Tier 2)
  │   No path survives all constraints
  │   Resolution: invest in infra > accept suboptimal path > revisit Tier 1
  │   Cannot proceed to Tier 3
  │
  ▼
STRATEGY TENSION (Tier 3)
  │   Selected choices conflict
  │   Resolution: adjust selection > invest in capability > accept with docs > escalate to Tier 2
  │   Can proceed with documented tension
```

> **Core principle:** Containerization amplifies architectural qualities — good or bad. This framework exists to ensure you know which you're amplifying before you commit.