# C1: Infrastructure Availability

## Core Question

**What deployment targets are actually available, supported, and operational?**

Applied FIRST in constraint sequence because it can hard-eliminate deployment paths. The hardest constraint.

---

## Classifications

| Code | Name | Description |
|------|------|-------------|
| IA1 | Full Cloud-Native Platform | Managed Kubernetes with ecosystem (service mesh, observability, CI/CD integration, secret management). |
| IA2 | Container-Capable | Container runtime available but limited orchestration. Docker hosts, ECS without full ecosystem, or self-managed K8s without ecosystem tooling. |
| IA3 | PaaS-Constrained | Cloud Run, App Engine, Heroku, Azure App Service. Managed platform with opinionated deployment model. |
| IA4 | Traditional Infrastructure Only | VMs, bare metal. No container runtime in production. |

### Overlay: IA5 — Multi-Target Required

IA5 is NOT a standalone classification. It overlays on the primary IA1-IA4 classification when the application must deploy to multiple infrastructure targets simultaneously.

**Example:** IA1 + IA5 = Full cloud-native platform but must also deploy to a secondary VM environment for disaster recovery.

---

## Decision Tree

```
START
│
├─ Q: Is Kubernetes available in the target environment?
│
├─ YES ──► Q: Is it managed (GKE, EKS, AKS) with
│          operational ecosystem (monitoring, CI/CD,
│          secrets, networking)?
│          │
│          ├─ YES ──► Classification: IA1 (Full Cloud-Native)
│          │
│          └─ NO ───► Classification: IA2 (Container-Capable)
│                     Reason: K8s exists but ecosystem gaps.
│
└─ NO ───► Q: Is a container runtime available
           in any form?
           │
           ├─ YES ──► Q: Is it a managed PaaS
           │          (Cloud Run, App Engine, etc.)?
           │          │
           │          ├─ YES ──► Classification: IA3 (PaaS-Constrained)
           │          │
           │          └─ NO ───► Classification: IA2 (Container-Capable)
           │                     Reason: raw runtime without platform.
           │
           └─ NO ───► Classification: IA4 (Traditional Infra Only)

OVERLAY CHECK:
  Q: Must the application deploy to multiple
     different infrastructure targets?
  YES → Add IA5 overlay to primary classification.
```

---

## Path Viability Matrix

| Fitness → | Container-Native | Container-w/-Constraints | PaaS | VM/IaaS |
|-----------|:---------------:|:-----------------------:|:----:|:-------:|
| **IA1** | ✅ Viable | ✅ Viable | ✅ Viable | ✅ Viable |
| **IA2** | ⚠️ Viable with gaps | ✅ Viable | ❌ N/A | ✅ Viable |
| **IA3** | ❌ Eliminated | ❌ Eliminated | ✅ Viable | ✅ Viable |
| **IA4** | ❌ Eliminated | ❌ Eliminated | ❌ Eliminated | ✅ Viable |

**Key deadlock:** HIGH fitness + IA4 = CONSTRAINT DEADLOCK (app is container-fit but containers unavailable).

---

## Collection Method

C1 is typically known by the assessor. Minimal dialogue needed.

**Question:**
> What is the target deployment environment? Specifically: is Kubernetes available and managed? Is there a container runtime? Or are we deploying to VMs only? Must we support multiple targets?

**Follow-up if unclear:**
> Is the infrastructure operated by your team, a platform team, or a managed service provider? This affects what ecosystem tooling is available.

---

## Accumulated Requirements by Classification

| IA Level | Requirements Added to Path |
|----------|---------------------------|
| IA1 | None — full platform available |
| IA2 | Must provision: monitoring, CI/CD integration, secret management, networking. Gap analysis needed. |
| IA3 | Must conform to PaaS constraints: deployment size limits, cold start behavior, limited network config, no persistent volumes. |
| IA4 | VM deployment tooling required: Ansible/Terraform/Packer. No container orchestration benefits. |
| IA5 overlay | Multi-target CI/CD, environment parity strategy, potentially different deployment models per target. |
