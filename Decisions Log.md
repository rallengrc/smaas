---
title: Decisions Log — Burstable MLaaS
description: Chronological record of key architectural, contractual, and technical decisions for Burstable MLaaS
keywords:
- decisions log
- architecture decisions
- ADR
- Burstable MLaaS
- GE Vernova
- governance
tags:
- log
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- decisions log
- project decisions
- architecture choices
- burstable mlaas decisions
---

# Decisions Log

> **TL;DR:** Running decision log tracking technical, infrastructure, and contractual decisions made across the Burstable MLaaS engagement.
> **Use this for:** Reviewing historical context, rationale, and approvals for key project decisions.

Track significant decisions made during the engagement — especially anything that touches contract scope (see [[SOW - Burstable MLaaS]] § Out of Scope Work) or architecture ([[Static AWS GPU Environment]], [[On-Demand MLaaS POC]]).

| Date | Decision | Rationale | Owner |
|---|---|---|---|
| 2026-08-11 | POC run as a defined project deliverable (working AWS environment), not LTI's typical staff-aug/T&M model | Client (Michael Russo) wants a concrete deliverable to evaluate, per [[2026-08-11 Engagement Structure Email]] | Michael Young / Michael Russo |
| 2026-08-11 | Roles split: Jim Tallman's team (GE Vernova) owns app/workload requirements; LTI's cloud engineers own cloud infrastructure only | Clarified in [[2026-08-11 Engagement Structure Email]] | Michael Young / Michael Russo |
| 2026-08-11 | Background checks/drug tests required for all contractors (incl. remote) added to GE's VNDLY system for SSO/environment access | Standard GE Vernova contractor policy, confirmed in [[2026-08-11 Engagement Structure Email]] | Michael Russo |
| 2026-09-14 | Planning proceeds against the updated scope document `SOW - Scope.pdf`: ~~Phase 1 = Sept–Oct 2026, Phase 2 = Nov–Dec 2026~~ — **dates superseded 2026-10-04** (see below); the 8-deliverable Phase 1 scope still stands | Client-supplied updated SOP; supersedes the single-month Phase 1 framing in prior project notes. See [[Phase 1 Project Plan]] | [[Nam Park]] |
| 2026-09-14 | **[[Chris Burke]] replaces Earle Flynn** as the second Sr. Cloud Infrastructure Engineer on the engagement | Earle is no longer a team member. Project docs now name Chris forward-looking; dated records (meeting notes, the 2026-08-11 email, executed Exhibit A) keep Earle's name as a matter of record | [[Nam Park]] |
| 2026-09-14 | Pending confirmation, **D8 is planned as landing zone + a time-boxed burst proof point** — explicitly excluding the app tier, multi-tenancy, platform services, and CI/CD | Phase 2 contains no build work, so the burst build has nowhere else to sit; but the broad reading risks over-commitment in 6.5 weeks. See [[Phase 1 Project Plan]] §2.1 | [[Nam Park]] — **needs Michael Russo's written confirmation** |
| 2026-10-04 | **Phase dates re-baselined:** Phase 1 = **October–November 2026**; Phase 2 = **December 2026–February 2027** | Updated SOW contents supplied by the client. Resolves the mismatch between a 2026-10-06 GE kickoff and a Phase 1 that previously ended 2026-10-31. Deliverables unchanged in both phases | [[Nam Park]] |
| 2026-10-04 | **[[Rick Allen]] joins delivery at 50%**; allocations set to Nam 100% / Chris 50% / Rick 50% | Per [[LTI Internal Kickoff Brief]]. Same ~2.0 FTE nominal as Exhibit A's two resources, split three ways; Rick may increase as his other project winds down | [[Nam Park]] |
| 2026-10-04 | Kickoffs scheduled: **internal Mon 2026-10-05**, **GE Tue 2026-10-06**, both 11:00 ET | Per [[LTI Internal Kickoff Brief]] §6; GE invite sent by Michael Russo | Michael Russo / LTI |
| 2026-10-04 | AWS account shape: **dedicated account for this application only**, standalone, **no integration** with the GE Vernova Enterprise Master Payer account hosting the existing environment | Per [[LTI Internal Kickoff Brief]] §5 — partly resolves the long-open AWS account question | Michael Russo |
| 2026-10-06 | **Electrification is the funding business unit** — the GPU servers are paid from Electrification 2026 Program funds, and the environment is positioned as a surrogate model accelerator for that business | Per [[Surrogate ML Accelerator - Electrification]] slide 1, shared by Mike Russo at the GE kickoff. First concrete customer for the "surrogate in a box" vision | Mike Russo |
| 2026-10-06 | **Instance family effectively decided: p5.48xlarge (8 × H100 80GB)** | Named directly in the Electrification deck; AWS capacity discussions for P5 instances already underway. Still needs checking against Alpharetta parity for D7 | Mike Russo |
| 2026-10-06 | **The AWS account sits inside the GEV ENT MasterPayer Org**, with QB-equivalent security and compliance controls | Corrects the earlier reading of [[LTI Internal Kickoff Brief]] as "standalone, no integration" — that referred to the *existing* environment, not the account hierarchy | Mike Russo |
| 2026-10-06 | **Todd Shirback** confirmed (not "Shirbak"), and he is **Project Manager**. Mike Russo is **Sponsor / Block Breaker**; Dave Garber covers **on-prem ↔ cloud** | Per the deck's team slide, matching the 2026-08-11 email signature | — |
| 2026-10-12 | **The environment is framed as a research sandbox, not a production platform** — researchers operate as "applied ML engineers", configuring and scaling models themselves without production ticketing or formal deployment queues | Per [[2026-10-12 Research Team Kickoff]]. Sets the operating model the infrastructure must support | Jim Tallman |
| 2026-10-12 | **Shell/SSH access is prioritized over web UIs** as a stated strategic priority ("Infrastructure Agility") | Per [[2026-10-12 Research Team Kickoff]] §Strategic Priorities. Consistent with D3's command-line access; newly explicit that rich UI is *not* wanted for the sandbox | Jim Tallman |
| 2026-10-12 | **Stack named as EKS / Ray / Argo** by the research team, who own the architectural requirements | Per [[2026-10-12 Research Team Kickoff]] §Deliverables. Ray matches [[EKS Platform Replication Plan]]; Argo is new. **Does not reconcile** with the deck's FastAPI/Flyte/Dask/MLflow or the earlier Java Spring/React — see Unresolved | Jim Tallman / research team |
| 2026-10-12 | **GPU capacity is to be requested with single-AZ placement** | Per [[2026-10-12 Research Team Kickoff]] action items. Consistent with placement groups and low-latency interconnect for multi-node training; trades AZ resilience for performance | Mike Russo |
| 2026-10-12 | **Primary technical proof is linear scaling from 1 to N GPUs**, with utilization targeted at **>90%** against a 60–70% on-prem baseline, and training time collapsing from days to hours | Per [[2026-10-12 Research Team Kickoff]] §Core Objective. This is the research team's own success definition | Jim Tallman |
| 2026-10-12 | **A "Project Lab Notebook" is established** as a central record of configurations, dependencies and lessons learned, intended as a blueprint for enterprise-wide adoption | Per [[2026-10-12 Research Team Kickoff]]. Owned by Todd Shirback at Medium priority | Todd Shirback |
| 2026-10-19 | **Recommendation re-derived and re-affirmed: EKS + Karpenter + Ray**, now on the grounds of **pipeline unification and the development loop** rather than gang scheduling, EFA or bin-packing — two of which no longer apply | Per [[2026-10-19 Research Workload Q&A - Deepak Akhare]]. The workload is three shapes (CPU preprocessing, single-node multi-GPU training, CPU rendering) and Ray spans all three in one framework. **The margin over AWS Batch is now narrow**, and would tip to Batch if development happens on-prem rather than on AWS. See [[Recommended Architecture - Surrogate ML Accelerator]] §0 | [[Nam Park]] |
| 2026-10-19 | **Workload shape established: single-server training, 4–8 GPUs, one model; multi-server not currently required** | Per Deepak Akhare, [[2026-10-19 Research Workload Q&A - Deepak Akhare]]. Removes EFA, gang scheduling and cluster placement from the Phase 1 critical path, and **reopens the architecture comparison** — ECS was ruled out solely on the gang-scheduling gap | Deepak Akhare / research team |
| 2026-10-19 | **A dedicated CPU tier is a first-class requirement** — 100–200 CPUs for preprocessing, 150 for video generation, 8–16 per GPU for data loading | Per [[2026-10-19 Research Workload Q&A - Deepak Akhare]] §6.2. Running CPU-only rendering on a p5.48xlarge would burn a $30,536/month GPU server on work needing no GPU | [[Nam Park]] |
| 2026-10-19 | **Java Spring / React is DT4D's stack, not this project's.** This engagement reuses DT4D *concepts* only and builds a wholly new cloud architecture for MLaaS | Clarified by [[Nam Park]]. The Java Spring backend and React frontend recorded at the [[2026-07-30 Discovery Meeting]] describe the **predecessor DT4D system**; they were never a candidate stack here. The "three-way application stack contradiction" therefore collapses to a question about the *Python* stack only | [[Nam Park]] |
| 2026-10-19 | **GPU footprint settled: 3 × p5.48xlarge — 24 H100 GPUs total.** Resolves the 3/24 vs 4/32 conflict in favour of the SOW's D1 wording | Decided by GE Vernova. On-demand run rate is now **~$91,609/month** (3 × $30,536.19), not the ~$122k costed for four servers. Quota, capacity reservation and the D7 scaling sweep all size to 24 GPUs | Michael Russo |
| 2026-10-12 | **Support model: flat and decentralized, with no blocker persisting beyond 24 hours**; the engineering team acts as a direct support layer for research | Per [[2026-10-12 Research Team Kickoff]] §Key Takeaways. Scope of the commitment (hours, on-call, owner) is undefined — see [[Risks & Open Questions]] | Jim Tallman |

