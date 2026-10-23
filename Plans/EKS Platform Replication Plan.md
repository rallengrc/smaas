---
title: EKS Platform Replication Plan
description: Technical implementation plan for replicating the QB reference platform on Amazon EKS for GE Vernova
keywords:
- EKS replication
- Karpenter
- Terraform
- Kubernetes
- AWS EKS
- surrogate platform
tags:
- plan
- architecture
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- eks replication plan
- kubernetes build plan
- platform replication aws
---

# EKS Platform Replication Plan

> **TL;DR:** Step-by-step infrastructure provisioning roadmap for deploying the Kubernetes, Karpenter, storage, and networking layers on AWS.
> **Use this for:** Guiding technical build tasks for future EKS-based burstable deployments.

Plan to design, build, and operate an ARC-owned equivalent of [[QB Application-Level Architecture (EKS)]] inside GE Vernova ARC's own AWS environment.

**Status: technical build plan, not committed scope.** This plan covers the full application-level architecture (ingress, platform services, security, data plane, observability, CI/CD). Per [[Build Analysis - Target Platform on AWS]], that is substantially larger than what [[SOW - Burstable MLaaS]] currently commits to (a static GPU environment plus "milestones toward" an on-demand POC). Read this alongside that gap analysis — the phasing below is the engineering roadmap *if/when* the fuller scope is approved, with call-outs where a phase is already inside the current SOW versus where it would need a Work Scope Amendment.

## 0. Source & relationship to other docs
- Target reference: [[QB Application-Level Architecture (EKS)]] (service-communication view) and [[QB Reference Architecture]] (landing-zone view) — same underlying Quantum Black platform, two levels of detail.
- Current committed scope: [[Static AWS GPU Environment]] (Sept 2026) and [[On-Demand MLaaS POC]] (Oct–Dec 2026).
- Gap between the two: [[Build Analysis - Target Platform on AWS]].
- Open items referenced throughout below are tracked centrally in [[Risks & Open Questions]] and [[Decisions Log]] — this plan doesn't duplicate them, it points at them.

---

## 1. Phased approach

Phased by **architecture maturity**, not calendar month — mapped against the SOW's actual timeline where an overlap exists.

| Phase | Focus | Maps to SOW? |
|---|---|---|
| **0. Landing zone & prerequisites** | AWS account/network baseline, decisions unblocked, quotas | Precondition for everything; not itself a SOW line item |
| **1. Compute foundation** | EKS cluster + static/fixed GPU node group | Overlaps [[Static AWS GPU Environment]] (Sept) — but that deliverable is plain EC2, not EKS; standing up EKS itself is **new scope** |
| **2. Burst compute** | Karpenter node pool for on-demand GPU scaling | This *is* the core of [[On-Demand MLaaS POC]] (Oct–Dec) — the most direct in-scope overlap |
| **3. Ingress & edge auth** | Route 53, ACM, WAF, ALB, ALB Ingress Controller, OIDC at the ALB | Partially in scope per [[On-Demand MLaaS POC]]'s open "auth foundation" question — otherwise new |
| **4. Security & data plane** | IRSA, KMS, SSM Parameter Store, RDS, S3, EFS, EBS, ECR, VPC endpoints | Mostly **new scope** — Build Analysis flags data/secrets layer as "not started" |
| **5. Platform services** | JupyterHub, Argo Workflows/Flyte, Argo CD, monitoring service | **New scope** — no app/platform tier in current SOW |
| **6. User workloads** | Workspace pods, Ray cluster | Depends on GE Vernova's app team ("Jim's team," per [[2026-08-11 Engagement Structure Email]]) supplying workload requirements |
| **7. Observability & CI/CD** | Prometheus/Grafana/Loki, GitHub Actions → ECR → Argo CD | **New scope** |
| **8. Hardening & handoff** | Security review, DR/backup, cost guardrails, runbooks | Precondition for calling this "production-ready" per Michael Russo's stated longer-term intent ([[2026-08-11 Engagement Structure Email]]) |

Rationale for this order: each phase is a hard dependency for the next — there's no ingress without a cluster, no OIDC auth without ingress, no platform services without IRSA/secrets, no user workloads without platform services, and CI/CD only becomes meaningful once there's something running to deploy into.

---

## 2. What each layer requires

Using the same layer labels as [[QB Application-Level Architecture (EKS)]].

