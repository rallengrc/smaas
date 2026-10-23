---
title: Timeline — 2026-10 October Phase 1 Kickoff
description: Phase 1 execution log and deliverables tracking for October 2026 on the Burstable MLaaS project
keywords:
- October 2026
- timeline
- Phase 1
- kickoff
- static environment
- deliverables
tags:
- timeline
- deliverable
category: status
classification: 🟢🛡️ General
last_updated: '2026-10-12'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- october 2026 timeline
- october status
- phase 1 execution log
month: 2026-10
phase: 1
---

# October 2026 — Phase 1, Month 1 of 2

> **TL;DR:** Execution log detailing Phase 1 kickoff, static EC2 server provisioning, VPC configuration, and baseline validation.
> **Use this for:** Tracking current October delivery milestones and weekly achievements.

**Phase 1 (Design, Build & Deploy) runs October – November 2026** per the SOW, re-baselined 2026-10-04. See [[Phase 1 Project Plan]] for the full plan; this note tracks the October portion.

## Kickoffs
- [ ] **Mon 2026-10-05, 11:00 ET — internal LTI kickoff.** Align responsibilities, expectations, initial priorities, and the questions for GE. Attendees: [[Nam Park]], [[Chris Burke]], [[Rick Allen]]. See [[LTI Internal Kickoff Brief]].
- [ ] **Tue 2026-10-06, 11:00 ET — GE kickoff.** Confirm scope, delivery priorities, dependencies, next actions. Invite sent by Michael Russo.
- [x] **Mon 2026-10-12 — research team kickoff** led by Jim Tallman. Applied-ML sandbox strategy, linear scaling as the primary proof, six research deliverables, and interim action items. See [[2026-10-12 Research Team Kickoff]].

**Three things must come out of the GE kickoff in writing:** the D8 scope reading ([[Phase 1 Project Plan]] §2.1), the application/infrastructure/support split (§2.3), and the term coverage for February 2027 (§8.1).

> **Still outstanding after the research kickoff:** a **weekly recurring meeting** is to be scheduled, and Jim Tallman's **formal plan** is still to come. The six research deliverables do not map cleanly onto D1–D8 — see [[Risks & Open Questions]].

## Action items from the research kickoff (2026-10-12)
| Action | Owner | Priority | Status |
|---|---|---|---|
| Provision laptops & accounts (Nam/Rick) | Todd / IT | Critical | [ ] **Day 0 blocker** |
| Initial architecture diagram — EKS/Ray/Argo | **Cloud Team (LTI)** | Critical | [ ] *Ours* |
| AWS GPU cluster capacity request, single-AZ | Mike Russo | Critical | [ ] |
| Finalize on-prem connectivity link | Dave Garber | Critical | [ ] |
| Initiate Project Lab Notebook | Todd Shirback | Medium | [ ] |

## Focus this month — unblock, then build the foundation
- [ ] **File all long-lead requests** in kickoff week: GPU service quota increase, Alpharetta stack inventory, cybersecurity requirements doc, network/transfer security approval
- [ ] **Obtain** the CloudFormation templates, YAML, and Karpenter scaling configuration referenced in [[LTI Internal Kickoff Brief]] §5
- [ ] **WS0** — VNDLY onboarding / SSO / AWS access confirmed for all three engineers
- [ ] **Decisions locked:** AWS region, GPU instance family, auth model, file transfer mechanism
- [ ] **WS1** — landing zone (VPC, IAM, logging) built in Terraform
- [ ] **WS2** — 3 static servers / 24 total GPUs provisioned *(D1)*
- [ ] **WS3** — command-line, shell, and script-based access for ~4 ARC researchers *(D3)*
- [ ] **WS4** — file transfer path live both directions *(D2)*

## Milestones
- **M0 (Oct 6)** — kickoffs held; every external dependency formally requested
- **M1 (Oct 23)** — D1 + D3: 24 GPUs reachable by researchers
- **M2 (Oct 30)** — D2: data moves both directions

## Exclusion
Scheduling/queuing software is **not** included in the static environment. Researchers self-manage job scheduling.

## Related
- [[Phase 1 Project Plan]]
- [[LTI Internal Kickoff Brief]]
- [[2026-11 November]]
