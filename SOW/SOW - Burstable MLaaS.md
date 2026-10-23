---
title: SOW — Burstable MLaaS Contract Terms & Scope
description: Executed statement of work (SOW) terms, deliverables, team allocations, and governance for GE Vernova engagement
keywords:
- SOW
- statement of work
- contract
- GE Vernova
- LTI
- deliverables
- staffing
tags:
- sow
- contract
category: requirements
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- sow burstable mlaas
- contract terms
- statement of work
- executed sow
engagement-title: Burstable MLaaS
effective-date: 2026-08-12
term-end: 2027-01-30
---

# SOW — Burstable MLaaS

> **TL;DR:** Full summary of the executed SOW between GE Vernova and LTI, detailing Phase 1/2 scope, resource hours, term dates, and change processes.
> **Use this for:** Verifying contractual scope, delivery obligations, exclusions, and governance rules.

Source document: [[Burstable MLaaS - SOW - 2026 (Shareable).pdf]]

## Parties
- **Client:** General Electric Company, acting through its GE Vernova — 58 Charles St, Cambridge, MA 02141
- **Agency:** Logic Technology, Inc. ("LTI") — 108 State Street, 5th Floor, Schenectady, NY 12305
- Governed by the Master Services Agreement between Client and Agency, effective 2013-11-01.

## Engagement Title
Burstable MLaaS

## Project Scope
LTI will design, build, deploy, and support an AWS-based GPU environment to support GE Vernova ARC's surrogate modeling workloads.

- **Phase 1 — Design, Build & Deploy (October – November 2026):** deploy a static AWS GPU environment modeled after the Alpharetta on-premises MLaaS environment, *and* design/build/deploy the infrastructure supporting the Burstable MLaaS offering. Eight deliverables — see [[Phase 1 Project Plan]].
- **Phase 2 — Support & Enhance (December 2026 – February 2027):** support and troubleshoot the GPU environment, enhance per the GE Vernova application team's requirements, and support ongoing development of the offering.

> **Phase dates re-baselined 2026-10-04** (previously Sept–Oct and Nov–Dec). The deliverables themselves are unchanged. ⚠️ **Phase 2 now ends one month after the term below** — see [[Phase 1 Project Plan]] §8.1.

**Division of responsibility:**
- GE Vernova provides the surrogate modeling workloads and application requirements.
- LTI provides the cloud infrastructure and architecture required to support those workloads.

## Timeline & Deliverables
**Phase 1:** [[2026-10 October]] · [[2026-11 November]]
**Phase 2:** [[2026-12 December]] · [[2027-01 January]] · [[2027-02 February]]
*(Mobilization: [[2026-09 September]])*

## Resources (Exhibit A)
Available 40 hrs/week for ML-as-a-Service support work, as directed by Client, excluding approved leave.

| Resource | Role | Number of Months | Actual allocation |
|---|---|---|---|
| [[Nam Park]] | Sr. Cloud Infrastructure Engineer | 5 | **100%** |
| [[Chris Burke]] | Sr. Cloud Infrastructure Engineer | 5 | **50%** (more hours initially) |
| [[Rick Allen]] | Cloud Infrastructure Engineer | — | **50%** (may increase) |

> **Resource substitution and team structure:** the **executed SOW names Earle Flynn** in the second position, and Exhibit A names only **two** resources at 40 hrs/week each. Earle left the engagement on 2026-09-14 and [[Chris Burke]] took the role. The table above shows the current resource; the signed contract is unchanged. Delivery is additionally staffed with [[Rick Allen]] at 50%, per [[LTI Internal Kickoff Brief]] — same ~2.0 FTE nominal, split three ways. Confirm with Michael Russo whether the substitution and the three-person structure need documenting against Exhibit A — tracked in [[Risks & Open Questions]].

## Hours of Service, Travel & Expenses
- Normal business hours, Monday–Friday.
- Work should not exceed 40 hrs/week per person; overtime counted as "flex-time" (taken as vacation/saved time).
- Travel requiring reimbursement needs Client pre-approval + estimated expense as part of travel authorization.
- Agency invoices Client once per calendar month for actual, approved travel/living expenses.

## Out of Scope Work (Change Process)
1. Client submits a written change proposal to Agency.
2. Agency responds in writing within **14 days**, covering resource availability and impact on price/timeline/scope.
3. Any approved change is documented as a **Work Scope Amendment**, signed by both parties.
4. If Agency doesn't approve the amendment, Agency is not obligated to perform the additional work.

> See [[Decisions Log]] and [[Risks & Open Questions]] for tracking anything that might need a Work Scope Amendment.

## Term & Termination
- **Term:** 2026-08-12 → **2027-01-30** per the executed contract. At expiry, both parties evaluate work completed and decide whether a new SOW is needed.

- Either party may terminate with **30 days' written notice**, specifying the effective termination date.
- On termination, both parties cooperate in good faith to wind down and complete outstanding deliverables/transition activities.
- Termination doesn't relieve either party of obligations/liabilities accrued before the termination date.

> ⚠️ **Term vs. Phase 2 mismatch.** Phase 2 runs through **February 2027**, a month past this term end. [[LTI Internal Kickoff Brief]] §4 describes "the current contract period, which runs through February," which suggests the term has moved and this record is behind. **Confirm the actual term end and update this line.** If it really is 2027-01-30, an extension or follow-on SOW must be signed during January — tracked in [[2027-01 January]] and [[Risks & Open Questions]].


## Exclusions
- Scheduling/queuing software is **not** included in the initial static environment. Researchers self-manage job scheduling.
