# Phase 1 Hybrid Implementation Plan

## Subagent-Based Static Analysis on Local LLM Infrastructure

**Version:** 1.0  
**Date:** 2026-02-17  
**Branch:** `main`  
**Baseline:** `release/v1` (single-agent Anthropic implementation, frozen)

---

## Objective

Validate the hybrid execution architecture end-to-end: Ollama-served local LLM running Claude Code subagents for Phase 1 static analysis evidence gathering, producing an Evidence Package suitable for Anthropic-side synthesis handoff.

---

## Implementation Sequence Overview

The plan is organized into three sequential stages, each with a clear gate condition that must be satisfied before proceeding to the next.

| Stage | Focus | Gate Condition |
|-------|-------|----------------|
| **Stage 1** | Infrastructure Plumbing | Claude Code subagent successfully invokes a tool via Ollama-served model and returns structured output |
| **Stage 2** | Single Subagent Proof-of-Concept | D4 Lifecycle Compliance subagent produces a valid per-dimension evidence report against a real repository |
| **Stage 3** | Full Decomposition & Integration | Complete Phase 1 subagent ensemble produces a coherent Evidence Package against a real or representative repository |

---

## Stage 1 — Infrastructure Plumbing

**Purpose:** Establish a working execution environment where Claude Code communicates with a local LLM via Ollama, and subagent invocation functions correctly through the local endpoint.

**Entry condition:** GCP project with billing enabled, SSH access configured.

### Task 1.1 — GCE VM Provisioning

Provision a GPU-equipped VM on Google Compute Engine suitable for serving a 13B–30B parameter model.

| Aspect | Specification |
|--------|---------------|
| GPU | NVIDIA A100 40 GB VRAM (see rationale below) |
| Machine type | `a2-highgpu-1g` or equivalent (A100-attached) |
| OS | Ubuntu 24.04 LTS |
| Disk | 100 GB SSD (model weights + working space) |
| Region | Select based on A100 availability and cost |

**GPU selection rationale:** The plan anticipates testing both 14B models (Q6_K/Q8_0) and 32B models (Q4_K_M through Q6_K) during Stage 2, Task 2.5. An L4 (24 GB VRAM) handles 14B comfortably but fits 32B only at Q4_K_M under tight conditions. An A100 40 GB provides comfortable headroom for the full model size range without reprovisioning. The cost delta between L4 (~$0.80/hr) and A100 40 GB (~$3.70/hr on-demand, significantly less on spot/preemptible) over a testing period measured in days is trivial compared to the time and effort cost of reprovisioning the entire Stage 1 chain (drivers, Docker, Ollama, model downloads, re-validation). Provision once for the full testing envelope.

**Steps:**

1. Create the VM instance with GPU attachment and appropriate firewall rules (SSH only — Ollama API stays on localhost or internal network).
2. Install NVIDIA drivers and verify GPU visibility (`nvidia-smi`).
3. Install Docker with NVIDIA Container Toolkit (`nvidia-docker`).

**Exit criteria:**  
`nvidia-smi` shows the L4 GPU, Docker can run `--gpus all` containers.

---

### Task 1.2 — Ollama Deployment and Model Serving

Deploy Ollama and pull a candidate model for initial testing.

**Steps:**

1. Deploy Ollama via Docker with GPU passthrough:
   ```
   docker run -d --gpus all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
   ```
2. Pull the initial candidate model — **Qwen3-Coder** (recommended starting point for tool calling fidelity). Select quantization based on 40 GB VRAM budget:
   - 14B at Q6_K or Q8_0 (comfortable, leaves significant VRAM headroom for context)
   - 32B at Q4_K_M through Q6_K (all fit within 40 GB with usable context window)
3. Verify the model serves responses:
   ```
   curl http://localhost:11434/api/generate -d '{"model":"qwen3-coder","prompt":"Hello"}'
   ```
