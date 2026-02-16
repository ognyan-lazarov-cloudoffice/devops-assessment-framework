# C2: Compliance Posture

## Core Question

**What regulatory, security, and governance requirements constrain build, deploy, and operate?**

Applied SECOND. Rarely eliminates paths outright but accumulates mandatory requirements onto the chosen path.

---

## Classifications

| Code | Name | Description |
|------|------|-------------|
| CP1 | Unrestricted | Team discretion. No external compliance requirements beyond common sense. |
| CP2 | Standard Organizational | Organization-level policies: vulnerability scanning, RBAC, audit logging, environment isolation, encrypted secrets, dependency scanning. |
| CP3 | Regulated | Named regulatory regime: SOC2, HIPAA, PCI-DSS, GDPR, FedRAMP Moderate, ISO 27001. Formal controls required. |
| CP4 | Highly Regulated | Multiple frameworks, air-gap requirements, FIPS cryptography, multi-party authorization, tamper-evident audit, dedicated infrastructure per regulatory boundary. |

---

## Decision Tree

```
START
│
├─ Q: Does the application process data subject to
│  external regulatory requirements?
│
├─ YES ──► Q: How many regulatory frameworks apply?
│          │
│          ├─ 1 framework ──► Q: Does the framework require
│          │                  air-gap, FIPS, or dedicated infra?
│          │                  │
│          │                  ├─ YES ──► Classification: CP4 (Highly Regulated)
│          │                  └─ NO ───► Classification: CP3 (Regulated)
│          │
│          └─ Multiple ──► Classification: CP4 (Highly Regulated)
│
└─ NO ───► Q: Does the organization mandate security
           policies for deployments (scanning, RBAC,
           audit, etc.)?
           │
           ├─ YES ──► Classification: CP2 (Standard Organizational)
           │
           └─ NO ───► Classification: CP1 (Unrestricted)
```

---

## Accumulated Requirements by Classification

Requirements are CUMULATIVE — each level adds to the previous.

### CP1 (Unrestricted)
No mandatory requirements added.

### CP2 (Standard Organizational)
Adds:
- Image vulnerability scanning (Trivy, Grype, Snyk)
- RBAC for cluster/namespace access
- Audit logging for deployments
- Environment isolation (staging ≠ production)
- Encrypted secrets management (not plaintext in repo)
- Dependency scanning (Dependabot, Renovate)

### CP3 (Regulated)
Adds to CP2:
- Segregation of duties (deployer ≠ approver)
- Formal approval gates in CI/CD pipeline
- Data residency requirements (region-specific deployment)
- Signed container images (cosign, Notary)
- Immutable artifact registry (no tag overwriting)
- Audit trail linking deployment to approval to change request
- Evidence collection for compliance reporting

### CP4 (Highly Regulated)
Adds to CP3:
- Air-gapped deployment pipeline (no internet in production)
- FIPS 140-2/3 validated cryptography
- Software Bill of Materials (SBOM) per image
- Multi-party authorization for production deployments
- Tamper-evident audit logs (append-only, externally verifiable)
- Dedicated infrastructure per regulatory boundary
- Potentially: dedicated registry per environment, no shared network segments

---

## Path Elimination (Rare but Possible)

CP4 can eliminate paths:
- **Cloud PaaS eliminated** if air-gap required (no internet access in managed PaaS)
- **Shared K8s cluster eliminated** if dedicated infrastructure required per regulatory boundary
- **Multi-tenant anything eliminated** if strict isolation mandated

CP1-CP3 do NOT eliminate paths — they add requirements.

---

## Collection Method

**Question:**
> What compliance or regulatory requirements apply to this application? Specifically: SOC2, HIPAA, PCI, GDPR, FedRAMP, or other named frameworks? Are there organizational security policies even without external regulation?

**Follow-up probes:**
> Are there air-gap requirements? FIPS cryptography mandates? Multi-party approval requirements?
> Is there a separate compliance or security team that must approve deployment architecture?
