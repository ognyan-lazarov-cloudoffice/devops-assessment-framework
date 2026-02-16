# Constraint Map Template

## Tier 2 Output — Constraint Map

Complete this template after applying all three constraints sequentially (C1 → C2 → C3).

---

## Constraint Classifications

| Constraint | Classification | Confidence | Notes |
|---|---|---|---|
| C1 Infrastructure Availability | `[IA1/IA2/IA3/IA4]` (+IA5 overlay if applicable) | `[HIGH/MEDIUM/LOW]` | |
| C2 Compliance Posture | `[CP1/CP2/CP3/CP4]` | `[HIGH/MEDIUM/LOW]` | |
| C3 Organizational Topology | `[O1/O2/O3/O4]` | `[HIGH/MEDIUM/LOW]` | |

---

## Path Viability Assessment

Candidate paths from Tier 1 fitness classification: `[HIGH/MEDIUM/LOW]`

| Candidate Path | After C1 | After C2 | After C3 | Final Status |
|---|---|---|---|---|
| Container-Native (K8s) | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` |
| Container-Simplified (PaaS) | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` |
| VM/IaaS | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` |
| Hybrid | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` | `[VIABLE/GAPS/ELIMINATED]` |

---

## Accumulated Mandatory Requirements

### From C1 (Infrastructure)
- [ ] _Requirement 1_
- [ ] _Requirement 2_

### From C2 (Compliance)
- [ ] _Requirement 1_
- [ ] _Requirement 2_

### From C3 (Organization)
- [ ] _Requirement 1_
- [ ] _Requirement 2_

### Compound Requirements (Constraint Interactions)
- [ ] _Compound requirement from C?×C? interaction_

---

## Capability Gaps

| Gap Area | Current State | Required For | Mitigation |
|---|---|---|---|
| _e.g., Kubernetes operations_ | _No team experience_ | _Container-Native path_ | _Training plan + managed K8s_ |

---

## Constraint Deadlock Assessment

**Deadlock detected:** `[YES/NO]`

_If YES:_

| Field | Value |
|---|---|
| Blocking constraint(s) | |
| Resolution strategy | `[INVEST / ACCEPT_SUBOPTIMAL / REASSESS_TIER1]` |
| Trade-offs accepted | |
| Approved by | |
| Date | |

---

## Recommended Path

**Selected path:** `[path name]`

**Rationale:** _Why this path was selected over alternatives._

**Known trade-offs:** _What is suboptimal about this path and why it was accepted._

---

## Transition Notes for Tier 3

- Tier 3 options narrowed by: _[list specific constraints affecting strategic choices]_
- Capability gaps affecting velocity: _[list gaps that limit deployment frequency/strategy]_
- Compliance gates affecting risk tolerance: _[list approval/segregation requirements]_