4. Verify the **Anthropic Messages API compatibility endpoint** is functional:
   ```
   curl http://localhost:11434/v1/messages \
     -H "Content-Type: application/json" \
     -H "x-api-key: ollama" \
     -d '{"model":"qwen3-coder","max_tokens":256,"messages":[{"role":"user","content":"Respond with a JSON object containing key greeting and value hello"}]}'
   ```

**Exit criteria:**  
Ollama serves the model via the Anthropic-compatible `/v1/messages` endpoint, returning well-formed JSON responses.

**Observation notes:**  
Record response latency, tokens/second, and any malformed output for baseline comparison.

---

### Task 1.3 — Claude Code Connection to Local Endpoint

Configure Claude Code on the development machine (or on the VM itself) to route API calls through the Ollama endpoint.

**Steps:**

1. Set the environment variables for Claude Code to use the local endpoint:
   ```
   export ANTHROPIC_BASE_URL=http://<VM_IP>:11434
   export ANTHROPIC_AUTH_TOKEN=ollama
   ```
   If running Claude Code on the VM itself, use `http://localhost:11434`.
2. Launch Claude Code and verify basic interaction — send a simple prompt and confirm the response comes from the local model (not from Anthropic's API).
3. Verify that Claude Code's structural infrastructure is intact:
   - `CLAUDE.md` is loaded and respected
   - Slash commands are recognized
   - File read/write operations function
   - Bash execution works

**Exit criteria:**  
Claude Code operates interactively via the local model, recognizing its structural configuration files.

**Baseline test (recommended before proceeding to Task 1.4):**  
At this point, the current `release/v1` framework is fully functional through the local model — no transformation has occurred yet. Run the existing `/assess` command against a repository to establish a baseline measurement:
- Does the single-agent flow complete, or does it break under the local model?
- What is the quality of evidence gathering compared to expectations from Anthropic-powered execution?
- Where does the local model struggle most (tool calling sequences? classification reasoning? output formatting?)?

This baseline is the "before" measurement against which all subsequent subagent-based improvements are evaluated. It also reveals whether specific failure modes are model-inherent (appear in single-agent too) or subagent-specific (appear only after transformation).

**Risk note:**  
If running Claude Code remotely (on the VM via SSH), consider latency and terminal session management (tmux/screen). If running locally, ensure network connectivity to the VM is stable and firewall rules permit the Ollama port.

---

### Task 1.4 — Subagent Invocation Validation

This is the **critical gate task** for Stage 1. Validate that Claude Code's subagent mechanism works through the local Ollama endpoint.

**Steps:**

1. Create a minimal test subagent definition file:
   ```
   # .claude/agents/test-subagent.md
   ---
   name: test-subagent
   description: Minimal validation subagent
   tools:
     - Bash
     - Read
   ---
   You are a test subagent. When invoked, execute `ls -la` in the current directory 
   and return the output as a JSON object with keys: "file_count" (integer), 
   "largest_file" (string), "total_size_kb" (integer).
   ```
2. From the main Claude Code session, invoke the subagent and capture its output.
3. Evaluate the output against three criteria:
   - **Invocation success:** Did the subagent spawn and execute without errors?
   - **Tool calling fidelity:** Did the subagent correctly invoke `ls -la` via Bash tool?
   - **Structured output compliance:** Did it return valid JSON matching the requested schema?
4. Run the test 5 times to assess consistency. Log any failures, malformed outputs, or tool calling glitches.

**Exit criteria:**  
≥4 out of 5 invocations produce correct structured JSON output from the subagent via the local model. Tool calls execute without requiring manual intervention.

**Failure protocol:**  
If subagent invocation fails consistently:
- Check whether the model supports tool calling at the selected quantization level.
- Try an alternative model (GLM-5, Kimi-K2.5).
- Try a higher quantization or smaller model size.
- Check Ollama logs for tool call format issues (known friction point: Jinja template compatibility).
- Document the failure mode precisely — this is the most likely point where the architecture could require revision.

---

### Stage 1 Gate

**Pass condition:** All four tasks complete successfully. Claude Code subagent invokes a tool via the Ollama-served local model and returns structured output reliably.

**Fail condition:** Subagent invocation is unreliable after testing multiple models and configurations. **Decision point:** evaluate whether the failure is model-specific (solvable by model selection) or architectural (requires rethinking the subagent approach for local execution).

---

## Stage 2 — Single Subagent Proof-of-Concept

**Purpose:** Implement one complete dimension subagent (D4 Lifecycle Compliance) against a real repository and validate that it produces evidence of sufficient quality and structure to feed into the synthesis phase.

**Entry condition:** Stage 1 gate passed.

### Why D4 First

D4 is the optimal proof-of-concept candidate for three reasons:

1. **Highest static analysis ceiling** (70–80%) — maximizes the chance of meaningful results even with a less capable model.
2. **Most deterministic tool outputs** — Hadolint linting results, health endpoint detection via grep/Semgrep, SIGTERM handler detection are all binary or near-binary signals.
3. **Clearest mapping from tool output to framework classification** — L1/L2/L3/L4 classifications in the framework correspond directly to observable artifacts (Dockerfile quality, health endpoints present/absent, startup time indicators).

### Task 2.1 — Select Target Repository

Identify a repository to use as the assessment target for the proof-of-concept.

**Options (in order of preference):**

1. **A real client-representative repository** (if available from prior engagements with appropriate permissions) — highest signal, most realistic test.
2. **A well-known open-source project** with known containerization characteristics — provides a verifiable baseline (e.g., a project with Dockerfiles, health endpoints, and known architectural patterns).
3. **A purpose-built test repository** — controlled conditions but lower ecological validity.

**Exit criteria:**  
A repository is selected, cloned to the VM, and its general characteristics are documented (language, presence of Dockerfiles, CI configuration, approximate size).

---

### Task 2.2 — Implement the D4 Subagent Definition

Create the D4 Lifecycle Compliance subagent as a `.claude/agents/d4-lifecycle.md` file, drawing from the existing reference material in `reference/dimensions/d4-lifecycle-compliance.md`.

**Steps:**

1. Draft the subagent definition with:
   - **System prompt** incorporating D4-specific assessment criteria (startup time indicators, SIGTERM handling, configuration model, health endpoints).
   - **Tool restrictions** limited to: Bash, Read (and optionally Write for evidence output).
   - **Explicit output contract** specifying the expected structured format for the per-dimension evidence report.
2. The output contract should include (at minimum):
   - Classification signals detected (with file paths and line references).
   - Tool outputs (Hadolint JSON, Semgrep matches).
   - Preliminary classification suggestion with confidence level.
   - Explicit unknowns (signals that could not be determined from static analysis alone).
3. The subagent must load only D4-relevant reference material — not the full framework. This validates the context isolation principle.

**Exit criteria:**  
The subagent definition file is complete, syntactically valid, and references only D4-relevant framework content.

---

### Task 2.3 — Implement the Tooling Subagent

Create a minimal tooling subagent (`.claude/agents/tooling.md`) responsible for tool installation and execution.

**Steps:**

1. Draft the tooling subagent definition with:
   - Capability to check for and install applicable tools (Hadolint, Semgrep, Trivy) based on repository content.
   - Structured output: tool availability status per the existing tooling manifest format.
2. The tooling subagent is invoked first by the orchestrator, and its output (tooling manifest) is passed as context to the D4 subagent.

**Exit criteria:**  
The tooling subagent correctly detects applicable tools, installs missing ones (on the VM), and returns a valid tooling manifest.

---

### Task 2.4 — Execute D4 Assessment Against Target Repository

Run the D4 subagent against the selected repository with the orchestrator (main Claude Code session) managing the invocation flow.

**Steps:**

1. The orchestrator invokes the tooling subagent → receives tooling manifest.
2. The orchestrator invokes the D4 subagent with:
   - Repository path.
   - Tooling manifest (which tools are available).
   - Instructions to assess D4 Lifecycle Compliance.
3. Capture the D4 subagent's complete output.
4. Evaluate output quality against multiple dimensions:

| Quality Dimension | Evaluation Criteria |
|-------------------|-------------------|
| **Structural compliance** | Does the output match the specified contract format? |
| **Evidence traceability** | Are file paths and line references accurate and verifiable? |
| **Tool output integration** | Are Hadolint/Semgrep results correctly parsed and incorporated? |
| **Classification coherence** | Does the preliminary classification align with the evidence presented? |
| **Unknown identification** | Are genuinely unresolvable questions flagged (not hallucinated)? |
| **No source code leakage** | Does the output contain raw source code, or only structured abstractions? |

5. If the output is deficient, iterate: adjust the subagent system prompt, output contract, or tool invocation patterns. Record what needed adjustment and why.

**Exit criteria:**  
The D4 subagent produces an evidence report that scores satisfactory (usable without major rework) on at least 5 of the 6 quality dimensions above. The "no source code leakage" dimension must pass unconditionally.

---

### Task 2.5 — Assess Model Quality Baseline

With a working D4 subagent, systematically evaluate the local model's performance characteristics.

**Steps:**

1. Run the D4 assessment 3 times against the same repository. Compare outputs for:
   - **Consistency:** Do the same evidence items appear across runs?
   - **Classification stability:** Does the preliminary classification vary?
   - **Hallucination detection:** Do any runs introduce signals not present in the repository?
2. Run the same assessment with a 32B model at Q6_K (the A100 40 GB accommodates this without reprovisioning) and compare quality differential. This informs the cost/quality trade-off for eventual production deployment on constrained hardware (Apple Silicon UMA).
3. Document the observed quality characteristics as a baseline:
   - What the model handles well (e.g., Dockerfile analysis, pattern matching).
   - Where it struggles (e.g., cross-file reasoning, nuanced classification).
   - Failure modes (e.g., tool call formatting errors, output truncation).

**Exit criteria:**  
A documented model quality baseline exists, with clear characterization of strengths, weaknesses, and failure modes. This baseline informs decisions in Stage 3 about subagent prompt engineering depth and output validation requirements.

---

### Stage 2 Gate

**Pass condition:** The D4 subagent produces structurally valid, evidence-traceable, source-code-free dimension reports with acceptable consistency. The model quality baseline is documented.

**Fail condition:** The D4 subagent cannot produce usable evidence reports after prompt iteration. **Decision point:** evaluate whether the failure is (a) model capability (try larger model or different architecture), (b) subagent design (restructure the task decomposition), or (c) fundamental — local models cannot reliably drive the evidence gathering pipeline (requires strategic reassessment).

---

## Stage 3 — Full Decomposition and Integration

**Purpose:** Implement the complete Phase 1 subagent ensemble (tooling + D1–D4 + orchestrator), execute against a real or representative repository, and produce a coherent Evidence Package suitable for Anthropic-side synthesis.

**Entry condition:** Stage 2 gate passed.

### Task 3.1 — Implement Remaining Dimension Subagents (D1, D2, D3)

Using the D4 subagent as a proven template, implement the three remaining dimension subagents.

**Steps:**

1. **D1 Deployment Unit Topology** (`.claude/agents/d1-topology.md`):
   - Focus: build artifacts, dependency graphs, CI structure, process model indicators.
   - Primary tools: dependency-cruiser (JS/TS) or equivalent, Semgrep for import pattern analysis.
   - Key challenge: detecting distributed monolith indicators (T4) requires cross-file reasoning about deployment coupling.

2. **D2 State and Data Model** (`.claude/agents/d2-state.md`):
   - Focus: database/cache library detection, file I/O patterns, session management, state externalization indicators.
   - Primary tools: Semgrep for state pattern detection, dependency manifest analysis.
   - Key challenge: distinguishing S2 (managed statefulness) from S3 (embedded state) requires understanding the application's data flow, not just library presence.

3. **D3 Independence Profile** (`.claude/agents/d3-independence.md`):
   - Focus: inter-service contracts, resilience library presence, communication patterns, scaling indicators.
   - Primary tools: Semgrep, dependency-cruiser for coupling graph.
   - Key challenge: hidden coupling (I4) detection has the lowest static analysis ceiling (40–50%). The subagent must be calibrated to flag uncertainty rather than false confidence.

4. For each subagent, apply the same output contract structure validated with D4. Adjust evidence categories and classification signals per dimension.

**Implementation order:** D1 → D2 → D3 (descending static analysis ceiling, allowing momentum from easier to harder dimensions).

**Exit criteria:**  
All four dimension subagents (D1–D4) produce structurally valid evidence reports against the target repository. Each subagent loads only its dimension-relevant reference material.

---

### Task 3.2 — Implement the Orchestrator Flow

Implement the main agent orchestration logic that sequences subagent invocations and assembles outputs.

**Steps:**

1. Define the orchestrator's execution sequence:
   ```
   T0.5  Tooling Subagent → Tooling Manifest
   T1    Repository Inventory (orchestrator, direct) → Repo Boundary Map
   T1.D1 D1 Subagent (with Tooling Manifest + Repo Map) → D1 Evidence Report
   T1.D2 D2 Subagent (with Tooling Manifest + Repo Map) → D2 Evidence Report
   T1.D3 D3 Subagent (with Tooling Manifest + Repo Map) → D3 Evidence Report
   T1.D4 D4 Subagent (with Tooling Manifest + Repo Map) → D4 Evidence Report
   ```
2. The orchestrator performs cross-dimension correlation after all subagents complete:
   - D1–D3 consistency check (deployment topology vs. independence profile).
   - D2–D4 consistency check (state model vs. lifecycle compliance).
   - Flag contradictions for the Dialogue Agenda.
3. The orchestrator assembles the Evidence Package from subagent outputs.
4. Implement the evidence validation scan: automated check confirming no raw source code in the assembled Evidence Package.
5. If Tier 2 preliminary signals were detected during subagent execution (C1 infrastructure indicators from K8s manifests, C2 compliance indicators from security configurations), incorporate them into a Tier 2 Preliminary section.

**Exit criteria:**  
The orchestrator successfully sequences all subagent invocations, performs cross-dimension correlation, and assembles a coherent Evidence Package.

---

### Task 3.3 — Evidence Package Assembly and Validation

Validate the complete Evidence Package against the intended handoff contract.

**Steps:**

1. Review the assembled Evidence Package for:
   - **Completeness:** All four dimensions represented with evidence reports.
   - **Structural consistency:** Uniform format across dimension reports.
   - **Cross-reference integrity:** Orchestrator's cross-dimension observations reference real evidence items from subagent reports.
   - **Dialogue Agenda quality:** Unresolved questions are specific, evidence-contextual, and actionable (not vague).
   - **Source code absence:** The automated validation scan passes — zero raw code fragments in the package.
   - **Tier 2 preliminary signals:** Present if detectable, absent without fabrication.
2. Produce the Evidence Package as a structured output file (Markdown or JSON — format to be determined by what the D4 PoC revealed as most practical).
3. Assess whether the Evidence Package, as produced, would be suitable for handoff to an Anthropic model for synthesis. Key question: does an informed reader (Ogi or equivalent) reviewing the package understand the assessment state without needing the source code?

**Exit criteria:**  
The Evidence Package passes all validation criteria. An informed reader confirms it communicates assessment state without requiring source code access.

---

### Task 3.4 — Synthesis Handoff Dry Run (Optional but Recommended)

If the Evidence Package quality is satisfactory, perform a dry-run handoff to an Anthropic model to validate the synthesis phase.

**Steps:**

1. Switch Claude Code back to Anthropic API (restore standard `ANTHROPIC_BASE_URL`).
2. Provide the Evidence Package as input context.
3. Instruct the Anthropic model to:
   - Perform cross-dimensional tension detection.
   - Generate preliminary scoring hypotheses.
   - Compose a Dialogue Agenda from the evidence gaps.
4. Evaluate whether the Anthropic model's synthesis output is materially better than what the local model could produce — this validates the hybrid architecture's core premise.

**Exit criteria:**  
The synthesis output demonstrates quality uplift over what the local model produced in cross-dimension analysis, confirming the hybrid split is justified.

---

### Task 3.5 — Document Findings and Update Repository

Consolidate all findings from Stages 1–3 into the repository.

**Steps:**

1. Update `README.md` to reflect the hybrid architecture, Ollama configuration, and subagent structure.
2. Create the operational setup guide (new file: `docs/hybrid-execution-setup.md` or equivalent) documenting:
   - GCE VM provisioning steps.
   - Ollama deployment and model selection.
   - Claude Code configuration for local endpoint.
   - Known model limitations and workarounds.
3. Commit the new subagent definitions (`.claude/agents/*.md`).
4. Document the model quality baseline and observed failure modes.
5. Update the task registry and exemplar workflow to reflect the subagent-based execution flow.
6. Record decisions made during implementation that resolved the pending design questions (output contract format, scoring split point, evidence validation approach).

**Exit criteria:**  
The `main` branch contains a complete, documented, testable hybrid implementation. A new contributor could follow the setup guide and reproduce the assessment pipeline.

---

### Stage 3 Gate

**Pass condition:** The full subagent ensemble produces a coherent Evidence Package that passes validation. The repository is updated with all implementation artifacts and documentation. Optionally, the synthesis handoff dry run confirms the hybrid architecture's value.

**Fail condition:** The ensemble produces inconsistent or low-quality evidence across dimensions. **Decision point:** evaluate whether to (a) invest in per-dimension prompt engineering refinement, (b) accept reduced coverage ceiling with documented limitations, or (c) reassess the subagent decomposition model itself.

---

## Model Selection Reference

For initial Stage 1 testing, the following candidates are recommended based on tool calling capability and Claude Code compatibility:

| Model | Parameters | Quantization at 40 GB VRAM | Tool Calling | Notes |
|-------|-----------|---------------------------|--------------|-------|
| **Qwen3-Coder** | 14B / 32B | 14B: Q8_0 with headroom; 32B: Q6_K comfortable | Strong | Recommended starting point |
| **GLM-5** | 9B / 32B | 9B: FP16 trivial; 32B: Q6_K comfortable | Good | Alternative if Qwen3 struggles |
| **Kimi-K2.5** | 14B | Q8_0 with headroom | Good | Strong reasoning, verify tool format |

Model selection is empirical — the Stage 1 gate testing (Task 1.4) will determine which model proceeds to Stage 2.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Local model tool calling unreliable | Medium | **Blocks Stage 1** | Test multiple models and quantizations; check Ollama logs for format issues; try Jinja template adjustments |
| Subagent structured output inconsistent | Medium | Degrades Stage 2 quality | Strengthen output contract in system prompt; add JSON schema validation; iterate prompt engineering |
| D3 hidden coupling detection too weak | High | Reduces Phase 1 ceiling for D3 | Expected — D3 has lowest static ceiling (40–50%); calibrate subagent to flag uncertainty rather than guess; transfer to Dialogue Agenda |
| Cross-dimension correlation quality low | Medium | Weakens Evidence Package coherence | May require orchestrator to use Anthropic API for this step even during Phase 1 (mini-handoff for synthesis operations) |
| VRAM insufficient for target quantization | Very Low | Limits model quality | Mitigated by A100 40 GB provisioning decision — fits 32B at Q6_K comfortably; only relevant if testing 70B+ models (not currently in scope) |
| Evidence Package contains source code fragments | Low | **Blocks handoff** | Automated validation scan; subagent prompts explicitly prohibit raw code inclusion; grep-based post-check |

---

## Relationship to Current Framework and Transformation Agenda

### What Is Testable Without Any Framework Changes

The current `release/v1` framework (single-agent, Anthropic-targeted) can be exercised against the new infrastructure **through Stage 1, Task 1.3** without modifying a single file. This produces a valuable but often overlooked baseline:

| Stage | Task | Requires Framework Changes? | What It Tests |
|-------|------|----------------------------|---------------|
| 1 | 1.1 — GCE VM Provisioning | No | Pure infrastructure |
| 1 | 1.2 — Ollama Deployment | No | Pure infrastructure |
| 1 | 1.3 — Claude Code Connection | No | Claude Code structural infrastructure (CLAUDE.md, slash commands, file ops, bash) via local model |

**Implicit baseline test at Task 1.3 completion:** Before proceeding to Task 1.4, the current `/assess` command can be run as-is against a repository through the local model. This is the existing single-agent flow — no subagents, no hybrid split, no transformation — just the `release/v1` framework operating through Ollama instead of Anthropic's API. The result is a direct measurement of how the current framework degrades (or doesn't) when the underlying model changes from Anthropic to a local OSS model. This baseline is essential: it establishes the "before" against which all subsequent transformation improvements are measured.

