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

*To be defined during Task 3.2 implementation.*
