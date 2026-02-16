# Static Analysis Tooling — Criteria & Provisioning

## Purpose

Defines when each static analysis tool is needed, how to detect the need, and how to provision tools during Phase 1 without breaking autonomous execution.

---

## Tool Criteria System

Each tool has deterministic selection criteria based on repository content detected during the inventory step (T1, step 1). A tool is APPLICABLE when its trigger conditions are met.

### Semgrep

| Field | Value |
|---|---|
| Purpose | Custom pattern detection across all four dimensions: deployment coupling signals, state management patterns, inter-service communication, lifecycle compliance indicators |
| Trigger condition | **Always applicable.** Any repository with source code benefits from Semgrep pattern scanning. |
| Dimensions served | D1, D2, D3, D4 (all four) |
| Install method | `pip install semgrep` or `brew install semgrep` |
| Verification | `semgrep --version` |
| Fallback if absent | Pure code reading via grep/ripgrep/AST parsing. Coverage drops ~10-15% across all dimensions. |

### Hadolint

| Field | Value |
|---|---|
| Purpose | Dockerfile best practices: base image selection, multi-stage builds, layer optimization, health check presence, user directives |
| Trigger condition | **One or more Dockerfiles detected in the repository.** |
| Not applicable when | No Dockerfiles exist. |
| Dimensions served | D4 (primary), D1 (secondary — multi-stage build patterns) |
| Install method | `brew install hadolint` or download binary from GitHub releases |
| Verification | `hadolint --version` |
| Fallback if absent | Manual Dockerfile review. Misses subtle best-practice violations but catches major issues. Coverage drop ~5-10% for D4. |

### Trivy

