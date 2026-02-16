# Exemplar Workflow: `/assess /path/to/target/repo`

## Purpose

Step-by-step algorithmic trace of a complete single-repo assessment. Shows every file load, action, decision point, output write, and transition. This is the reference execution path Claude Code is expected to follow.

---

## Notation

```
LOAD ──► file loaded into context
EXEC ──► action performed
WRITE ──► file written to output/
ASK ──► human dialogue required
CHECK ──► conditional branch
GATE ──► hard stop if condition met
```

---

## T0: Pre-Flight

```
EXEC    Parse $ARGUMENTS → repo_path = "/path/to/target/repo"
CHECK   Does repo_path exist and is readable?
        ├─ NO  → STOP. Report: "Repository path not found or not accessible."
        └─ YES → continue
EXEC    Create output/ directory if not exists
EXEC    Announce to human:
        "Assessing: /path/to/target/repo
         Estimated time: ~1.5-2.5 hours
         Phase 1 runs autonomously (~15-30 min). I'll engage you for Phase 2."
```

**Completion marker:** `output/` directory exists

---

## T0.5: Tooling Readiness

```
LOAD    reference/protocol/tooling-provisioning.md

EXEC    Quick-scan repo for file type markers:
        ├─ ls for Dockerfile* → Hadolint + Trivy applicable?
        ├─ ls for package.json, *.ts, *.js → dependency-cruiser applicable?
        ├─ ls for go.mod → go mod graph built-in (no install needed)
        ├─ ls for requirements.txt, *.py → pydeps applicable?
        ├─ ls for pom.xml, *.java → jdeps built-in (no install needed)
        ├─ ls for K8s manifests → Trivy applicable?
        └─ Semgrep: ALWAYS APPLICABLE

EXEC    Compile applicable tools list (e.g.):
        "Tools applicable for this repository:
         - Semgrep (pattern detection across all dimensions)
         - Hadolint (Dockerfile analysis — 2 Dockerfiles detected)
         - Trivy (vulnerability scanning — Dockerfiles + package.json detected)"

ASK     "As part of Phase 1, I may need to install static analysis tools
         that aren't already on your system. [list above].

         May I install any needed tools during the scan?

         If you decline, the assessment proceeds with reduced static analysis
         coverage — more ambiguity in evidence, more questions for you in
         Phase 2, and potentially lower-confidence classifications."

CHECK   Human response:
        ├─ CONSENT → Record: tool_install_consent = TRUE
        │               Proceed to T1 with full provisioning authority.
        │
        ├─ DECLINE → Record: tool_install_consent = FALSE
        │              WARN: "Understood. Proceeding without tool installation.
        │                     Evidence gathering will rely on code reading and
        │                     basic pattern matching. Phase 2 will be longer.
        │
        │                     You can change this decision at any time before
        │                     Phase 1 completes by saying 'install the tools'."
        │              Proceed to T1 in degraded mode.
        │
        └─ PARTIAL → Record per-tool consent. Proceed accordingly.
```

**Completion marker:** Consent decision recorded

---

## T1: Repository Analysis (Autonomous)

