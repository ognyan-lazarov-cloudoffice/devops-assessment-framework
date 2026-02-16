# D4: Lifecycle Compliance

## Core Question

**Does the application respect container orchestration behavioral contracts?**

Assesses startup/shutdown behavior, configuration injection model, and health signaling to determine if the application cooperates with orchestrator lifecycle management (scheduling, scaling, rolling deploys, self-healing).

---

## Classifications

| Code | Name | Score | Description |
|------|------|-------|-------------|
| L1 | Cloud-Native Lifecycle | 3 | Fast startup, graceful shutdown, externalized config, distinct readiness + liveness probes. Fully cooperates with orchestrator. |
| L2 | Compliant with Gaps | 2 | Mostly compliant but missing some contracts. May have slow startup, missing probes, or partial config externalization. Fixable without architectural change. |
| L3 | Legacy Lifecycle | 1 | Significant lifecycle friction. Long startup, no signal handling, hardcoded config. **Caps overall fitness at MEDIUM.** Requires remediation effort. |
| L4 | Incompatible Lifecycle | 0 | **DISQUALIFYING for container-native path.** Requires host-level access, custom init systems, or fundamentally incompatible runtime behavior. |

### Scoring Notes

- L1 = 3: Orchestrator can manage this app as a first-class citizen. Auto-scaling, rolling deploys, and self-healing all work correctly.
- L2 = 2: Viable with workarounds (longer startup probes, preStop hooks, config maps). No architectural barriers.
- L3 = 1: **Caps overall fitness at MEDIUM.** Containers will work but fight the orchestrator. Constant operational friction.
- L4 = 0: Triggers BLOCKED. Container-native path not viable. Evaluate VM deployment or fundamental remediation.

---

## Decision Tree

```
START
│
├─ Q: Does the application start up and become ready
│  to serve traffic within a reasonable time?
│  (<30s optimal, 30s-2min acceptable, >2min problematic)
│
├─ <=2min ──► Q: Does the application handle SIGTERM
│             gracefully (drain connections, finish
│             in-flight work, clean shutdown)?
│             │
│             ├─ YES ──► Q: Is configuration injectable
│             │          at runtime without rebuilding
│             │          the image? (env vars, config maps,
│             │          mounted files)
│             │          │
│             │          ├─ YES ──► Q: Does the application
│             │          │          expose health endpoints?
│             │          │          (distinct readiness and
│             │          │          liveness probes)
│             │          │          │
│             │          │          ├─ Both ──► L1 (Cloud-Native)
│             │          │          ├─ One ───► L2 (Compliant with Gaps)
│             │          │          └─ None ──► L2 (Compliant with Gaps)
│             │          │
│             │          └─ NO ───► L2 if minor config changes needed
│             │                    L3 if config is deeply hardcoded
│             │
│             └─ NO ───► L2 if adding signal handler is straightforward
│                        L3 if shutdown behavior is complex/dangerous
│
├─ >2min ──► L3 (Legacy Lifecycle)
│            Reason: slow startup breaks rolling deploy
│            timing, HPA responsiveness, pod scheduling.
│
└─ Requires host-level access, custom init, systemd,
   specific kernel modules, or GUI ──► L4 (Incompatible)
```

### L4 Hard Disqualifiers

Any of the following = L4 classification:

- Requires running as PID 1 with custom init system (not tini/dumb-init)
- Requires systemd or other host init system
- Requires direct hardware access (GPU excluded — GPU scheduling is a solved K8s problem)
- Requires specific kernel modules not available in container runtime
- Requires graphical display / GUI
- Requires Windows-specific services on Linux target (or vice versa)
- Requires privileged container mode for core functionality (not just a misconfiguration)

---

## Static Analysis Indicators

### Strong Indicators (high confidence)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Health check endpoints (`/health`, `/ready`, `/live`, `/healthz`) | L1/L2 | Source code routes, framework config |
| SIGTERM / signal handling code | L1/L2 | Source code (signal handlers, shutdown hooks) |
| Environment variable reading for config | L1/L2 | Source code, framework config |
| `ENTRYPOINT` / `CMD` using exec form in Dockerfile | L1/L2 (signals forwarded correctly) | Dockerfile |
| `STOPSIGNAL` in Dockerfile | Awareness of shutdown signaling | Dockerfile |
| Graceful shutdown hooks (Spring `@PreDestroy`, Node.js `process.on('SIGTERM')`, Go `signal.Notify`) | L1/L2 | Source code |
| Hardcoded config values (IP addresses, ports, file paths) | L3 risk | Source code, config |
| Long initialization sequences (DB migrations at startup, large cache warming) | L3 risk | Source code, startup scripts |
| `privileged: true` in K8s manifests | L4 risk | K8s YAML |
| `hostNetwork: true`, `hostPID: true`, `hostIPC: true` | L4 risk | K8s YAML |
| Systemd service files in repo | L4 risk | Repo root, deployment config |

