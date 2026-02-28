# qwen3-coder:30b-a3b-q8_0 — Phase 1 Assessment Capability Evaluation
**Scope:** 12-repo validation test set
**Date:** 2026-02-28
**Model:** qwen3-coder:30b-a3b-q8_0 (local Ollama, ~3B active params MoE)
**Evaluator:** Claude Sonnet 4.6 (CC T1.8 synthesis across all 12 repos)

---

## Executive Verdict

The model is capable of executing Phase 1 as a **mechanical protocol walker**. It can run tools, traverse the prescribed steps, populate templates, and produce output that superficially resembles expert analysis. It cannot reliably perform the reasoning that makes Phase 1 useful. Across 12 repos, **50% of runs required score corrections**, **75% of L4 disqualifier firings were false positives**, and the model produced direct evidence-conclusion contradictions in its own reports on multiple occasions without detecting them.

This is not a performance profile that degrades gracefully with model size. It is a profile that produces confident-sounding wrong answers — which is worse than "I don't know."

---

## Quantitative Scorecard

**Score accuracy per repo:**

| Repo | Reported | Corrected | Direction | Root cause |
|------|----------|-----------|-----------|-----------|
| minio | 8/12 | 8/12 | — | D1 T3→T2 arguable but no score diff; D2 correct answer, wrong reasoning |
| airflow | 4/12 | 6/12 | **↑+2** | D4 false positive (CI container scoped as production) |
| keycloak | 9/12 | 9/12 | — | D1 T1→T2 arguable but no score diff; Infinispan question unasked |
| nextcloud | 7/12 | 8/12 | **↑+1** | D4 false positive (absence of Dockerfile = L4, despite own CLEAR check) |
| ghost | 9/12 | 8/12 | **↓−1** | D3 scoring error: I3 assigned score=2 (correct: 1) |
| vault | 9/12 | 7–9/12 | pending | D4 unsealing not assessed; D2 BoltDB dismissed without justification |
| gitea | 9/12 | 10/12 | **↑+1** | D1 scan false negative: 0 Dockerfiles returned; T3 built on null evidence |
| portainer | 9/12 | 8–9/12 | pending | D2 scan failure: BoltDB missed ("no embedded databases" is wrong) |
| spring-petclinic | 7/12 | 6–8/12 | pending | D3 scoring error; D4 L3 false (Spring Boot JVM hooks) |
| prometheus | 9/12 | 8/12 | **↓−1** | D2: S3 described throughout, classified S2+S3cap=NO — direct contradiction |
| docker-mailserver | 6/12 | 5/12 | **↓−1** | D3 scoring error; D3 category confusion (intra vs inter-container coupling) |
| traefik | 10/12 | 10/12 | — | D4 env var false negative (library abstraction); 3 extra files |

**6 out of 12 runs (50%) have confirmed score errors.** 3 are downward corrections (model overscored), 3 are upward corrections (model underscored via false positives that inflated penalty). The errors are bidirectional — this is not a consistent bias, it is noise.

---

## Failure Taxonomy

### Category 1 — Mechanical scoring rule failures (3/12 = 25%)

The D3 scoring table is explicit: I3 = score 1, I2 = score 2. qwen3 assigned I3 classification with score=2 in ghost, spring-petclinic, and docker-mailserver. This is a rule that requires no domain knowledge to apply — it requires only reading a table and checking that classification and score are consistent. The model failed it 25% of the time. The SCORING CONSISTENCY RULE guard injected into d1-topology.md (Category C fix) prevented the analogous D1 error from occurring, which confirms the guard helps. The D3 equivalent guard was not added; the error recurred freely.

This is the most indicting failure category. If the model cannot reliably apply its own scoring rules, the quantitative output of Phase 1 cannot be trusted without verification.

### Category 2 — Disqualifier false positives (3 false positives out of 4 firings = 75% FPR)

L4 fired on: airflow (CI container), nextcloud (absent Dockerfile), spring-petclinic (JVM hooks invisible), docker-mailserver (genuine). Three of four are wrong.

The nextcloud case is the most structurally severe: the D4 disqualifier check returned **CLEAR — no indicators found**, and the model assigned L4 anyway with HIGH confidence. Those two statements cannot coexist in a coherent report. The model wrote CLEAR, then ignored it. This indicates the model does not read back its own prior outputs within the same turn to check consistency — it produces each section as a forward pass without backward verification.

