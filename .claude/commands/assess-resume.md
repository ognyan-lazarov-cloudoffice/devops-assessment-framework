# Resume Interrupted Assessment

Resume a previously interrupted assessment from the last completed checkpoint.

## Arguments

`$ARGUMENTS` is optional. If provided, it specifies which phase or dimension to resume from (e.g., `phase2-d3`, `phase3-c2`). If not provided, auto-detect from output files.

## State Detection

Load `.claude/task-registry.md` and use the **State Detection Summary** table as the authoritative mapping from output files to task progress.

Check `output/` directory to determine assessment progress:

| File Present | Implies Completed | Next Task |
|---|---|---|
| `output/evidence-package.md` (no synthesis-notes.md) | T1 — Phase 1 complete | T1.8 Synthesis |
| `output/synthesis-notes.md` | T1.8 — Synthesis complete | T1.5 (multi-repo) or T2 |
| `output/dimension-d1.md` | T2 — D1 locked | T3 |
| `output/dimension-d2.md` | T3 — D2 locked | T4 |
| `output/dimension-d3.md` | T4 — D3 locked | T5 |
| `output/dimension-d4.md` | T5 — D4 locked | T5.5 → T6 |
| `output/tier1-fitness-report.md` | T6 — Tier 1 complete | T7a (if not BLOCKED) |
| `output/constraint-map.md` | T7.5 — Tier 2 complete | T8a (if no DEADLOCK) |
| `output/deployment-profile.md` | T9 — Assessment complete | Nothing to resume |

## Resume Logic

1. Load `.claude/task-registry.md`.
2. Scan `output/` for existing files.
3. Map files to completed tasks using the State Detection Summary.
4. **Check gate states:**
   - If `output/tier1-fitness-report.md` contains `BLOCKED` → announce gate state, do NOT proceed past T6.
   - If `output/constraint-map.md` contains `Deadlock detected: YES` → announce gate state, do NOT proceed past T7.5.
5. Determine the next task from the dependency chain.
6. Announce: "Assessment state detected. Last completed: [task]. Resuming from: [next task]."
7. Load the reference files specified in the task registry for the next task.
8. **If next task is T1.8 (evidence-package.md exists, synthesis-notes.md does not):**
   Read `output/evidence-package.md` and perform CC-level cross-dimension analysis to produce `output/synthesis-notes.md`:
   1. **Evidence Quality Assessment** — Note tooling gaps, low-confidence findings, surface-scan limitations. Flag dimensions where evidence is insufficient to support a preliminary hypothesis.
   2. **Cross-Dimension Tension Detection** — Check all four dimension summaries against each other for tensions that span dimensions (frequently missed by subagents operating in isolation). Load `reference/tensions/cross-dimension-tensions.md` for known tension patterns.
   3. **Scoring Hypotheses** — For the 2-3 most plausible operator configuration scenarios, estimate likely dimension scores and total fitness range.
   4. **Dialogue Agenda Sharpening** — Review the qwen3-proposed questions from the evidence package. Replace with the 3-4 discriminating questions that most directly resolve identified tensions. A question resolving two tensions simultaneously is worth more than two single-tension questions.
   5. **Per-Dimension Starting Positions** — For each dimension: CC's Phase 2 entry hypothesis, key open questions, classification-changing evidence that dialogue must resolve.
   Write `output/synthesis-notes.md`.
   **Validation pause:** Present a concise summary to the human:
   - Evidence quality issues (if any)
   - Cross-dimension tensions found (count and severity)
   - Whether CC's scoring hypothesis differs from qwen3's preliminary classification
   - Revised dialogue agenda (final question list)
   Ask: "T1.8 synthesis complete. Proceed to Phase 2 dialogue, or do you want to adjust the agenda first?"
   Do not proceed to T2 until the human confirms.
9. If resuming mid-Phase 2 (some dimensions locked, others not): present a brief summary of locked dimensions before continuing with the next unlocked dimension.
10. If resuming at Phase 3: re-read the Tier 1 fitness report to re-establish context before collecting constraints.

## Critical Rule

Do NOT re-assess already-locked dimensions unless the human explicitly requests it. Locked classifications are final. If the human wants to change a locked classification, use `/assess-dimension` instead.

## If No State Found

If `output/` is empty or doesn't exist:
> "No assessment state found. Use `/assess [repo-path]` to start a new assessment."
