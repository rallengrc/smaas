---
title: QB Application-Level Architecture (EKS)
description: Deep-dive analysis of Quantum Black application-level microservices, workflows, and EKS deployments
keywords:
- Quantum Black
- application architecture
- EKS
- microservices
- surrogate model
- Kubernetes
tags:
- architecture
- reference
category: architecture
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- qb app architecture
- qb eks architecture
- quantum black application tier
---

# QB Application-Level Architecture (EKS)

> **TL;DR:** Deconstruction of Quantum Black's application services, data pipelines, and UI/backend container orchestration on AWS EKS.
> **Use this for:** Analyzing the software tier, metadata databases, and service communication of the reference platform.

Source: [[Quantum Black_AppFLowandInfra.png]]

Parsed from Quantum Black's **application-level architecture diagram** — service communication within their Amazon EKS cluster (lab environment, `lab.example.com`). This is a narrower, service-communication view than [[QB Reference Architecture]]; per the diagram's own notes, it complements the broader landing-zone architecture rather than replacing it.

This note corrects two gaps found in an earlier AI-generated PDF summary of the same diagram (`eks_architecture_summary.pdf`, in [[Reference]]): a missing Security layer, and a conflated EFS/EBS storage entry.

## Edge Routing & Access (Layers A – C)
- **Ingress & DNS:** Browser traffic hits Route 53 (`lab.example.com`), passes through AWS WAF, and terminates at an Application Load Balancer (ALB) with TLS via ACM.
- **Ingress controller:** AWS Load Balancer Controller watches/updates the ALB and routes by host/path to Kubernetes Services (`hub`, `proxy`, `workflow`, `argocd-server`, `monitoring`) via an `alb` IngressClass.
- **Authorization (Layer C):** Enforced at the ALB listener (port 443) via OIDC/OAuth2 redirects (302/303), against Corporate IdPs and an enterprise broker (Keycloak-style realm/SSO).

## Platform Services & Orchestration (Layer D)
Namespace: `JupyterHub`
- **JupyterHub & Proxy:** Multi-user data science environment; authenticates via OIDC and provisions per-user workspace pods.
- **Argo Workflows / Flyte:** Workflow orchestration for heavier compute/data pipelines.
- **Argo CD:** GitOps deployment automation, reconciling cluster state with the GitHub repo.
- **Monitoring Service (Grafana):** Dashboards for platform observability.
- **Karpenter:** Watches/updates the Kubernetes API server for node provisioning and autoscaling.

## Workloads & Data Plane (Layers E – F)
- **User Workloads (Layer E):** Pooled compute user workspace pods, plus a Ray cluster for distributed compute.
- **Data Persistence (Layer F):**
  - **Amazon RDS (PostgreSQL):** Hub metadata DB.
  - **Amazon S3:** Object storage.
  - **Amazon EFS:** Shared file storage, mounted via NFS.
  - **Amazon EBS (CSI):** Block storage, mounted via Persistent Volume Claims (PVC/RWO) — separate from EFS/NFS.
  - **Amazon ECR:** Image pull/push (HTTP) for container images.
- **Private connectivity:** Data plane traffic routes through private VPC endpoints — S3 (Gateway), ECR API, ECR DKR, and STS (Interface endpoints).

## Security (Layer G)
- **IAM Roles for Service Accounts (IRSA):** Scoped, short-lived AWS permissions for workloads, no static credentials.
- **AWS KMS:** Encryption keys for data at rest.
- **AWS Systems Manager Parameter Store:** Configuration and secrets storage.

## Observability & CI/CD (Layers H – I)
- **Observability (Layer H, in-cluster):** Prometheus scrapes metrics (HTTP) → Grafana dashboards → Grafana Loki log aggregation → shipped to Amazon S3 (Loki backend for logs, via S3 API/HTTPS).
- **CI/CD (Layer I):** GitHub repo (source) → GitHub Actions (build & push images) → Amazon ECR → Argo CD (GitOps sync/apply) → Kubernetes API server (EKS-managed).

## Numbered flow (as annotated on the diagram)
1. Browser accesses `https://lab.example.com` via Route 53.
2. Traffic passes AWS WAF and reaches the ALB.
3. ALB terminates TLS using ACM.
4. ALB performs OIDC authorization via the Corporate IdP / enterprise broker (redirects).
5. Authorized traffic enters EKS via the AWS Load Balancer Controller and Ingress routes.
6. Platform services in the `JupyterHub` namespace handle hub/proxy, workflow orchestration, Argo CD (GitOps), and monitoring (Grafana).
7. Karpenter interacts with the Kubernetes API for node provisioning/autoscaling.
8. User workspace pods run pooled compute workloads (and Ray cluster jobs).
9. Data access hits RDS, S3, EFS, EBS, and ECR, with private endpoint connectivity where applicable.
10. CI/CD path: GitHub Actions → ECR; Argo CD syncs/deploys to EKS.

## Notes from the diagram
- Application-level service-communication view for DevOps; complements the broader landing-zone architecture — not a replacement for it.
- Authorization is shown at the ALB via OIDC integration.
- Ingress uses the AWS Load Balancer Controller with an `alb` IngressClass.
- The platform namespace is shown as `JupyterHub`.
- The security lane uses IRSA + KMS + SSM Parameter Store.
- CI/CD is part of the main architecture flow (not optional).
