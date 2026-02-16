# S3: Risk Tolerance

## Core Question

**How should deployment risk be managed?**

Applied THIRD (most tactical). This is the most directly actionable Tier 3 selection — it maps almost 1:1 to deployment tooling and configuration.

---

## Classifications

| Code | Name | Description |
|------|------|-------------|
| RT1 | Progressive (Canary) | Gradual traffic shifting to new version. Automated rollback on metric degradation. Minimum blast radius. |
| RT2 | Parallel (Blue-Green) | Full new environment alongside old. Instant switch with instant rollback capability. Higher resource cost. |
| RT3 | Rolling | Sequential instance replacement. Zero-downtime but full fleet eventually runs new version. No instant full-rollback. |
| RT4 | Direct | Replace in place. Downtime window acceptable or irrelevant. Simplest operationally. |

---

## Decision Tree

```
START
│
├─ Q: Is deployment downtime acceptable for this application?
│
├─ YES ──► Classification: RT4 (Direct)
│          Typical for: internal tools, batch processors, LS4 sunset apps.
│
└─ NO ───► Q: Does the team have the infrastructure and
           observability for automated canary analysis?
           │
           ├─ YES ──► Q: Does the business need gradual
           │          rollout (feature validation, A/B testing)?
           │          │
           │          ├─ YES ──► Classification: RT1 (Progressive/Canary)
           │          │
           │          └─ NO ───► Classification: RT2 (Parallel/Blue-Green)
           │                     (Can switch instantly, don't need gradual)
           │
           └─ NO ───► Classification: RT3 (Rolling)
                      Standard zero-downtime without advanced tooling.
```

---

## Impact on Deployment Strategy

| RT Level | Infrastructure Requirements | Observability Requirements | Rollback Capability | Resource Overhead |
|---|---|---|---|---|
| RT1 | Traffic splitting (Istio, Argo Rollouts, Flagger), metrics pipeline | Real-time metrics, automated analysis, alerting on canary degradation | Automated, instant for canary percentage | Low overhead (small canary %) |
| RT2 | Duplicate environment (blue + green), load balancer switch | Health checks on green before switch, post-switch monitoring | Instant full rollback (switch back to blue) | 2x resource during deployment |
| RT3 | Rolling update support (K8s native), readiness probes | Health checks per instance, error rate monitoring during rollout | Partial — must re-roll forward or scale down new pods | Surge capacity during rolling update |
| RT4 | Minimal — stop old, start new | Basic health check post-deploy | Redeploy previous version (downtime during rollback too) | None |

---

## Key Interactions

- **RT1 + VT1** → Cloud-Native Ideal archetype. Maximum safety at maximum velocity. Requires significant infrastructure investment.
- **RT1 + IA2** → Canary requires traffic splitting that container-capable infra may not provide. May force RT3.
- **RT2 + CP3/CP4** → Blue-green in regulated environments: both environments must maintain compliance. Double the compliance surface during deployment.
- **RT3 + O2** → Rolling update across shared pipeline with multiple teams. Must ensure one team's rollout doesn't break another team's components.
- **RT4 + VT1** → Contradiction. Continuous deployment with downtime per deploy means constant disruption. Challenge this combination.
- **RT1/RT2 + LS3** → Advanced deployment strategy for a stable app with rare changes. Is the investment justified?

---

## Collection Method

**Question:**
> How do you currently handle deployment risk? Is downtime acceptable during deployments? Do you use canary deployments, blue-green, rolling updates, or direct replacement?

**Follow-up probes:**
> What happens when a bad deployment reaches production? How long does rollback take today?
> Do you have automated rollback triggers, or is rollback a manual decision?
> Is there a business requirement for gradual rollout (A/B testing, staged feature release)?
