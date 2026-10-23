---
title: 2026-07-30 Discovery Meeting Notes
description: Initial technical discovery meeting between GE Vernova ARC and LTI discussing surrogate platform requirements
keywords:
- discovery meeting
- GE Vernova
- LTI
- kickoff
- surrogate in a box
- requirements
tags:
- meeting
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- discovery meeting 2026-07-30
- initial discovery notes
- ge vernova kickoff notes
date: 2026-07-30
attendees:
- Mike Russo
- Todd Shirback
- Nam Park
- Earle Flynn
---

# Discovery Meeting — 2026-07-30

> **TL;DR:** Foundational discovery discussion capturing GE Vernova's desire to transition from Quantum Black to an in-house ARC platform.
> **Use this for:** Tracing original stakeholder requirements, vision statements, and scope boundaries.

Source: [[GEV - DT4D Discovery Meeting - 7_30_2026.pdf]]

**Attendees:** GE — Michael Russo, Todd Shirback *(spelled "Shirbak" in the source PDF; corrected per [[2026-08-11 Engagement Structure Email]]'s email signature)* · LTI — [[Nam Park]], Earle Flynn

> **Personnel note:** Earle Flynn left the engagement on 2026-09-14 and was replaced by [[Chris Burke]]. His name is kept in this note because it records who actually attended and what they said — see [[Chris Burke]] for the handover.
**Topic:** DT4D / AWS — HPC and MLaaS

Questions below are attributed to "MY" in the source PDF — confirmed as **[[Michael Young]]**, LTI/Jahnel Group (not a GE Vernova attendee), per [[2026-08-11 Engagement Structure Email]].

This is the precursor meeting to [[SOW - Burstable MLaaS|Burstable MLaaS]] — it explains the business motivation and target end state behind the SOW's static-environment-then-on-demand-POC plan.

## Background
GE Vernova's wind and power businesses currently pay Quantum Black (a McKinsey-owned firm) millions to run surrogate modeling platforms — capabilities that replicate what the original DT4D project once did internally. ARC leadership sees this as both a gap and an opportunity: rebuild these capabilities internally rather than keep paying an external vendor.

## Project overview
GE Vernova Research is rebuilding surrogate modeling capability internally, using **Quantum Black's architecture as a reference blueprint** — not extending or taking over Quantum Black's platform (which stays owned by the wind business after that contract ends), but building a new version from the ground up inside ARC's own AWS environment.

The result is meant to be packaged as **"surrogate in a box"** — a shared service other GE Vernova business units (wind, power, electrification, etc.) can consume, not a one-off for ARC.

**Technology stack (as stated):** Kubernetes, S3 storage, Ansys CFX, Java Spring backend, React frontend, AWS burstable compute for scalability — this is where the SOW's "Burstable" naming comes from.

> **Clarified 2026-10-19:** the **Java Spring backend and React frontend describe the predecessor DT4D system**, not what this engagement builds. This project reuses DT4D's *concepts* and builds a wholly new cloud architecture for MLaaS. The stack is recorded here as stated at the time; it was never a candidate for this build. See [[Decisions Log]].

See [[QB Reference Architecture]] for the blueprint architecture referenced here, and [[Build Analysis - Target Platform on AWS]] for what building this actually requires.

## Goal
Develop ARC's own internal surrogate modeling capability that:
- Leverages existing LTI DT4D knowledge and team expertise
- Reduces external vendor dependency and associated cost
- Builds AWS cloud expertise within ARC
- Serves as a reusable tool across GE Vernova business units

## Next steps (as of this meeting)
1. **Documentation review** — Nam, Earl, and Dave Garber to review DT4D and Quantum Black architecture documentation.
2. **Prepare feedback** — identify questions, gaps, improvement opportunities.
3. **Internal follow-up call** — Tuesday 9:30am ET; [[Michael Young]] to email Michael Russo to confirm understanding and cover kickoff details — see [[2026-08-11 Engagement Structure Email]] for that follow-up.
4. **Business case** — Michael Russo presenting to leadership the following week for formal approval and funding.
5. **Resource coordination** — start with core LTI team, scale as needed.

## Open questions raised
1. (Michael Young) What is the plan for the app stack layer (Java, React)? — *Partially answered in [[2026-08-11 Engagement Structure Email]]: "Jim's team" (GE Vernova) owns app/workload requirements; exact Java/React build ownership still unconfirmed.*
2. (Michael Young) When does this project kick off? Nam Park has other projects competing for his time — this seemed like the best fit for him, but timing clarity is needed. — *Answered: initial POC targeted for EOY 2026.*
3. (Earle Flynn) Are we actually rebuilding from the ground up, or extending Quantum Black's existing platform? — *Partially answered: using the shared AWS design as a starting point for new build, not extending the live Quantum Black platform.*

> Tracked in [[Risks & Open Questions]].

## Action items
- [x] Confirm outcome of the internal follow-up call — see [[2026-08-11 Engagement Structure Email]]. Leadership business-case approval status still unconfirmed.
- [~] Resolve "rebuild vs. extend" question — reasonably clarified (see above); no explicit IP/licensing statement yet. Still relevant to [[On-Demand MLaaS POC]] scope.
- [~] Get clarity on app stack ownership — Jim's team owns app requirements; specific Java Spring/React build ownership still open.
