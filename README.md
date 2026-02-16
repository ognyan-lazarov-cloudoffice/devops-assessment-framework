# DevOps Assessment Framework — Agentic Implementation

## What This Is

Reference files for an AI-assisted Containerization Fitness & Deployment Path Assessment. The agent (Claude Code) uses these files to conduct a structured interview protocol that produces a **Deployment Profile** — a comprehensive classification of an application's containerization fitness, deployment constraints, and strategic deployment choices.

This implements Framework 1 of the Two-Framework Architecture. Framework 2 (Migration Execution Planning) is out of scope.

## Framework Summary

### Three-Tier Model

| Tier | Question | Model | Output |
|---|---|---|---|
| **Tier 1: Fitness** | How well does the app fit the container model? | Scoring (4 dimensions, 0-3 each) | BLOCKED / LOW / MEDIUM / HIGH |
| **Tier 2: Constraints** | What external factors filter or constrain the path? | Filtering & Accumulation (3 constraints) | Surviving paths + mandatory requirements |
| **Tier 3: Strategy** | How should the deployment be executed? | Selection & Composition (3 choice areas) | Execution archetype + strategy tensions |

### Three-Phase Protocol

| Phase | Mode | What Happens | Duration |
|---|---|---|---|
| **Phase 1** | Autonomous | Agent scans repos, runs static analysis, assembles evidence | 15-30 min (no human) |
| **Phase 2** | Dialogue | Agent presents evidence per dimension, human confirms/overrides, dialectical challenges | 40-60 min |
| **Phase 3** | Dialogue | Agent collects constraints and strategic selections | 35-65 min |

Total envelope: **1.5-2.5 hours** (~30 min autonomous + ~90 min human engagement).

## File Structure

```
reference/
├── dimensions/              # Tier 1 — one file per dimension
│   ├── d1-deployment-unit-topology.md
│   ├── d2-state-and-data-model.md
│   ├── d3-independence-profile.md
│   └── d4-lifecycle-compliance.md
│
├── constraints/             # Tier 2 — one file per constraint
│   ├── c1-infrastructure-availability.md
│   ├── c2-compliance-posture.md
│   └── c3-organizational-topology.md
│
├── choices/                 # Tier 3 — one file per choice area
│   ├── s1-lifecycle-stage.md
│   ├── s2-velocity-target.md
│   └── s3-risk-tolerance.md
│
├── aggregation/             # Cross-element logic per tier
│   ├── tier1-scoring.md
│   ├── tier2-filtering.md
│   └── tier3-composition.md
│
├── tensions/                # Pre-defined conflict catalogs
│   ├── cross-dimension-tensions.md
│   └── strategy-tensions.md
│
├── protocol/                # Dialogue and procedural rules
│   ├── phase1-evidence-gathering.md
│   ├── phase2-assessment-dialogue.md
│   ├── phase3-strategic-guidance.md
│   ├── dialectical-challenges.md
│   └── tooling-provisioning.md
│
└── templates/               # Structured output formats
    ├── evidence-package.md
    ├── dimension-assessment.md
    ├── tier1-fitness-report.md
    ├── constraint-map.md
    └── deployment-profile.md
```

## Design Principles

**One file per assessment unit.** A task assessing D2 loads only `d2-state-and-data-model.md` + `phase2-assessment-dialogue.md`. No monolithic reference document.

**Protocol files define HOW, reference files define WHAT.** Clean separation between procedural rules and domain knowledge.

**Templates define OUTPUT CONTRACTS.** What each phase must produce, field by field.

**Self-contained dimension/constraint/choice files.** Each includes its own decision tree, question bank, static indicators, classification mapping, and dialectical triggers.

## How to Use

### For Manual Assessment

1. Read through dimension files (d1-d4) to understand the scoring model.
2. Walk through each dimension's decision tree for your application.
3. Use `tier1-scoring.md` to aggregate scores into fitness classification.
4. Apply constraints (c1-c3) using `tier2-filtering.md`.
5. Make strategic selections (s1-s3) using `tier3-composition.md`.
6. Fill in the `deployment-profile.md` template.

### For Agentic Assessment (Claude Code)

All three implementation layers are included:

- **Reference files** (`reference/`) — domain knowledge, rules, question banks, tension catalogs, output contracts. The **brain**.
- **Slash commands** (`.claude/commands/`) — entry points: `/assess` (full run), `/assess-resume` (checkpoint recovery), `/assess-dimension` (targeted re-assessment). The **muscle**.
- **Task registry** (`.claude/task-registry.md`) — 16-node dependency chain with completion markers, gate conditions, and invariants. The **skeleton**.
- **Agent identity** (`CLAUDE.md`) — behavioral rules, on-demand reference loading strategy, tone.
- **Exemplar workflow** (`.claude/exemplar-workflow.md`) — step-by-step algorithmic trace of a complete assessment run.

Static analysis tooling (Semgrep, Hadolint, Trivy, dependency-cruiser) is provisioned adaptively during Phase 1. Before scanning, the agent determines which tools are applicable based on repository content (e.g., Hadolint only if Dockerfiles exist, dependency-cruiser only for JS/TS repos) and requests upfront consent to install any that are missing. With consent, tools are installed silently during the autonomous scan. Without consent, the framework proceeds with reduced coverage and the dialogue phase compensates with additional questions. See `reference/protocol/tooling-provisioning.md` for the full criteria system.

To run: open this project in Claude Code and invoke `/assess /path/to/target/repo`.

## Version

Framework v1.0 — complete and ready for real-world testing.

## Related Artifacts

Companion documents in `docs/`:

- **Comprehensive DevOps Workflow Decision Framework.pdf** — 9-page teaching document with diagrams (original framework document)
- **DevOps Containerization & Deployment Decision Making Flow.md** — Practitioner's quick-reference with decision trees, scoring mechanics, and failure modes

Both predate this implementation; this repo operationalizes the same framework for agentic assessment.
