# D3: Independence Profile

## Core Question

**Can components live, fail, and scale independently?**

Assesses coupling characteristics, communication patterns, failure isolation, and scaling semantics to determine how well the application leverages container orchestration independence guarantees.

---

## Classifications

| Code | Name | Score | Description |
|------|------|-------|-------------|
| I1 | Fully Independent | 3 | Components fail, restart, and scale independently. Communication is async or sync-with-resilience. No hidden coupling. |
| I2 | Bounded Independence | 2 | Independence within defined boundaries. Some coordination required (e.g., circuit breakers, retry budgets). Coupling is explicit and managed. |
| I3 | Coordinated Dependence | 2 | Components require active coordination for lifecycle events. Deployment ordering, health dependencies, or shared resource pools. Coupling is known but not isolated. |
| I4 | Hidden Coupling | 0 | **DISQUALIFYING.** Coupling exists but is not visible, documented, or managed. Manifests as production failures. Unresolved risk. |

### Scoring Notes

- I1 = 3: Ideal for container orchestration. Auto-scaling, rolling deploys, and failure recovery all function as designed.
- I2 = 2: Workable with explicit operational procedures. Circuit breakers, timeouts, and retry policies manage the coupling.
- I3 = 2: Same score as I2 but qualitatively different — coordination overhead is higher. Requires deployment runbooks and dependency awareness.
- I4 = 0: Triggers BLOCKED. Hidden coupling by definition cannot be managed. Manifests as cascading failures, mysterious timeouts, deployment-order bugs.

### I2 vs I3 Distinction

Both score 2, but the distinction matters for operational planning:
- **I2:** "We know services talk to each other, and we've instrumented the boundaries with circuit breakers and timeouts."
- **I3:** "We know services depend on each other, and we manage this through deployment ordering and coordination."
- I2 invests in resilience at boundaries. I3 invests in coordination at the process level. Both are valid but have different operational profiles.

---

## Decision Tree

```
START
│
├─ Q: Can individual components fail (crash, restart)
│  without causing failures in other components?
│
├─ YES ──► Q: Can individual components be restarted
│          independently (no required startup ordering
│          relative to other components)?
│          │
│          ├─ YES ──► Q: Can individual components be scaled
│          │          independently (add replicas of A without
│          │          changing B)?
│          │          │
│          │          ├─ YES ──► Classification: I1 (Fully Independent)
│          │          │
│          │          └─ NO ───► Classification: I2 (Bounded Independence)
│          │                     Reason: scaling requires coordination.
│          │
│          └─ NO ───► Classification: I3 (Coordinated Dependence)
│                     Reason: startup/restart dependencies exist.
│
└─ NO ───► Q: Is the failure propagation DOCUMENTED
           and MANAGED (circuit breakers, bulkheads,
           explicit dependency maps)?
           │
           ├─ YES ──► Classification: I2 (Bounded Independence)
           │          Reason: coupling exists but is explicitly managed.
           │
           └─ NO ───► Classification: I4 (Hidden Coupling)
                      Risk: coupling manifests in production.
```

### Communication Pattern Sub-Assessment

Communication patterns provide strong evidence for independence classification:

| Pattern | Independence Implication |
|---------|------------------------|
| In-process calls (shared memory, function calls) | No independence — single unit. Relevant for D1 not D3. |
| Shared filesystem / shared memory between processes | Breaks isolation. Strong I4 indicator. |
| Synchronous HTTP/gRPC WITHOUT resilience (no timeouts, retries, circuit breakers) | Fragile coupling. I3 or I4 depending on awareness. |
| Synchronous HTTP/gRPC WITH circuit breakers, timeouts, retries, bulkheads | Bounded coupling. I2. |
| Asynchronous messaging (queues, event streams) | Strong independence. I1 if properly implemented. |
| Database-mediated communication (polling shared tables) | Hidden coupling. I4 risk — changes to schema affect both sides. |

---

## Static Analysis Indicators

### Strong Indicators (high confidence)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Circuit breaker libraries (Hystrix, resilience4j, Polly, cockatiel) | I2 | Dependencies |
| Retry/timeout configuration in HTTP clients | I2 | Source code, config |
| Message queue client libraries (RabbitMQ, Kafka, SQS, NATS) | I1 indicator (async communication) | Dependencies |
| Event-driven architecture patterns (event bus, pub/sub) | I1 indicator | Source code patterns |
| `readinessProbe` depending on other services' health | I3 | K8s manifests |
| `initContainers` waiting for dependencies | I3 | K8s manifests |
| Hardcoded service URLs (especially localhost or IP addresses) | I4 risk | Source code, config |
| No timeout configuration on HTTP clients | I3 or I4 risk | Source code |
| Shared database tables with write access from multiple services | I4 risk (also D2 S4) | Source code, migrations |

