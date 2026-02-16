# D2: State and Data Model

## Core Question

**Where does state live, how long must it survive, and who owns the data?**

Assesses runtime state management, data ownership patterns, and transaction boundaries to determine compatibility with container ephemerality.

---

## Classifications

| Code | Name | Score | Description |
|------|------|-------|-------------|
| S1 | Cloud-Native Stateless | 3 | No local state. All persistence externalized (DB, cache, object store). Any instance is interchangeable. Horizontal scaling is trivial. |
| S2 | Managed Statefulness | 2 | State exists but is explicitly managed. Uses StatefulSets, persistent volumes, or external state stores with clear ownership. Scaling requires awareness but is achievable. |
| S3 | Embedded State | 1 | State embedded in process memory or local filesystem. Requires sticky sessions, cannot lose instances without data loss. **Caps overall fitness at MEDIUM.** |
| S4 | Distributed State Coupling | 0 | **DISQUALIFYING.** Multiple services sharing mutable state without clear ownership. Data consistency depends on deployment coordination. Architectural problem. |

### Scoring Notes

- S1 = 3: Gold standard. Container restarts, scaling, rolling deploys all safe.
- S2 = 2: Viable but requires operational awareness. StatefulSets, PVCs, or managed databases with connection management.
- S3 = 1: **Any dimension scoring 1 caps overall fitness at MEDIUM regardless of total.** This is the #1 reason container migrations fail.
- S4 = 0: Triggers BLOCKED. Fix data ownership before containerization.

---

## Decision Tree

```
START
│
├─ Q: Does the application write to the local filesystem
│  or maintain in-memory state that must survive restarts?
│
├─ NO ──► Q: Is all persistent state externalized to
│         managed services (DB, Redis, S3, etc.)?
│         │
│         ├─ YES ──► Q: Can multiple instances run concurrently
│         │          against the same external state without
│         │          conflicts (no global locks, no singleton
│         │          assumptions)?
│         │          │
│         │          ├─ YES ──► Classification: S1 (Cloud-Native Stateless)
│         │          │
│         │          └─ NO ───► Classification: S2 (Managed Statefulness)
│         │                     Reason: requires instance coordination.
│         │
│         └─ NO ───► INVESTIGATE: Where is non-externalized
│                    state? Classify accordingly.
│
└─ YES ──► Q: Is the local state designed for container
           environments (explicit PVC claims, StatefulSet
           patterns, designated temp directories)?
           │
           ├─ YES ──► Classification: S2 (Managed Statefulness)
           │
           └─ NO ───► Q: Do multiple services/processes write
                      to the same data store without clear
                      ownership boundaries?
                      │
                      ├─ YES ──► Classification: S4 (Distributed State Coupling)
                      │
                      └─ NO ───► Classification: S3 (Embedded State)
```

---

## Static Analysis Indicators

### Strong Indicators (high confidence)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| No filesystem writes outside `/tmp` or designated temp dirs | S1 | Source code file I/O operations |
| Database connection to managed service (RDS, Cloud SQL, managed Redis) | S1 or S2 | Config files, env vars, connection strings |
| `StatefulSet` in K8s manifests | S2 | K8s YAML |
| `PersistentVolumeClaim` in deployment specs | S2 | K8s YAML |
| SQLite file or embedded DB (H2, BerkeleyDB) in application | S3 | Dependencies, file paths |
| Session affinity / sticky sessions in ingress config | S3 | Ingress/service YAML, load balancer config |
| File uploads stored to local filesystem (not object store) | S3 | Source code, storage config |
| Multiple services importing same ORM models or DB schemas | S4 risk | Source code, shared packages |
| Multiple services with write access to same DB tables | S4 | Migration files, DB access patterns |

### Moderate Indicators (needs confirmation)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| In-memory caching (local cache, not distributed) | S2 or S3 depending on loss tolerance | Source code, cache config |
| Connection pooling configuration | Neutral but reveals DB architecture | Config files |
| Message queue connections (RabbitMQ, Kafka) | Positive S1/S2 indicator (async patterns) | Dependencies, config |
| Local log files (not stdout/stderr) | S3 risk if logs contain state | Logging config |
| Scheduled jobs writing to local filesystem | S3 | Cron config, scheduler code |