```
LOAD    reference/protocol/phase1-evidence-gathering.md
LOAD    reference/protocol/tooling-provisioning.md
LOAD    reference/templates/evidence-package.md

EXEC    1. REPOSITORY INVENTORY
        ├─ Detect primary language(s) (file extensions, package manifests)
        ├─ Detect build system (Makefile, package.json, pom.xml, go.mod, etc.)
        ├─ Detect dependency manifest(s) and parse dependencies
        ├─ Detect Dockerfile(s) — count, location, base images
        ├─ Detect docker-compose.yml — services, volumes, networks, depends_on
        ├─ Detect CI/CD config (.github/workflows/, .gitlab-ci.yml, Jenkinsfile, etc.)
        ├─ Detect K8s manifests (deployments, services, ingress, HPA, etc.)
        └─ Detect config patterns (.env files, config maps, secrets references)

EXEC    2. ADAPTIVE TOOL PROVISIONING
        FOR EACH applicable tool (from T0.5 applicability list):
        │
        ├─ CHECK: Is tool installed? (run verification command)
        │  ├─ YES → Record: tool = AVAILABLE
        │  └─ NO  → CHECK: tool_install_consent?
        │         ├─ TRUE  → EXEC: Install silently (per platform methods)
        │         │         CHECK: Install succeeded?
        │         │         ├─ YES → Record: tool = INSTALLED
        │         │         └─ NO  → Record: tool = INSTALL_FAILED, reason
        │         │                  (NO dialogue interruption. Continue.)
        │         └─ FALSE → Record: tool = SKIPPED_BY_USER
        │
        RESULT: Tooling manifest:
        ├── Semgrep: INSTALLED
        ├── Hadolint: AVAILABLE (already on system)
        ├── Trivy: INSTALL_FAILED (network timeout)
        └── dependency-cruiser: NOT_APPLICABLE

EXEC    3. PER-DIMENSION STATIC EVIDENCE COLLECTION
        │
        ├─ D1 signals:
        │   ├─ Count Dockerfiles and build contexts
        │   ├─ Analyze CI pipeline structure (single vs multi-service)
        │   ├─ Check for cross-service imports or shared DB migrations
        │   ├─ Check docker-compose for deployment coupling signals
        │   └─ Classify: strong/moderate/weak indicators per D1 reference
        │
        ├─ D2 signals:
        │   ├─ Detect DB/cache/queue client libraries in dependencies
        │   ├─ Search for filesystem I/O patterns (writes to local disk)
        │   ├─ Search for in-memory state patterns (global variables, singletons with state)
        │   ├─ Check for session management approach
        │   └─ Classify: strong/moderate/weak indicators per D2 reference
        │
        ├─ D3 signals:
        │   ├─ Detect circuit breaker / retry / resilience libraries
        │   ├─ Detect inter-service communication patterns (HTTP clients, gRPC, message queues)
        │   ├─ Analyze dependency graph for coupling density
        │   ├─ Check for shared libraries (versioned vs path-referenced)
        │   └─ Classify: strong/moderate/weak indicators per D3 reference
        │
        └─ D4 signals:
            ├─ Check Dockerfile for health endpoint exposure
            ├─ Search for SIGTERM / graceful shutdown handlers
            ├─ Check for externalized config (env vars, config injection)
            ├─ Analyze startup sequence (heavy initialization, migration-on-start)
            ├─ Run Hadolint on Dockerfile(s) if available
            └─ Classify: strong/moderate/weak indicators per D4 reference

EXEC    4. EVIDENCE ASSEMBLY
        ├─ Populate evidence-package template with all findings
        ├─ Include tooling manifest (what ran, what didn't, why)
        ├─ Per dimension: list evidence, assign confidence (HIGH/MEDIUM/LOW)
        └─ Per dimension: generate dialogue agenda (confirmed facts, ambiguities, questions to ask)

WRITE   output/evidence-package.md

EXEC    5. Announce Phase 1 complete:
        "Phase 1 complete. Evidence package assembled.
         Key findings: [2-3 sentence summary of most notable signals].
         Ready for Phase 2 — structured assessment dialogue."
```

**Completion marker:** `output/evidence-package.md` exists

---

## T1.5: Repo Boundary Confirmation

```
CHECK   Multi-repo assessment?
        ├─ YES → ASK: Present repo boundary map, collect human confirmation
        └─ NO  → SKIP (single repo, boundaries are the repo itself)
```

---

## Phase 2: Structured Assessment Dialogue

```
LOAD    reference/protocol/phase2-assessment-dialogue.md
```

### T2: D1 Assessment

