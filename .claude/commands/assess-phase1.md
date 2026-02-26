# Phase 1 Evidence Gathering

Run Phase 1 static analysis for the target repository via local qwen3 subagents.
Use this command in the qwen3 CC session (local model). Do NOT use /assess in the qwen3 session.

## Arguments

`$ARGUMENTS` contains the absolute path to the repository to assess.

## Execution

Follow these steps precisely. Do NOT write any files yourself. Do NOT run any bash commands or read any files between steps — your only permitted actions are invoking the specified subagents via the Task tool and tracking their results.

IMPORTANT — subagent result retrieval: Each subagent call (Task tool) is synchronous. The result is returned directly in the tool response — you already have it the moment the call completes. Do NOT call TaskOutput after any subagent call. TaskOutput calls will always fail with "No task found". If you see that error, ignore it completely and proceed immediately to the next step using the result you already received. Never re-run a subagent because of a TaskOutput failure.

---

**Step 1:** Invoke the `tooling` subagent with this exact prompt (replace REPO_PATH with $ARGUMENTS):

"Scan the repository at REPO_PATH. Installation consent = TRUE. Return the tooling manifest."

**Step 2:** From the returned manifest table, find every row where Status contains INSTALLED. Produce exactly one line:
`Installed tools: <name>, <name>, ...` — or `Installed tools: none` if no rows have INSTALLED status.
Label this line TOOLS_LINE.
Do NOT verify any tool installation yourself. Do NOT run any commands to check tool availability. The tooling subagent's report is the authoritative source — use it exactly as returned and proceed immediately to Step 3.

**Step 3:** Invoke the `d1-topology` subagent with this exact prompt (replace REPO_PATH with $ARGUMENTS, replace [TOOLS_LINE] with the line from Step 2):

"Assess D1 Deployment Unit Topology for the repository at REPO_PATH.
[TOOLS_LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d1-evidence-report.md and return the correlation summary."

**Step 4:** From the result, find the block starting with `## D1 Correlation Summary`. Copy it verbatim. Label it D1_SUMMARY.

**Step 5:** Invoke the `d2-state-model` subagent with this exact prompt:

"Assess D2 State and Data Model for the repository at REPO_PATH.
[TOOLS_LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d2-evidence-report.md and return the correlation summary."

**Step 6:** From the result, find the block starting with `## D2 Correlation Summary`. Copy it verbatim. Label it D2_SUMMARY.

**Step 7:** Invoke the `d3-independence` subagent with this exact prompt:

"Assess D3 Independence Profile for the repository at REPO_PATH.
[TOOLS_LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d3-evidence-report.md and return the correlation summary."

**Step 8:** From the result, find the block starting with `## D3 Correlation Summary`. Copy it verbatim. Label it D3_SUMMARY.

**Step 9:** Invoke the `d4-lifecycle` subagent with this exact prompt:

"Assess D4 Lifecycle Compliance for the repository at REPO_PATH.
[TOOLS_LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d4-evidence-report.md and return the correlation summary."

**Step 10:** From the result, find the block starting with `## D4 Correlation Summary`. Copy it verbatim. Label it D4_SUMMARY.

**Step 11:** Invoke the `evidence-assembler` subagent with this exact prompt (replace all placeholders):

"Assemble the Evidence Package for the repository at REPO_PATH.
[TOOLS_LINE]
D1 Summary:
[D1_SUMMARY]
D2 Summary:
[D2_SUMMARY]
D3 Summary:
[D3_SUMMARY]
D4 Summary:
[D4_SUMMARY]
Read the four evidence reports from output/ and write output/evidence-package.md."

**Step 12:** Confirm `output/evidence-package.md` was written. Report exactly this and nothing else:

"Phase 1 complete. output/evidence-package.md written. Switch to the CC session (Anthropic API) and run /assess-resume to proceed with synthesis."