### Where Transformation Begins

From **Task 1.4 onward**, the plan begins creating new artifacts that constitute transformation agenda work:

| Stage | Task | First Transformation Item | Agenda Mapping |
|-------|------|--------------------------|----------------|
| 1 | 1.4 — Subagent Invocation Validation | Creates test subagent definition (`.claude/agents/test-subagent.md`) — throwaway, but validates the mechanism that all subsequent transformation depends on | Prerequisite for Agenda Item 1 |
| 2 | 2.2 — D4 Subagent Implementation | Creates first production subagent definition (`.claude/agents/d4-lifecycle.md`) with output contract — this is the first concrete artifact of the architectural split | **Agenda Items 1 + 4** |
| 2 | 2.3 — Tooling Subagent | Creates tooling subagent (`.claude/agents/tooling.md`) — extends the subagent architecture | **Agenda Item 1** |
| 2 | 2.4 — D4 Assessment Execution | First test of source code absence in output — early evidence validation signal | **Agenda Item 3** (early signal) |
| 3 | 3.1 — Remaining Subagents (D1–D3) | Full subagent decomposition complete | **Agenda Item 1** (complete) |
| 3 | 3.2 — Orchestrator Flow | Cross-dimension correlation, Tier 2 preliminary signal collection, evidence validation scan | **Agenda Items 3 + 5** |
| 3 | 3.3 — Evidence Package Validation | Full evidence validation as automated scan — formal implementation | **Agenda Item 3** (complete) |
| 3 | 3.4 — Synthesis Handoff Dry Run | Tests the architectural split end-to-end (local → handoff → Anthropic) | **Agenda Item 1** (validated) |
| 3 | 3.5 — Documentation | README update, operational setup guide, model quality baseline documentation | **Agenda Items 2 + 6 + 7** |

