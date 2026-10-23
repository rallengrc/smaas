---
title: Burstable MLaaS Architecture Index
description: Index of infrastructure specifications, cloud architectures, and surrogate modeling blueprints
keywords:
- architecture index
- AWS
- EKS
- GPU
- Quantum Black
- Karpenter
- surrogate modeling
category: index
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: thatsafact
ai_search_aliases:
- architecture index
- find architecture docs
- mlaas architecture list
---

# Burstable MLaaS Architecture Index

> **TL;DR:** Index of architectural documents comparing Phase 1 static GPU servers, Phase 2 on-demand POC, and target EKS platforms.
> **Use this for:** Locating architectural designs, hardware specs, gap analyses, and surrogate ML platform blueprints.

## Contents

| File / Folder | Description | Keywords |
|---------------|-------------|----------|
| 📄 [Recommended Architecture - Surrogate ML Accelerator.md](Recommended Architecture - Surrogate ML Accelerator.md) | Recommended tooling and build sequence for the research sandbox, derived from the 2026-10-12 kickoff vision and deliverables | recommended architecture, EKS, Ray, KubeRay, Karpenter, Argo, EFA, FSx Lustre, utilization |
| 📄 [Alternative Architecture - AWS Batch.md](Alternative Architecture - AWS Batch.md) | Batch-based alternative to the Karpenter design, the extra tooling it requires, and a head-to-head comparison | AWS Batch, MNP, gang scheduling, fair-share, EFA, comparison |
| 📄 [Alternative Architecture - Amazon ECS.md](Alternative Architecture - Amazon ECS.md) | ECS-based alternative, its Managed Instances limitations, and the three-way comparison against the Karpenter and Batch designs | Amazon ECS, ECS Managed Instances, fractional GPU, ECS Exec, gang scheduling, three-way comparison |
| 📄 [Architecture Decision - Questions for Researchers.md](Architecture Decision - Questions for Researchers.md) | Prioritised, decision-linked questions for the research team to settle the architecture choice and size the Phase 1 build | researcher questions, architecture decision, discovery, Alpharetta baseline, benchmark |
| 📄 [Build Analysis - Target Platform on AWS.md](Build Analysis - Target Platform on AWS.md) | Gap analysis between SOW commitments and target Quantum Black platform on AWS | build analysis, AWS, EKS, gap analysis, Karpenter |
| 📄 [On-Demand MLaaS POC.md](On-Demand MLaaS POC.md) | Phase 2 proof-of-concept architecture for dynamic burstable GPU capacity | on-demand, POC, burstable GPU, Karpenter, AWS |
| 📄 [QB Application-Level Architecture (EKS).md](QB Application-Level Architecture (EKS).md) | Deconstruction of Quantum Black application services, microservices, and UI on EKS | QB app, microservices, EKS, Kubernetes |
| 📄 [QB Reference Architecture.md](QB Reference Architecture.md) | Blueprint of Quantum Black reference platform with multi-AZ, EFS, and Aurora | QB reference, blueprint, multi-AZ, EFS, Aurora |
| 📄 [Static AWS GPU Environment.md](Static AWS GPU Environment.md) | Phase 1 specification for 3 static EC2 GPU instances mirroring Alpharetta | static environment, GPU, EC2, Phase 1, NVIDIA |
| 📄 [Surrogate ML Accelerator - Electrification.md](Surrogate ML Accelerator - Electrification.md) | Computational workflow analysis for GE Vernova wind blade surrogate ML models | surrogate ML, electrification, CFD, Ansys CFX, wind blade |
| 📄 [delivery-options-and-3-node-hardware-analysis.md](delivery-options-and-3-node-hardware-analysis.md) | Comprehensive delivery options, 3-node GPU hardware feasibility, and blind spots analysis | delivery options, 3-node GPU, feasibility, blind spots |
