# Tier 2: Constraint Filtering & Accumulation

## Purpose

Filter candidate deployment paths from Tier 1 by applying external constraints. Constraints do NOT score — they **filter** (eliminate infeasible paths) and **accumulate** (add mandatory requirements to surviving paths).

---

## Application Order

Constraints are applied sequentially from hardest to softest:

```
C1 Infrastructure Availability (hardest — can eliminate paths)
        │
        ▼
C2 Compliance Posture (moderate — rarely eliminates, heavy accumulation)
        │
        ▼
C3 Organizational Topology (softest — primarily adds operational requirements)
```

**Why this order?** Infrastructure availability is a physical reality that cannot be argued away. Compliance is an external mandate. Org topology is the most flexible — teams can reorganize.

---

## Path Viability Matrix

Tier 1 fitness produces candidate paths. Each constraint classification either **VIABLE**, **VIABLE WITH GAPS**, or **ELIMINATED** for each path.

### C1 Infrastructure Availability × Deployment Path

| Path | IA1 (Full K8s) | IA2 (Container-Capable) | IA3 (PaaS-Constrained) | IA4 (Traditional Only) |
|---|---|---|---|---|
| Container-Native (K8s) | VIABLE | VIABLE WITH GAPS | ELIMINATED | ELIMINATED |
| Container-Simplified (PaaS) | VIABLE | VIABLE WITH GAPS | VIABLE | ELIMINATED |
| VM/IaaS | VIABLE | VIABLE | VIABLE | VIABLE |
| Hybrid | VIABLE | VIABLE WITH GAPS | VIABLE WITH GAPS | Per-component |

### C2 Compliance Posture × Deployment Path

| Path | CP1 | CP2 | CP3 | CP4 |
|---|---|---|---|---|
| Container-Native (K8s) | VIABLE | VIABLE (adds scanning, RBAC, audit) | VIABLE (adds signed images, approval gates, segregation) | VIABLE unless air-gap or dedicated infra eliminates shared K8s |
| Container-Simplified (PaaS) | VIABLE | VIABLE | VIABLE WITH GAPS (limited control over infra compliance) | ELIMINATED if air-gap required |
| VM/IaaS | VIABLE | VIABLE | VIABLE | VIABLE (but heavy operational burden) |

### C3 Organizational Topology × Deployment Path

C3 does NOT eliminate paths. It accumulates requirements.

| Path | O1 | O2 | O3 | O4 |
|---|---|---|---|---|
| Any path | No additions | Adds coordination requirements | Adds isolation + contract testing | Adds cross-org auth, SLA, network segmentation |

---

## Constraint Compounding

Constraints interact — combined effects can be greater than individual effects.

### Key Compound Patterns

| Combination | Compound Effect |
|---|---|
| IA2 + CP3 | Need orchestration features the infra doesn't provide + compliance needs managed platform capabilities. Gap is infrastructure AND compliance simultaneously. |
| IA1 + CP4 + O4 | Full cloud-native but dedicated clusters per org, separate registries, air-gapped promotion, multi-party cross-org approval. Maximum operational complexity. |
| IA3 + CP3 + O3 | PaaS limits compliance control, multiple teams need isolation PaaS may not provide. CONSTRAINT DEADLOCK candidate. |
| IA4 + O3 | VM-only with distributed teams. Each team needs independent deployment pipeline for VMs — significant tooling investment. |
| CP4 + O4 | Cross-organizational highly-regulated: every organizational boundary is also a regulatory boundary. Exponential compliance surface. |

---

## Constraint Deadlock

### Definition

No viable deployment path survives all three constraint filters. Symmetrical with Tier 1 BLOCKED — represents a hard stop requiring resolution before proceeding.

### Detection

After applying C1 → C2 → C3 sequentially, if ALL candidate paths from Tier 1 show ELIMINATED status:

```
ALL paths ELIMINATED → CONSTRAINT DEADLOCK
```

### Resolution Order

1. **Invest to change the hardest blocking constraint.** Usually C1 — provision new infrastructure. Sometimes C2 — negotiate compliance scope.
2. **Accept a suboptimal path with documented trade-offs.** Explicitly record what requirements cannot be met and why the chosen path is "best available."
3. **Return to Tier 1 reassessment.** If constraints make containerization non-viable, the fitness assessment itself may need recalibration (e.g., accept VM path even for HIGH fitness application).

### Resolution Record

Every deadlock resolution must be documented:
- Which constraint(s) caused the deadlock
- Which resolution strategy was chosen
- What trade-offs were accepted
- Who approved the trade-off decision

---

## Accumulated Requirements Assembly

After all three constraints are applied, assemble the complete requirements list:

```
TIER 2 OUTPUT:
├── Constraint Classifications: C1=[IA?], C2=[CP?], C3=[O?]
├── Surviving Paths: [list of VIABLE and VIABLE WITH GAPS paths]
├── Accumulated Mandatory Requirements:
│   ├── From C1: [infrastructure gap requirements]
│   ├── From C2: [compliance requirements]
│   ├── From C3: [organizational requirements]
│   └── Compound: [requirements from constraint interactions]
├── Capability Gaps: [from C3 team capability sub-assessment]
├── Recommended Path: [best surviving path considering all constraints]
├── Path Trade-offs: [what is suboptimal about recommended path, if anything]
└── CONSTRAINT DEADLOCK: [YES/NO — if YES, resolution record required]
```

---

## Transition to Tier 3

Tier 2 output becomes input to Tier 3. Specifically:

- **Recommended path** constrains which Tier 3 selections are feasible
- **Accumulated requirements** may narrow Tier 3 options (e.g., CP4 air-gap eliminates continuous deployment from external registry)
- **Capability gaps** inform Tier 3 velocity target (team that can't do K8s can't do continuous canary)
- **If CONSTRAINT DEADLOCK** → Tier 3 is skipped until deadlock is resolved
