---
title: "GE Vernova — DT4D Discovery Meeting Notes (2026-07-30)"
description: "Foundational discovery meeting notes between GE Vernova ARC and LTI on surrogate modeling and MLaaS"
keywords: [discovery meeting, GE Vernova, DT4D, MLaaS, HPC, Mike Russo, Nam Park, Earle Flynn, Quantum Black]
category: reference
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
related:
  - ../Meetings/2026-07-30 Discovery Meeting.md
  - Burstable_MLaaS_Project_Kickoff.md
  - SOW - Scope.md
ai_search_aliases:
  - dt4d discovery meeting notes
  - ge vernova discovery 7-30-2026
  - mike russo discovery meeting
---

# 📌 GE Vernova — DT4D Discovery Meeting Notes (2026-07-30)

> **Verbatim notes from foundational discovery discussion between GE Vernova Research (Mike Russo, Todd Shirbak) and LTI (Nam Park, Earle Flynn).**
> **Source:** `Projects/Burstable MLaaS/Reference/GEV - DT4D Discovery Meeting - 7_30_2026.pdf`
> **Generated:** 2026-10-11
> **Converter:** `scripts/pdf_to_md.py` (PyMuPDF 1.28.2)

## 🎯 TL;DR

- **Background:** GE Vernova wind & power were spending millions with Quantum Black to replicate capabilities originally developed under DT4D.
- **Vision:** Launch an internal ARC initiative to rebuild surrogate modeling capabilities ("surrogate in a box") from the ground up in AWS.
- **Technology Stack:** Kubernetes, Amazon S3, Ansys CFX, Java Spring backend, React frontend, and burstable AWS compute.
- **Immediate Next Steps:** DT4D and Quantum Black architecture review by Nam Park, Earle Flynn, and Dave Garber; business case presentation by Mike Russo.
- **Use this for:** Reviewing the initial genesis, stakeholder attendees, and original problem statement of the Burstable MLaaS initiative.

---

## Page 1

Attendees:
GE: Mike Russo, Todd Shirbak
LTI: Nam Park, Earle Flynn
DT4D / AWS
Notes:
HPC and MlaaS

DT4D/AWS Project Summary

Background

GE Vernova’s wind and power businesses are currently spending millions with Quantum Black
(a McKinsey-owned firm) to build surrogate modeling platforms—capabilities that replicate what
the original DT4D project once did. ARC leadership recognizes this represents both an
opportunity and a gap: these are capabilities GRC previously built internally and should be able
to develop again.

Project Overview

GE Vernova Research is launching an initiative to rebuild surrogate modeling capabilities
internally using Quantum Black’s architecture as a reference blueprint. Rather than maintaining
or extending Quantum Black’s platform (which will be owned by the wind business after their
contract ends), we’re building our own version from the ground up within ARC’s AWS
environment. The platform will be packaged as “surrogate in a box”—a shared service offering
that other GE Vernova business units can access.

Technology Stack: Kubernetes, S3 storage, Ansys CFX, Java Spring backend, React frontend,
with AWS burstable compute for scalability.

Goal

Develop ARC’s own internal surrogate modeling capability that:

●​ Leverage existing LTI DT4D knowledge and team expertise

## Page 2

●​ Reduces external vendor dependency and associated costs​
●​ Builds AWS cloud expertise within ARC​
●​ Serves as a reusable tool across GE Vernova business units (wind, power,
electrification, etc.)​

Next Steps

1.​ Documentation Review — Nam, Earl, and Dave Garber to review DT4 D and Quantum
Black architecture documentation​
2.​ Prepare Feedback — Identify questions, gaps, and improvement opportunities​
3.​ Internal Follow-up Call — Tuesday at 9:30am ET; Mike Young will send an email to
Michael Russo for confirmation of understanding and more high level kickoff details​
4.​ Business Case — Michael Russo presenting to leadership next week for formal
approval and funding​
5.​ Resource Coordination — Begin with core LTI team; scale resources as needed based
on project requirements

Questions:

1.​ MY - What is the plan for the app stack layer (Java, react?) ​
2.​ MY - At this point, do you know when this project might kick off? Nam does have a
couple other projects but to me this seems like the best fit for him. I can hold him for a bit
but any additional clarity there would be helpful. ​
3.​ EF - Are we actually rebuilding from the ground up or extending?


---

## Extracted images

0 actually-drawn image placement(s) -> 0 unique image(s) in `gev-dt4d-discovery-meeting-7-30-2026.assets/` (0 treated as running logo/footer; 0 tiny image(s) dropped; 0 page render(s)).

_No images were produced._
