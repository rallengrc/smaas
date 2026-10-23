---
title: Burstable MLaaS — Project Home & Map of Content
description: Map of content (MOC) and central hub for the GE Vernova ARC Burstable MLaaS project engagement
keywords:
- Burstable MLaaS
- Home
- MOC
- GE Vernova
- LTI
- AWS
- GPU
- roadmap
tags:
- project
- moc
category: index
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- project home
- burstable mlaas overview
- moc burstable mlaas
- ge vernova project
---

# Burstable MLaaS

> **TL;DR:** Master project navigation hub for LTI's engagement with GE Vernova ARC to design, deploy, and support an AWS GPU environment for surrogate ML modeling.
> **Use this for:** Navigating all project documentation, SOW contracts, architecture designs, timelines, and meeting notes.

**Client:** GE Vernova (General Electric Company) — GE Vernova ARC
**Agency:** Logic Technology, Inc. (LTI)
**Term:** 2026-08-12 → 2027-01-30 *(⚠️ Phase 2 runs to Feb 2027 — term end needs confirming)*
**Status:** 🟡 Active

## What this is
LTI is designing, building, deploying, and supporting an AWS-based GPU environment for GE Vernova ARC's surrogate modeling workloads. Two phases:

1. **Design, Build & Deploy** (**Oct–Nov 2026**) — a static AWS GPU environment modeled after GE Vernova's on-premises MLaaS environment (Alpharetta), *plus* the infrastructure to support the Burstable MLaaS offering. Eight deliverables — see [[Phase 1 Project Plan]].
2. **Support & Enhance** (**Dec 2026 – Feb 2027**) — troubleshoot user issues, enhance per the GE Vernova application team's requirements, and support ongoing development. No build line items.

> **Phase dates re-baselined 2026-10-04.** Kickoffs: internal Mon 2026-10-05, GE Tue 2026-10-06 — see [[LTI Internal Kickoff Brief]]. See [[SOW - Burstable MLaaS]] for the executed contract terms and [[Phase 1 Project Plan]] §8 on which document governs.

**Bigger picture:** this SOW sits inside a larger GE Vernova Research initiative to stop paying Quantum Black for surrogate modeling platforms and build an ARC-owned equivalent — "surrogate in a box" — in-house. [[QB Reference Architecture]] is the reference blueprint for that end state; [[Build Analysis - Target Platform on AWS]] lays out the gap between the SOW's current scope and that target. Per [[2026-07-30 Discovery Meeting]] and its [[2026-08-11 Engagement Structure Email|2026-08-11 follow-up]]: the initial POC targets **EOY 2026**, GE Vernova's own team (applied ML research) owns application/workload requirements while LTI owns cloud infrastructure, and this runs as a defined-deliverable engagement rather than pure staff-aug — though leadership funding approval for the broader vision is still unconfirmed.

## Vault structure (PARA)

All project documentation lives under `prjdocs/`:

- **0-Inbox/** — unsorted notes awaiting filing into the folders below (empty for now).
- **1-Projects/Burstable MLaaS/** — everything below lives here; this is currently the vault's only active project.
  - [[SOW - Burstable MLaaS]] — contract terms, scope, exclusions, term & termination
  - Plans
    - [[Phase 1 Project Plan]] — the current delivery plan (Oct–Nov 2026)
    - [[LTI Internal Kickoff Brief]] — team, allocations, technical direction, kickoff agenda
    - [[EKS Platform Replication Plan]] — technical build plan for the fuller target platform
  - Timeline & Deliverables
    - [[2026-09 September]] — mobilization (pre-Phase 1)
    - [[2026-10 October]] · [[2026-11 November]] — **Phase 1**
    - [[2026-12 December]] · [[2027-01 January]] · [[2027-02 February]] — **Phase 2**
  - Architecture
    - [[Static AWS GPU Environment]]
    - [[On-Demand MLaaS POC]]
    - [[QB Reference Architecture]] — target-state blueprint (Quantum Black's current platform)
    - [[Build Analysis - Target Platform on AWS]] — gap analysis + proposed phasing
  - Team
    - [[Nam Park]] — 100%
    - [[Chris Burke]] — 50%
    - [[Rick Allen]] — 50%
    - [[Michael Young]] — LTI/Jahnel Group account contact (not a named SOW resource)
  - [[GE Vernova ARC]] — client/stakeholder notes
  - [[Status Updates]] — monthly status reports
  - [[Meetings]] — meeting notes
  - [[Reference]] — project-specific reference material (specs, on-prem docs, vendor datasheets)
  - [[Decisions Log]]
  - [[Risks & Open Questions]]
- **2-Areas/** — ongoing responsibilities not tied to this one project (empty for now).
- **3-Resources/Templates/** — reusable templates: [[Weekly Status Update]], [[Meeting Note]].
- **4-Archives/** — inactive projects/areas move here when the engagement wraps or a new SOW supersedes this one.

## Quick facts
- 3 static servers, 24 total GPUs, one AWS data center
- ~4 ARC researchers as initial users
- No scheduling/queuing software in the static environment — researchers self-manage job scheduling
- Resources: [[Nam Park]] (100%), [[Chris Burke]] (50%), [[Rick Allen]] (50%) — ~2.0 FTE nominal
- Kickoffs: internal 2026-10-05, GE 2026-10-06
