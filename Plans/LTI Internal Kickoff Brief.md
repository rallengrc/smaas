---
title: LTI Internal Kickoff Brief
description: Internal briefing for the LTI delivery team detailing staffing, roles, timelines, and technical expectations
keywords:
- internal kickoff
- briefing
- team allocation
- roles
- delivery plan
- LTI
tags:
- plan
- internal
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- lti internal kickoff
- internal briefing
- team allocation kickoff
source: Burstable_MLaaS_Project_Kickoff.docx.pdf
dated: 2026-10-04
---

# LTI Internal Kickoff Brief

> **TL;DR:** Internal briefing document outlining team allocations (Nam, Chris, Rick), milestone dates, and execution priorities.
> **Use this for:** Reviewing team roles, operational norms, and project expectations.

Parsed from `Burstable_MLaaS_Project_Kickoff.docx.pdf` (added to [[Reference]] 2026-10-04). **Internal LTI planning document — not for distribution outside LTI.**

This is LTI's own alignment document ahead of the GE kickoff. It is **not** a contract document and does not supersede [[SOW - Burstable MLaaS]] or the `SOW - Scope.pdf` scope document — but it changes several working assumptions in [[Phase 1 Project Plan]].

---

## 1. Purpose
Establish a **standalone** surrogate modeling environment inside ARC's AWS environment, drawing on LTI's DT4D experience and the Quantum Black reference architecture.

## 2. Objectives
Unchanged in substance from [[2026-07-30 Discovery Meeting]] — rebuild internally what GE Vernova currently buys from Quantum Black, packaged as "surrogate in a box" for wind, power, electrification and other business units. Aims: apply LTI DT4D knowledge, reduce vendor dependency and cost, build ARC's AWS expertise and scalable compute, create a reusable capability.

## 3. Team and allocation

| Organization | Team member | Role | Planned allocation |
|---|---|---|---|
| GE Vernova | Mike Russo; Todd Shirback | Project stakeholders | — |
| LTI | [[Nam Park]] | Sr. Cloud Infrastructure Engineer | **100%** |
| LTI | [[Chris Burke]] | Sr. Cloud Infrastructure Engineer | **50%** |
| LTI | [[Rick Allen]] | Sr. Cloud Infrastructure Engineer & AI Systems Lead | **50%** |

> **Titles** per the Team profiles ([[Nam Park]], [[Chris Burke]], [[Rick Allen]]); Nam's dropped "Lead" and Rick's gained "Senior" on 2026-10-13. Note Exhibit A names only two Sr. Cloud Infrastructure Engineers — see §8.3 of [[Phase 1 Project Plan]].
> **Todd Shirback** was spelled "Shirbak" in the original brief; corrected per [[Decisions Log]] (2026-10-06).

- Nam is dedicated full time. Chris and Rick contribute part time, with **Chris expected to provide more hours initially** given his AWS architecture and HPC expertise. **Rick may increase involvement** as his other project winds down. Weekly allocations coordinated as priorities evolve.
- **Supporting knowledge resources** (not assigned to delivery; available for environment knowledge and historical context): **Dave Garber** (MLaaS Team Lead), **Milton Whitney**, **Lalo Munoz**, **Sherwin Pagtakhan**.

> **Differs from the SOW's Exhibit A**, which names two resources at 40 hrs/week each for 5 months. Nominal capacity is the same 2.0 FTE, but it is now split three ways with one new joiner. See §"What this changes" below.

## 4. LTI internal objective
Deliver **Phase 1 successfully during the current contract period, which runs through February**, and establish LTI as Mike Russo's trusted AWS delivery team. Strong execution should position LTI for renewal.

> ⚠️ **"Runs through February"** is consistent with the re-baselined **Phase 2 (December 2026 – February 2027)**, but *not* with the executed SOW's term end of **2027-01-30** recorded in [[SOW - Burstable MLaaS]]. Either the term has been extended and the project record is behind, or Phase 2's final month is uncovered. **Confirm the actual term end at the GE kickoff** — see [[Phase 1 Project Plan]] §8.1 and [[2027-01 January]].

## 5. Technical direction
Reflects Mike Russo's responses to an **August 5 follow-up email**, as the starting point for kickoff alignment.

