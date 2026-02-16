# Resume Interrupted Assessment

Resume a previously interrupted assessment from the last completed checkpoint.

## Arguments

`$ARGUMENTS` is optional. If provided, it specifies which phase or dimension to resume from (e.g., `phase2-d3`, `phase3-c2`). If not provided, auto-detect from output files.

## State Detection

Load `.claude/task-registry.md` and use the **State Detection Summary** table as the authoritative mapping from output files to task progress.

Check `output/` directory to determine assessment progress:

| File Present | Implies Completed |
|---|---|
| `output/evidence-package.md` | Phase 1 complete |
| `output/dimension-d1.md` | D1 assessment locked |
| `output/dimension-d2.md` | D2 assessment locked |
| `output/dimension-d3.md` | D3 assessment locked |
| `output/dimension-d4.md` | D4 assessment locked |
| `output/tier1-fitness-report.md` | Tier 1 aggregation complete |
| `output/constraint-map.md` | Tier 2 complete |
| `output/deployment-profile.md` | Assessment complete (nothing to resume) |

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
8. If resuming mid-Phase 2 (some dimensions locked, others not): present a brief summary of locked dimensions before continuing with the next unlocked dimension.
9. If resuming at Phase 3: re-read the Tier 1 fitness report to re-establish context before collecting constraints.

## Critical Rule

Do NOT re-assess already-locked dimensions unless the human explicitly requests it. Locked classifications are final. If the human wants to change a locked classification, use `/assess-dimension` instead.

## If No State Found

If `output/` is empty or doesn't exist:
> "No assessment state found. Use `/assess [repo-path]` to start a new assessment."
