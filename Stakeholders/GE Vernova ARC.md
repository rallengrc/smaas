---
title: Stakeholders — GE Vernova ARC
description: Organizational profile, leadership contacts, and operational stakeholders at GE Vernova Advanced Research Center
keywords:
- stakeholders
- GE Vernova
- ARC
- contacts
- leadership
- organization
tags:
- stakeholder
- client
category: reference
classification: 🟢🛡️ General
last_updated: '2026-10-12'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- ge vernova stakeholders
- arc contacts
- stakeholder profiles
company: General Electric Company (GE Vernova)
address: 58 Charles St, Cambridge, MA 02141
---

# GE Vernova ARC

> **TL;DR:** Directory of client-side stakeholders, technical leads, and research managers at GE Vernova ARC.
> **Use this for:** Identifying key contacts, escalation paths, and stakeholder roles.

Client organization for [[SOW - Burstable MLaaS|Burstable MLaaS]]. GE Vernova ARC provides the surrogate modeling workloads and application requirements that the AWS GPU environment supports.

## Known details
- **The first paying customer is the Electrification business**, funding the GPU servers from its 2026 program — see [[Surrogate ML Accelerator - Electrification]]
- ~4 ARC researchers expected to use the static environment initially ([[2026-10 October]])
- Researchers are to operate as **"applied ML engineers"** — self-sufficient in troubleshooting, configuring and scaling their own models, with no production ticketing or deployment queues in the path ([[2026-10-12 Research Team Kickoff]])
- The organization is **intentionally flat**: decentralized technical problem-solving, engineering acting as a direct support layer, and no blocker persisting beyond 24 hours
- Existing on-premises MLaaS environment located in **Alpharetta**, which the static AWS environment is modeled after
- Governed by MSA between GE Vernova and Logic Technology, Inc., effective 2013-11-01
- Broader motivation: replacing paid Quantum Black surrogate-modeling platforms with an ARC-owned "surrogate in a box" shared service — see [[2026-07-30 Discovery Meeting]]

## Contacts
- **Michael Russo** — michael.russo1@gevernova.com — **Sponsor / "Block Breaker"**; presenting the business case to leadership for the broader DT4D/AWS initiative; expects LTI's cloud engineers (now [[Nam Park]], [[Chris Burke]] and [[Rick Allen]]) to be GE Vernova's "key AWS support and architects" post-POC (see [[2026-08-11 Engagement Structure Email]], where the pair named was Nam and Earle Flynn)
- **Todd Shirback** — shirback@gevernova.com — **Project Manager** for the Electrification project *(spelling confirmed 2026-10-06; earlier documents varied between "Shirbak" and "Shirback")*
- **Dave Garber** — **MLaaS Team Lead**; reviewing DT4D/Quantum Black architecture documentation alongside the LTI team, and a supporting knowledge resource per [[LTI Internal Kickoff Brief]]
- **Jim Tallman** — leads the engineering/application team and the **GE Vernova researchers**. His team owns and provides the requirements for the surrogate modeling workloads that LTI builds cloud infrastructure to support ([[2026-08-11 Engagement Structure Email]]). Per [[LTI Internal Kickoff Brief]] §5, LTI is to **deploy his team's application and frontend into the new environment and then support it** — the exact division of application / infrastructure / support responsibility is still unconfirmed. *(Surname resolved 2026-10-04; earlier notes recorded him only as "Jim".)* **Ran the research kickoff on 2026-10-12** ([[2026-10-12 Research Team Kickoff]]), where he set the applied-ML operating model, named the EKS/Ray/Argo stack, and committed to a weekly recurring meeting and a formal plan to follow. He is the direct source for research-side requirements.
- **Deepak Akhare** and **Priyesh Kakka** — researchers/business alongside Jim Tallman, per [[Surrogate ML Accelerator - Electrification]]. Two of the SOW's "approximately four ARC researchers"; the fourth is unidentified.
- **Supporting knowledge resources** (not assigned to delivery, available for environment knowledge and historical context, per [[LTI Internal Kickoff Brief]]): **Milton Whitney**, **Lalo Munoz**, **Sherwin Pagtakhan**

> Note: **Michael Young** (myoung@jahnelgroup.com) is LTI/Jahnel-Group-side, not a GE Vernova contact — see [[Michael Young]] under Team.

## Related
- [[Static AWS GPU Environment]]
- [[QB Reference Architecture]]
- [[2026-07-30 Discovery Meeting]]
- [[2026-08-11 Engagement Structure Email]]
