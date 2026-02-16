# Task Registry

## Purpose

Authoritative definition of the assessment dependency chain. The agent reads this file to determine:
- What task comes next
- What must be complete before a task can start
- How to detect task completion (output file markers)
- Where to stop if a gate condition triggers

This is the SKELETON — procedural discipline. Domain logic lives in reference files. Execution protocol lives in slash commands.

---

## Task Dependency Chain

```
T0 Pre-Flight
 │
 ▼
T0.5 Tooling Readiness ───────────────── [AUTONOMOUS → DIALOGUE (consent)]
 │
 ▼
T1 Repository Analysis ─────────────── [AUTONOMOUS, includes adaptive tool install]
 │
 ▼
T1.5 Repo Boundary Confirmation ───── [DIALOGUE, multi-repo only]
 │
 ├──────┬──────┬──────┐
 ▼      ▼      ▼      ▼
T2     T3     T4     T5 ────────────── [DIALOGUE, sequential not parallel]
D1     D2     D3     D4
 │      │      │      │
 └──────┴──────┴──────┘
         │
         ▼
T5.5 Cross-Dimension Tension Check ── [AUTONOMOUS → DIALOGUE if tensions fire]
         │
         ▼
T6 Tier 1 Aggregation ──────────────── [AUTONOMOUS]
         │
         ▼
      ┌──┴──┐
      │GATE │ ◄── If BLOCKED: stop. Remediation required.
      └──┬──┘
         │
    ┌────┴────┐
    ▼         ▼
T7a  T7b  T7c ──────────────────────── [DIALOGUE, sequential]
C1   C2   C3
    │         │
    └────┬────┘
         │
         ▼
T7.5 Tier 2 Aggregation ────────────── [AUTONOMOUS]
         │
         ▼
      ┌──┴──┐
      │GATE │ ◄── If CONSTRAINT DEADLOCK: stop. Resolution required.
      └──┬──┘
         │
    ┌────┴────┐
    ▼         ▼
T8a  T8b  T8c ──────────────────────── [DIALOGUE, sequential]
S1   S2   S3
    │         │
    └────┬────┘
         │
         ▼
T9 Deployment Profile Assembly ──────── [AUTONOMOUS → DIALOGUE for confirmation]
         │
         ▼
T10 Completion ──────────────────────── [AUTONOMOUS]
```

---

## Task Definitions

### T0: Pre-Flight

| Field | Value |
|---|---|
| Mode | Autonomous |
| Blocked by | Nothing |
| Input | Repository path(s) from user |
| Action | Validate paths exist, create `output/`, announce assessment |
| Completion marker | `output/` directory exists |
| Gate | If any repo path invalid → stop, report error |
| Reference files | None |

### T0.5: Tooling Readiness

| Field | Value |
|---|---|
| Mode | Autonomous (quick scan) → Dialogue (consent) |
| Blocked by | T0 |
| Input | Repository path(s) |
| Action | Quick-scan repo for file types (Dockerfiles, manifests, language markers). Determine which static analysis tools are applicable per criteria in `protocol/tooling-provisioning.md`. Present applicable tools list. Collect blanket consent, decline, or partial consent. |
| Completion marker | Consent decision recorded (consent/decline/partial) |
| Gate | None — assessment proceeds regardless of consent decision (with degradation if declined) |
| Reference files | `protocol/tooling-provisioning.md` |
| Estimated duration | 1-2 min |

### T1: Repository Analysis

| Field | Value |
|---|---|
| Mode | Autonomous |
| Blocked by | T0.5 |
| Input | Validated repository path(s) |
| Action | Inventory repos, adaptively provision tools (check availability → install if consented → log status), run static analysis with available tools, assemble evidence with tooling manifest, generate dialogue agenda |
| Completion marker | `output/evidence-package.md` exists |
| Gate | None — always produces output even if tooling is limited |
| Reference files | `protocol/phase1-evidence-gathering.md`, `templates/evidence-package.md` |
| Estimated duration | 15-30 min |

### T1.5: Repo Boundary Confirmation

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T1 |
| Condition | **Multi-repo only.** Skip if single repo. |
| Input | Evidence package with repo boundary map |
| Action | Present boundary map, human confirms service ownership and repo relationships |
| Completion marker | Boundary map confirmed (noted in `output/evidence-package.md` or separate annotation) |
| Gate | Human must confirm before dimension assessments begin |
| Reference files | None (uses evidence package content) |

### T2: D1 Assessment (Deployment Unit Topology)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T1 (single-repo) or T1.5 (multi-repo) |
| Input | Evidence package D1 section |
| Action | Present evidence → propose classification → gap resolution (max 3 Qs) → dialectical challenges → lock |
| Completion marker | `output/dimension-d1.md` exists |
| Gate | Classification must be locked before T3 begins |
| Reference files | `dimensions/d1-deployment-unit-topology.md`, `protocol/phase2-assessment-dialogue.md`, `protocol/dialectical-challenges.md`, `templates/dimension-assessment.md` |
| Estimated duration | 10-15 min |