### Moderate Indicators (needs confirmation)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Service mesh configuration (Istio, Linkerd) | I2 (resilience at infra level) | K8s manifests, mesh config |
| Health check endpoints that test downstream dependencies | I3 (health coupled) | Source code |
| Global distributed locks (ZooKeeper, etcd, Redis locks) | I3 or I4 — need to understand scope | Dependencies, source code |
| Saga pattern / distributed transaction library | I2 (managed distributed state) | Dependencies, source code |
| Contract testing infrastructure (Pact, Spring Cloud Contract) | Positive I1/I2 indicator | Test config, dependencies |

### Weak Indicators (context-dependent)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Service discovery configuration (Consul, Eureka, K8s DNS) | Normal for distributed systems. Neutral. | Config |
| API versioning in URLs or headers | Positive indicator of boundary management | Source code |
| Feature flags referencing other services | Could indicate coupling or independence | Config, source |

### Static Analysis Ceiling: ~40-50%

**CAN detect:** Resilience library usage, communication patterns, dependency declarations, timeout configs, health check implementations.

**CANNOT detect:** Hidden coupling (by definition not visible in code), actual failure propagation behavior, whether circuit breakers are properly tuned, real cascading failure patterns under load.

**Lowest static ceiling of all four dimensions.** D3 relies most heavily on dialogue.

---

## Question Bank

**Q-D3-1: Failure Propagation Reality**
> If [Service X] goes down for 5 minutes, what happens to [Service Y]? Does Y return errors, queue requests, or continue normally? Has this actually happened?

- *Purpose:* Determines real failure isolation behavior.
- *Triggers when:* Inter-service communication detected but resilience patterns unclear.
- *Maps to:* I1/I2 vs I3/I4 boundary.

**Q-D3-2: Scaling Independence Verification**
> Can you scale [Service X] from 1 to 5 replicas without changing anything about [Service Y]? Are there shared resources (connection pools, rate limits, queue partitions) that create implicit coupling at scale?

- *Purpose:* Detects coupling that only manifests under scaling.
- *Triggers when:* Services appear independent at single-replica but shared resources detected.
- *Maps to:* I1 vs I2/I3 boundary.

**Q-D3-3: Hidden Dependency Discovery**
> In the last 6 months, have there been production incidents where deploying or restarting one component unexpectedly affected another? What was the root cause?

- *Purpose:* Surfaces I4 hidden coupling from operational history.
- *Triggers when:* Cannot determine coupling level from code alone (common with D3).
- *Maps to:* I2/I3 vs I4 boundary.

---

## Dialectical Triggers

### Category 1: Evidence-Statement Contradictions

| Human Claims | Evidence Shows | Challenge |
|---|---|---|
| "Services are fully independent" | No circuit breakers, no timeouts on HTTP clients | "HTTP clients at `[path]` have no timeout or circuit breaker configuration. If a downstream service hangs, what prevents cascading hangs?" |
| "We handle failures gracefully" | Health checks depend on downstream service availability | "Readiness probe at `[path]` checks downstream `[service]` health. If that service is down, won't this service also be marked unready?" |
| "Loosely coupled" | Shared database tables with writes from multiple services | "Services `[A]` and `[B]` both write to table `[X]`. A schema migration by either service could break the other. How is this coordinated?" |

### Category 3: Downstream Implication Surfacing

| Classification | Implication | Surface |
|---|---|---|
| I4 = 0 | **BLOCKED.** Must perform dependency analysis under realistic load before containerization. Remediation: map all dependencies, instrument with timeouts/circuit breakers, then reclassify. | Always when I4 locked. |
| I3 = 2 | Deployment runbooks required. Auto-scaling may cause issues if coordination is manual. Document startup ordering and scaling constraints in operational procedures. | When target platform is K8s with HPA. |
| I1 claimed but only 1 replica ever tested | Classification may be aspirational rather than validated. Flag as confidence note. | When T1 topology but no evidence of multi-replica operation. |

---

## Common Misclassifications

| Looks Like | Actually Is | How to Detect |
|---|---|---|
| "Independent services" with sync calls and no resilience | I3 or I4 — one service down = all down | Check for circuit breakers, timeouts, fallbacks |
| Async messaging but with synchronous reply-wait patterns | I2/I3 — request-reply over messaging is sync-in-disguise | Check if publishers block waiting for response |
| Services behind API gateway | Independence depends on what's behind the gateway, not the gateway itself | Assess inter-service communication, not client-to-gateway |
| "Event-driven" but with required event ordering | I2/I3 — ordering requirements create implicit coupling | Check for ordered consumption, event sequencing logic |
| Container sidecar dependencies (logging, mesh proxy) | Infrastructure coupling, not application coupling — not I4 | Distinguish infra dependencies from app dependencies |
