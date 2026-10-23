---
title: Reference Index — Burstable MLaaS
description: Index of external architecture documents, vendor references, and engineering notes for Burstable MLaaS
keywords:
- reference index
- architecture reference
- external docs
- Burstable MLaaS
tags:
- index
category: index
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- reference index
- reference documents
- mlaas reference materials
---

# Reference

> **TL;DR:** Directory of architectural reference materials, hardware guides, and distributed computing literature.
> **Use this for:** Finding background research and architecture standards.

Project-specific reference material for [[SOW - Burstable MLaaS|Burstable MLaaS]] — things consulted while doing the work but not deliverables themselves (spec sheets, on-prem environment documentation, vendor datasheets, security/auth requirement docs, etc.).

Material reusable across other projects belongs in the vault-level `3-Resources/` instead.

## Log
- [[Surrogate ML Accelerator - Electrification Project.pptx]] — **shared by Mike Russo at the GE kickoff, 2026-10-06.** The business case and funding vehicle sitting above our SOW: Electrification is the paying business unit, hardware is **4 × p5.48xlarge / 32 H100 GPUs** in an account inside the **GEV ENT MasterPayer Org**, costed at **$1.23M–$1.83M over 15 months**. Slide 4 is a McKinsey DLS application architecture (FastAPI / Flyte / Dask / MLflow). Slide 3 duplicates [[QB Application-Level Architecture (EKS)]]; slide 2 is a Confluence link to the Quantum Black PRD (GEVDMND0007346). See [[Surrogate ML Accelerator - Electrification]] for the parsed version and the **conflicts it raises with our current plan**.
- [[Burstable_MLaaS_Project_Kickoff.docx.pdf]] — **LTI internal kickoff planning document (added 2026-10-04). Internal — not for distribution outside LTI.** Sets the delivery team and allocations (Nam 100%, Chris 50%, [[Rick Allen]] 50%), the technical direction from Mike Russo's responses, and the kickoff dates (internal 2026-10-05, GE 2026-10-06). See [[LTI Internal Kickoff Brief]] for the parsed version.
- [[SOW - Scope.pdf]] — **updated scope document (added 2026-09-14)**. Defines Phase 1 with an eighth deliverable (design/build/deploy the Burstable MLaaS infrastructure) and Phase 2 as **Support & Enhance**. **Dates re-baselined 2026-10-04 to Phase 1 = October–November 2026 and Phase 2 = December 2026–February 2027** (the originally-filed version said Sept–Oct and Nov–Dec). Also broadens the engagement framing to "Cloud Infrastructure Engineering services" generally, naming Burstable HPC with THOR+ as possible additional work. See [[Phase 1 Project Plan]] for the parsed version and the resulting plan. **Note:** this is a scope document, not the executed contract — see that plan's §8 on which document governs.
- [[GEV - DT4D Discovery Meeting - 7_30_2026 (1).pdf]] — notes from the 2026-07-30 discovery meeting; see [[2026-07-30 Discovery Meeting]] for the parsed version
- [[QB_ArchDiagram_Current.png]] — Quantum Black's current AWS architecture, used as the reference blueprint; see [[QB Reference Architecture]] for the parsed version
- [[POC Kickoff Email - 2026-08-11]] — email screenshot confirming POC engagement structure and roles; see [[2026-08-11 Engagement Structure Email]] for the parsed version
- [[Quantum Black_AppFLowandInfra.png]] — Quantum Black's application-level architecture diagram (service communication within EKS); see [[QB Application-Level Architecture (EKS)]] for the parsed version. `eks_architecture_summary.pdf` is an AI-generated summary of this diagram, corrected to match it (was missing the Security layer and had conflated the EFS/EBS storage entries).
- [[EKS Platform Replication Plan]] — technical build plan for replicating [[QB Application-Level Architecture (EKS)]] inside ARC's own AWS account (phasing, per-layer tasks, AWS service feasibility); see [[Build Analysis - Target Platform on AWS]] for how its scope compares to the current SOW.
