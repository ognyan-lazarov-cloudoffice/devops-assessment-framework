# Tier 1: Scoring and Fitness Classification

## Scoring Model

Each of the four dimensions (D1-D4) produces a score from 0 to 3. Maximum total: 12.

### Score Table

| Dimension | Code Range | Score Range |
|-----------|-----------|-------------|
| D1 Deployment Unit Topology | T1-T4 | 0, 2, 3 |
| D2 State and Data Model | S1-S4 | 0, 1, 2, 3 |
| D3 Independence Profile | I1-I4 | 0, 2, 3 |
| D4 Lifecycle Compliance | L1-L4 | 0, 1, 2, 3 |

Note: D1 and D3 skip score 1 (no classification maps to 1). D2 and D4 include score 1 (S3 and L3 respectively).

---

## Fitness Classification Rules

Applied in this order — first matching rule wins.

### Rule 1: BLOCKED (any dimension = 0)

```
IF any dimension scores 0 → FITNESS = BLOCKED
```

A score of 0 indicates a disqualifying condition. Assessment cannot proceed until the blocker is addressed.

**Blocked classifications and their remediation paths:**

| Blocker | Remediation |
|---------|-------------|
| T4 (Distributed Monolith) | Consolidate into true monolith OR decouple into genuine independent services |
| S4 (Distributed State Coupling) | Establish clear service-to-data ownership, introduce API boundaries for cross-service data access |
| I4 (Hidden Coupling) | Perform dependency analysis under realistic load, instrument with timeouts/circuit breakers, map all dependencies |
| L4 (Incompatible Lifecycle) | Evaluate modifiability of lifecycle barriers. If removable → remediate and reassess. If not → VM/IaaS path. |

**Multiple blockers:** Document ALL blockers. Remediation must address all before reassessment. A single blocker is sufficient to halt.

### Rule 2: MEDIUM cap (any dimension = 1)

```
IF any dimension scores 1 → FITNESS = MEDIUM (regardless of total)
```

A score of 1 indicates a significant constraint that limits containerization benefit.

Only two classifications produce score 1:
- **S3 (Embedded State):** #1 cause of container migration failures.
- **L3 (Legacy Lifecycle):** Constant operational friction with orchestrator.

Both are remediable without architectural change, but require explicit investment.

### Rule 3: HIGH (total ≥ 10, no dimension below 2)

```
IF total >= 10 AND all dimensions >= 2 → FITNESS = HIGH
```

Application is well-suited for container-native deployment. Full GitOps, HPA, rolling/canary deployments recommended.

**Possible HIGH configurations (all score combos totaling ≥10 with min 2):**

| D1 | D2 | D3 | D4 | Total |
|----|----|----|-----|-------|
| 3 | 3 | 3 | 3 | 12 |
| 3 | 3 | 3 | 2 | 11 |
| 3 | 3 | 2 | 3 | 11 |
| 3 | 2 | 3 | 3 | 11 |
| 2 | 3 | 3 | 3 | 11 |
| 3 | 3 | 2 | 2 | 10 |
| 3 | 2 | 3 | 2 | 10 |
| 3 | 2 | 2 | 3 | 10 |
| 2 | 3 | 3 | 2 | 10 |
| 2 | 3 | 2 | 3 | 10 |
| 2 | 2 | 3 | 3 | 10 |

### Rule 4: MEDIUM (total 6-9, all dimensions ≥ 2)

```
IF total >= 6 AND total <= 9 AND all dimensions >= 2 → FITNESS = MEDIUM
```

Application can be containerized but with constraints. Consider:
- Container-with-Constraints path (workarounds for specific gaps)
- PaaS abstraction (Cloud Run, App Engine — simplifies operational burden)
- Hybrid approach (containerize what fits, VM what doesn't)

### Rule 5: LOW (total ≤ 5, all dimensions ≥ 2)

```
IF total <= 5 AND all dimensions >= 2 → FITNESS = LOW
```

Note: With minimum score of 2 per dimension, minimum total is 8 — so this rule is technically unreachable with current scoring. It exists as a safety net if scoring is recalibrated.

**Effective LOW:** Reached via Rule 2 (MEDIUM cap from dim=1) when total would otherwise be low.

### Rule 6: Fallback LOW

```
IF none of the above rules match → FITNESS = LOW
```

Safety net. Should not be reached with valid inputs.

---

## Fitness Outcome Descriptions

### HIGH FITNESS

**Path:** Container-Native
**Characteristics:**
- Full GitOps workflow viable
- Horizontal Pod Autoscaler (HPA) effective
- Rolling deployments, canary releases, blue-green all viable
- Self-healing (pod restart on failure) works correctly
- Independent scaling per service (if T1)

**Proceed to:** Tier 2 (Extrinsic Constraints)

### MEDIUM FITNESS

**Paths (choose one based on Tier 2 constraints):**
- Container-with-Constraints: containerize with documented workarounds
- PaaS Abstraction: use managed platform (Cloud Run, App Engine, Heroku) to reduce operational burden
- Hybrid: containerize what fits, VM for what doesn't

**Proceed to:** Tier 2 (Extrinsic Constraints)

### LOW FITNESS

**Paths:**
- VM/IaaS: traditional deployment, container benefits don't justify cost
- PaaS with heavy abstraction: if available and appropriate
- Refactor First: invest in addressing fitness gaps before containerization

**Proceed to:** Tier 2 (Extrinsic Constraints) — even LOW fitness has deployment decisions

### BLOCKED

**Action:** Must address blocker(s) before any deployment path selection.
**Does NOT proceed to Tier 2** until resolved or explicitly accepted as permanent with documented trade-offs.

---

## Structured Output: Tier 1 Fitness Report

After all four dimensions are classified, produce the following:

```
TIER 1 FITNESS REPORT
=====================

DIMENSION SCORES:
  D1 Deployment Unit Topology:  [T?] = [score] — [one-line rationale]
  D2 State and Data Model:      [S?] = [score] — [one-line rationale]
  D3 Independence Profile:      [I?] = [score] — [one-line rationale]
  D4 Lifecycle Compliance:       [L?] = [score] — [one-line rationale]

TOTAL: [sum]/12

ACTIVE RULES:
  [List which classification rules triggered, in order]

FITNESS CLASSIFICATION: [HIGH / MEDIUM / LOW / BLOCKED]

BLOCKERS (if any):
  - [Dimension]: [Classification] — [remediation path]

MEDIUM CAPS (if any):
  - [Dimension]: [Classification] — [implication]

FLAGGED CONCERNS:
  - [Concerns that don't affect classification but should inform Tier 2/3]

UNRESOLVED TENSIONS (from cross-dimension checks):
  - [Any tensions noted but not resolved during dialogue]

PATH CANDIDATES FOR TIER 2:
  - [List viable deployment paths given fitness level]
```

---

## Cross-Dimension Tension Check

Executed AFTER all four dimensions are locked but BEFORE aggregation. See `cross-dimension-tensions.md` for the full catalog.

Quick reference of checks:
1. **D1↔D3 consistency:** T1 (microservices) should pair with I1/I2. T1 + I3/I4 = red flag.
2. **D2↔D4 interaction:** S2 (managed statefulness) + L3 (legacy lifecycle) = high risk — state management requires lifecycle cooperation.
3. **D1↔D2 alignment:** T1 + S4 = contradiction — can't be independent services with shared mutable state.
4. **D3↔D4 alignment:** I1 (fully independent) + L3 (legacy lifecycle) = suspect — truly independent services usually have good lifecycle hygiene.