### T3: D2 Assessment (State and Data Model)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T2 |
| Input | Evidence package D2 section |
| Action | Same as T2 pattern |
| Completion marker | `output/dimension-d2.md` exists |
| Gate | Classification must be locked before T4 begins |
| Reference files | `dimensions/d2-state-and-data-model.md`, `protocol/phase2-assessment-dialogue.md`, `protocol/dialectical-challenges.md`, `templates/dimension-assessment.md` |
| Estimated duration | 10-15 min |

### T4: D3 Assessment (Independence Profile)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T3 |
| Input | Evidence package D3 section |
| Action | Same as T2 pattern |
| Completion marker | `output/dimension-d3.md` exists |
| Gate | Classification must be locked before T5 begins |
| Reference files | `dimensions/d3-independence-profile.md`, `protocol/phase2-assessment-dialogue.md`, `protocol/dialectical-challenges.md`, `templates/dimension-assessment.md` |
| Estimated duration | 10-15 min |

### T5: D4 Assessment (Lifecycle Compliance)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T4 |
| Input | Evidence package D4 section |
| Action | Same as T2 pattern |
| Completion marker | `output/dimension-d4.md` exists |
| Gate | Classification must be locked before T5.5 begins |
| Reference files | `dimensions/d4-lifecycle-compliance.md`, `protocol/phase2-assessment-dialogue.md`, `protocol/dialectical-challenges.md`, `templates/dimension-assessment.md` |
| Estimated duration | 10-15 min |

### T5.5: Cross-Dimension Tension Check

| Field | Value |
|---|---|
| Mode | Autonomous → Dialogue if tensions fire |
| Blocked by | T2, T3, T4, T5 (all four dimension assessments) |
| Input | All four locked dimension classifications |
| Action | Check tension catalog. If tensions fire → present to human for acknowledgment/resolution. |
| Completion marker | Tensions section populated in evidence or noted (no separate output file — tensions are recorded in `output/tier1-fitness-report.md` during T6) |
| Gate | All fired tensions must be either resolved or acknowledged before T6 |
| Reference files | `tensions/cross-dimension-tensions.md` |
| Estimated duration | 0-10 min (0 if no tensions fire) |

### T6: Tier 1 Aggregation

| Field | Value |
|---|---|
| Mode | Autonomous |
| Blocked by | T5.5 |
| Input | Four dimension scores + tension resolutions |
| Action | Calculate total score, apply threshold rules, determine fitness classification |
| Completion marker | `output/tier1-fitness-report.md` exists |
| **GATE** | **If fitness = BLOCKED → HARD STOP. Present remediation options. Do NOT proceed to T7.** |
| Reference files | `aggregation/tier1-scoring.md`, `templates/tier1-fitness-report.md` |

### T7a: C1 Constraint Collection (Infrastructure Availability)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T6 (and T6 gate must pass — not BLOCKED) |
| Input | Tier 1 fitness result, any infrastructure evidence from Phase 1 |
| Action | Ask collection question → classify → apply viability filter → report surviving paths |
| Completion marker | C1 classification recorded (held in memory until T7.5 writes constraint-map) |
| Gate | Classification locked before T7b |
| Reference files | `constraints/c1-infrastructure-availability.md`, `aggregation/tier2-filtering.md` |
| Estimated duration | 3-5 min |

### T7b: C2 Constraint Collection (Compliance Posture)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T7a |
| Input | C1 result + path viability status |
| Action | Same pattern as T7a |
| Completion marker | C2 classification recorded |
| Gate | Classification locked before T7c |
| Reference files | `constraints/c2-compliance-posture.md`, `aggregation/tier2-filtering.md` |
| Estimated duration | 5-10 min |

### T7c: C3 Constraint Collection (Organizational Topology)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T7b |
| Input | C1+C2 results + path viability status |
| Action | Same pattern as T7a. Include team capability sub-assessment. |
| Completion marker | C3 classification recorded |
| Gate | Classification locked before T7.5 |
| Reference files | `constraints/c3-organizational-topology.md`, `aggregation/tier2-filtering.md` |
| Estimated duration | 5-10 min |

### T7.5: Tier 2 Aggregation

| Field | Value |
|---|---|
| Mode | Autonomous |
| Blocked by | T7a, T7b, T7c |
| Input | Three constraint classifications + path viability filters |
| Action | Assemble constraint map, check for compound effects, determine final path viability |
| Completion marker | `output/constraint-map.md` exists |
| **GATE** | **If CONSTRAINT DEADLOCK → HARD STOP. Present resolution options. Do NOT proceed to T8.** |
| Reference files | `aggregation/tier2-filtering.md`, `templates/constraint-map.md` |

