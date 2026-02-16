# Phase 1: Autonomous Evidence Gathering

## Purpose

Autonomous repository scanning and evidence assembly. Produces the Dialogue Agenda for Phase 2. No human interaction required during this phase.

**Time budget:** 15-30 minutes autonomous execution.

---

## Execution Sequence

### Task 1: Repository Inventory

**Objective:** Map the complete scope of what needs assessment.

**Steps:**

1. **Enumerate repositories** provided for assessment
2. **Per repository, detect:**
   - Primary language(s) and framework(s)
   - Build system (Maven, Gradle, npm, Go modules, etc.)
   - Dockerfile presence and structure
   - CI/CD pipeline configuration
   - Kubernetes manifests / Helm charts / Kustomize
   - Docker Compose files
   - Test infrastructure
3. **Produce:** Repository inventory table

```
REPOSITORY INVENTORY
====================

| Repo | Language | Framework | Build System | Dockerfile | CI/CD | K8s Manifests |
|------|----------|-----------|-------------|------------|-------|---------------|
| ...  | ...      | ...       | ...         | Y/N        | Type  | Y/N + Type    |
```

### Task 1.5: Repository Boundary Confirmation (DIALOGUE REQUIRED)

**This is the ONE Phase 1 human touchpoint.**

If multiple repositories are in scope, present the boundary map and ask:

> Here is my understanding of the repository structure:
> [boundary map]
> 
> Questions:
> 1. Is this the complete set of repositories for this application/system?
> 2. Are there repositories I should be aware of that aren't provided?
> 3. Which repositories constitute a single deployable unit vs. independent services?

**Why:** Misidentifying boundaries corrupts all four dimension assessments. 5 minutes here saves 30+ minutes of wrong-track analysis.

**Skip condition:** Single repository → skip Task 1.5, proceed to scanning.

---

### Adaptive Tool Provisioning

**Objective:** Ensure the best available static analysis tooling is in place before scanning begins.

**Reference:** See `protocol/tooling-provisioning.md` for the full criteria system, verification commands, and installation methods.

Using the inventory results, determine which tools are applicable (Semgrep is always applicable; Hadolint if Dockerfiles exist; Trivy if Dockerfiles, dependency manifests, or K8s manifests exist; dependency-cruiser if JS/TS, or language-specific alternatives for Python/Go/Java).

For each applicable tool: check if installed via verification command. If not installed and tool install consent was granted during T0.5, install silently using platform-appropriate method. If installation fails, log the failure and continue. Record the complete tooling manifest (tool, applicability, status, impact).

**This step runs autonomously with no human interaction**, provided consent was obtained during T0.5.

---

### Task 1 (continued): Per-Repository Static Scan

**Objective:** Gather evidence for all four dimensions from code and configuration. Use all available/installed tools from the provisioning step.

**Per repository, scan for:**

#### D1 Evidence (Deployment Unit Topology)

- [ ] Count Dockerfiles and their locations
- [ ] Analyze CI/CD pipelines: single vs. multi-service builds
- [ ] Check for monorepo structure indicators
- [ ] Map build artifact outputs (how many images produced?)
- [ ] Identify inter-service imports or references
- [ ] Check deployment manifest structure (single vs. per-service)
- [ ] Look for shared database migration directories
- [ ] Identify docker-compose service definitions and their dependencies

#### D2 Evidence (State and Data Model)

- [ ] Identify database libraries and connection patterns
- [ ] Scan for filesystem write operations (excluding temp/logs)
- [ ] Check for session management configuration
- [ ] Identify caching libraries and patterns (local vs. distributed)
- [ ] Look for embedded databases (SQLite, H2, BerkeleyDB)
- [ ] Check K8s manifests for PersistentVolumeClaims, StatefulSets
- [ ] Scan for in-memory data structures that grow without bound
- [ ] Identify message queue / event store connections

#### D3 Evidence (Independence Profile)

- [ ] Check for circuit breaker / resilience libraries
- [ ] Scan HTTP client configurations for timeouts and retries
- [ ] Identify message queue client libraries
- [ ] Look for service mesh configuration
- [ ] Check readiness probes for downstream dependencies
- [ ] Scan for distributed lock patterns
- [ ] Identify contract testing infrastructure
- [ ] Look for hardcoded service URLs / addresses

#### D4 Evidence (Lifecycle Compliance)

- [ ] Check for health endpoint definitions (/health, /ready, /live)
- [ ] Scan for signal handling code (SIGTERM, shutdown hooks)
- [ ] Analyze Dockerfile ENTRYPOINT/CMD form (exec vs. shell)
- [ ] Check for environment variable configuration reading
- [ ] Identify hardcoded configuration values
- [ ] Look for startup initialization sequences (migrations, cache warming)
- [ ] Check K8s manifests for probe configuration
- [ ] Scan for privileged/host access requirements
- [ ] Check for multi-process patterns (supervisord, multiple CMDs)

---

### Evidence Assembly

**Objective:** Organize raw findings into per-dimension evidence packages.

Per dimension, produce:

```
DIMENSION [D?] EVIDENCE SUMMARY
================================

STATIC INDICATORS FOUND:
  Strong:
    - [indicator]: [location] → points to [classification]
  Moderate:
    - [indicator]: [location] → points to [classification]
  Weak:
    - [indicator]: [location] → points to [classification]

PRELIMINARY HYPOTHESIS: [most likely classification based on evidence]
CONFIDENCE: [HIGH / MEDIUM / LOW]
CONFIDENCE RATIONALE: [why this confidence level]

GAPS REQUIRING DIALOGUE:
  - [what static analysis cannot determine]
  - [which question bank items should trigger]

CONTRADICTORY SIGNALS:
  - [evidence pointing in different directions]
```

---

### Dialogue Agenda Assembly

**Objective:** Determine Phase 2 dialogue structure.

For each dimension, decide:
1. **Which gap-resolution questions to ask** (from question bank, max 3 per dimension)
2. **What evidence to present** (strongest indicators first)
3. **Which dialectical triggers might fire** (based on preliminary hypothesis vs. likely human input)
4. **Estimated dialogue time** per dimension

```
DIALOGUE AGENDA
===============

DIMENSION ORDER: D1 → D2 → D3 → D4
(Fixed order — matches framework sequence)

Per dimension:
  Evidence to present: [summary of strongest signals]
  Questions planned: [Q-D?-1, Q-D?-2, ...] (from question bank)
  Potential challenges: [which dialectical triggers may fire]
  Estimated time: [X minutes]

Total estimated dialogue time: [sum] minutes
Target: 70-90 minutes for complete Phase 2
```

---

## Phase 1 Output: Evidence Package

The complete Evidence Package is handed to Phase 2. It contains:

1. Repository Inventory (Task 1)
2. Tooling Manifest (tool applicability, status, coverage impact)
3. Boundary Confirmation (Task 1.5, if applicable)
4. Per-dimension Evidence Summaries (4 documents)
5. Dialogue Agenda

**The Evidence Package is the ONLY input to Phase 2.** Phase 2 does not re-scan repositories.

---

## Scan Protocol Notes

- **Read-only access only.** Never modify repository contents.
- **Skip binary files, vendored dependencies, generated code** unless specifically relevant.
- **Prioritize configuration files and entry points** over deep source code analysis.
- **Note what you CANNOT determine** as explicitly as what you can — gaps feed the dialogue.
- **If a repository has no Dockerfile or K8s manifests,** that IS evidence (relevant for D4, potentially D1).
- **Time-box scanning.** If a repository is very large (>10k files), focus on entry points, configuration, build files, and deployment manifests. Note limited scan depth.
