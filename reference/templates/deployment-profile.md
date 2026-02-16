# Deployment Profile Template

## Final Framework Output

Complete this template as the end product of the three-tier assessment. This is the Deployment Profile — the authoritative summary of the assessment.

---

## Application Identity

| Field | Value |
|---|---|
| Application name | |
| Repository / repositories | |
| Assessment date | |
| Assessor (human) | |
| Assessment facilitator | |

---

## Tier 1: Containerization Fitness

### Dimension Scores

| Dimension | Classification | Score | Confidence | Key Evidence | Notes |
|---|---|---|---|---|---|
| D1 Deployment Unit Topology | `[T1/T2/T3/T4]` | `[0-3]` | `[HIGH/MEDIUM/LOW]` | | |
| D2 State and Data Model | `[S1/S2/S3/S4]` | `[0-3]` | `[HIGH/MEDIUM/LOW]` | | |
| D3 Independence Profile | `[I1/I2/I3/I4]` | `[0-3]` | `[HIGH/MEDIUM/LOW]` | | |
| D4 Lifecycle Compliance | `[L1/L2/L3/L4]` | `[0-3]` | `[HIGH/MEDIUM/LOW]` | | |

### Aggregation

| Field | Value |
|---|---|
| Total score | `[0-12]` |
| Any dimension = 0? | `[YES → BLOCKED / NO]` |
| Any dimension = 1? | `[YES → caps at MEDIUM / NO]` |
| All dimensions ≥ 2? | `[YES/NO]` |
| **Fitness Classification** | **`[BLOCKED / LOW / MEDIUM / HIGH]`** |

### Cross-Dimension Tensions Detected

| Tension ID | Dimensions | Description | Resolution |
|---|---|---|---|
| _e.g., CDT-01_ | _D1↔D3_ | _description_ | _how resolved or "accepted"_ |

### BLOCKED Remediation (if applicable)

| Blocking Dimension | Classification | Remediation Required |
|---|---|---|
| | | |

---

## Tier 2: Extrinsic Constraints

### Constraint Classifications

| Constraint | Classification | Confidence | Notes |
|---|---|---|---|
| C1 Infrastructure Availability | `[IA1/IA2/IA3/IA4]` (+IA5?) | `[HIGH/MEDIUM/LOW]` | |
| C2 Compliance Posture | `[CP1/CP2/CP3/CP4]` | `[HIGH/MEDIUM/LOW]` | |
| C3 Organizational Topology | `[O1/O2/O3/O4]` | `[HIGH/MEDIUM/LOW]` | |

### Path Viability

| Candidate Path | Status | Reason |
|---|---|---|
| Container-Native (K8s) | `[VIABLE/GAPS/ELIMINATED]` | |
| Container-Simplified (PaaS) | `[VIABLE/GAPS/ELIMINATED]` | |
| VM/IaaS | `[VIABLE/GAPS/ELIMINATED]` | |
| Hybrid | `[VIABLE/GAPS/ELIMINATED]` | |

### Recommended Path

**Selected:** `[path name]`

**Rationale:**

### Accumulated Mandatory Requirements

_List all requirements accumulated from C1, C2, C3, and compound effects._

1. 
2. 
3. 

### Capability Gaps

| Gap | Impact | Mitigation |
|---|---|---|
| | | |

### Constraint Deadlock (if applicable)

| Field | Value |
|---|---|
| Deadlock detected | `[YES/NO]` |
| Blocking constraint(s) | |
| Resolution strategy | |
| Trade-offs accepted | |

---

## Tier 3: Strategic Choices

### Selections

| Choice Area | Selection | Rationale |
|---|---|---|
| S1 Lifecycle Stage | `[LS1/LS2/LS3/LS4]` | |
| S2 Velocity Target | `[VT1/VT2/VT3/VT4]` | |
| S3 Risk Tolerance | `[RT1/RT2/RT3/RT4]` | |

### Execution Archetype

**Matching archetype:** `[name or "Non-standard"]`

**Description:**

### Strategy Tensions Detected

| Tension ID | Description | Severity | Resolution |
|---|---|---|---|
| _e.g., ST-04_ | _description_ | `[Advisory/Warning/Conflict]` | _how resolved_ |

### Constraint Influence on Selections

_List which Tier 2 constraints narrowed or eliminated Tier 3 options._

---

## Summary

### Deployment Profile (One-Line)

> **[Application name]**: `[FITNESS]` fitness → `[Path]` via `[Archetype or strategy summary]`

### Key Decisions

_3-5 most important decisions or findings from the assessment._

1. 
2. 
3. 

### Open Items

_Unresolved questions, noted tensions accepted without resolution, areas requiring follow-up._

| Item | Context | Owner | Target Date |
|---|---|---|---|
| | | | |

### Framework Boundary

This Deployment Profile is the output of Framework 1 (Containerization Fitness & Deployment Path Assessment). It does NOT include:
- Migration execution planning (Framework 2 scope)
- Specific tooling selection
- Environment topology design
- Testing strategy
- Monitoring stack selection

These are downstream activities informed by this profile.