### T8a: S1 Selection (Lifecycle Stage)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T7.5 (and T7.5 gate must pass — no DEADLOCK) |
| Input | Surviving paths + accumulated requirements |
| Action | Present options → collect selection → check for immediate tensions |
| Completion marker | S1 selection recorded (held in memory until T9) |
| Gate | Selection locked before T8b |
| Reference files | `choices/s1-lifecycle-stage.md` |
| Estimated duration | 2-3 min |

### T8b: S2 Selection (Velocity Target)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T8a |
| Input | S1 selection + constraint map |
| Action | Present options narrowed by constraints → collect → check tensions → VT4 validation if applicable |
| Completion marker | S2 selection recorded |
| Gate | Selection locked before T8c. **VT4 validation must pass if selected.** |
| Reference files | `choices/s2-velocity-target.md`, `tensions/strategy-tensions.md` |
| Estimated duration | 5-10 min |

### T8c: S3 Selection (Risk Tolerance)

| Field | Value |
|---|---|
| Mode | Dialogue |
| Blocked by | T8b |
| Input | S1+S2 selections + constraint map |
| Action | Present options → collect → full strategy tension check → archetype matching |
| Completion marker | S3 selection recorded |
| Gate | All strategy tensions must be resolved or acknowledged |
| Reference files | `choices/s3-risk-tolerance.md`, `tensions/strategy-tensions.md`, `aggregation/tier3-composition.md` |
| Estimated duration | 5-10 min |

### T9: Deployment Profile Assembly

| Field | Value |
|---|---|
| Mode | Autonomous → Dialogue for confirmation |
| Blocked by | T8c |
| Input | All tier outputs (fitness report, constraint map, strategy selections) |
| Action | Assemble complete profile → present for human review → handle revision cascades → lock |
| Completion marker | `output/deployment-profile.md` exists |
| Gate | Human must confirm the profile. Revisions trigger cascades per protocol. |
| Reference files | `templates/deployment-profile.md`, `protocol/phase3-strategic-guidance.md` (cascade rules) |

### T10: Completion

| Field | Value |
|---|---|
| Mode | Autonomous |
| Blocked by | T9 |
| Input | Locked deployment profile |
| Action | Announce completion, present one-line summary, state framework boundary |
| Completion marker | Assessment complete |
| Reference files | None |

---

## State Detection Summary

For `/assess-resume` and general state awareness:

| Output File | Task Completed | Next Task |
|---|---|---|
| _(nothing)_ | None | T0 (or no assessment started) |
| `output/evidence-package.md` | T1 | T1.5 (multi-repo) or T2 |
| `output/dimension-d1.md` | T2 | T3 |
| `output/dimension-d2.md` | T3 | T4 |
| `output/dimension-d3.md` | T4 | T5 |
| `output/dimension-d4.md` | T5 | T5.5 → T6 |
| `output/tier1-fitness-report.md` | T6 | T7a (if not BLOCKED) |
| `output/constraint-map.md` | T7.5 | T8a (if no DEADLOCK) |
| `output/deployment-profile.md` | T9 | T10 (done) |

### Gate States

Gates are recorded inside the relevant output file:

- **BLOCKED** gate: `output/tier1-fitness-report.md` contains `Fitness Classification: BLOCKED`
- **DEADLOCK** gate: `output/constraint-map.md` contains `Deadlock detected: YES`

If a gate is active, `/assess-resume` should announce the gate state and wait for human direction rather than attempting to proceed.

---

## Timing Budget

| Phase | Tasks | Mode | Duration |
|---|---|---|---|
| Pre-flight | T0 | Autonomous | 1 min |
| Phase 1 | T1, T1.5 | Autonomous + brief dialogue | 15-30 min |
| Phase 2 | T2-T5, T5.5, T6 | Dialogue | 40-60 min |
| Phase 3 | T7a-T7c, T7.5, T8a-T8c, T9, T10 | Dialogue | 35-65 min |
| **Total** | | | **~1.5-2.5 hours** |

---

## Invariants

Rules that must hold across all tasks. Violation of any invariant is a protocol error.

1. **Sequential enforcement:** No task executes before all its blockers are complete.
2. **One dimension at a time:** T2, T3, T4, T5 never overlap or interleave.
3. **Gate respect:** BLOCKED and DEADLOCK gates halt forward progress unconditionally.
4. **Output immutability:** Once written, output files are only modified via explicit re-assessment (`/assess-dimension`) with cascade handling.
5. **Reference file scoping:** Each task loads only the reference files listed in its definition. No bulk loading.
6. **Human authority:** In dialogue tasks, human classification/selection overrides agent proposal. Always.
7. **Circuit breakers:** Dialectical challenges respect max round limits. No infinite loops.