> **Unresolved:**
> - Whether `SOW - Scope.pdf` supersedes the executed SOW contractually, or requires a signed Work Scope Amendment. See [[Phase 1 Project Plan]] §8.2.
> - **The actual term end.** The executed SOW says 2027-01-30; Phase 2 now runs through February 2027 and [[LTI Internal Kickoff Brief]] §4 says the contract period "runs through February." See [[Phase 1 Project Plan]] §8.1.
> - **Application stack — narrowed 2026-10-19.** Java Spring / React is **out**: it belongs to DT4D, not to this build. What remains is whether the Python tier is the Electrification deck's **FastAPI / Flyte / Dask / MLflow** or the kickoff's **EKS / Ray / Argo** — and those may be complementary rather than competing, since Ray and Argo are compute and orchestration while FastAPI and MLflow are serving and tracking. The kickoff's shell-over-UI priority still suggests the app tier may be out of the sandbox entirely.
> - **Whether the research team's six deliverables or the SOW's D1–D8 govern acceptance**, and how they map. Raised 2026-10-12.
> - **Whether Phase 2 includes build work.** "SMaaS Foundation (Phase 2) — development of the underlying framework" ([[2026-10-12 Research Team Kickoff]]) contradicts the 2026-09-14 premise that Phase 2 contains no build work — the premise that put the burst build in D8.
> - **GPU funding is not yet secured** — "Secure funding from business for GPU Servers" is an open next step in the deck, and it blocks D1.
> - **The application/infrastructure/support boundary**, which the kickoff brief and the earlier role-split analysis describe differently. See [[Phase 1 Project Plan]] §2.3.
