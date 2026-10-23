---
title: "EKS Platform Architecture Summary"
description: "Comprehensive overview of service communication, network layers, and Amazon EKS infrastructure for MLaaS"
keywords: [EKS, architecture summary, service communication, Kubernetes, AWS, data plane, control plane, Karpenter, IRSA]
category: architecture
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
related:
  - ../Architecture/QB Application-Level Architecture (EKS).md
  - ../Architecture/QB Reference Architecture.md
  - Ray and Flyte - Orchestration and Distributed Compute.md
ai_search_aliases:
  - eks architecture summary
  - kubernetes mlaas architecture
  - quantum black eks summary
---

# 📌 EKS Platform Architecture Summary

> **Comprehensive overview of service communication, network layers, and Amazon EKS infrastructure blueprint for Quantum Black / Burstable MLaaS.**
> **Source:** `Projects/Burstable MLaaS/Reference/eks_architecture_summary.pdf`
> **Generated:** 2026-10-11
> **Converter:** `scripts/pdf_to_md.py` (PyMuPDF 1.28.2)

## 🎯 TL;DR

- **Edge Routing (Layers A–C):** Route 53 DNS, AWS WAF, Application Load Balancer with TLS/ACM, and OIDC corporate authentication broker.
- **Platform Orchestration (Layer D):** JupyterHub dynamic user pods, Argo Workflows / Flyte compute pipelines, Argo CD GitOps synchronization, Prometheus/Grafana monitoring, and Karpenter smart autoscaling.
- **Workloads & Data Plane (Layers E–F):** Pooled compute workloads and distributed Ray clusters backed by Amazon RDS, S3, EFS (NFS), EBS (CSI PVC), and ECR via private VPC endpoints.
- **Security & Observability (Layers G–I):** IRSA IAM authentication, KMS encryption, SSM Parameter Store secrets, Loki logging, and GitHub Actions CI/CD to ECR/Argo CD.
- **Use this for:** Rapid reference on EKS architectural layers, security boundaries, and Kubernetes infrastructure building blocks.

---

## Page 1

Application Architecture Summary

Comprehensive Overview of Service Communication & Amazon EKS Infrastructure

Context: This document synthesizes the multi-layered Amazon EKS architecture diagram, detailing edge routing,

authentication, platform orchestration, user workloads, data persistence, security, and CI/CD automation pipelines.

1. Overview & Edge Routing (Layers A – C)

Ingress & DNS: External browser traffic hits Route 53 ( lab.example.com ), passes through AWS WAF for security

filtering, and terminates at an Application Load Balancer (ALB) leveraging ACM for TLS certificates.

Authorization & Security: Layer C enforces authentication prior to workload routing via OpenID Connect (OIDC)

integration connected with Corporate Identity Providers (IdPs) and enterprise brokers (Keycloak-style OIDC).

2. Platform Services & Orchestration (Layer D)

Core Platform Components

JupyterHub & Proxy: Coordinates multi-user data science environments, authenticating via OIDC and provisioning

dynamic, isolated workspace pods for individual users.

Argo Workflows / Flyte: Orchestrates heavy compute workflows, data pipelines, and batch operations.

Argo CD: Implements GitOps-driven deployment, reconciling live cluster states with the version-controlled GitHub
repository.

Monitoring Service (Prometheus & Grafana): Scrapes internal metrics and visualizes system observability dashboards.

Karpenter: Handles automated cluster node provisioning and smart horizontal node autoscaling based on live resource

demands.

Quantum Black Architecture Specification
Page 1 of 2

## Page 2

3. Workloads & Data Plane (Layers E – F)

Compute & Storage Architecture

User Workloads (Layer E): Pooled compute workloads, dedicated Jupyter workspace pods, and distributed Ray clusters.

Data Persistence (Layer F):

Amazon RDS: Manages relational database states (e.g., Hub metadata).

Amazon S3: Provides scalable object storage and log archives.

Amazon EFS: Supplies shared network file storage mounted via NFS.

Amazon EBS: Provides block storage volumes attached via CSI, mounted with Persistent Volume Claims (PVC/RWO).

Amazon ECR: Stores secure, versioned container images.

Private Connectivity: All data plane interactions route securely via private AWS VPC endpoints (S3, ECR API, DKR, STS).

4. Security (Layer G)

Security & Access Control

IAM Roles for Service Accounts (IRSA): Grants Kubernetes workloads scoped, short-lived AWS permissions without

long-lived static credentials.

AWS KMS: Manages encryption keys used to protect data at rest across the platform's storage services.

AWS Systems Manager Parameter Store: Securely stores and retrieves configuration values and secrets used by

platform services.

5. Observability & CI/CD Pipelines (Layers H – I)

Observability (Layer H): Prometheus collects metrics, Grafana provides dashboard interfaces, and Grafana Loki

aggregates system logs into S3 storage.

CI/CD Lifecycle (Layer I): Code changes committed to GitHub trigger GitHub Actions to build and push container

images to Amazon ECR. Argo CD then automatically applies synchronization to the EKS cluster.

Quantum Black Architecture Specification
Page 2 of 2


---

## Extracted images

0 actually-drawn image placement(s) -> 0 unique image(s) in `eks-architecture-summary.assets/` (0 treated as running logo/footer; 0 tiny image(s) dropped; 0 page render(s)).

_No images were produced._