```
LOAD    reference/dimensions/d1-deployment-unit-topology.md

EXEC    1. PRESENT EVIDENCE
        "For D1 (Deployment Unit Topology), here's what I found:
         Strong indicators: [list from evidence package]
         Moderate indicators: [list]
         Weak indicators: [list]
         Overall confidence: [HIGH/MEDIUM/LOW]"

EXEC    2. PROPOSE CLASSIFICATION
        "Based on this evidence, I'd propose: [T1/T2/T3/T4] — [name].
         Rationale: [1-2 sentences mapping evidence to decision tree path].
         This is a proposal — your call."

ASK     3. GAP RESOLUTION (only questions triggered by ambiguity)
        CHECK   Are there ambiguities in the evidence?
        ├─ YES → Ask from question bank (max 3):
        │        Q-D1-1 if T1 vs T4 boundary unclear
        │        Q-D1-2 if T2 vs T3 boundary unclear
        │        Q-D1-3 if hidden coupling signals present
        │        Map each answer to classification implication
        └─ NO  → Skip to step 4

EXEC    4. DIALECTICAL CHALLENGES
        LOAD    reference/protocol/dialectical-challenges.md
        │
        CHECK   Category 1: Does human's stated classification contradict evidence?
        │       ├─ YES → Challenge (max 2 rounds):
        │       │        "The CI pipeline at [path] builds all services together.
        │       │         Can you explain how independent deployment works in practice?"
        │       │        ├─ Human provides satisfactory explanation → accept
        │       │        └─ Round 2 exhausted → record as noted tension, proceed with human's classification
        │       └─ NO  → skip
        │
        CHECK   Category 3: Does the classification trigger downstream implications?
                ├─ T4 locked → Surface: "T4 = BLOCKED. Must address before proceeding."
                ├─ T3 + other dims scoring 3 → Surface: "T3 caps orchestration benefits."
                └─ T1 + many services → Surface: "Multi-service T1. Confirm repo boundary map."

EXEC    5. LOCK CLASSIFICATION
        Record: D1 = [code], score = [0-3], confidence = [H/M/L]

LOAD    reference/templates/dimension-assessment.md
WRITE   output/dimension-d1.md

EXEC    Announce: "D1 locked: [code] [name] (score [N]). Moving to D2."
```

### T3: D2 Assessment

```
LOAD    reference/dimensions/d2-state-and-data-model.md

        [Same 5-step pattern as T2:
         Present evidence → Propose → Gap resolution → Dialectical → Lock]

WRITE   output/dimension-d2.md
```

### T4: D3 Assessment

```
LOAD    reference/dimensions/d3-independence-profile.md

        [Same 5-step pattern]

WRITE   output/dimension-d3.md
```

### T5: D4 Assessment

```
LOAD    reference/dimensions/d4-lifecycle-compliance.md

        [Same 5-step pattern]

WRITE   output/dimension-d4.md
```

### T5.5: Cross-Dimension Tension Check

```
LOAD    reference/tensions/cross-dimension-tensions.md

EXEC    For each tension in catalog:
        CHECK   Do locked D1/D2/D3/D4 classifications match this tension's trigger?
        │
        ├─ MATCH → Surface to human:
        │          "Tension detected: [ID] — [description].
        │           D[X]=[code] and D[Y]=[code] create [tension explanation].
        │           Options: (1) revise one classification, (2) acknowledge and proceed."
        │
        │          ASK    Human decision
        │          ├─ Revise → re-open affected dimension via T2/T3/T4/T5 pattern
        │          │           (NOTE: this is a mini-reassessment, not full /assess-dimension)
        │          └─ Acknowledge → record tension as accepted, proceed
        │
        └─ NO MATCH → skip

CHECK   All fired tensions resolved or acknowledged?
        ├─ YES → proceed to T6
        └─ NO  → remain in T5.5 until resolved
```

### T6: Tier 1 Aggregation

```
LOAD    reference/aggregation/tier1-scoring.md
LOAD    reference/templates/tier1-fitness-report.md

EXEC    1. Collect scores: D1=[n], D2=[n], D3=[n], D4=[n]
        2. Total = D1 + D2 + D3 + D4
        3. Apply rules:
           ├─ Any dimension = 0? → FITNESS = BLOCKED
           ├─ Total ≥ 10 AND all dimensions ≥ 2? → FITNESS = HIGH
           ├─ Total 6-9 OR any dimension = 1? → FITNESS = MEDIUM
           └─ Total ≤ 5? → FITNESS = LOW
        4. If any dimension = 1 → cap at MEDIUM regardless of total
        5. Determine candidate deployment paths per fitness level

WRITE   output/tier1-fitness-report.md

EXEC    Present result:
        "Tier 1 complete.
         Scores: D1=[n], D2=[n], D3=[n], D4=[n]. Total: [N]/12.
         Fitness: [BLOCKED/LOW/MEDIUM/HIGH].
         Candidate paths: [list]."

GATE    FITNESS = BLOCKED?
        ├─ YES → HARD STOP.
        │        "Assessment is BLOCKED. Dimension(s) [list] scored 0.
        │         Remediation required before deployment path assessment.
        │         Blocking issue(s): [from fitness outcomes reference].
        │         This assessment cannot proceed to Tier 2 until blockers are resolved."
        │        ──► STOP. Do NOT proceed to Phase 3.
        │
        └─ NO  → proceed to Phase 3
```

