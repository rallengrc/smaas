---
title: 2026-08-11 Engagement Structure Email
description: Clarification of SOW engagement model, deliverables, and team responsibilities between GE Vernova and LTI
keywords:
- engagement structure
- email
- SOW
- deliverables
- staffing
- LTI
tags:
- meeting
- email
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- engagement structure email
- sow alignment email
- lti staffing agreement
date: 2026-08-11
---

# Engagement Structure Email — 2026-08-11

> **TL;DR:** Key correspondence establishing that the engagement operates on milestone-based deliverables rather than pure staff augmentation.
> **Use this for:** Referencing agreed engagement boundaries and communication protocols.

Source: [[POC Kickoff Email - 2026-08-11]]

**From:** Michael Young (LTI/Jahnel Group) — myoung@jahnelgroup.com
**To:** Michael Russo (GE Vernova) — michael.russo1@gevernova.com; Todd Shirback (GE Vernova) — shirback@gevernova.com
**Sent:** Tue 2026-08-11, 2:52 PM — the day before [[SOW - Burstable MLaaS|the SOW]]'s effective date (2026-08-12)

This is the confirmation follow-up referenced as a next step in [[2026-07-30 Discovery Meeting]], and it resolves several of that meeting's open questions.

## Engagement model
Rather than LTI's typical staff-augmentation (time-and-materials) model, this POC will be run toward a **defined project deliverable**: a working AWS environment is the primary POC deliverable, not just billed hours.

## Roles, clarified
- **Jim and his team (GE Vernova)** — act as the application team; they own and provide the requirements for the surrogate modeling workloads.
- **[[Nam Park]] and Earle Flynn (LTI)** — use the AWS design previously shared (i.e. [[QB Reference Architecture]]) as the starting point to design, build, deploy, and support the cloud infrastructure needed to run those workloads.

> **Personnel note:** Earle Flynn left the engagement on 2026-09-14; [[Chris Burke]] now holds that role. Names in this note reflect the email as sent on 2026-08-11 and are left unchanged; everything forward-looking names Chris.

This effectively answers the discovery meeting's open "app stack ownership" question in spirit: the application/workload layer is owned by GE Vernova's own team (Jim's), not LTI. LTI's scope is cloud infrastructure. It does **not** explicitly confirm who owns the Java Spring/React app-stack work named in the discovery meeting — worth a direct confirmation if that matters for scope boundaries.

It also partially answers the "rebuild vs. extend" question: Nam/Earle are using the previously-shared AWS design (the QB reference diagram) as a **design starting point** for new infrastructure — not extending Quantum Black's live platform.

## Timeline & continuity (Q&A with Michael Russo)
- **Target timeline for the initial POC:** confirmed as **end of year (EOY) 2026** — consistent with the SOW's Dec 2026 milestone language and term end of 2027-01-30.
- **Post-POC:** Russo expects Nam/Earle to continue in a staff-aug role beyond the initial POC — supporting the environment and potentially building more. He characterized them as GE Vernova's "**KEY AWS support and architects**."
- **Longer term:** if the POC succeeds, Russo expects this to evolve into a **production environment** that LTI continues to help maintain and develop.

> None of this is contractually committed yet — it's stated intent from the client side ahead of/around the SOW's start. Worth tracking as a signal for future SOW renewal/expansion, not as scope.

## Operational items
- **Background checks / drug tests** are standard for all contractors added to GE's **VNDLY** system, which provisions Nam/Earle's SSO and access to GE environments — applies to remote team members too.
- **Office space:** no constraints; GE Vernova is flexible with remote/LTI office space.

## Related
- [[2026-07-30 Discovery Meeting]]
- [[QB Reference Architecture]]
- [[Build Analysis - Target Platform on AWS]]
- [[Risks & Open Questions]]
- [[Decisions Log]]
