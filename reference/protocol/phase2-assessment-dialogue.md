# Phase 2: Structured Assessment Dialogue

## Purpose

The primary value generator. Static analysis produced the agenda and evidence; dialogue produces the actual assessment. Every question traces to a specific framework element. No exploratory conversation.

**Time budget:** 70-90 minutes human engagement.
**Participants:** Agent (assessment facilitator) + Human (domain expert).

---

## Ground Rules

1. **Every agent question must map to a framework element.** No "tell me more about your architecture" fishing expeditions.
2. **Human always wins classification decision** but agent ensures full awareness of contradictions.
3. **Framework permits disagreement but requires acknowledgment** — if human overrides evidence, the override is documented, not suppressed.
4. **Dimensions assessed in fixed order:** D1 → D2 → D3 → D4. No skipping, no reordering.
5. **Cross-dimension tension check fires after D4 lock,** before Tier 1 aggregation.

---

## Per-Dimension Assessment Template

Each dimension follows this exact sequence. No deviation.

### Layer 1: Evidence Presentation (~3-5 min per dimension)

**Agent presents:**
1. Static evidence summary (strongest indicators first)
2. Preliminary hypothesis with confidence level
3. Specific gaps identified

**Format:**
> **D[N] Assessment: [Dimension Name]**
> 
> Here's what I found in the code:
> - [Strong indicator 1] at `[path]` → suggests [classification]
> - [Strong indicator 2] at `[path]` → suggests [classification]
> - [Moderate indicator] at `[path]` → suggests [classification]
> 
> Based on static analysis, my preliminary hypothesis is **[classification]** with **[HIGH/MEDIUM/LOW]** confidence.
> 
> **Gaps I cannot determine from code:**
> - [gap 1]
> - [gap 2]

**Human responds** with confirmation, correction, or additional context.

### Layer 2: Gap Resolution (~5-10 min per dimension)

**Agent asks gap-resolution questions** from the dimension's question bank. Only questions triggered by actual gaps — never all three.

**Rules:**
- Max 3 gap-resolution questions per dimension
- Questions come from the pre-defined question bank ONLY (see dimension reference files)
- Each question maps to a specific classification boundary
- Agent maps human answers to framework classifications in real-time

**If human's answers resolve all gaps:** Proceed to Layer 3.
**If ambiguity remains after 3 questions:** Note remaining uncertainty and proceed. Do not invent additional questions.

### Layer 3: Dialectical Challenge (~3-5 min per dimension, may be 0 min)

Three categories of challenges. All have deterministic triggers — they fire or they don't based on conditions, not agent judgment.

#### Category 1: Evidence-Statement Contradictions

**Trigger:** Human claim directly contradicts static evidence.
**Source:** Per-dimension dialectical trigger tables in dimension reference files.
**Max rounds:** 2 per trigger.
**Circuit breaker:** After 2 rounds, record as "noted contradiction — human classification stands, evidence documented."

#### Category 2: Cross-Dimension Inconsistency

**Trigger:** NOT during per-dimension assessment. Fires ONLY during the cross-dimension tension check after all four dimensions are locked.
**Source:** `cross-dimension-tensions.md` catalog.
**Max rounds:** 2 per tension.

#### Category 3: Downstream Implication Surfacing

**Trigger:** At classification lock time, when the classification activates a high-consequence rule (=0 BLOCKED, =1 MEDIUM cap).
**Source:** Per-dimension dialectical trigger tables, "Category 3" section.
**Max rounds:** 1 per trigger.
**Purpose:** Not to change the classification but to ensure the human understands the downstream consequences before locking.

### Layer 4: Classification Lock (~1 min per dimension)

**Agent proposes classification** based on all evidence and dialogue:

> Based on the evidence and our discussion, I'm classifying D[N] as **[Code] ([Name]) = [Score]**.
> 
> Rationale: [one-line summary of key deciding factors]
> 
> [If any dialectical challenges were raised:]
> Noted tensions: [list]
> 
> Do you confirm this classification?

**Human confirms or overrides.**

**If human overrides:**
> Understood. Recording D[N] as **[human's classification]** with annotation: [reason for divergence from agent recommendation].

**Classification is now LOCKED.** No revisiting unless a cross-dimension tension check (after D4) surfaces a reclassification need.

---

## Dimension Assessment Order

| Sequence | Dimension | Typical Duration | Notes |
|----------|-----------|-----------------|-------|
| 1st | D1 Deployment Unit Topology | 10-15 min | Sets architectural context for all subsequent dimensions |
| 2nd | D2 State and Data Model | 10-15 min | State patterns inform D3 independence assessment |
| 3rd | D3 Independence Profile | 15-20 min | Lowest static ceiling — most dialogue-dependent |
| 4th | D4 Lifecycle Compliance | 10-15 min | Highest static ceiling — dialogue confirms/disconfirms |

**D3 gets the most time** because static analysis covers only 40-50%, so dialogue carries most of the assessment weight.

---

## Cross-Dimension Tension Check

**Fires:** After D4 is locked, before Tier 1 aggregation.
**Duration:** 5-15 min depending on how many tensions fire.
**Source:** `cross-dimension-tensions.md`

**Procedure:**

1. Load all 6 tension patterns
2. Check each against current D1-D4 classifications
3. For each match: surface the challenge, allow max 2 rounds
4. If a tension resolves with a classification change:
   - Update the classification
   - Recheck ALL tensions against updated set (one pass only)
5. Record all tensions (fired and not fired) in the tension summary

---

## Anti-Drift Enforcement

### Structural (Layer 1)

Dimension order is fixed. Cannot skip ahead. Cannot revisit unless tension check mandates.

### Conversational (Layer 2)

Agent selects questions ONLY from the pre-defined question bank. If human raises a topic outside current dimension scope:

> That's relevant to [D?/Tier 2/Tier 3] — I'll note it and we'll address it when we get there. For now, let's stay with D[N].

**Parking lot:** Agent maintains a list of out-of-scope topics raised during Phase 2 and surfaces them at the appropriate time.

### Validation (Layer 3)

Every human response is mapped to a framework classification. If a response doesn't map cleanly:

> I want to make sure I'm mapping this correctly. When you say [human statement], in framework terms that sounds closest to [classification]. Is that accurate?

---

## Session Persistence

If Phase 2 must be split across sessions:

1. **Save:** All locked classifications, unlocked evidence, current dimension, parking lot
2. **Resume:** Present summary of locked classifications, resume at current dimension Layer 1
3. **No re-assessment** of locked dimensions unless human explicitly requests

---

## Phase 2 Output

1. **Four locked dimension classifications** with scores, rationales, and annotations
2. **Cross-dimension tension check results**
3. **Parking lot items** for Tier 2/3
4. Ready for Tier 1 aggregation (Task 6)
