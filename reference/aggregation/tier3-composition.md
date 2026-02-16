# Tier 3: Strategic Composition

## Purpose

Determine HOW to traverse the deployment path selected by Tiers 1 and 2. Tier 3 uses a **selection-and-composition** model — genuine human choices, not scoring or filtering.

---

## Application Order

```
S1 Lifecycle Stage (most foundational — constrains what's realistic)
        │
        ▼
S2 Velocity Target (shaped by lifecycle and constraints)
        │
        ▼
S3 Risk Tolerance (most tactical — directly maps to tooling)
```

---

## Execution Archetypes

Common selection combinations that form recognizable patterns. These are descriptive, not prescriptive — they help validate that selections are internally coherent.

| Archetype | S1 | S2 | S3 | Typical Fitness | Typical Constraints | Description |
|---|---|---|---|---|---|---|
| Cloud-Native Ideal | LS1/LS2 | VT1 | RT1 | HIGH | IA1, CP1-CP2, O1-O3 | Maximum velocity, minimum blast radius. Full automation. |
| Enterprise Standard | LS2 | VT2-VT3 | RT2-RT3 | HIGH/MEDIUM | IA1-IA2, CP2-CP3, O2-O3 | Balanced. On-demand or cadenced with blue-green/rolling. |
| Controlled Evolution | LS2 | VT3 | RT2 | MEDIUM | IA1-IA2, CP3, O2 | Regulated environment with planned release windows. |
| Regulated Continuous | LS2 | VT1 | RT1 | HIGH | IA1, CP3-CP4, O1-O3 | High velocity despite regulation. Heavy automation of compliance gates. |
| Pragmatic Maintenance | LS3 | VT2-VT3 | RT3-RT4 | Any | Any | Minimal investment. Deploy when needed, simple strategy. |
| Sunset Minimal | LS4 | VT4 | RT4 | Any | Any | Keep running, minimize change. Coordinated only for migration milestones. |

### Using Archetypes

1. After all three selections are made, check if the combination matches a known archetype.
2. If YES → Confirm with human. Archetype provides a sanity check and shorthand.
3. If NO → This doesn't mean the combination is wrong. It means it's unusual. Surface the deviation and confirm it's intentional.

---

## Selection Validation Rules

### Hard Incompatibilities

These combinations are internally contradictory. If they arise, one selection must be revised.

| S1 | S2 | S3 | Contradiction | Resolution |
|---|---|---|---|---|
| LS4 | VT1 | Any | Continuous deployment of a sunset app | Revise S2 to VT4 or challenge LS4 classification |
| Any | VT1 | RT4 | Continuous deployment with downtime each time | Revise S3 (at minimum RT3) or revise S2 |
| LS3 | VT1 | RT1 | Full canary infrastructure for rarely-changing app | Revise S2 to VT2, or confirm investment is justified |

### Soft Tensions

These combinations work but create friction. Surface as STRATEGY TENSION for acknowledgment.

See `tensions/strategy-tensions.md` for the full catalog.

---

## Tier 2 Constraint Influence on Tier 3

Tier 2 outputs narrow which Tier 3 selections are feasible:

| Tier 2 Condition | Tier 3 Impact |
|---|---|
| IA2 (Container-Capable, limited orchestration) | RT1 may not be feasible (requires traffic splitting). Cap at RT3 unless additional tooling invested. |
| IA3 (PaaS-Constrained) | S3 options limited to what PaaS supports. Cloud Run → RT3 native. No RT2. |
| CP3/CP4 (Regulated/Highly Regulated) | VT1 requires automated compliance gates. VT3 may be forced by approval cycle length. |
| CP4 air-gap | VT1 impossible from external sources. Internal registry + internal CI only. |
| O2 (Multi-Team Shared) | VT1 creates merge pressure. VT2/VT3 more natural for shared pipelines. |
| O4 (Cross-Organizational) | VT4 may be forced at organizational boundaries regardless of internal velocity. |
| Capability gaps flagged | Low K8s experience → RT1 unrealistic without training. Cap at RT3. |

---

## Structured Output

```
TIER 3 OUTPUT:
├── Selections:
│   ├── S1 Lifecycle Stage: [LS?]
│   ├── S2 Velocity Target: [VT?]
│   └── S3 Risk Tolerance: [RT?]
├── Matching Archetype: [name or "Non-standard"]
├── Strategy Tensions: [list of tensions from catalog, or "None"]
├── Constraint Influence: [which Tier 2 constraints narrowed options]
├── Validation: [PASS / HARD_INCOMPATIBILITY / SOFT_TENSION]
└── Notes: [any human overrides or justifications]
```

---

## Tier 3 Scope Boundary

Tier 3 determines deployment STRATEGY. It does NOT determine:

- **Specific tooling** (Argo CD vs Flux vs Jenkins — implementation detail)
- **Environment topology** (how many environments, naming — infrastructure design)
- **Testing strategy** (unit/integration/e2e split — quality engineering)
- **Monitoring stack** (Prometheus vs Datadog — operational tooling)

These are downstream decisions informed by the Deployment Profile but outside framework scope.
