# Containerization Fitness & Deployment Path Assessment

Initiate a full three-phase assessment for the target repository/repositories.

## Arguments

`$ARGUMENTS` should contain one or more repository paths to assess. Example:
- Single repo: `/assess /path/to/repo`
- Multi-repo: `/assess /path/to/repo1 /path/to/repo2`

## Execution Protocol

### Pre-Flight

1. Parse `$ARGUMENTS` into a list of repository paths.
2. Verify each path exists and is accessible (read-only is sufficient).
3. Create `output/` directory if it doesn't exist.
4. Announce: state the repos being assessed, estimated timeline (~1.5-2.5 hours total), and that Phase 1 will run autonomously before interactive dialogue begins.

### Tooling Readiness (T0.5)

Load `reference/protocol/tooling-provisioning.md` and execute:

1. **Quick-scan** repo for file types: Dockerfiles, dependency manifests (package.json, go.mod, requirements.txt, pom.xml), K8s manifests, language markers.
2. **Determine applicable tools** per the criteria system in the provisioning reference.
3. **Present applicable tools list** to the human. Request blanket consent to install any that are missing during Phase 1.
4. **Record consent decision**: full consent, decline (with degradation warning and option to reconsider), or partial (per-tool).

### Phase 1: Autonomous Evidence Gathering (qwen3-Delegated)

**Privacy constraint:** Repository code must not reach Anthropic's API. Phase 1 static analysis is delegated to local qwen3 subagents via the Task tool. CC acts as orchestrator only — it invokes subagents, receives correlation summaries (structured abstractions, no raw code), and assembles them into the evidence package. CC does NOT read repository files directly during Phase 1.

Load `reference/protocol/phase1-evidence-gathering.md` as the evidence specification reference (describes what each subagent gathers).

Execute Phase 1 via sequential subagent invocations. Replace REPO_PATH with the actual repository path throughout.

**Step 1 — Tooling Provisioning:** Invoke the `tooling` subagent:
- Prompt: `"Scan the repository at REPO_PATH. Installation consent = TRUE. Return the tooling manifest."`
- From the returned manifest table, find every row where Status contains INSTALLED. Produce exactly one line:
  `"Installed tools: <name>, <name>, ..."` or `"Installed tools: none"`. Label this TOOLS_LINE.

**Step 2 — D1:** Invoke the `d1-topology` subagent:
- Prompt: `"Assess D1 Deployment Unit Topology for the repository at REPO_PATH.\n[TOOLS_LINE]\nFor Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d1-evidence-report.md and return the correlation summary."`
- Extract and retain the `## D1 Correlation Summary` block verbatim. Label D1_SUMMARY.

**Step 3 — D2:** Invoke the `d2-state-model` subagent with the same pattern. Output to `output/d2-evidence-report.md`. Label D2_SUMMARY.

**Step 4 — D3:** Invoke the `d3-independence` subagent with the same pattern. Output to `output/d3-evidence-report.md`. Label D3_SUMMARY.

**Step 5 — D4:** Invoke the `d4-lifecycle` subagent with the same pattern. Output to `output/d4-evidence-report.md`. Label D4_SUMMARY.

**Step 6 — Evidence Assembly:** Invoke the `evidence-assembler` subagent:
- Prompt: `"Assemble the Evidence Package for the repository at REPO_PATH.\n[TOOLS_LINE]\nD1 Summary:\n[D1_SUMMARY]\nD2 Summary:\n[D2_SUMMARY]\nD3 Summary:\n[D3_SUMMARY]\nD4 Summary:\n[D4_SUMMARY]\nRead the four evidence reports from output/ and write output/evidence-package.md."`
- Verify `output/evidence-package.md` exists before proceeding.

**If multi-repo:** After evidence assembly, present the repository boundary map and ask the human to confirm repo boundaries and service ownership.

Announce Phase 1 complete.

### Phase 1 Synthesis (T1.8)

Read `output/evidence-package.md`. Perform CC-level cross-dimension analysis to produce `output/synthesis-notes.md`.

1. **Evidence Quality Assessment** — Note tooling gaps, low-confidence findings, surface-scan limitations that reduce assessment reliability. Flag any dimension where evidence is insufficient to support a preliminary hypothesis.