### Weak Indicators (context-dependent)

| Signal | Points Toward | Where to Find |
|--------|---------------|---------------|
| Redis dependency present | Could be S1 (cache) or S2 (session store) — need to verify usage | Dependencies |
| File system libraries imported | Could be temp files (fine) or persistent state (S3) | Dependencies |
| Volume mounts in docker-compose without clear purpose | Investigate — could be S2 or S3 | `docker-compose.yml` |

### Static Analysis Ceiling: ~50-60%

**CAN detect:** Database libraries, file I/O patterns, K8s volume configurations, session management libraries, caching frameworks.

**CANNOT verify:** Whether state is truly safe to lose, actual data ownership boundaries between services, whether concurrent instances actually work, real-world data consistency behavior.

---

## Question Bank

**Q-D2-1: State Survival Requirements**
> Static analysis shows [filesystem writes / in-memory data structures / embedded DB]. What happens if a running instance is killed without warning? Is any data lost that cannot be reconstructed?

- *Purpose:* Determines if local state is truly ephemeral or required for correctness.
- *Triggers when:* Local filesystem writes or significant in-memory structures detected.
- *Maps to:* S1/S2 vs S3 boundary.

**Q-D2-2: Concurrent Instance Safety**
> Can multiple instances of the application run simultaneously against the same data stores? Have you run >1 replica in production? Any issues with duplicate processing, lock contention, or data corruption?

- *Purpose:* Validates horizontal scaling readiness.
- *Triggers when:* External state detected but concurrency safety unclear.
- *Maps to:* S1 vs S2 boundary.

**Q-D2-3: Data Ownership Boundaries**
> [When multiple services access same DB]: Which service owns the `[table/collection]` for writes? Do other services read directly or through an API? Are there cross-service transactions?

- *Purpose:* Detects S4 distributed state coupling.
- *Triggers when:* Multiple services sharing database access detected.
- *Maps to:* S2 vs S4 boundary.

---

## Dialectical Triggers

### Category 1: Evidence-Statement Contradictions

| Human Claims | Evidence Shows | Challenge |
|---|---|---|
| "Fully stateless" | SQLite file or local file writes detected | "Source code at `[path]` shows writes to `[file/db]`. Is this ephemeral cache or persistent state?" |
| "State is externalized" | Session affinity / sticky sessions configured | "Sticky sessions in `[config]` suggest instance-specific state. What breaks if traffic shifts to a different instance?" |
| "Each service owns its data" | Multiple services importing same DB models | "Services `[A]` and `[B]` both import models for `[table]`. Who owns writes? Are there cross-service transactions?" |

### Category 3: Downstream Implication Surfacing

| Classification | Implication | Surface |
|---|---|---|
| S3 = 1 | **Caps overall fitness at MEDIUM** regardless of total score. This is the #1 cause of container migration failures. Container restarts lose state, scaling creates data inconsistency. | Always when S3 locked. Explicit acknowledgment required. |
| S4 = 0 | **BLOCKED.** Fix data ownership first. Remediation: establish clear service-to-data ownership, introduce API boundaries for cross-service data access. | Always when S4 locked. |
| S2 with StatefulSet | Operational complexity: StatefulSets have ordered deployment, stable network identities, specific scaling procedures. Confirm team is aware of operational requirements. | When S2 locked and K8s is target platform. |

---

## Common Misclassifications

| Looks Like | Actually Is | How to Detect |
|---|---|---|
| "Stateless" app with Redis | Could be S2 if Redis holds session state that must survive | Check what happens when Redis is flushed — app still works? |
| Local file writes for temp processing | S1 if truly temporary, S3 if processed files must not be lost | Check if files survive past single request lifecycle |
| "Microservices with own databases" but shared schema | S4 — separate connection strings to same schema is not data ownership | Compare connection strings and target schemas |
| Event-sourced system | Usually S1/S2 (state reconstructable from events) but verify rebuild capability | Check if service can rebuild state from event store |
