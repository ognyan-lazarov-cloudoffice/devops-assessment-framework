# Dialectical Challenge Mechanism

## Purpose

Structured challenges that fire on deterministic triggers. Not improvised debate — framework-derived validation that ensures classification accuracy.

**Key principle:** Challenges are bounded. Every trigger is pre-defined, every challenge has a max round count, and circuit breakers prevent Pyrrhic arguments.

---

## Three Categories

### Category 1: Evidence-Statement Contradictions

**When:** During per-dimension assessment (Phase 2, Layer 3)
**Trigger:** Human claim directly contradicts concrete static evidence
**Source:** Per-dimension dialectical trigger tables in `d1-*.md` through `d4-*.md`
**Max rounds:** 2 per trigger
**Circuit breaker:** Record as "noted contradiction — human classification stands, evidence `[X]` documented"

**Rules:**
- Only fires on CONCRETE evidence (file paths, specific configurations, measurable signals)
- Does NOT fire on absence of evidence ("I didn't find X" is not a contradiction of "we have X")
- Does NOT fire on weak indicators — only strong and moderate indicators
- Human wins after 2 rounds — their operational knowledge may explain what code cannot

**Agent behavior:**
1. State the contradiction clearly: "You said [X], but I found [Y] at [path]"
2. Ask for explanation: "Can you help me understand this discrepancy?"
3. If explanation is satisfactory: drop the challenge
4. If explanation doesn't resolve: present one more piece of evidence if available
5. After round 2: record and proceed regardless

### Category 2: Cross-Dimension Inconsistency

**When:** After ALL four dimensions are locked (before Tier 1 aggregation)
**Trigger:** Classification combination matches a pre-defined tension pattern
**Source:** `cross-dimension-tensions.md` (6 enumerated patterns)
**Max rounds:** 2 per tension
**Circuit breaker:** Record as "noted tension — classifications stand as locked"

**Rules:**
- Fires ONLY against the pre-defined catalog — no improvised cross-dimension challenges
- Can result in reclassification of one or both involved dimensions
- If reclassification occurs, recheck all tensions (one pass only — no loops)
- Resolution must be one of the pre-defined resolution paths for that tension

**Agent behavior:**
1. State which tension fired and why
2. Present the pre-defined challenge text from the catalog
3. Process human response against resolution paths
4. If resolved: update classifications if needed
5. If unresolved after 2 rounds: record and proceed

### Category 3: Downstream Implication Surfacing

**When:** At classification lock time during per-dimension assessment
**Trigger:** Classification activates a high-consequence rule
**Source:** Per-dimension dialectical trigger tables, "Category 3" section
**Max rounds:** 1 (this is informational, not adversarial)
**Circuit breaker:** N/A — always resolved in 1 round

**Rules:**
- Fires when classification = 0 (BLOCKED) or = 1 (MEDIUM cap)
- Purpose is NOT to change classification but to ensure informed consent
- Human must acknowledge the downstream consequence before lock
- No argument — just surfacing and confirming awareness

**High-consequence triggers:**

| Classification | Consequence | Surface Text |
|---|---|---|
| Any dim = 0 | BLOCKED — assessment halts at Tier 1 | "This classification triggers BLOCKED status. The assessment cannot proceed to deployment path selection until this is addressed. Understood?" |
| D2 S3 = 1 | MEDIUM cap — overall fitness capped at MEDIUM regardless of total | "S3 caps overall fitness at MEDIUM. Even if all other dimensions score 3 (total 10), the highest achievable fitness is MEDIUM. This is the #1 cause of container migration failures. Confirmed?" |
| D4 L3 = 1 | MEDIUM cap — same as above | "L3 caps overall fitness at MEDIUM. Slow startup, ungraceful shutdown, and hardcoded config create constant operational friction with the orchestrator. Confirmed?" |
| T3 = 2 (borderline) | Limits orchestration benefit when other dims are high | "T3 means the entire monolith scales as one unit. With your other dimensions scoring high, you'll have container-native infrastructure managing a monolith — which works but doesn't leverage per-service scaling, canary, or independent deployment." |

---

## Timing Summary

| Phase | Category 1 | Category 2 | Category 3 |
|-------|-----------|-----------|-----------|
| D1 Assessment | ✅ | ❌ | ✅ at lock |
| D2 Assessment | ✅ | ❌ | ✅ at lock |
| D3 Assessment | ✅ | ❌ | ✅ at lock |
| D4 Assessment | ✅ | ❌ | ✅ at lock |
| Cross-Dim Check | ❌ | ✅ | ❌ |

---

## Total Challenge Budget

Worst case (all triggers fire):
- Category 1: 4 dimensions × ~2 triggers each × 2 rounds = ~16 challenge rounds
- Category 2: 6 tensions × 2 rounds = ~12 challenge rounds  
- Category 3: 4 dimensions × 1 round = ~4 informational rounds

**Realistic case:** 4-8 Category 1 rounds, 2-4 Category 2 rounds, 1-2 Category 3 rounds = **7-14 total challenge rounds** adding ~15-20 minutes to the assessment.

---

## Recording Format

Every challenge interaction is recorded:

```
DIALECTICAL CHALLENGE RECORD
=============================

Category: [1/2/3]
Dimension(s): [D?/D?↔D?]
Trigger: [specific condition that fired]
Challenge presented: [text]

Round 1:
  Human response: [summary]
  Resolution: [resolved/unresolved/acknowledged]

Round 2 (if needed):
  Human response: [summary]
  Resolution: [resolved/unresolved]

Outcome: [classification change / no change / noted tension / acknowledged]
Classification impact: [none / D? changed from X to Y]
```
