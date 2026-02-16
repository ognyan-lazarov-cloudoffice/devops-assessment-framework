# S2: Velocity Target

## Core Question

**How frequently should changes reach production?**

Applied SECOND. Velocity is a genuine human choice — different business contexts legitimately require different deployment cadences.

---

## Classifications

| Code | Name | Description |
|------|------|-------------|
| VT1 | Continuous | Every merged change is a deployment candidate. Multiple deployments per day. Feature flags decouple deploy from release. |
| VT2 | On-Demand | Deploy when ready, no fixed schedule. Batched when convenient but not blocked by calendar. Days to weekly cadence. |
| VT3 | Cadenced | Fixed schedule: weekly, biweekly, monthly. Release trains with cut-off dates. Change advisory boards possible. |
| VT4 | Coordinated | Multiple systems must deploy together. Cross-team synchronization required. Quarterly or milestone-based releases. |

---

## Decision Tree

```
START
│
├─ Q: Must multiple systems/teams deploy simultaneously
│  for a release to succeed?
│
├─ YES ──► Classification: VT4 (Coordinated)
│          │
│          └─ VALIDATION: Is this coordination driven by
│             business need or by technical coupling?
│             If technical coupling → revisit D1/D3 in Tier 1.
│
└─ NO ───► Q: Is there a fixed release schedule
           (weekly/biweekly/monthly)?
           │
           ├─ YES ──► Classification: VT3 (Cadenced)
           │
           └─ NO ───► Q: Does every merge to main
                      automatically reach production?
                      │
                      ├─ YES ──► Classification: VT1 (Continuous)
                      │
                      └─ NO ───► Classification: VT2 (On-Demand)
```

---

## Impact on Deployment Strategy

| VT Level | CI/CD Requirements | Risk Strategy Compatibility | Infrastructure Needs |
|---|---|---|---|
| VT1 | Full automation, zero manual gates except policy | RT1 (Progressive/Canary) optimal, RT2 (Parallel) acceptable | Automated rollback, feature flag system, observability |
| VT2 | Automated build+test, manual deploy trigger | Any RT compatible | Standard CI/CD, manual promotion |
| VT3 | Automated build+test, scheduled promotion windows | RT2 (Parallel/Blue-Green) or RT3 (Rolling) typical | Environment management for staged releases |
| VT4 | Orchestrated multi-system deployment, integration testing | RT3 (Rolling) or RT4 (Direct) typical, RT1 rarely feasible | Cross-system integration environment, deployment orchestrator |

---

## VT4 Validation Rule

**VT4 requires mandatory validation:** If the coordination requirement comes from **technical coupling** (services can't function without simultaneous deployment), this is not a velocity choice — it's a symptom of T4 (Distributed Monolith) or I4 (Hidden Coupling) from Tier 1.

**If VT4 is driven by business need** (regulatory approval cycle, contractual milestone, multi-party coordination): legitimate, proceed.

**If VT4 is driven by technical coupling:** Flag this as a Tier 1 reassessment signal. The D1 or D3 classification may need revision.

---

## Key Interactions

- **VT1 + CP4** → Continuous deployment into highly-regulated environment requires automated compliance gates (signed images, automated SBOM, automated approval workflows). Feasible but expensive.
- **VT1 + O2** → Continuous deployment with shared pipeline creates merge-conflict pressure. Consider trunk-based development with feature flags.
- **VT3 + LS1** → Fixed cadence on a greenfield app is unusual. Challenge whether this is an inherited organizational process rather than a genuine need.
- **VT4 + LS4** → Coordinated releases on a sunset app suggests entanglement with other systems that must be resolved during decommission.

---

## Collection Method

**Question:**
> How frequently do you currently deploy to production, and how frequently do you *want* to deploy? Is there a fixed schedule, or is it on-demand?

**Follow-up probes:**
> When you deploy, do other systems need to deploy at the same time?
> Is the current deployment frequency a technical limitation or a business decision?
> Are there change advisory boards, release trains, or approval cycles that dictate timing?