### Transformation Agenda Coverage Summary

| Agenda Item | First Addressed | Fully Resolved | Notes |
|-------------|----------------|----------------|-------|
| 1. Architectural split (local → handoff → Anthropic) | Task 1.4 (mechanism) | Task 3.4 (end-to-end validation) | Progressive — each stage adds a layer |
| 2. Operational configuration (Ollama, profiles, setup guide) | Task 1.1 (infrastructure) | Task 3.5 (documented) | Configuration established in Stage 1, formalized in Stage 3 |
| 3. Evidence Package validation (no source code leakage) | Task 2.4 (early signal) | Task 3.3 (automated scan) | Validated incrementally from first subagent output |
| 4. Subagent output contract | Task 2.2 (D4 definition) | Task 3.1 (all dimensions) | Contract designed for D4, extended to D1–D3 |
| 5. Tier 2 preliminary signals | Task 3.2 (orchestrator) | Task 3.3 (in Evidence Package) | Only addressable once full orchestrator exists |
| 6. README update | — | Task 3.5 | End-of-plan documentation |
| 7. Degradation/fallback protocol | Gate failure protocols (all stages) | Task 3.5 (formalized) | Observed failure modes during testing inform the formal protocol |

**Items deferred beyond this plan:** The exact scoring split point (local per-dimension scoring vs. Anthropic aggregation) and the Dialogue Agenda template extraction. Both will be informed by empirical observation during Stages 2–3 and formalized in a subsequent iteration.
