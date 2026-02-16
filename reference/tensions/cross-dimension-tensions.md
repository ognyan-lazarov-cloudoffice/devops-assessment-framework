# Cross-Dimension Tensions

## Purpose

This catalog defines the **pre-defined, enumerable** tension patterns between Tier 1 dimensions. These are the ONLY Category 2 dialectical challenges that can fire. No improvised cross-dimension challenges.

Tensions are checked AFTER all four dimensions are locked but BEFORE Tier 1 aggregation (between Task 5 completion and Task 6 execution).

---

## Tension Format

Each tension has:
- **Pattern:** The specific classification combination that triggers it
- **Severity:** HIGH (likely misclassification) / MEDIUM (worth verifying) / LOW (note and proceed)
- **Challenge:** The exact challenge to surface to the human
- **Resolution paths:** How the tension can be resolved
- **Max rounds:** 2 per tension (circuit breaker)

---

## Tension Catalog

### TENSION-1: D1↔D3 — Microservices Without Independence

**Pattern:** T1 (True Microservices) + I3 (Coordinated Dependence) or I4 (Hidden Coupling)

**Severity:** HIGH

**Why it matters:** True microservices by definition have independent lifecycles. If components require coordination or have hidden coupling, the topology is more likely T4 (Distributed Monolith) than T1.

**Challenge:**
> D1 is classified as T1 (True Microservices) but D3 shows [I3 Coordinated Dependence / I4 Hidden Coupling]. True microservices should be independently deployable and operable. If services require startup ordering or have cascading failures, this may actually be a Distributed Monolith (T4). Can you explain how services achieve deployment independence despite the coupling identified in D3?

**Resolution paths:**
1. **Reclassify D1 to T4** if coupling is fundamental to architecture
2. **Reclassify D3 to I2** if coupling is managed but was initially underestimated
3. **Accept with annotation** if coupling is limited to specific service pairs (document which pairs)
4. **No change** with justification (e.g., coupling is in infrastructure layer, not application layer)

---

### TENSION-2: D2↔D4 — Managed State With Legacy Lifecycle

**Pattern:** S2 (Managed Statefulness) + L3 (Legacy Lifecycle)

**Severity:** HIGH

**Why it matters:** Managed statefulness (StatefulSets, PVCs) requires precise lifecycle cooperation — ordered startup, graceful shutdown with state flushing, health signaling for readiness. L3 apps fight the orchestrator on exactly these requirements.

**Challenge:**
> D2 is classified as S2 (Managed Statefulness) requiring careful lifecycle management, but D4 shows L3 (Legacy Lifecycle) with significant orchestrator friction. StatefulSets rely on ordered, graceful lifecycle transitions. How will state be preserved during the long/ungraceful startups and shutdowns indicated by L3?

**Resolution paths:**
1. **Reclassify D2 to S3** if state management is actually more fragile than initially assessed
2. **Reclassify D4 to L2** if lifecycle gaps are narrower than initially assessed
3. **Accept with annotation** documenting the operational risk and required compensating controls
4. **Flag for remediation** — L3→L2 remediation becomes prerequisite for S2 deployment

---

### TENSION-3: D1↔D2 — Independent Services With Shared State

**Pattern:** T1 (True Microservices) + S4 (Distributed State Coupling)

**Severity:** HIGH (this combination should already be caught — both are 0-score, but verify consistency)

**Why it matters:** This is a logical contradiction. Services cannot be independently deployable if they share mutable state without ownership boundaries. If both are classified, the assessment has an error.

**Challenge:**
> D1 is classified as T1 (independently deployable services) but D2 is S4 (distributed state coupling). These are contradictory — services sharing mutable state without ownership cannot be independently deployed. Which assessment better reflects reality?

**Resolution paths:**
1. **Reclassify D1 to T4** — most likely outcome; shared state makes "independence" illusory
2. **Reclassify D2 to S2** — if state ownership is actually clearer than initially assessed
3. **Both are correct** is NOT a valid resolution for this tension

