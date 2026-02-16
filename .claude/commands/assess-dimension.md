# Re-Assess a Specific Dimension

Re-open a previously locked dimension classification for revision.

## Arguments

`$ARGUMENTS` must specify which dimension to re-assess: `d1`, `d2`, `d3`, or `d4`.

Example: `/assess-dimension d3`

## Protocol

1. Parse `$ARGUMENTS` to identify the target dimension.
2. Verify `output/dimension-dN.md` exists (cannot re-assess what hasn't been assessed).
3. Read the existing assessment from `output/dimension-dN.md`. Present: "Current classification: [code] [name] (score [N]). Locked based on: [key evidence/rationale]."
4. Ask: "What has changed or what was incorrect?"
5. Load the dimension's reference file (`reference/dimensions/dN-*.md`).
6. Run through the classification decision tree with the new information.
7. If classification changes: update `output/dimension-dN.md`.

## Cascade Warning

If the new classification differs from the locked one, warn about cascading effects:

- **Score change** → Tier 1 fitness may change → path viability may change → strategy may need revision.
- **If Tier 1 report already exists** (`output/tier1-fitness-report.md`): re-run Tier 1 aggregation. Load `reference/aggregation/tier1-scoring.md` and recalculate.
- **If constraint map exists** (`output/constraint-map.md`): re-filter paths. Load `reference/aggregation/tier2-filtering.md`.
- **If deployment profile exists** (`output/deployment-profile.md`): mark as STALE. Full profile must be re-validated.

State clearly what will be recalculated and ask for confirmation before proceeding.

## Cross-Dimension Tension Re-Check

After relocking the revised dimension, re-run cross-dimension tension checks against all other locked dimensions. Load `reference/tensions/cross-dimension-tensions.md`.
