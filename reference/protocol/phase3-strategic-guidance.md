# Phase 3: Strategic Selection Guidance

## Purpose

Guide the human through Tier 2 constraint collection and Tier 3 strategic selection. Phase 3 produces the complete Deployment Profile — the final framework output.

---

## Prerequisites

- Phase 2 complete: All four dimension assessments locked, Tier 1 fitness classification produced.
- **If Tier 1 = BLOCKED:** Phase 3 does NOT proceed. Remediation required first. Record BLOCKED status in final output.

---

## Phase 3 Structure

```
Phase 3
├── 3A: Tier 2 Constraint Collection (C1 → C2 → C3)
│   ├── Present Tier 1 result as context
│   ├── Collect constraints sequentially
│   ├── Apply path viability matrix
│   ├── Check for CONSTRAINT DEADLOCK
│   └── OUTPUT: Constraint Map
│
├── 3B: Tier 3 Strategic Selection (S1 → S2 → S3)
│   ├── Present surviving paths + accumulated requirements
│   ├── Collect selections sequentially
│   ├── Check for strategy tensions
│   ├── Validate against archetypes
│   └── OUTPUT: Tier 3 Selections
│
└── 3C: Deployment Profile Assembly
    ├── Synthesize Tiers 1+2+3
    ├── Present complete profile for confirmation
    └── OUTPUT: Complete Deployment Profile
```

---

## Phase 3A: Tier 2 Constraint Collection

### Protocol

For each constraint (C1, then C2, then C3):

1. **State the constraint question** from the constraint reference file.
2. **Present any static evidence** if available (e.g., Kubernetes manifests found in repo suggest IA1/IA2).
3. **Collect the classification** from the human.
4. **Apply the viability filter** immediately — inform the human which paths survived.
5. **Accumulate requirements** — list what this constraint adds to surviving paths.

### Timing

- C1: 3-5 minutes (usually clear-cut)
- C2: 5-10 minutes (may require discussion of specific regulatory frameworks)
- C3: 5-10 minutes (team structure can be nuanced)
- Total 3A: ~15-25 minutes

### Anti-Drift Rules

- One constraint at a time. Do not combine.
- Apply immediately after classification. The human sees the filter effect in real time.
- If CONSTRAINT DEADLOCK detected: **stop 3A.** Present deadlock with resolution options. Do not proceed to 3B until resolved.

### Transition to 3B

Present the Constraint Map summary:
> "Based on constraints [C1=IA?, C2=CP?, C3=O?], the surviving deployment paths are: [list]. The accumulated requirements are: [summary]. Now we'll determine the deployment strategy."

---

## Phase 3B: Tier 3 Strategic Selection

### Protocol

For each choice area (S1, then S2, then S3):

1. **State the choice question** from the choice area reference file.
2. **Present options NARROWED by Tier 2 constraints** — don't offer options that Tier 2 has made infeasible.
3. **Collect the selection** from the human.
4. **Check for strategy tensions** against the catalog immediately after each selection.
5. **If tension detected:** Surface it. Human resolves (adjust, accept, invest, escalate).

### Timing

- S1: 2-3 minutes (lifecycle stage is usually obvious)
- S2: 5-10 minutes (velocity often triggers discussion about current vs desired state)
- S3: 5-10 minutes (risk tolerance requires understanding of current deployment pain)
- Tension resolution: 0-10 minutes depending on count and severity
- Total 3B: ~15-30 minutes

### VT4 Validation (Mandatory)

If S2=VT4 is selected, **always** execute the VT4 validation rule:
> "VT4 (Coordinated) requires validation: is this coordination driven by business need or by technical coupling? If technical coupling, this may indicate D1/D3 should be revisited."

### Archetype Check

After all three selections are made:
1. Check if the combination matches a known execution archetype.
2. If match: "Your selections align with the [archetype name] pattern: [brief description]. Does this feel right?"
3. If no match: "Your selections don't match a common pattern — that's not wrong, but it's unusual. The combination is: [summary]. Is this intentional?"

### Transition to 3C

> "All strategic selections are complete. Let me assemble the complete Deployment Profile."

---

## Phase 3C: Deployment Profile Assembly

### Protocol

1. **Synthesize all three tiers** into the Deployment Profile template.
2. **Present the complete profile** to the human for review.
3. **Allow corrections** — any field can be revised. Revisions may cascade (changing a Tier 1 score changes fitness, which changes viable paths, etc.).
4. **Lock the profile** when the human confirms.

### Cascade Rules

If the human requests a revision during 3C:

| Revised Element | Cascade |
|---|---|
| Tier 1 dimension score | Recalculate fitness → re-filter paths → re-validate strategy |
| Tier 2 constraint | Re-filter paths → re-validate strategy |
| Tier 3 selection | Re-check tensions → re-validate archetype |

### Final Output

The locked Deployment Profile is the complete framework output. See `templates/deployment-profile.md` for the template.

---

## Total Phase 3 Timing

| Sub-phase | Duration |
|---|---|
| 3A Constraint Collection | 15-25 min |
| 3B Strategic Selection | 15-30 min |
| 3C Profile Assembly | 5-10 min |
| **Total Phase 3** | **35-65 min** |

Combined with Phases 1-2, total assessment envelope: **1.5-2.5 hours**.

---

## Phase 3 Dialogue Tone

Phase 3 collects information the agent CANNOT know from code. The agent's role shifts from "evidence presenter" (Phase 2) to "structured interviewer" (Phase 3). Questions are direct. The agent:

- Presents options clearly with brief explanations
- Does NOT elaborate at length on each option (the human is a domain expert)
- Challenges unusual combinations via the tension catalog
- Does NOT advocate for specific selections (human choice is sovereign in Tier 3)
- Moves efficiently — Phase 3 should feel like a well-run intake form, not a philosophy seminar