---

### TENSION-4: D3↔D4 — Full Independence With Legacy Lifecycle

**Pattern:** I1 (Fully Independent) + L3 (Legacy Lifecycle)

**Severity:** MEDIUM

**Why it matters:** Fully independent services typically exhibit cloud-native lifecycle characteristics because the same engineering practices that produce independence also produce good lifecycle behavior. I1 + L3 is unusual and worth verifying.

**Challenge:**
> D3 is classified as I1 (Fully Independent) but D4 shows L3 (Legacy Lifecycle). Services that achieve full failure and scaling independence usually also have fast startup, graceful shutdown, and externalized config. Is the independence truly validated, or is it aspirational?

**Resolution paths:**
1. **Reclassify D3 to I2** if independence is partially aspirational
2. **Reclassify D4 to L2** if lifecycle gaps are narrower than assessed
3. **Accept with annotation** — legitimate in cases where services are architecturally independent but built on legacy frameworks with lifecycle limitations
4. **No change** with justification (e.g., legacy JVM app that is genuinely independent but slow to start)

---

### TENSION-5: D1↔D2 — Monolith Claiming Cloud-Native Statelessness

**Pattern:** T3 (Traditional Monolith) + S1 (Cloud-Native Stateless)

**Severity:** LOW

**Why it matters:** Not impossible (a stateless monolith serving pure API calls exists) but uncommon. Traditional monoliths typically accumulate state over time. Worth a brief verification.

**Challenge:**
> D1 is classified as T3 (Traditional Monolith) with tightly coupled internals, but D2 shows S1 (Cloud-Native Stateless) with fully externalized state. This combination is unusual — monoliths without internal boundaries typically accumulate local state. Can you confirm there is truly no local state dependency?

**Resolution paths:**
1. **Reclassify D2 to S2/S3** if state was overlooked
2. **Accept** — legitimate for API-only monoliths, pure computation services
3. **No change** — low severity, proceed with annotation

---

### TENSION-6: D2↔D3 — Stateless But Coordinated

**Pattern:** S1 (Cloud-Native Stateless) + I3 (Coordinated Dependence)

**Severity:** LOW

**Why it matters:** If an app is truly stateless, what creates the coordination requirement? Coordination usually stems from state management or deployment ordering. Worth a brief probe.

**Challenge:**
> D2 is S1 (Cloud-Native Stateless) but D3 is I3 (Coordinated Dependence). If the application has no local state, what requires the deployment coordination identified in D3? Is the coordination driven by the application or by external dependencies?

**Resolution paths:**
1. **Reclassify D3 to I2** if coordination is at infrastructure level, not application
2. **Accept** — coordination may be driven by downstream dependencies, not internal state
3. **No change** — low severity, proceed with annotation

---

## Application Rules

1. **Check all 6 tensions** after locking D1-D4.
2. **Only surface tensions that match** — do not challenge non-matching patterns.
3. **HIGH severity first**, then MEDIUM, then LOW.
4. **Max 2 rounds** per tension. After 2 rounds without resolution, record as "noted tension" and proceed.
5. **Multiple tensions can fire simultaneously.** Process each independently.
6. **Resolution changes a classification:** If a tension resolution changes a score, recheck ALL tensions against the new classification set (one pass only — no infinite loops).
7. **All tensions resolved or noted:** Proceed to Tier 1 aggregation.

---

## Tension Summary Template

```
CROSS-DIMENSION TENSION CHECK
==============================

Classifications at check time:
  D1=[T?] D2=[S?] D3=[I?] D4=[L?]

Tensions fired:
  [TENSION-N]: [severity] — [one-line description]
    Resolution: [how resolved or "noted, proceeding"]
    Classification changes: [none / D?: X→Y]

Tensions not fired: [list by number]

Final classifications (post-tension):
  D1=[T?] D2=[S?] D3=[I?] D4=[L?]

Proceed to: Tier 1 Aggregation
```