The airflow case (CI directory scoped as production) shows inadequate path analysis: `scripts/ci/dockerfiles/krb5-kdc-server/` should be obviously CI-scoped. The model has the evidence in front of it and misclassifies it.

The spring-petclinic case reveals a domain knowledge floor: Spring Boot's SIGTERM handling is framework-level and produces no visible signal handler code. This is well-known in Java deployment contexts. The model has no knowledge of it and classifies the absence as a disqualifier.

### Category 3 — D2 evidence quality failures (6/12 = 50%)

This is the broadest failure category. D2 is the framework's most evidence-dependent dimension — it asks "what does the application write to disk, and is that managed?" The model's D2 scanner relies on pattern matching against known database clients and local write patterns. It fails in multiple distinct ways:

- **Pattern miss:** bbolt (`go.etcd.io/bbolt`) not in the standard DB pattern library. Portainer's entire persistence layer is bbolt, and D2 returned "no embedded databases." D3 found `api/database/boltdb/db.go` in the same run. The model did not cross-reference its own evidence between dimensions.

- **Application-domain blindness:** Gitea stores git repositories as files in `/data/gitea/repositories/`. This is Gitea's primary content store — every git push writes there. D2 did not assess it at all. A human familiar with Gitea would ask this as the first D2 question. The model has no operational knowledge of what Gitea stores.

- **Evidence-conclusion inversion — worst case (prometheus):** The D2 report documented WAL on local disk, chunk files on local disk, index files on local disk, mmapped query tracking, and explicitly stated *"This is not a stateless application in the traditional sense, as it must maintain state in local storage."* The conclusion section returned S2 with S3 Cap = NO. The evidence and the conclusion are in direct contradiction. The model did not detect this. For a production decision-support framework, this category of failure — confident wrong answer backed by evidence that refutes itself — is the most dangerous possible output.

- **Dismissal without justification:** Vault's D2 flagged BoltDB in the Agent cache as an S3 indicator, then returned "S3 Cap: Not applicable" without explanation. No reasoning given for why a flag was raised and then dismissed. This is not analysis — it is the appearance of analysis.

**Affected repos:** minio (wrong evidence), prometheus (contradiction), portainer (bbolt missed), docker-mailserver (embedded Redis missed), gitea (git repo storage not assessed), vault (BoltDB dismissed).

### Category 4 — Domain knowledge gaps (systematic, ~6/12)

The model lacks operational knowledge of specific technologies' deployment patterns:

- **Vault unsealing:** the most critical Vault lifecycle concern (sealed container = zero-operation until keys provided) does not appear anywhere in the D4 assessment. The model treated Vault's D4 as a generic Go binary.
- **Spring Boot JVM shutdown hooks:** framework-level SIGTERM handling via `ConfigurableApplicationContext.close()` is standard Spring Boot behavior. Invisible to pattern-based scanning. The model classified the absence as a lifecycle deficiency.
- **Spring Boot buildpacks:** OCI images built via `mvn spring-boot:build-image` produce valid containers without Dockerfiles. K8s manifests with `/readyz` and `/livez` probes in the same repo confirm the app runs containerized. The model cited "no production Dockerfile" as evidence of non-containerization while K8s probe configs for that container existed in the same repository.
- **Prometheus TSDB:** single-writer local-disk time-series database is the canonical S3 pattern. The model found all the evidence (WAL, chunks, index, mmap) and still returned S2.
- **Traefik paerser library:** env var configuration via struct tags + reflection produces no `os.Getenv()` calls. The scanner found nothing and concluded no env var support exists. The conclusion is wrong in a way that matters for D4 classification.

The pattern is consistent: when a technology implements a standard behavior through a non-trivial abstraction or framework convention, the model defaults to "not found = not present" rather than "not found = inconclusive."

### Category 5 — D3 conceptual failures

Beyond the scoring error, D3 shows a deeper confusion in docker-mailserver: the model applied intra-container supervisord startup ordering as D3 evidence. D3 measures external service coupling — dependencies on *other deployed services* that constrain independent deployment and scaling. The internal ordering of services within a single container is a D1/D4 concern, not D3. The model crossed dimension boundaries and used evidence from the wrong level of analysis.