**Completion marker:** `output/tier1-fitness-report.md` exists

---

## Phase 3A: Tier 2 Constraint Collection

```
LOAD    reference/protocol/phase3-strategic-guidance.md
LOAD    reference/aggregation/tier2-filtering.md

EXEC    Transition announcement:
        "Tier 1 fitness is [level]. Candidate paths: [list].
         Now collecting external constraints to filter these paths.
         Three constraints, applied sequentially."
```

### T7a: C1 Infrastructure Availability

```
LOAD    reference/constraints/c1-infrastructure-availability.md

ASK     "What deployment infrastructure is available for this application?
         Specifically: is there a managed Kubernetes cluster (GKE, EKS, AKS)?
         Container runtime without full orchestration? PaaS only? VMs/bare metal only?"

        CHECK   Any infrastructure evidence from Phase 1?
                (K8s manifests found, Helm charts, Terraform with GKE, etc.)
                ├─ YES → "Phase 1 found [evidence] suggesting [IA level]. Does this match?"
                └─ NO  → collect from human directly

EXEC    Classify: C1 = [IA1/IA2/IA3/IA4] (+IA5 overlay?)
EXEC    Apply viability filter immediately:
        "With [IA level], path viability:
         Container-Native: [VIABLE/GAPS/ELIMINATED]
         Container-Simplified: [VIABLE/GAPS/ELIMINATED]
         VM/IaaS: [VIABLE/GAPS/ELIMINATED]"
```

### T7b: C2 Compliance Posture

```
LOAD    reference/constraints/c2-compliance-posture.md

ASK     "What compliance or regulatory requirements apply?
         SOC2, HIPAA, PCI, GDPR, FedRAMP, other? Or just organizational policies?"

EXEC    Classify: C2 = [CP1/CP2/CP3/CP4]
EXEC    Apply cumulative filter:
        "With [CP level] on top of [IA level]:
         [updated path viability]
         Accumulated requirements added: [list from CP level]"
```

### T7c: C3 Organizational Topology

```
LOAD    reference/constraints/c3-organizational-topology.md

ASK     "How is the team organized around this application?
         One team owning everything? Multiple teams? Cross-organizational?"

EXEC    Classify: C3 = [O1/O2/O3/O4]
EXEC    Team capability sub-assessment:
        ASK  "What's the team's experience with Kubernetes and GitOps?"
EXEC    Apply final filter:
        "With [O level] on top of [IA+CP]:
         [final path viability]
         Additional operational requirements: [list]
         Capability gaps flagged: [list or none]"
```

### T7.5: Tier 2 Aggregation

```
LOAD    reference/templates/constraint-map.md

EXEC    1. Assemble constraint map: C1=[IA?], C2=[CP?], C3=[O?]
        2. Check compound effects (reference: tier2-filtering.md compound patterns table)
        3. Final surviving paths with all accumulated requirements
        4. Check for CONSTRAINT DEADLOCK: all candidate paths ELIMINATED?

WRITE   output/constraint-map.md

GATE    CONSTRAINT DEADLOCK?
        ├─ YES → HARD STOP.
        │        "CONSTRAINT DEADLOCK. No viable deployment path survives all constraints.
        │         Blocking constraints: [list].
        │         Resolution options:
        │         1. Invest to change the hardest constraint (usually C1).
        │         2. Accept a suboptimal path with documented trade-offs.
        │         3. Return to Tier 1 reassessment."
        │        ASK  Human chooses resolution
        │        ──► If resolved: update constraint-map.md, proceed
        │        ──► If unresolved: STOP.
        │
        └─ NO  → proceed to Phase 3B

EXEC    Transition announcement:
        "Constraints applied. Surviving path(s): [list].
         Accumulated requirements: [summary count].
         Now determining deployment strategy."
```

