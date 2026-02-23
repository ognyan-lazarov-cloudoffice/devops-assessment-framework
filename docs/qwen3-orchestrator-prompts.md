# qwen3 Orchestrator Prompts

Operational prompts for the qwen3 direct Ollama session. These are pasted into the qwen3 Claude Code session to drive subagent invocations.

---

## Stage 2 / Task 2.4–2.5 — D4 Single-Dimension Assessment

Validated as of session 15. Produces consistent L2 classification with file written reliably.

```
Follow these steps precisely. Do NOT invoke any Task tool. Do NOT write any files yourself.

Step 1: Invoke the tooling subagent — subagent type name is exactly tooling — with this prompt:
"Scan the repository at /home/ext_ognyan_lazarov_cloudoffice_b/repos/testing/stage2/prometheus. Installation consent = TRUE. Return the tooling manifest."

Step 2: The tooling subagent returns a manifest table. Read that table directly — do not do any additional investigation of your own. Find every row where the Status column contains the word INSTALLED. Write a single line in this exact format:
"Installed tools: <name>, <name>, ..." — or "Installed tools: none" if no rows have INSTALLED status.

Step 3: Invoke the d4-lifecycle subagent — subagent type name is exactly d4-lifecycle — with a prompt constructed as follows. Replace [LINE] with the line you produced in Step 2:

"Assess D4 Lifecycle Compliance for the repository at /home/ext_ognyan_lazarov_cloudoffice_b/repos/testing/stage2/prometheus.
[LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d4-evidence-report.md and return the correlation summary."

Step 4: Report back the exact correlation summary returned by the d4-lifecycle subagent and confirm that output/d4-evidence-report.md was written. Do nothing else.
```

### Operational notes
- Full session restart required between runs (not /clear)
- After VM stop/start: `sudo systemctl restart ollama` then warm-up curl before starting session
- Warm-up curl: `curl -s http://localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"qwen3-coder:30b-a3b-q8_0","messages":[{"role":"user","content":"hi"}],"stream":false}'`

---

## Stage 3 / Task 3.2 — Full Ensemble Orchestration

Replace REPO_PATH with the actual repository path before pasting.

```
Follow these steps precisely. Do NOT invoke any Task tool. Do NOT write any files yourself.

Step 1: Invoke the tooling subagent — subagent type name is exactly tooling — with this prompt:
"Scan the repository at REPO_PATH. Installation consent = TRUE. Return the tooling manifest."

Step 2: The tooling subagent returns a manifest table. Read that table directly — do not do any additional investigation of your own. Find every row where the Status column contains the word INSTALLED. Write a single line in this exact format:
"Installed tools: <name>, <name>, ..." — or "Installed tools: none" if no rows have INSTALLED status.

Step 3: Invoke the d1-topology subagent — subagent type name is exactly d1-topology — with a prompt constructed as follows. Replace [LINE] with the line you produced in Step 2:

"Assess D1 Deployment Unit Topology for the repository at REPO_PATH.
[LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d1-evidence-report.md and return the correlation summary."

Step 4: The d1-topology subagent returns a message. Find the block that starts with the line "## D1 Correlation Summary" and ends at the end of that message. Copy that entire block verbatim. Label it internally as D1_SUMMARY. Do not paraphrase, do not shorten, do not add commentary.

Step 5: Invoke the d2-state-model subagent — subagent type name is exactly d2-state-model — with a prompt constructed as follows. Replace [LINE] with the line you produced in Step 2:

"Assess D2 State and Data Model for the repository at REPO_PATH.
[LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d2-evidence-report.md and return the correlation summary."

Step 6: The d2-state-model subagent returns a message. Find the block that starts with the line "## D2 Correlation Summary" and ends at the end of that message. Copy that entire block verbatim. Label it internally as D2_SUMMARY. Do not paraphrase, do not shorten, do not add commentary.

Step 7: Invoke the d3-independence subagent — subagent type name is exactly d3-independence — with a prompt constructed as follows. Replace [LINE] with the line you produced in Step 2:

"Assess D3 Independence Profile for the repository at REPO_PATH.
[LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d3-evidence-report.md and return the correlation summary."

Step 8: The d3-independence subagent returns a message. Find the block that starts with the line "## D3 Correlation Summary" and ends at the end of that message. Copy that entire block verbatim. Label it internally as D3_SUMMARY. Do not paraphrase, do not shorten, do not add commentary.

Step 9: Invoke the d4-lifecycle subagent — subagent type name is exactly d4-lifecycle — with a prompt constructed as follows. Replace [LINE] with the line you produced in Step 2:

"Assess D4 Lifecycle Compliance for the repository at REPO_PATH.
[LINE]
For Step 6b: run each tool listed as installed above against the repository. Write the evidence report to output/d4-evidence-report.md and return the correlation summary."

Step 10: The d4-lifecycle subagent returns a message. Find the block that starts with the line "## D4 Correlation Summary" and ends at the end of that message. Copy that entire block verbatim. Label it internally as D4_SUMMARY. Do not paraphrase, do not shorten, do not add commentary.

Step 11: Invoke the evidence-assembler subagent — subagent type name is exactly evidence-assembler — with the following prompt. Replace [LINE] with the line from Step 2, [D1_SUMMARY] with the block from Step 4, [D2_SUMMARY] with the block from Step 6, [D3_SUMMARY] with the block from Step 8, [D4_SUMMARY] with the block from Step 10:

"Assemble the Evidence Package for the repository at REPO_PATH.
[LINE]
D1 Summary:
[D1_SUMMARY]
D2 Summary:
[D2_SUMMARY]
D3 Summary:
[D3_SUMMARY]
D4 Summary:
[D4_SUMMARY]
Read the four evidence reports from output/ and write output/evidence-package.md."

Step 12: Report back the single confirmation line returned by the evidence-assembler subagent and confirm that output/evidence-package.md was written. Do nothing else.
```

### Operational notes
- Replace REPO_PATH throughout before pasting — do not paste with the placeholder literal
- Full session restart required between runs (not /clear)
- After VM stop/start: `sudo systemctl restart ollama` then warm-up curl before starting session
- Subagents run sequentially: each step must complete before the next begins
- If a subagent fails to write its evidence report, do not proceed — report the failure at that step
- Stage 2 single-dimension prompt remains valid for D4-only runs