- **Standalone environment** — new environment within ARC using the Quantum Black design as reference architecture. The existing environment sits in the **GE Vernova Enterprise Master Payer account**; **no integration with it is planned**.
- **Application deployment** — work with **Jim Tallman** and his engineering team to **deploy their application and frontend into the new environment, then support it**. Division of application / infrastructure / support responsibilities to be confirmed at kickoff.
- **Available reference materials** — some infrastructure **CloudFormation templates and YAML files**, including **Karpenter scaling configuration**. Application service deployment materials have *not* been provided.
- **Dedicated AWS account** — intended solely for this application; no other applications or services planned.
- **Architecture flexibility** — the original DT4D application stack can serve as a starting point; Russo is open to alternatives that exploit later technology improvements.
- **Initial technology baseline** (subject to architecture review) — Kubernetes, Amazon S3, Ansys CFX, and AWS compute that scales with workload demand. *(The Java Spring backend and React frontend listed here originally are **DT4D's stack**, not this project's — corrected 2026-10-19, see [[Decisions Log]]. This build reuses DT4D concepts only.)*.

## 6. Kickoff preparation and next steps

| Action | Participants / timing |
|---|---|
| Review DT4D and Quantum Black architecture documentation and available infrastructure configuration | Nam, Chris, Rick, Dave Garber — before internal kickoff |
| Consolidate questions, gaps, dependencies, architecture improvement opportunities | LTI delivery team — for kickoff discussion |
| **Internal kickoff** — align responsibilities, expectations, initial priorities, questions for GE | **Monday, 2026-10-05, 11:00 a.m. ET** |
| **GE kickoff** — confirm scope, delivery priorities, dependencies, next actions | **Tuesday, 2026-10-06, 11:00 a.m. ET** (invite sent by Russo) |
| Identify additional former DT4D stakeholders; coordinate involvement with Jim Tallman's engineering team | Nam, Rick, Chris |

---

## What this changes for [[Phase 1 Project Plan]]

**1. The kickoff timing is now consistent — resolved.** ✅
When this document arrived, the scope document still put Phase 1 at September–October 2026, which would have meant a GE kickoff on 6 October against a phase ending 31 October. **The SOW has since been re-baselined (2026-10-04) to Phase 1 = October–November 2026 and Phase 2 = December 2026–February 2027.** Phase 1 now begins at the kickoff, as it should. See [[Phase 1 Project Plan]] §0.

This also confirms §4's "current contract period, which runs through February" — though the executed SOW's recorded term end is still 2027-01-30, which is a separate open item (§6 below).

**2. The application tier now looks in scope.**
[[Build Analysis - Target Platform on AWS]] and [[EKS Platform Replication Plan]] both treat the Java Spring / React app tier as *out* of LTI's scope, on the basis of the [[2026-08-11 Engagement Structure Email]] role split. §5 here says LTI will "deploy their application and frontend into the new environment, then support it." Deploying and supporting someone else's application is not the same as building it — but it is more than the pure-infrastructure boundary those documents assume. **Confirm the application / infrastructure / support split at the GE kickoff**, as §5 itself instructs.

**3. Capacity is the same on paper, thinner in practice.**
2.0 FTE nominal, but split 100/50/50 across three people, one of whom ([[Rick Allen]]) is new to the engagement and one of whom ([[Chris Burke]]) joined on 2026-09-14 and may still be in VNDLY onboarding. Part-time allocations also carry more coordination overhead than two full-time engineers.

**4. Some build inputs already exist.**
CloudFormation templates, YAML, and **Karpenter scaling configuration** are available. Karpenter is exactly the mechanism [[Phase 1 Project Plan]] §WS7 proposes for D8's burst layer — having a working reference configuration materially de-risks that deliverable. **Get these files before the GE kickoff.**

**5. Open questions this answers.**
- "Jim" is **Jim Tallman** — resolved in [[GE Vernova ARC]].
- The AWS account question is partly answered: a **dedicated account for this application only**, standalone, no integration with the Enterprise Master Payer account that hosts the existing environment.
- Region is still unstated.

**6. Two discrepancies to check.**
- **"August 5 follow-up email"** — the vault records a follow-up email dated **2026-08-11** ([[2026-08-11 Engagement Structure Email]]). Different document, or a date error?
- **"Todd Shirbak"** — the vault corrected this to **Shirback** per that email's signature. This document reverts to "Shirbak". Worth settling from his actual signature block.

## Related
- [[Phase 1 Project Plan]]
- [[SOW - Burstable MLaaS]]
- [[Rick Allen]] · [[Nam Park]] · [[Chris Burke]]
- [[GE Vernova ARC]]
- [[Risks & Open Questions]] · [[Decisions Log]]