This is not a tool capability issue. It is a framework-semantic issue. The model does not consistently maintain the conceptual distinction between "services within a container" and "services between containers." This limits D3 assessment quality for any complex single-container application.

### Category 6 — Output hygiene failures (8/12 = 67%)

8 of 12 runs produced files outside the expected 5-file set. Portainer produced 4 extra files including one (`d3_report_portainer.md`) with the wrong filename entirely. The D3 evidence report would have been lost as a separately named file if the assembler had only looked for the standard name. The model receives explicit instructions on what files to write and writes additional files anyway — consistently, in two-thirds of runs.

### Category 7 — Agenda degeneration (systematic, ~10/12)

The dialogue agenda is the primary Phase 2 deliverable from Phase 1. In most runs, questions are:
- Generic ("What are actual deployment practices?" repeated across 3 dimensions — minio)
- Duplicated verbatim between dimensions (D2 and D3 identical questions — gitea, airflow)
- Redundant (10 questions in keycloak, 12 in portainer; collapsed to 3 meaningful ones each in synthesis)
- Wrongly scoped to the wrong dimension (D2 asking D3 questions — airflow)

The framework provides question banks in reference files for each dimension. The model is not using them effectively — it is generating questions ad hoc and producing volume over precision. The agenda in virtually every run required significant CC rewriting before it was usable for Phase 2.

Traefik was the exception: questions were distinct and domain-appropriate. That is 1/12.

### Category 8 — Parking lot cross-signal error (systematic, 5/12)

"Named volume/local storage → T4 detection" appeared in the D2→D1 parking lot of vault, ghost, prometheus, portainer, and docker-mailserver. T4 is a topology disqualifier — it fires when deployment units are so tightly coupled they cannot be independently containerized. Local storage has no logical relationship to T4. This is a hallucinated cross-signal that the model reproduced in 5+ consecutive runs without correction, suggesting it is a learned pattern that the model cannot reason out of.

Confirmed trigger: volume mounts present in docker-compose. Traefik has no docker-compose volume mounts — and the T4 parking lot signal is absent. The pattern is systematic, not random.

---

## Reliability by Dimension

### D1 — Deployment Unit Topology
**Reliability: MEDIUM**

The model correctly identifies single-Dockerfile / single-binary structure. It correctly runs T4 disqualifier checks in most cases and correctly identifies shared migration directories as T4 indicators (airflow). It fails at T1 vs T2 boundary reasoning (keycloak: multiple Dockerfiles ≠ microservices) and has at least one tooling-level scan failure (gitea: 0 Dockerfiles returned). Score errors tied directly to D1 are uncommon because T1 and T2 share score=3, absorbing the classification imprecision. If the scoring table penalized T1/T2 distinctions, D1 error rate would be more visible.

### D2 — State and Data Model
**Reliability: LOW**

The worst dimension by evidence quality. 6/12 runs have material D2 issues. The model's scanner is effectively a standard library import search, which catches PostgreSQL, Redis, and similar obvious clients but misses embedded databases with non-standard import paths (bbolt), application-domain file storage (git repos, mail Maildir), and framework-abstracted state (Prometheus TSDB). The prometheus run produced a direct evidence-conclusion contradiction that the model did not detect — the hardest possible evidence of unreliable reasoning. D2 conclusions cannot be accepted without CC verification for any application with non-standard state management.

### D3 — Independence Profile
**Reliability: LOW-MEDIUM**

Two independent failure modes stack here: (1) scoring errors that occur 25% of the time regardless of classification quality, and (2) classification reasoning that conflates levels of analysis (intra-container vs inter-service coupling). The 40-50% static ceiling acknowledgment in the header is correct — but the model then systematically reports HIGH confidence anyway, negating the value of the caveat. D3 is the dimension the framework explicitly acknowledges has high dialogue dependency. The model's tendency to fill in HIGH regardless undermines that signal entirely.

On the positive side: traefik's D3 is the best in the set — correct classification, correct score, substantive evidence with real library names and line references. The model CAN perform well on D3 for well-structured Go applications with obvious resilience patterns. The failure mode is systematic overconfidence on ambiguous cases.

### D4 — Lifecycle Compliance
**Reliability: MEDIUM-HIGH for L1/L2/L3; LOW for L4 disqualifier**

