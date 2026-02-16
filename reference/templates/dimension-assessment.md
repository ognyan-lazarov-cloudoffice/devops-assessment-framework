# Template: Dimension Assessment Record

## Purpose

Per-dimension record produced at classification lock. One per dimension (4 total).

---

## Template

```markdown
# DIMENSION ASSESSMENT: D[N] — [Dimension Name]

## Classification

**Code:** [T?/S?/I?/L?]
**Name:** [classification name]
**Score:** [0/1/2/3]
**Locked by:** [human confirmed / human override]

## Evidence Summary

### Static Evidence (from Phase 1)
- [indicator]: `[path]` → [classification implication]
- [indicator]: `[path]` → [classification implication]

### Dialogue Evidence (from Phase 2)
- [human statement/confirmation mapped to framework element]
- [human statement/confirmation mapped to framework element]

## Gap Resolution

| Question Asked | Human Response | Classification Impact |
|---|---|---|
| [Q-D?-N] | [summary of response] | [confirmed/shifted hypothesis from X to Y] |
| [Q-D?-N] | [summary of response] | [confirmed/shifted] |

Gaps remaining after dialogue: [none / list]

## Dialectical Challenges

### Category 1 (Evidence-Statement Contradictions)
[If fired:]
- Trigger: [condition]
- Challenge: [text presented]
- Resolution: [resolved in round 1/2 — human explained X / unresolved — noted]
- Impact: [none / classification changed]

[If none fired:]
- No evidence-statement contradictions identified.

### Category 3 (Downstream Implications)
[If fired:]
- Trigger: [score = 0 or = 1 or borderline condition]
- Implication surfaced: [text]
- Human acknowledgment: [confirmed understanding / requested clarification]

[If none fired:]
- No downstream implications to surface.

## Classification Rationale

[2-3 sentence summary of WHY this classification was chosen, referencing the strongest evidence and dialogue outcomes]

## Annotations

[Any overrides, noted contradictions, confidence caveats, or parking lot items]
- [annotation]

## Metadata

- Assessment duration: [X minutes]
- Questions asked: [N of max 3]
- Challenges fired: [N]
- Human overrides: [Y/N — if Y, from what to what]
```
