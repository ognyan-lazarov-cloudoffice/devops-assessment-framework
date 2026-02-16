# Template: Evidence Package

## Purpose

Phase 1 output → Phase 2 input. The complete evidence gathered during autonomous scanning.

---

## Template

```markdown
# EVIDENCE PACKAGE
Generated: [date/time]
Assessment scope: [application/system name]

## REPOSITORY INVENTORY

| # | Repository | Language | Framework | Build System | Dockerfile | CI/CD | K8s Manifests | Notes |
|---|-----------|----------|-----------|-------------|------------|-------|---------------|-------|
| 1 | [name/path] | [lang] | [framework] | [build] | [Y/N] | [type] | [Y/N + type] | [notes] |
| 2 | ... | | | | | | | |

Total repositories: [N]
Total detected services/components: [N]

## TOOLING MANIFEST

| Tool | Applicability | Status | Impact on Evidence |
|---|---|---|---|
| Semgrep | ALWAYS | `[AVAILABLE / INSTALLED / INSTALL_FAILED / SKIPPED_BY_USER]` | [impact if not available] |
| Hadolint | `[APPLICABLE / NOT_APPLICABLE]` | `[AVAILABLE / INSTALLED / INSTALL_FAILED / SKIPPED_BY_USER / N/A]` | [impact if not available] |
| Trivy | `[APPLICABLE / NOT_APPLICABLE]` | `[AVAILABLE / INSTALLED / INSTALL_FAILED / SKIPPED_BY_USER / N/A]` | [impact if not available] |
| dep-cruiser/pydeps/etc | `[APPLICABLE / NOT_APPLICABLE]` | `[AVAILABLE / INSTALLED / INSTALL_FAILED / SKIPPED_BY_USER / N/A]` | [impact if not available] |

Tool install consent: `[FULL / DECLINED / PARTIAL]`
Overall static analysis coverage: `[FULL / DEGRADED / MINIMAL]`
Degradation notes: [specific gaps caused by missing tools, or "None"]

## BOUNDARY MAP

[If multi-repo:]
- [Repo A] → [Service X, Service Y] (single deployable unit / independent services)
- [Repo B] → [Service Z]
- Boundary confirmation status: [confirmed by human / pending confirmation]

[If single repo:]
- Single repository scope. No boundary confirmation needed.

---

## D1 EVIDENCE: DEPLOYMENT UNIT TOPOLOGY

### Strong Indicators
- [indicator]: `[file path]` → points to [T?]
  Evidence: [specific detail, e.g., "3 Dockerfiles in /services/api/, /services/worker/, /services/web/"]

### Moderate Indicators
- [indicator]: `[file path]` → points to [T?]

### Weak Indicators
- [indicator]: `[file path]` → points to [T?]

### Preliminary Hypothesis: [T?] ([name])
### Confidence: [HIGH / MEDIUM / LOW]
### Confidence Rationale: [why]

### Gaps Requiring Dialogue:
1. [gap → triggers Q-D1-?]
2. [gap → triggers Q-D1-?]

### Contradictory Signals:
- [if any: signal A suggests T1 but signal B suggests T4]

---

## D2 EVIDENCE: STATE AND DATA MODEL

### Strong Indicators
- [indicator]: `[file path]` → points to [S?]

### Moderate Indicators
- [indicator]: `[file path]` → points to [S?]

### Weak Indicators
- [indicator]: `[file path]` → points to [S?]

### Preliminary Hypothesis: [S?] ([name])
### Confidence: [HIGH / MEDIUM / LOW]
### Confidence Rationale: [why]

### Gaps Requiring Dialogue:
1. [gap → triggers Q-D2-?]
2. [gap → triggers Q-D2-?]

### Contradictory Signals:
- [if any]

---

## D3 EVIDENCE: INDEPENDENCE PROFILE

### Strong Indicators
- [indicator]: `[file path]` → points to [I?]

### Moderate Indicators
- [indicator]: `[file path]` → points to [I?]

### Weak Indicators
- [indicator]: `[file path]` → points to [I?]

### Preliminary Hypothesis: [I?] ([name])
### Confidence: [HIGH / MEDIUM / LOW]
### Confidence Rationale: [why]
### Note: Lowest static ceiling (~40-50%). Expect significant dialogue dependency.

### Gaps Requiring Dialogue:
1. [gap → triggers Q-D3-?]
2. [gap → triggers Q-D3-?]

### Contradictory Signals:
- [if any]

---

## D4 EVIDENCE: LIFECYCLE COMPLIANCE

### Strong Indicators
- [indicator]: `[file path]` → points to [L?]

### Moderate Indicators
- [indicator]: `[file path]` → points to [L?]

### Weak Indicators
- [indicator]: `[file path]` → points to [L?]

### Preliminary Hypothesis: [L?] ([name])
### Confidence: [HIGH / MEDIUM / LOW]
### Confidence Rationale: [why]
### Note: Highest static ceiling (~70-80%). Expect dialogue to mostly confirm.

### Gaps Requiring Dialogue:
1. [gap → triggers Q-D4-?]

### Contradictory Signals:
- [if any]

---

## DIALOGUE AGENDA

Dimension order: D1 → D2 → D3 → D4 (fixed)

| Dimension | Questions Planned | Potential Challenges | Est. Time |
|-----------|-------------------|---------------------|-----------|
| D1 | [Q-D1-1, Q-D1-3] | [Cat 1: CI pipeline contradiction] | [12 min] |
| D2 | [Q-D2-1] | [none expected] | [10 min] |
| D3 | [Q-D3-1, Q-D3-2, Q-D3-3] | [Cat 1: no circuit breakers] | [18 min] |
| D4 | [Q-D4-1] | [none expected] | [10 min] |

Cross-dimension tension check: [10 min]
Tier 1 aggregation: [5 min]

**Total estimated Phase 2 time: [65 min]**

## PARKING LOT

[Items noted during scanning that are relevant for Tier 2/3, not Tier 1]
- [item]
```
