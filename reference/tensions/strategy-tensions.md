# Strategy Tensions Catalog

## Purpose

Pre-defined catalog of Tier 3 selection conflicts. These are SOFT tensions — the combination works but creates friction that must be acknowledged and documented. Strategy tensions are the Tier 3 equivalent of cross-dimension tensions in Tier 1.

---

## Tension Detection Rule

After all three Tier 3 selections are made, check every tension in this catalog. If the combination matches, surface the tension. The human either:

1. **Adjusts a selection** to resolve the tension.
2. **Invests in capability** to bridge the gap.
3. **Accepts the tension** with documentation.
4. **Escalates to Tier 2** — if the tension reveals a constraint that wasn't captured.

---

## Catalog

### ST-01: Greenfield Over-Engineering

| Trigger | S1=LS1 + S3=RT1 or RT2 |
|---|---|
| Tension | Investing in progressive/parallel deployment for an app with zero users. No traffic to canary against. |
| Question | "This is a greenfield application. Who are you protecting with canary deployments when there are no users yet? Would starting with RT3 (rolling) and upgrading to RT1 when traffic arrives be more pragmatic?" |
| Resolution options | Accept (build the infra early), Defer (start with RT3, upgrade later), Challenge LS1 (maybe there ARE existing users?) |

### ST-02: Maintenance Over-Investment

| Trigger | S1=LS3 + S2=VT1 |
|---|---|
| Tension | Continuous deployment infrastructure for an application that rarely changes. Operational burden without proportional benefit. |
| Question | "This application is in maintenance mode with infrequent changes. Continuous deployment infrastructure requires ongoing maintenance itself. Is VT2 (on-demand) sufficient?" |
| Resolution options | Accept (infrastructure already exists), Simplify (VT2), Challenge LS3 (maybe more active than thought?) |

### ST-03: Sunset Complexity

| Trigger | S1=LS4 + S2=VT1 or VT2 + S3=RT1 or RT2 |
|---|---|
| Tension | Any significant deployment infrastructure investment for an application being decommissioned. |
| Question | "This application is being sunset. Investment in deployment infrastructure won't be recovered. Can deployments use the simplest possible strategy (VT4+RT4)?" |
| Resolution options | Simplify (VT4+RT4), Justify (migration milestones need safety), Challenge LS4 (is sunset actually committed?) |

### ST-04: Velocity Without Safety Net

| Trigger | S2=VT1 + S3=RT3 or RT4 |
|---|---|
| Tension | High deployment frequency without proportional risk mitigation. Every failed deployment impacts all users simultaneously. |
| Question | "Continuous deployment with rolling/direct strategy means every bad merge reaches 100% of users before detection. Is this an accepted risk, or should risk tolerance increase to RT1/RT2?" |
| Resolution options | Accept risk (fast rollback is sufficient), Upgrade RT (invest in canary/blue-green), Reduce VT (VT2 gives manual gate) |

### ST-05: Coordinated Velocity with Progressive Risk

| Trigger | S2=VT4 + S3=RT1 |
|---|---|
| Tension | Canary deployments require independent service rollout. Coordinated releases negate canary's incremental exposure benefit. |
| Question | "Coordinated releases deploy multiple systems together, but canary strategy assumes independent gradual rollout. These approaches conflict. Is the coordination genuinely needed, or is it a symptom of coupling?" |
| Resolution options | Accept (canary within coordinated window), Investigate coupling (may need Tier 1 D1/D3 revisit), Adjust RT to RT2 (parallel swap of entire coordinated set) |

### ST-06: Regulated Velocity Friction

| Trigger | S2=VT1 + C2=CP3 or CP4 (from Tier 2) |
|---|---|
| Tension | Continuous deployment in regulated environment. Approval gates, segregation of duties, and audit requirements create friction with continuous flow. |
| Question | "Continuous deployment under [CP3/CP4] compliance requires fully automated compliance gates — signed images, automated SBOM, automated approval workflows. Is the team prepared to invest in this automation, or is VT2/VT3 more realistic given current compliance tooling?" |
| Resolution options | Invest (automate compliance for continuous flow), Accept friction (VT3 with formal gates), Hybrid (continuous to staging, gated to production) |

### ST-07: Distributed Teams with High Velocity

| Trigger | S2=VT1 + C3=O2 (from Tier 2) |
|---|---|
| Tension | Continuous deployment through a shared pipeline with multiple contributing teams. Merge conflicts and deployment queue contention. |
| Question | "Multiple teams sharing a pipeline with continuous deployment creates bottleneck risk. Is trunk-based development with feature flags in place, or do teams block each other on deployment?" |
| Resolution options | Accept (teams have mature trunk-based practice), Invest (implement feature flags and deployment queues), Restructure (move to O3 with independent pipelines) |

### ST-08: Capability-Velocity Mismatch

| Trigger | S2=VT1 or S3=RT1 + Capability gap flagged in C3 |
|---|---|
| Tension | Team doesn't have the skills for the selected velocity/risk strategy. |
| Question | "The team has capability gaps in [specific area]. [VT1/RT1] requires operational maturity in this area. Is there a training plan, or should the strategy be adjusted to match current capability?" |
| Resolution options | Invest (training + mentoring), Start lower (VT2+RT3, upgrade as capability grows), External support (platform team, SRE overlay) |

---

## Tension Severity

| Severity | Meaning | Action Required |
|---|---|---|
| Advisory | Unusual but functional. Document and proceed. | Acknowledge in Deployment Profile |
| Warning | Creates operational friction. Mitigation recommended. | Document mitigation plan or adjust selection |
| Conflict | Selections are logically contradictory. Cannot proceed without resolution. | Must adjust at least one selection |

### Severity by Tension

| Tension | Default Severity |
|---|---|
| ST-01 Greenfield Over-Engineering | Advisory |
| ST-02 Maintenance Over-Investment | Warning |
| ST-03 Sunset Complexity | Warning |
| ST-04 Velocity Without Safety Net | Warning |
| ST-05 Coordinated + Progressive | Conflict |
| ST-06 Regulated Velocity | Warning |
| ST-07 Distributed + High Velocity | Warning |
| ST-08 Capability Mismatch | Warning |