2. **Cross-Dimension Tension Detection** — Check all four dimension summaries against each other. Surface tensions that span dimensions — these are frequently missed by subagents operating in isolation (e.g. a D2 state mechanism that invalidates a D4 lifecycle assumption). Check against `reference/tensions/cross-dimension-tensions.md` for known tension patterns.

3. **Scoring Hypotheses** — For the 2-3 most plausible operator configuration scenarios, estimate likely dimension scores and total fitness range. State what classification each scenario produces and which scenario the current evidence favors.

4. **Dialogue Agenda Sharpening** — Review the qwen3-proposed question selections from the evidence package. Replace with the 3-4 discriminating questions that most directly resolve the identified tensions and scoring uncertainties. A question that simultaneously resolves two tensions is worth more than two single-tension questions.

5. **Per-Dimension Starting Positions** — For each dimension, record: CC's Phase 2 entry hypothesis (which may differ from qwen3's), key open questions, and any classification-changing evidence that dialogue must resolve.

Write `output/synthesis-notes.md`.

**Validation pause:** Present a concise summary of synthesis-notes.md to the human:
- Evidence quality issues (if any)
- Cross-dimension tensions found (count and severity)
- Whether CC's scoring hypothesis differs from qwen3's preliminary classification
- Revised dialogue agenda (final question list)

Ask: "Review complete. Proceed to Phase 2 dialogue, or do you want to adjust the agenda first?"

Do not proceed to Phase 2 until the human confirms.

### Phase 2: Structured Assessment Dialogue

Load `reference/protocol/phase2-assessment-dialogue.md`.

For each dimension (D1, D2, D3, D4) sequentially:

1. Load the dimension's reference file (`reference/dimensions/dN-*.md`).
2. **Present Evidence** — Show what static analysis found, organized by strong/moderate/weak indicators. State confidence level.
3. **Propose Initial Classification** — Based on evidence, propose a classification with rationale. Make clear this is a proposal, not a determination.
4. **Gap Resolution** — Ask questions from the question bank that address ambiguities. Max 3 questions per dimension.
5. **Dialectical Challenges** — Load `reference/protocol/dialectical-challenges.md`. If triggers fire (evidence-statement contradictions or downstream implications), execute the challenge. Max rounds per the protocol.
6. **Lock Classification** — Record the final classification. Write to `output/dimension-dN.md` using `reference/templates/dimension-assessment.md`.

After all four dimensions are locked:

7. Load `reference/tensions/cross-dimension-tensions.md`. Check for cross-dimension tensions. Surface any that fire.
8. Load `reference/aggregation/tier1-scoring.md`. Calculate aggregate fitness.
9. Write `output/tier1-fitness-report.md` using `reference/templates/tier1-fitness-report.md`.
10. Present the Tier 1 result. If BLOCKED, stop and discuss remediation — do NOT proceed to Phase 3.

### Phase 3: Strategic Selection Guidance

Load `reference/protocol/phase3-strategic-guidance.md`.

**Phase 3A: Tier 2 Constraints**

For each constraint (C1, C2, C3) sequentially:
1. Load the constraint's reference file (`reference/constraints/cN-*.md`).
2. Ask the collection question. Collect classification.
3. Load `reference/aggregation/tier2-filtering.md`. Apply viability filter immediately. Report which paths survived.
4. After all three: write `output/constraint-map.md` using `reference/templates/constraint-map.md`.
5. If CONSTRAINT DEADLOCK: stop and discuss resolution.

**Phase 3B: Tier 3 Selections**

For each choice area (S1, S2, S3) sequentially:
1. Load the choice area's reference file (`reference/choices/sN-*.md`).
2. Present options narrowed by Tier 2 constraints.
3. Collect selection. Check for strategy tensions immediately.
4. Load `reference/tensions/strategy-tensions.md` as needed.

**Phase 3C: Profile Assembly**

1. Load `reference/templates/deployment-profile.md`.
2. Assemble the complete Deployment Profile from all outputs.
3. Present for human confirmation.
4. Handle any revision cascades per the protocol.
5. Write final `output/deployment-profile.md`.

### Completion

Announce assessment complete. Summarize the one-line Deployment Profile. Remind that this is Framework 1 output — migration execution planning is a separate activity.