**Completion marker:** `output/constraint-map.md` exists

---

## Phase 3B: Tier 3 Strategic Selection

### T8a: S1 Lifecycle Stage

```
LOAD    reference/choices/s1-lifecycle-stage.md

ASK     "Where is this application in its lifecycle?
         LS1 Greenfield — no production users yet
         LS2 Active Evolution — users + active feature development
         LS3 Stable/Maintenance — bug fixes and patches only
         LS4 Sunset — being decommissioned"

EXEC    Record: S1 = [LS?]
CHECK   Immediate tension?
        ├─ LS4 selected → note: expect minimal deployment investment
        └─ otherwise → proceed
```

### T8b: S2 Velocity Target

```
LOAD    reference/choices/s2-velocity-target.md
LOAD    reference/tensions/strategy-tensions.md

EXEC    Narrow options by Tier 2 constraints:
        ├─ CP4 air-gap? → flag VT1 infeasibility from external sources
        ├─ O2 shared pipeline? → flag VT1 merge pressure
        ├─ O4 cross-org? → flag VT4 may be forced at boundaries
        └─ Capability gaps? → flag VT1 realism

ASK     "How frequently should changes reach production?
         [Present only feasible options with brief constraint notes]
         VT1 Continuous — every merge is a deploy candidate [feasible/constrained/infeasible]
         VT2 On-Demand — deploy when ready, no fixed schedule
         VT3 Cadenced — fixed schedule (weekly/biweekly/monthly)
         VT4 Coordinated — multi-system synchronized releases"

EXEC    Record: S2 = [VT?]

CHECK   VT4 selected?
        ├─ YES → MANDATORY VALIDATION:
        │        ASK  "Is this coordination driven by business need or technical coupling?
        │              If technical coupling → may need to revisit D1/D3."
        │        ├─ Business need → accept VT4
        │        └─ Technical coupling → flag Tier 1 reassessment signal, record in notes
        └─ NO  → proceed

CHECK   Strategy tensions (S1 × S2):
        ├─ ST-02: LS3 + VT1? → surface tension
        ├─ ST-03: LS4 + VT1/VT2? → surface tension
        └─ ST-07: VT1 + O2? → surface tension
        For each fired: ASK human to accept/adjust/invest
```

### T8c: S3 Risk Tolerance

```
LOAD    reference/choices/s3-risk-tolerance.md

EXEC    Narrow options by constraints + prior selections:
        ├─ IA2? → RT1 may lack traffic splitting infra
        ├─ IA3 PaaS? → RT options limited to PaaS capabilities
        ├─ Capability gaps? → RT1 may be unrealistic
        └─ CP3/CP4? → RT2 doubles compliance surface

ASK     "How should deployment risk be managed?
         [Present only feasible options]
         RT1 Progressive (Canary) — gradual traffic shift, automated rollback
         RT2 Parallel (Blue-Green) — full duplicate env, instant switch
         RT3 Rolling — sequential replacement, zero-downtime
         RT4 Direct — replace in place, downtime acceptable"

EXEC    Record: S3 = [RT?]

CHECK   Full strategy tension scan (S1 × S2 × S3 + Tier 2):
        For each tension in strategy-tensions.md catalog:
        ├─ MATCH → surface with severity:
        │          Advisory → note and proceed
        │          Warning → recommend mitigation, ASK human
        │          Conflict → MUST resolve before proceeding
        └─ NO MATCH → skip

CHECK   Archetype matching:
        LOAD    reference/aggregation/tier3-composition.md
        EXEC    Compare [S1, S2, S3] against archetype table
        ├─ MATCH → "Your selections align with [archetype name]: [brief description]. Sound right?"
        └─ NO MATCH → "This combination doesn't match a standard pattern — that's fine,
                        but worth confirming it's intentional: [S1+S2+S3 summary]."
        ASK     Human confirms or adjusts
```

---

## T9: Deployment Profile Assembly