When D4 is not firing a disqualifier, it is the strongest dimension. The model reliably finds SIGTERM handlers, exec-form ENTRYPOINT, health endpoints, and env var patterns for standard Go and Node.js applications. Gitea's D4 is the best single-dimension output in the test set — STOPSIGNAL, HEALTHCHECK, exec ENTRYPOINT, graceful shutdown module with file path, health API with endpoint — genuine expert-level evidence gathering.

The L4 disqualifier is a different story. 75% false positive rate is not acceptable for a binary gate that blocks the entire assessment. The model fires L4 on CI containers, absent Dockerfiles, and invisible framework signals with equal confidence as genuine multi-daemon supervisord setups. It does not verify scope (CI vs production) before firing. It does not check whether disqualifier evidence is conclusory absence or positive presence.

---

## Root Cause Analysis

The 3B active parameter budget (MoE architecture — 30B total, ~3B active at inference) produces a specific capability profile: strong pattern matching on well-represented training patterns, weak cross-context reasoning that requires integrating evidence across sections of a long document.

The concrete evidence for this:

1. **Intra-document inconsistency** (nextcloud D4: CLEAR disqualifier check → L4 classification; prometheus D2: S3 evidence throughout → S2 conclusion) is a cross-context failure. The model processes each template section semi-independently. It does not hold earlier outputs in working memory when generating later outputs in a way that enables contradiction detection.

2. **Scoring rule failures** (I3→score 2) occur because the model generates a classification string in one pass and a score number in another pass, without explicitly checking the lookup table. A larger model under the same prompting would be more likely to self-verify; at 3B effective params the self-verification step appears unreliable.

3. **Generic agenda generation** reflects that the model is not retrieving from the framework's question banks — it is generating similar-sounding questions from its general training distribution. The question banks are specific; the generated questions are generic. This is a retrieval-depth failure.

4. **Domain knowledge gaps** reflect training coverage. The model knows about Docker SIGTERM and supervisord in general terms but does not have operational depth on Vault's seal lifecycle, Spring Boot's shutdown architecture, or Prometheus's TSDB design.

The important distinction: **most of these failures are not random noise**. They are systematic — the same parking lot cross-signal appears in 5 consecutive repos, the same D3 scoring error recurs independently, the same confidence inflation on D3 appears in 8 of 12 runs. Systematic failures suggest learned wrong patterns, not stochastic error. Learned wrong patterns do not improve with more prompting — they require either model improvement or structural guards.

---

## Capability Floor and Ceiling

**Floor — what it reliably delivers:**
- Protocol step execution (tool invocation, file writing, output format)
- Dockerfile structural analysis (multi-stage builds, ENTRYPOINT form, STOPSIGNAL)
- Single-technology surface scan (go.mod structure, CI pipeline filenames, K8s YAML presence)
- D4 L1/L2/L3 classification for standard Go and Node.js applications without framework abstractions
- D1 topology for applications with straightforward Dockerfile-count topology