### Moderate Indicators (needs confirmation)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Config file templates with placeholder substitution | L2 (config partially externalized) | Config dirs, entrypoint scripts |
| `preStop` lifecycle hooks in K8s manifests | L2 (compensating for imperfect shutdown) | K8s YAML |
| `terminationGracePeriodSeconds` > 60 | L2/L3 (long shutdown needed) | K8s YAML |
| `initialDelaySeconds` > 60 on readiness probe | L2/L3 (slow startup) | K8s YAML |
| Startup scripts that modify config files before running app | L2/L3 | Dockerfile `ENTRYPOINT`, scripts |
| Multi-stage Dockerfile with build-time config baking | L2/L3 (config partially baked) | Dockerfile |

### Weak Indicators (context-dependent)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| JVM application (known for startup time) | L2 risk (but GraalVM/Spring Boot 3+ mitigate) | Dependencies |
| Large Docker image size (>1GB) | Correlated with L3 but not causative | Dockerfile, CI artifacts |
| Multiple processes in single container (supervisord) | L3/L4 risk | Dockerfile, supervisord config |

### Static Analysis Ceiling: ~70-80% for presence

**CAN detect:** Health endpoints, signal handlers, config injection patterns, Dockerfile best practices, K8s probe config, privileged requirements.

**CANNOT measure:** Actual startup time, actual shutdown behavior under load, whether health endpoints return meaningful status, whether config injection actually works end-to-end.

**Highest static ceiling of all four dimensions.** Most L4 disqualifiers and L1 compliance signals are visible in code.

---

## Question Bank

**Q-D4-1: Startup Time Reality**
> What is the actual time from container start to ready-to-serve-traffic in a realistic environment (with DB connections, cache warming, etc.)? Not just "the process starts" but "first request can be served."

- *Purpose:* Validates startup time assessment — static analysis can detect patterns but not measure actual time.
- *Triggers when:* Heavy initialization patterns detected (DB migrations, cache warming) or JVM-based application.
- *Maps to:* L1/L2 vs L3 boundary (>2min = L3).

**Q-D4-2: Shutdown Behavior Under Load**
> What happens when the application receives SIGTERM while processing requests? Are in-flight requests completed? Is there a drain period? What about long-running background jobs?

- *Purpose:* Validates graceful shutdown — signal handler existence doesn't guarantee correct behavior.
- *Triggers when:* Signal handling detected but application has long-running operations (batch jobs, file processing, WebSocket connections).
- *Maps to:* L1 vs L2 boundary.

**Q-D4-3: Configuration Portability**
> Can the same container image run in staging and production with ONLY environment variable / config map differences? Or does the image need to be rebuilt per environment?

- *Purpose:* Validates config externalization — hardcoded values or build-time config baking break image portability.
- *Triggers when:* Mixed config patterns detected (some env vars, some hardcoded).
- *Maps to:* L1/L2 vs L3 boundary.

---

## Dialectical Triggers

### Category 1: Evidence-Statement Contradictions

| Human Claims | Evidence Shows | Challenge |
|---|---|---|
| "Fast startup" | DB migration runs at startup, JVM without optimized startup | "The startup sequence includes `[migration/initialization]` at `[path]`. In a cold start with network latency to DB, what's the realistic startup time?" |
| "Graceful shutdown" | No SIGTERM handler detected, shell form ENTRYPOINT (signals not forwarded) | "Dockerfile uses shell form `ENTRYPOINT` which doesn't forward signals to the application process. How does the app receive SIGTERM?" |
| "Config is externalized" | Hardcoded connection strings, file paths, or ports in source | "Found hardcoded `[value]` at `[path]`. Is this overridable at runtime or does the image need rebuilding?" |
| "Container-ready" | `privileged: true` or `hostNetwork: true` in manifests | "K8s manifests request `[privileged/hostNetwork]`. Is this actually required for the application or is it a deployment configuration that can be removed?" |

### Category 3: Downstream Implication Surfacing

| Classification | Implication | Surface |
|---|---|---|
| L3 = 1 | **Caps overall fitness at MEDIUM.** Slow startup means HPA cannot respond to load spikes in time. Rolling deploys take longer (fewer pods ready during transition). Self-healing is slow. | Always when L3 locked. |
| L4 = 0 | **BLOCKED for container-native path.** Evaluate modifiability: can L4 disqualifiers be removed with reasonable effort? If not, VM/IaaS is the recommended path. | Always when L4 locked. |
| L2 with multiple gaps | Individual gaps are fixable, but accumulation of gaps (slow startup + no probes + partial config) indicates significant remediation work. Validate effort estimate. | When L2 locked with ≥3 identified gaps. |

---

## Common Misclassifications

| Looks Like | Actually Is | How to Detect |
|---|---|---|
| "Has health endpoint" = L1 | L2 if only one endpoint (no readiness/liveness distinction) or endpoint returns 200 always | Check endpoint logic — does it actually test readiness? |
| JVM app = L3 | L1/L2 if using Spring Boot 3+, GraalVM, or optimized class loading | Check framework version and startup optimization config |
| `privileged: true` = L4 | Could be L2 if privilege is for an optional feature or misconfiguration | Ask if privileged mode is actually required |
| Runs on Docker = lifecycle compliant | Docker runs anything — lifecycle compliance is about orchestrator cooperation | Dockerfile existence proves nothing about lifecycle behavior |
| Has Kubernetes manifests = L1 | Manifests may be aspirational or misconfigured | Check if probes, resource limits, and signals are actually configured |