```
LOAD    reference/templates/deployment-profile.md

EXEC    1. READ all output files:
           ├─ output/evidence-package.md (for application identity, repo info)
           ├─ output/dimension-d1.md through dimension-d4.md
           ├─ output/tier1-fitness-report.md
           └─ output/constraint-map.md

        2. POPULATE template:
           ├─ Application Identity section
           ├─ Tier 1: dimension scores, aggregation, tensions
           ├─ Tier 2: constraints, path viability, requirements, gaps
           ├─ Tier 3: selections, archetype, strategy tensions
           ├─ Summary: one-line profile, key decisions, open items
           └─ Framework boundary reminder

        3. PRESENT to human:
           "Here is the complete Deployment Profile: [full profile content]"

ASK     "Does this accurately capture the assessment? Any corrections?"

CHECK   Human requests revision?
        ├─ YES → Identify what changed:
        │        ├─ Tier 1 score change → recalculate fitness → re-filter paths → re-validate strategy
        │        ├─ Tier 2 constraint change → re-filter paths → re-validate strategy
        │        └─ Tier 3 selection change → re-check tensions → re-match archetype
        │        EXEC cascade, re-present profile, ASK again
        └─ NO  → lock profile

WRITE   output/deployment-profile.md
```

**Completion marker:** `output/deployment-profile.md` exists

---

## T10: Completion

```
EXEC    Announce:
        "Assessment complete.

         [One-line summary, e.g.:]
         MyApp: HIGH fitness → Container-Native (K8s) via Cloud-Native Ideal
         (T1=3, S2=2, I2=2, L1=3 | IA1, CP2, O1 | LS2, VT1, RT1)

         This is Framework 1 output — the Deployment Profile.
         Migration execution planning (Framework 2) is a separate activity.

         Output files in output/:
         ├── evidence-package.md
         ├── dimension-d1.md through dimension-d4.md
         ├── tier1-fitness-report.md
         ├── constraint-map.md
         └── deployment-profile.md"
```

---

## Failure Mode Summary

| Condition | Where Detected | Action |
|---|---|---|
| Repo path invalid | T0 | Stop immediately. Report error. |
| Static analysis tooling unavailable | T1 | Degrade gracefully. Evidence package notes reduced coverage. Dialogue agenda has more gaps. |
| Any dimension = 0 (BLOCKED) | T6 gate | Hard stop. Present remediation. Do not proceed to Phase 3. |
| All paths eliminated (DEADLOCK) | T7.5 gate | Hard stop. Present resolution options. Do not proceed to Tier 3. |
| Hard incompatibility in Tier 3 | T8c tension check | Must resolve before profile assembly. At least one selection revised. |
| Human requests revision at T9 | T9 review | Execute cascade, re-present, re-confirm. |
| Session interrupted at any point | `/assess-resume` | Detect state from output files, resume at next incomplete task. |

---

## Timing Trace

```
T0  Pre-Flight ·························· ~1 min
T1  Repository Analysis ················· ~15-30 min  ─┐
                                                       ├─ AUTONOMOUS
T1.5 Boundary Confirmation ·············· ~0-3 min   ─┘
T2  D1 Assessment ······················· ~10-15 min ─┐
T3  D2 Assessment ······················· ~10-15 min  │
T4  D3 Assessment ······················· ~10-15 min  ├─ DIALOGUE
T5  D4 Assessment ······················· ~10-15 min  │
T5.5 Tension Check ······················ ~0-10 min   │
T6  Tier 1 Aggregation ·················· ~2 min     ─┘
T7a C1 Collection ······················· ~3-5 min  ──┐
T7b C2 Collection ······················· ~5-10 min   │
T7c C3 Collection ······················· ~5-10 min   ├─ DIALOGUE
T7.5 Tier 2 Aggregation ················· ~2 min      │
T8a S1 Selection ························ ~2-3 min    │
T8b S2 Selection ························ ~5-10 min   │
T8c S3 Selection ························ ~5-10 min  ─┘
T9  Profile Assembly ···················· ~5-10 min
T10 Completion ·························· ~1 min
─────────────────────────────────────────────────────
TOTAL ··································· ~90-160 min
```