**Ceiling — what it cannot reliably deliver:**
- D2 classification for applications with domain-specific state patterns (anything that isn't PostgreSQL/Redis/MySQL)
- D4 L4 disqualifier triage (75% FPR makes this a coin flip)
- Cross-section evidence consistency within a single run
- Application-specific operational domain knowledge (Vault, Spring Boot, Prometheus, bbolt, etc.)
- Precise scoring rule application under pressure (25% error rate on a table-lookup rule)
- Agenda generation that is distinct, non-redundant, and dimension-appropriate

**The compound problem:** The floor and ceiling overlap in a dangerous way. The model produces HIGH confidence across all failure categories. It does not systematically produce LOW confidence on the cases where it is wrong. The signal that should tell the human "verify this" is absent or inverted.

---

## Verdict: Fitness for Purpose

**Phase 1 mechanical execution:** ADEQUATE. The model traverses the protocol, runs tools, and produces output in the right format. This is the easiest part of the job.

**Phase 1 evidence quality:** INSUFFICIENT AS STANDALONE. 50% of runs require score corrections. The evidence package as produced by qwen3 cannot be handed to Phase 2 without CC synthesis to catch errors. This was always the architecture (two-session split exists for exactly this reason), but the error rate is high enough that CC synthesis is not an "optional enhancement" — it is a **mandatory correction layer**.

**Phase 1 domain coverage:** UNRELIABLE above basic patterns. Any application with:
- Non-standard DB clients (bbolt, embedded Redis, anything outside the top-10 list)
- Framework-level lifecycle handling (Spring Boot, Quarkus, any runtime with JVM hooks)
- Application-domain file state (git repos, mail Maildirs, time-series databases)
- Technology-specific operational concerns (Vault sealing, anything requiring domain expertise)

...will have material gaps that CC must independently verify or inject via domain knowledge.

**Phase 1 dialogue agenda quality:** POOR. The agenda is the primary Phase 2 input. In 11 of 12 runs it required full or partial rewrite. The model generates volume, not precision. Questions are generic, redundant, and frequently misscoped to the wrong dimension. This does not reduce Phase 2 workload — it transfers it to the agenda redesign step.

**Bottom line:** qwen3-coder:30b-a3b-q8_0 is viable as a **tool executor and template populator** for Phase 1. It is not viable as an **evidence analyst or assessment reasoner**. The two-session split correctly partitions this: let qwen3 do the scanning work (which it executes reliably), let CC do the reasoning work (which requires capabilities qwen3 doesn't have at this parameter budget). The framework architecture is sound. The model operating within it is at its capability ceiling on the reasoning tasks, and below it on some of the mechanical tasks (scoring rules, output hygiene).

The expectation that Phase 1 output is a reliable first-pass assessment that Phase 2 only needs to refine is not met. Phase 1 output requires correction. The corrections are often significant (false L4 gates, S3 dismissals, scoring errors). Plan for CC synthesis as a mandatory error-correction step, not an enhancement, for as long as qwen3 or equivalent-scale models are used for Phase 1.

---

## Appendix — Per-Run Issue Summary

| Repo | D1 | D2 | D3 | D4 | Extra files | Agenda |
|------|----|----|----|----|-------------|--------|
| minio | T3 reasoning flawed (no score diff) | Correct answer, wrong evidence | Confidence inflation | OK | 1 (d3-assessment-summary) | Degenerate (same Q×3 dims) |
| airflow | T4 correct | S2 solid | Confidence inflation; Q misrouted | L4 FALSE POSITIVE (CI container) | 0 | D2 Q is D3 question |
| keycloak | T1 misclassification (no score diff) | Infinispan mode unasked | Confidence inflation | OK | 1 (d1-correlation-summary) | 10 Qs, heavy redundancy |
| nextcloud | OK | OK | MEDIUM correctly stated | L4 FALSE POSITIVE (CLEAR check ignored) | 1 (nextcloud-assessment-summary) | 7 Qs, collapsed to 3 |
| ghost | OK | OK | I3 score=2 (should be 1); dev-config evidence only | OK (best D4 evidence) | 1 (detailed-analysis) | 11 Qs, collapsed to 3 |
| vault | OK | BoltDB dismissed without justification | Confidence inflation | Unsealing not assessed | 1 (d4-correlation-summary) | 8 Qs, collapsed to 3 |
| gitea | SCAN FALSE NEGATIVE (0 Dockerfiles) | Git repo storage not assessed | MEDIUM correctly stated | Strong (L1) | 0 | D2/D3 questions identical |
| portainer | OK | BoltDB entirely missed | MEDIUM correctly stated | MEDIUM correctly stated | 4 (worst run; wrong D3 filename) | 12 Qs, collapsed to 3 |
| spring-petclinic | T3 basis wrong (buildpacks) | OK | I3 score=2 (should be 1); reasoning confused | L3 FALSE (Spring Boot JVM hooks) | 0 | 8 Qs, collapsed to 3 |
| prometheus | OK | S3 described → S2 classified (direct contradiction) | Confidence inflation | Config concern overstated | 1 (d4-correlation-summary) | 6 Qs, adequate |
| docker-mailserver | OK | Rspamd Redis missed | I3 score=2; category confusion (intra vs inter) | L4 TRUE POSITIVE (first in set) | 0 | Generic Qs |
| traefik | OK | Redis rate limiter nuance missed | I2 correct score correct (best D3) | Env var false negative (library abstraction) | 3 (summaries, correct names) | Best agenda in set |
