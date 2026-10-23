---
title: QB Reference Architecture
description: Architectural breakdown and reverse-engineering of Quantum Black's multi-AZ AWS surrogate modeling platform
keywords:
- QB reference architecture
- Quantum Black
- AWS
- multi-AZ
- surrogate in a box
- EKS
- Karpenter
tags:
- architecture
- reference
category: architecture
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- qb reference architecture
- quantum black blueprint
- surrogate in a box architecture
---

# QB Reference Architecture

> **TL;DR:** Comprehensive blueprint of the Quantum Black reference platform featuring Karpenter auto-scaling, EFS/S3 storage, Aurora PostgreSQL, and ALB/OIDC authentication.
> **Use this for:** Serving as the target architectural benchmark for GE Vernova's internal surrogate modeling platform.

Source: [[QB_ArchDiagram_Current.png]]

This is **Quantum Black's current AWS architecture** for the wind business's surrogate modeling platform — the platform GE Vernova is paying Quantum Black to run today, per [[2026-07-30 Discovery Meeting]]. It is being used as a **reference blueprint**, not something LTI is taking over or extending: the goal is an ARC-owned equivalent, described as "surrogate in a box."

See [[Build Analysis - Target Platform on AWS]] for what standing up an equivalent means for this project.

See [[QB Application-Level Architecture (EKS)]] for a narrower, service-communication view inside the EKS cluster (ingress, OIDC auth, platform services, security) — per its own diagram notes, it complements this landing-zone-level view rather than replacing it.

## Environment
- AWS Cloud, **eu-west-1**, a **new account** (target state — separate from Quantum Black's current account)
- Existing/separate AWS account `geren-eu-dwf-sdm-prod` (356758783539), eu-west-1, holding the `sdm-v5-s3-project-storage-prod` S3 bucket — this is the wind business's existing design-data store, outside the new account, accessed read-only

## Components
- **Access & network:** GE Network → GE Firewall → internal HTTPS (port 443) to an ALB, secured via OIDC against the **GE Identity Provider**; multiple `*.gevernova.net` URLs; IRSA role and a KMS key present at the account boundary
- **Compute:** EKS cluster spanning **App az-1 / App az-2**, running on EC2 Linux (Amazon Linux) nodes
  - **EKS Node Group** (standard/SA-managed provisioning process) — instance classes `p4d.24xlarge` and `m4.large`, node group count 2, OS Amazon Linux
  - **EKS Node Pool** managed by the **Karpenter controller**, owned by the application team — nodes provisioned dynamically based on application demand (this is the "burstable" piece)
- **Data:**
  - Aurora PostgreSQL, Multi-AZ (`db.m6g.large`), DB az-1/az-2, read access from EKS over port 2483, credentials pulled from Secrets Manager; stores metadata
  - EFS — shared volume storage over port 2049
  - S3 — application image storage (png/jpeg)
- **CI/CD:** GE GitHub Repository → GitHub Actions → ECR (GESOS) → EKS pulls/deploys latest image
- **Secrets & config:** Secrets Manager (DB credentials)
- **Observability:** CloudWatch, fed by a dedicated logging microservice (Fluent Bit or Logstash) collecting app/container logs from EKS
- **External data integration:** EKS IAM role has read-only access to the SDM S3 bucket (separate account) so the app can pull wind blade design datasets for model training/optimization **without copying that data into the new platform's own storage**
  - `arn:aws:s3:::sdm-v5-s3-project-storage-prod/results/npi-mwc/conceptual_design/App_space_sweep/`

## Numbered flow (as annotated on the diagram)
1. User accesses the app via an internal HTTPS URL on port 443, secured via OIDC on the ALB.
2. ALB routes traffic to the EKS cluster on port 443, where built-in services run.
3. EKS reads the PostgreSQL RDS (Aurora) over port 2483 after pulling credentials from Secrets Manager; metadata is stored in the DB.
4. EFS is used as additional shared storage, port 2049.
5. EKS accesses the S3 bucket for stored images (png/jpeg).
6. GitHub Actions updates the ECR image; EKS retrieves and deploys the latest image from the repo.
7. In parallel, EKS retrieves DB login credentials from Secrets Manager.
8. EKS generates app/container logs, collected by a dedicated microservice (Fluent Bit or Logstash) and sent to CloudWatch.
9. The EKS role has read access to the SDM S3 bucket, letting the app securely retrieve wind blade design datasets for model training/optimization without persisting that data locally.

## Notes from the diagram author
- Both **Node Group** and **Node Pool** concepts are used for compute provisioning at once: the Node Group is managed through the standard SA process; the Node Pool is managed by the app team via the Karpenter controller, with nodes dynamically provisioned based on application requirements.

## Relationship to this project's SOW scope
- The SOW's [[Static AWS GPU Environment]] (3 static servers / 24 GPUs, CLI/shell access, no scheduler) is a **much smaller, lower-level compute foundation** than this diagram — it's raw GPU access for researchers, not an orchestrated multi-tenant platform.
- This diagram is closer to the target end state of the [[On-Demand MLaaS POC]] — a Kubernetes-orchestrated, web-fronted, burstable platform. Treat it as the north star for POC design, not something to be fully replicated by December 2026.