### Layer A–C — Edge routing, ingress, authorization
- Route 53 hosted zone + record for the chosen domain (ARC's own domain, not `lab.example.com`/`gevernova.net` — those are Quantum Black's/GE's existing zones).
- ACM certificate for that domain, validated (DNS validation via Route 53).
- AWS WAF web ACL attached to the ALB (managed rule groups at minimum).
- ALB provisioned via the **AWS Load Balancer Controller** add-on on EKS, driven by an `alb` IngressClass and per-service Ingress resources.
- OIDC/OAuth2 configured at the ALB listener rule (`authenticate-oidc` action) against a **Corporate IdP** — this requires knowing which IdP GE Vernova actually uses (Okta, Azure AD, Keycloak, etc.); QB's diagram shows a "Keycloak-style" broker but that may be QB's own choice, not GE Vernova's.
- Kubernetes Services fronted by ingress: `hub`, `proxy`, `workflow`, `argocd-server`, `monitoring`.

### Layer D — Platform services
- EKS namespace (e.g. `jupyterhub`) hosting:
  - **JupyterHub + Proxy** (Helm chart `zero-to-jupyterhub`), configured for OIDC login against the same IdP as the ALB.
  - **Argo Workflows** and/or **Flyte** for pipeline/batch orchestration — pick one; QB's diagram lists both as alternatives, not both in production.
  - **Argo CD** for GitOps deployment, pointed at the platform's GitHub repo.
  - **Monitoring service** (Grafana) deployment, wired to Layer H's Prometheus/Loki.
  - **Karpenter** controller + IAM role, provisioning/deprovisioning nodes against defined `NodePool`/`EC2NodeClass` resources.

### Layer E — User workloads
- User workspace pods: per-user JupyterHub singleuser pods, resource-limited, mounting Layer F storage.
- **Ray cluster** (via KubeRay operator) for distributed compute, sized/autoscaled through Karpenter node pools.
- This layer is the one most dependent on GE Vernova's application team defining actual workload shapes (GPU count, memory, image contents) — LTI's infra scope stops at "the platform can run whatever container the app team hands it."

### Layer F — Data plane
- **Amazon RDS** (PostgreSQL) for Hub/platform metadata — single-AZ acceptable for POC, Multi-AZ for production parity with QB's Aurora setup.
- **Amazon S3** buckets for object storage (images, artifacts).
- **Amazon EFS** + CSI driver for shared file storage (NFS-mounted).
- **Amazon EBS** + CSI driver for block storage (PVC/RWO) backing stateful pods.
- **Amazon ECR** repositories for platform + workload images.
- **VPC endpoints** (Gateway: S3; Interface: ECR API, ECR DKR, STS) so in-cluster traffic to these services stays off the public internet.

### Layer G — Security
- **IRSA**: OIDC provider registered on the EKS cluster, per-service-account IAM roles (least-privilege, scoped per workload — e.g. the JupyterHub pod's role differs from Karpenter's controller role).
- **AWS KMS**: customer-managed keys for EBS/EFS/S3/RDS encryption at rest.
- **AWS Systems Manager Parameter Store**: non-secret config; pair with **Secrets Manager** for credentials (QB's landing-zone diagram uses Secrets Manager for DB credentials — worth carrying that pattern into this layer even though the app-level diagram only lists Parameter Store).

### Layer H — Observability
- **Prometheus** (kube-prometheus-stack or similar) scraping in-cluster metrics.
- **Grafana** dashboards reading from Prometheus.
- **Grafana Loki** aggregating logs, with **Amazon S3** as its long-term backend store.

### Layer I — CI/CD
- GitHub repository for platform manifests/Helm values (and app code, if LTI ever owns that).
- **GitHub Actions** workflows: build container images, push to ECR.
- **Argo CD** auto-sync from the GitHub repo to the EKS cluster (this closes the loop with Layer D's Argo CD instance — same component, two roles).

---

## 3. How the layers interact

Request path (matches the diagram's own 10-step flow, now in [[QB Application-Level Architecture (EKS)]]):

```
Browser → Route 53 → AWS WAF → ALB (ACM/TLS) → OIDC redirect (Corporate IdP)
   → AWS Load Balancer Controller → Kubernetes Service (hub / proxy / workflow / argocd-server / monitoring)
   → Platform Service pod (Layer D) → User workspace pod / Ray cluster (Layer E)
   → Data plane (RDS / S3 / EFS / EBS / ECR, via VPC endpoints) (Layer F)
```

Cross-cutting layers (not a single path, but touched by everything above):
- **Layer G (Security)** underlies every hop: IRSA grants each pod its own scoped AWS credentials, KMS encrypts what Layer F stores, Parameter Store/Secrets Manager supplies config and DB credentials to Layer D/E pods.
- **Layer H (Observability)** watches every layer above it: Prometheus scrapes Layer D/E/F workloads, Loki collects their logs, both feed Layer D's Grafana dashboards.
- **Layer I (CI/CD)** feeds Layer D and E: GitHub Actions builds images that land in Layer F's ECR; Argo CD (running in Layer D) pulls from Git and applies changes to everything else in the cluster, including itself.
- **Karpenter** (Layer D) sits beside the Kubernetes API server watching pending pods from Layer E and provisioning EC2 capacity to satisfy them — the mechanism behind "burstable."

In short: A–C get a request in the door and through auth; D decides what handles it; E is where user/compute work actually runs; F is where anything that needs to persist goes; G, H, and I are always-on support layers rather than steps in a single request's path.

---

## 4. AWS service-component feasibility

| Component | Native AWS service? | Notes |
|---|---|---|
| Route 53, ACM, WAF, ALB | ✅ Fully native | No gaps |
| AWS Load Balancer Controller | ✅ AWS-authored, open-source, deployed as an EKS add-on | Standard practice |
| EKS cluster, managed node groups | ✅ Fully native | |
| Karpenter | ✅ AWS-authored open source, first-class EKS integration | Not a managed service you toggle on — it's a controller you deploy and configure (`NodePool`/`EC2NodeClass` CRDs) |
| IRSA, KMS, Parameter Store, Secrets Manager | ✅ Fully native | |
| RDS (PostgreSQL/Aurora), S3, EFS, EBS, ECR | ✅ Fully native | EFS/EBS need their CSI drivers installed as EKS add-ons |
| VPC endpoints (Gateway/Interface) | ✅ Fully native | |
| CloudWatch | ✅ Fully native | Used in QB's *landing-zone* diagram for logs; the app-level diagram uses Loki→S3 instead — pick one logging backend, don't build both |
| JupyterHub, JupyterHub Proxy | ❌ Not an AWS service | Open-source (Helm chart), self-operated on EKS |
| Argo Workflows / Flyte | ❌ Not an AWS service | Open-source, self-operated |
| Argo CD | ❌ Not an AWS service | Open-source, self-operated |
| Prometheus, Grafana, Grafana Loki | ❌ Not AWS services | Open-source, self-operated — **note:** Amazon Managed Prometheus/Grafana exist as managed alternatives if reducing self-ops burden is a goal; would be a deliberate deviation from QB's diagram, worth flagging as a design decision rather than assuming |
| Ray cluster (KubeRay) | ❌ Not an AWS service | Open-source operator, self-operated |
| Corporate IdP / "Keycloak-style" broker | ❌ Not an AWS service (unless replaced with Amazon Cognito) | **Biggest open unknown** — depends entirely on which IdP GE Vernova actually runs; QB's own choice of Keycloak isn't necessarily what ARC should replicate |

**Answer to "can everything be implemented with existing AWS components": mostly yes at the infrastructure layer** — every AWS-native piece in the diagram (compute, network, storage, security, DNS/edge) maps directly to a standard AWS service with no exotic requirements. The platform/application layer (JupyterHub, Argo, Prometheus stack, Ray, the IdP broker) is open-source software that runs *on* AWS/EKS rather than an AWS managed service itself — buildable, but it's operational software LTI would own the deployment and lifecycle of, not a checkbox in the AWS console. That operational burden (upgrades, Helm chart drift, on-call for these components) is worth naming explicitly as scope, since it's a materially different kind of work than provisioning managed AWS services.

---

## 5. Other considerations

- **This plan exceeds current signed scope.** Per [[Build Analysis - Target Platform on AWS]], phases 3–7 above are not covered by [[SOW - Burstable MLaaS]] as written. Anything beyond Phase 2 (burst compute) should go through the SOW's Out of Scope Work process (written proposal → 14-day response → signed Work Scope Amendment) before build effort starts, per [[Decisions Log]].
- **App/workload ownership boundary.** LTI (Nam/Chris) owns infrastructure; GE Vernova's "Jim's team" owns app/workload requirements. Layer E and any app-tier work (Java Spring/React, if that's ever built) sit on GE Vernova's side of that line unless a Work Scope Amendment changes it — don't let infra build absorb app-tier work by default.
- **Cost control for burst compute.** GPU instances are expensive; the [[On-Demand MLaaS POC]] doc already flags this as an open design question (burst trigger, auto-shutdown policy). This needs an answer before Phase 2 goes live, not after.
- **IdP decision blocks Layer C entirely.** Can't build OIDC-at-the-ALB without knowing the actual identity provider. This is the single highest-leverage open question to resolve early — it blocks Phase 3 and, downstream, JupyterHub auth in Phase 5.
- **AWS account & region.** [[Build Analysis - Target Platform on AWS]] and [[Static AWS GPU Environment]] both flag this as unresolved — QB's diagram is silent on region/account for *this* build (it shows "New account" generically); confirm before Phase 0 network design is final.
- **Licensing (Ansys CFX and similar).** Needed for Layer E workloads to actually do surrogate modeling; who holds the license (GE Vernova vs. LTI) affects how workspace images are built and distributed via Layer F's ECR.
- **Rebuild vs. extend / IP rights.** Per [[Risks & Open Questions]], it's "reasonably resolved in spirit" that this is a new build using QB's design as a reference, not a fork of QB's live platform — but there's no explicit IP/licensing statement. Don't copy QB's actual Helm values/configs/code verbatim without confirming that's permitted; treat the diagram as a design reference, not a source to clone.
- **Multi-tenancy for "surrogate in a box."** The long-term vision (per [[2026-07-30 Discovery Meeting]]) is multiple GE Vernova business units sharing this platform. Nothing in the current diagram addresses tenant isolation (namespaces per BU? shared JupyterHub with per-BU auth groups? separate clusters?) — worth designing for even if POC scope is single-tenant, so Phase 5+ doesn't require a rebuild later.
- **Business case / funding.** Per [[Risks & Open Questions]], leadership approval for the full "surrogate in a box" vision isn't confirmed. Treat phases 3–8 as conditional on that approval landing, not as a foregone conclusion.
- **DR/backup and production readiness.** Not in QB's diagram at all (it's a lab/POC-labeled environment — note the domain `lab.example.com`). If this platform is meant to become production (per Michael Russo's stated intent), Phase 8 needs to add backup/DR for RDS and EFS/EBS, multi-AZ where QB's diagram doesn't show it, and an incident-response runbook — none of which QB's own reference architecture models for you.

---

## 6. Preliminary research / prep work

Before committing engineering time beyond Phase 0–2:

1. **Resolve the blocking decisions already tracked in [[Risks & Open Questions]]:**
   - Target AWS account(s) and region for ARC's build.
   - Which corporate IdP to integrate against (blocks Layer C design entirely).
   - Ansys CFX (and other surrogate-modeling software) license ownership and package list.
   - Confirmation that using QB's architecture as a design reference (not clone) is IP-safe.
   - Business case / leadership funding status for anything past the POC.
2. **Technical spikes (small, time-boxed, before full build-out):**
   - GPU node bring-up on EKS: validate NVIDIA device plugin + driver/CUDA stack against whatever Alpharetta parity requires (this overlaps directly with the Sept static-environment work, so it may already be partially done there — check before duplicating).
   - Karpenter GPU provisioning proof-of-concept: confirm it can burst the specific GPU instance families needed, and check current AWS service-quota limits for those instance types in the target region (request increases early — this can take days).
   - JupyterHub-via-Helm + OIDC login spike against a test IdP, before committing to the real one.
   - KubeRay evaluation for the Ray cluster layer, sized against expected workload shapes (once GE Vernova's app team supplies them).
   - Cost model for burst GPU usage (on-demand vs. Spot vs. Savings Plans) to inform the cost-control open question above.
3. **Documentation/design review** — already an action item from the [[2026-07-30 Discovery Meeting]] (Nam, Earle, Dave Garber reviewing DT4D and QB architecture docs); this plan and [[QB Application-Level Architecture (EKS)]]/[[QB Reference Architecture]] are the parsed output of that review — treat further review as refining these, not starting over.
4. **Landing zone groundwork** — VPC/subnet design, IAM permission boundaries for LTI vs. GE Vernova operators, and initial AWS service-quota requests (GPU instances, EKS cluster limits) should start as soon as the account/region decision lands, since quota increases have their own lead time independent of build work.

## Related
- [[QB Application-Level Architecture (EKS)]]
- [[QB Reference Architecture]]
- [[Build Analysis - Target Platform on AWS]]
- [[Static AWS GPU Environment]]
- [[On-Demand MLaaS POC]]
- [[Risks & Open Questions]]
- [[Decisions Log]]