| Field | Value |
|---|---|
| Purpose | Image vulnerability scanning, dependency vulnerability scanning, misconfiguration detection in K8s manifests and Dockerfiles |
| Trigger condition | **Dockerfiles exist OR dependency manifests exist (package.json, go.mod, requirements.txt, pom.xml, etc.) OR K8s manifests exist.** |
| Not applicable when | No Dockerfiles, no dependency manifests, no K8s manifests (extremely rare — would mean no scannable artifacts). |
| Dimensions served | D4 (image security), plus C2 compliance evidence |
| Install method | `brew install trivy` or `curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \| sh` |
| Verification | `trivy --version` |
| Fallback if absent | Dependency analysis via manifest parsing only. No vulnerability data. Coverage drop minimal for Tier 1 fitness (Trivy's primary value is C2 compliance evidence, not fitness scoring). |

### dependency-cruiser

| Field | Value |
|---|---|
| Purpose | Dependency graph visualization and circular dependency detection. Module boundary validation. |
| Trigger condition | **JavaScript or TypeScript repository detected** (package.json with .js/.ts source files). |
| Not applicable when | Non-JS/TS repositories. |
| Dimensions served | D1 (module boundaries), D3 (coupling detection) |
| Install method | `npm install -g dependency-cruiser` |
| Verification | `depcruise --version` |
| Language-specific alternatives | Python: `pydeps` (`pip install pydeps`). Go: `go mod graph` (built-in). Java: `jdeps` (bundled with JDK). |
| Fallback if absent | Manual import analysis. Misses transitive dependency patterns. Coverage drop ~5-10% for D1/D3 in JS/TS repos. |

---

## Applicability Detection Logic

Run during T1 repository inventory, BEFORE scanning begins:

```
INVENTORY RESULTS:
├── Languages detected: [list]
├── Dockerfiles found: [YES/NO, count, paths]
├── Dependency manifests found: [YES/NO, list]
├── K8s manifests found: [YES/NO, paths]
└── CI/CD config found: [YES/NO, type]

TOOL APPLICABILITY:
├── Semgrep:           ALWAYS APPLICABLE
├── Hadolint:          IF Dockerfiles found
├── Trivy:             IF Dockerfiles OR dependency manifests OR K8s manifests found
└── dependency-cruiser: IF JS/TS detected
    └── Alt: pydeps    IF Python detected
    └── Alt: go mod    IF Go detected (built-in, no install needed)
    └── Alt: jdeps     IF Java detected (bundled with JDK, no install needed)
```

---

## Provisioning Protocol

### Step 1: Upfront Consent (during T0 Pre-Flight)

After announcing the assessment and before beginning T1:

```
EXEC    Determine which tools MIGHT be needed (based on repo file extensions
        and manifest presence — quick scan, not full inventory):
        ├── Quick-check: ls for Dockerfiles, package.json, go.mod, *.py, etc.
        └── Produce preliminary applicability list

ASK     "As part of the autonomous evidence gathering phase, I may need to
         install static analysis tools that aren't already on your system.
         Based on a preliminary look at the repository:

         Tools that may be needed:
         - Semgrep (pattern detection across all dimensions)
         - Hadolint (Dockerfile analysis)              [only if Dockerfiles detected]
         - Trivy (vulnerability and misconfiguration)   [only if applicable]
         - dependency-cruiser (JS/TS dependency graphs) [only if JS/TS detected]

         May I install any needed tools during the scan?

         If you decline, the assessment will proceed with reduced static
         analysis coverage. This means more ambiguity in the evidence,
         more questions for you during Phase 2, and potentially lower
         confidence in the resulting classifications."

CHECK   Human response:
        ├── CONSENT → Record: tool_install_consent = TRUE
        │              Proceed to T1 with full autonomous provisioning authority.
        │
        ├── DECLINE → Record: tool_install_consent = FALSE
        │              WARN: "Understood. Proceeding without tool installation.
        │                     Note: evidence gathering will rely on manual code
        │                     reading and basic pattern matching. The dialogue
        │                     phase will be longer and classifications may have
        │                     lower confidence.
        │
        │                     You can change this decision at any time before
        │                     Phase 1 completes by saying 'install the tools'."
        │
        │              Proceed to T1 with degraded mode.
        │
        └── PARTIAL → Human specifies which tools are acceptable.
                       Record per-tool consent. Proceed accordingly.
```

### Step 2: Adaptive Installation (during T1, after inventory)

After the full repository inventory (T1 step 1) produces the definitive applicability list:

```
FOR EACH applicable tool:
│
├── CHECK: Is tool already installed?
│          Run verification command (e.g., semgrep --version)
│          │
│          ├── YES (installed) → Record: tool = AVAILABLE. Proceed to use.
│          │
│          └── NO (not installed) →
│              │
│              CHECK: tool_install_consent?
│              │
│              ├── TRUE (consent given) →
│              │   EXEC: Install tool silently.
│              │   CHECK: Installation succeeded?
│              │   ├── YES → Record: tool = INSTALLED. Proceed to use.
│              │   └── NO  → Record: tool = INSTALL_FAILED, reason = [error].
│              │              Log failure in evidence package.
│              │              Continue without this tool.
│              │              (NO dialogue interruption.)
│              │
│              └── FALSE (consent declined) →
│                  Record: tool = SKIPPED_BY_USER.
│                  Log in evidence package.
│                  Continue without this tool.

RESULT: Tooling manifest recorded in evidence package:
        ├── Semgrep: [AVAILABLE / INSTALLED / INSTALL_FAILED / SKIPPED_BY_USER / NOT_APPLICABLE]
        ├── Hadolint: [same]
        ├── Trivy: [same]
        └── dep-cruiser/pydeps/etc: [same]
```

### Step 3: Evidence Package Annotation

The evidence package records the tooling state so Phase 2 knows what level of evidence to expect:

```
## Tooling Manifest

| Tool | Status | Impact on Evidence |
|---|---|---|
| Semgrep | INSTALLED | Full pattern detection active |
| Hadolint | AVAILABLE | Dockerfile analysis active |
| Trivy | INSTALL_FAILED (network timeout) | No vulnerability data. D4 image security assessment relies on manual Dockerfile review. |
| dependency-cruiser | NOT_APPLICABLE | Not a JS/TS repository |

Overall static analysis coverage: FULL / DEGRADED / MINIMAL
Degradation notes: [specific gaps caused by missing tools]
```

---

## Installation Methods by Platform

Claude Code runs on the user's machine. Detect platform first:

```
DETECT: uname -s → Darwin (macOS) / Linux
DETECT: which brew → Homebrew available?
DETECT: which pip / pip3 → Python available?
DETECT: which npm → Node.js available?
```

### macOS (most common for Claude Code users)

| Tool | Primary Method | Fallback |
|---|---|---|
| Semgrep | `brew install semgrep` | `pip3 install semgrep` |
| Hadolint | `brew install hadolint` | Download binary from GitHub |
| Trivy | `brew install trivy` | `curl` install script |
| dependency-cruiser | `npm install -g dependency-cruiser` | — |
| pydeps | `pip3 install pydeps` | — |

### Linux

| Tool | Primary Method | Fallback |
|---|---|---|
| Semgrep | `pip3 install semgrep` | Download binary from GitHub |
| Hadolint | Download binary from GitHub | — |
| Trivy | `curl` install script | Package manager if available |
| dependency-cruiser | `npm install -g dependency-cruiser` | — |
| pydeps | `pip3 install pydeps` | — |

---

## Coverage Impact Summary

| Scenario | Estimated Tier 1 Coverage | Phase 2 Impact |
|---|---|---|
| All applicable tools available | 55-65% | Standard question set, focused on gaps |
| Semgrep only | 45-55% | +1-2 questions per dimension for missing tool-specific signals |
| No tools (pure code reading) | 40-50% | Maximum question load, lowest confidence, longest Phase 2 |

The coverage percentages refer to what proportion of Tier 1 classification can be determined from static evidence alone, before human dialogue begins.
