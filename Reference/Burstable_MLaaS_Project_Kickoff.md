---
title: "Burstable MLaaS — Project Kickoff Briefing"
description: "Internal LTI kickoff planning document detailing project objectives, team allocations, and GE engagement structure"
keywords: [Burstable MLaaS, project kickoff, LTI planning, GE Vernova, DT4D, staffing, team allocations, Quantum Black]
category: planning
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
related:
  - ../Plans/LTI Internal Kickoff Brief.md
  - ../Plans/Phase 1 Project Plan.md
  - GEV - DT4D Discovery Meeting - 7_30_2026.md
ai_search_aliases:
  - burstable mlaas project kickoff
  - lti project kickoff briefing
  - dt4d mlaas kickoff
---

# 📌 Burstable MLaaS — Project Kickoff Briefing

> **Internal LTI Planning Briefing for DT4D / AWS Burstable MLaaS Project Kickoff with GE Vernova Research.**
> **Source:** `Projects/Burstable MLaaS/Reference/Burstable_MLaaS_Project_Kickoff.docx.pdf`
> **Generated:** 2026-10-11
> **Converter:** `scripts/pdf_to_md.py` (PyMuPDF 1.28.2)

## 🎯 TL;DR

- **Core Goal:** Establish a standalone surrogate modeling environment within ARC's AWS cloud environment, leveraging LTI's DT4D heritage and Quantum Black reference blueprints.
- **Delivery Strategy:** Deliver Phase 1 during the initial contract period through February, establishing LTI as GE Vernova ARC's trusted AWS cloud delivery partner.
- **Staffing Allocations:** Nam Park (Sr. Cloud Infrastructure Engineer, 100%), Chris Burke (Sr. Cloud Infrastructure Engineer, 50%, cloud/HPC architecture), Rick Allen (Sr. Cloud Infrastructure Engineer & AI Systems Lead, 50%).
- **Technical Baseline:** Kubernetes, Amazon S3, Ansys CFX, Karpenter auto-scaling. *(The Java Spring backend and React frontend named in the source document describe **DT4D**, not this build — clarified 2026-10-19. The transcribed body below is left as recorded.)*
- **Use this for:** Reviewing internal team allocations, project objectives, and technical direction established prior to the GE client kickoff.

---

## Page 1

Logic Technology, Inc.LTI Internal Planning | Burstable MLaaS DT4D / AWS

Burstable MLaaS Project Kickoff

DT4D / AWS | GE Vernova Research and LTI | Internal LTI Planning

1. Project Purpose

Establish a standalone surrogate modeling environment within ARC’s AWS environment, drawing on LTI’s
DT4D experience and the Quantum Black reference architecture. This document aligns the LTI team on
the project’s purpose, staffing, technical direction, and preparation for the GE kickoff.

2. Background and Objectives

GE Vernova’s wind and power businesses are investing millions of dollars with Quantum Black, a
McKinsey-owned firm, to develop surrogate modeling platforms. These capabilities overlap with work
previously delivered through DT4D. ARC leadership sees an opportunity to rebuild that expertise
internally and provide a reusable shared service across GE Vernova.

The intended offering is “surrogate in a box”: an internal platform that can support wind, power,
electrification, and other GE Vernova business units. The project aims to:

•​
Apply existing LTI DT4D knowledge and experience to accelerate delivery.

•​
Reduce external vendor dependency and associated costs.

•​
Build AWS cloud expertise within ARC and enable scalable compute capacity.

•​
Create a reusable surrogate modeling capability across business units.

3. Project Team and Allocation

Organization
Team Member
Planned Allocation

GE Vernova
Mike Russo; Todd Shirbak
Project stakeholders

LTI
Nam Park
100%

LTI
Chris Burke
50%

LTI
Rick Allen
50%

Nam will be dedicated full time. Chris and Rick will contribute part time, with Chris expected to provide
more hours initially given his AWS architecture and HPC expertise. Rick may increase his involvement as
his other project winds down. Actual weekly allocations will be coordinated as priorities evolve.

Supporting knowledge resources: Dave Garber (MLaaS Team Lead), Milton Whitney, Lalo Munoz, and
Sherwin Pagtakhan. These team members are not directly assigned to delivery but may assist with
environment knowledge and historical context.

Internal — Not for distribution outside LTIPage 1 of 3

## Page 2

Logic Technology, Inc.LTI Internal Planning | Burstable MLaaS DT4D / AWS

4. LTI Internal Objective

Deliver Phase 1 successfully during the current contract period, which runs through February, and
establish LTI as Mike Russo’s trusted AWS delivery team. Strong execution should position LTI for renewal
beyond the initial engagement.

5. Technical Direction

The following reflects Mike Russo’s responses to the August 5 follow-up email and provides the starting
point for kickoff alignment.

•​
Standalone environment: Establish a new environment within ARC using the Quantum Black design
as reference architecture. The existing environment is hosted in the GE Vernova Enterprise Master
Payer account; no integration with it is planned.

•​
Application deployment: Work with Jim Tallman and his engineering team to deploy their
application and frontend into the new environment, then support it. Confirm the division of
application, infrastructure, and support responsibilities at kickoff.

•​
Available reference materials: Some infrastructure CloudFormation templates and YAML files are
available, including Karpenter scaling configuration. Application service deployment materials have
not been provided.

•​
Dedicated AWS account: The account is intended solely for this application; no additional
applications or services are currently planned.

•​
Architecture flexibility: The original DT4D application stack can serve as a starting point. Russo is
open to alternative approaches that take advantage of subsequent technology improvements.

•​
Initial technology baseline (subject to architecture review): Kubernetes, Amazon S3, Ansys CFX, a
Java Spring backend, a React frontend, and AWS compute that can scale with workload demand.

6. Kickoff Preparation and Next Steps

Action
Participants / Timing

Review DT4D and Quantum Black architecture
documentation and available infrastructure configuration.

Nam, Chris, Rick, and Dave Garber;
before internal kickoff

Consolidate questions, gaps, dependencies, and
architecture improvement opportunities.

LTI delivery team; for kickoff discussion

Hold the internal kickoff to align responsibilities,
expectations, initial priorities, and questions for GE.

Monday, October 5, 2026
11:00 a.m. ET

Hold the GE kickoff to confirm scope, delivery priorities,
dependencies, and next actions.

Tuesday, October 6, 2026
11:00 a.m. ET; invite sent by Russo

Internal — Not for distribution outside LTIPage 2 of 3

## Page 3

Logic Technology, Inc.LTI Internal Planning | Burstable MLaaS DT4D / AWS

Action
Participants / Timing

Identify additional former DT4D stakeholders and
coordinate involvement with Jim Tallman’s engineering
team.

Nam, Rick, Chris

Internal — Not for distribution outside LTIPage 3 of 3


---

## Extracted images

0 actually-drawn image placement(s) -> 0 unique image(s) in `burstable-mlaas-project-kickoff.assets/` (0 treated as running logo/footer; 0 tiny image(s) dropped; 0 page render(s)).

_No images were produced._
