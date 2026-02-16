# Template: Tier 1 Fitness Report

## Purpose

Aggregated output of all four dimension assessments plus cross-dimension tension check. Input to Tier 2 constraint filtering.

---

## Template

```markdown
# TIER 1 FITNESS REPORT
Assessment: [application/system name]
Date: [date]

═══════════════════════════════════════

## DIMENSION SCORES

| Dim | Code | Classification | Score | Key Rationale |
|-----|------|---------------|-------|---------------|
| D1 | [T?] | [name] | [0-3] | [one line] |
| D2 | [S?] | [name] | [0-3] | [one line] |
| D3 | [I?] | [name] | [0-3] | [one line] |
| D4 | [L?] | [name] | [0-3] | [one line] |

**Total: [sum] / 12**

═══════════════════════════════════════

## CLASSIFICATION RULES APPLIED

[List rules in order of evaluation. Mark which triggered.]

- [ ] Rule 1: BLOCKED (any dim = 0) → [TRIGGERED / not triggered]
- [ ] Rule 2: MEDIUM cap (any dim = 1) → [TRIGGERED / not triggered]
- [ ] Rule 3: HIGH (total ≥ 10, all dims ≥ 2) → [TRIGGERED / not triggered]
- [ ] Rule 4: MEDIUM (total 6-9, all dims ≥ 2) → [TRIGGERED / not triggered]
- [ ] Rule 5: LOW (total ≤ 5, all dims ≥ 2) → [TRIGGERED / not triggered]
- [ ] Rule 6: Fallback LOW → [TRIGGERED / not triggered]

**Determining rule: Rule [N]**

═══════════════════════════════════════

## FITNESS CLASSIFICATION: [HIGH / MEDIUM / LOW / BLOCKED]

═══════════════════════════════════════

## BLOCKERS

[If BLOCKED:]
| Dimension | Classification | Score | Remediation Path |
|-----------|---------------|-------|------------------|
| D[N] | [code] ([name]) | 0 | [remediation from tier1-scoring.md] |

[If not BLOCKED:]
No blockers identified.

## MEDIUM CAPS

[If any dim = 1:]
| Dimension | Classification | Score | Implication |
|-----------|---------------|-------|-------------|
| D[N] | [code] ([name]) | 1 | [implication text] |

[If no dim = 1:]
No MEDIUM caps active.

═══════════════════════════════════════

## CROSS-DIMENSION TENSION CHECK

Classifications at check time: D1=[T?] D2=[S?] D3=[I?] D4=[L?]

### Tensions Fired

[For each fired tension:]

**TENSION-[N]: [D?↔D?] — [name]**
- Severity: [HIGH/MEDIUM/LOW]
- Challenge presented: [summary]
- Resolution: [outcome]
- Classification changes: [none / D? changed from X to Y]

### Tensions Not Fired

[List by number: TENSION-1, TENSION-3, TENSION-5, etc.]

### Post-Tension Classifications

[If any changes:]
D1=[T?] D2=[S?] D3=[I?] D4=[L?] (updated from pre-tension)
Total: [updated sum] / 12
Fitness: [updated if changed]

[If no changes:]
No classification changes from tension check.

═══════════════════════════════════════

## FLAGGED CONCERNS

[Items that don't affect fitness classification but should inform Tier 2/3 decisions]

- [concern — source dimension — relevance to downstream]

## UNRESOLVED ITEMS

[Contradictions or tensions that were noted but not resolved]

- [item — recorded as annotation on D[N]]

═══════════════════════════════════════

## PATH CANDIDATES FOR TIER 2

Based on [FITNESS LEVEL], the following deployment paths are candidates:

[If HIGH:]
- Container-Native (full GitOps, HPA, rolling/canary)

[If MEDIUM:]
- Container-with-Constraints (containerize with documented workarounds)
- PaaS Abstraction (Cloud Run, App Engine — reduced operational burden)
- Hybrid (containerize what fits, VM what doesn't)

[If LOW:]
- VM/IaaS (traditional deployment)
- PaaS with heavy abstraction
- Refactor First (invest in addressing fitness gaps)

[If BLOCKED:]
- No path candidates until blocker(s) addressed.
- Recommended action: [remediation path(s)]

═══════════════════════════════════════

## PROCEED TO

[If not BLOCKED:] Tier 2 — Extrinsic Constraints (Phase 3: C1 → C2 → C3)
[If BLOCKED:] Assessment paused. Address blocker(s) and reassess.

## PARKING LOT FOR TIER 2/3

[Items from Phase 2 dialogue relevant to later tiers]
- [item → relevant for C?/S?]
```
