# S1: Lifecycle Stage

## Core Question

**Where is this application in its product lifecycle?**

Applied FIRST in Tier 3. The most foundational strategic choice — it constrains what velocity and risk tolerance are realistic.

---

## Classifications

| Code | Name | Description |
|------|------|-------------|
| LS1 | Greenfield | New application. No existing users, no production traffic, no legacy constraints. Maximum freedom. |
| LS2 | Active Evolution | Established application under active feature development. Has users, has production traffic, has technical debt. |
| LS3 | Stable / Maintenance | Feature-complete or nearly so. Receives bug fixes, security patches, minor enhancements. Low change velocity. |
| LS4 | Sunset | Application being decommissioned. Migrating users away, reducing scope, preparing for shutdown. |

---

## Decision Tree

```
START
│
├─ Q: Does this application have production users and traffic today?
│
├─ NO ──► Classification: LS1 (Greenfield)
│
└─ YES ──► Q: Is the application under active feature development
           with regular deployments of new functionality?
           │
           ├─ YES ──► Classification: LS2 (Active Evolution)
           │
           └─ NO ───► Q: Is there an active plan to decommission
                      or replace this application?
                      │
                      ├─ YES ──► Classification: LS4 (Sunset)
                      │
                      └─ NO ───► Classification: LS3 (Stable / Maintenance)
```

---

## Impact on Deployment Strategy

| LS Level | Velocity Implications | Risk Implications | Investment Justification |
|---|---|---|---|
| LS1 | Maximum — no coordination with existing users | Low stakes — no existing traffic to break | Full investment justified: building for the future |
| LS2 | Moderate to high — must balance new features with stability | Medium to high — existing users at risk | Investment justified if aligned with product roadmap |
| LS3 | Low — infrequent changes | Low change risk, high availability risk | Minimal investment — keep operational, don't gold-plate |
| LS4 | Minimal — only what's needed for migration | Focus on data integrity during wind-down | No new investment — maintain just enough to complete shutdown |

---

## Key Interactions

- **LS1 + HIGH fitness** → Ideal scenario. Build container-native from scratch.
- **LS2 + MEDIUM fitness** → Most common real-world case. Incremental improvement during feature work.
- **LS3 + Any fitness** → Don't migrate to containers unless there's a compelling operational reason (cost, security patching burden).
- **LS4 + Any path** → Minimize change. Don't containerize a sunset application. Keep it running on current infrastructure.
- **LS4 should trigger validation:** If someone wants to containerize a sunset app, challenge whether the lifecycle classification is correct.

---

## Collection Method

**Question:**
> Where is this application in its lifecycle? Is it greenfield (no production users yet), actively evolving with regular feature releases, in stable maintenance mode, or being decommissioned?

**Follow-up probes:**
> How frequently are new features deployed to production?
> Is there a product roadmap for the next 12 months, or is the application in sustaining mode?
> Are there plans to replace or retire this application?
