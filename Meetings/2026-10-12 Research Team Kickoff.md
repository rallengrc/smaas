---
title: 2026-10-12 Research Team Kickoff
description: Jim Tallman's kickoff summary for the Surrogate ML Accelerator, establishing the applied-ML research sandbox strategy, deliverables, and initial action items
keywords:
- research kickoff
- Surrogate ML Accelerator
- Jim Tallman
- linear scaling
- applied ML
- EKS Ray Argo
- lab notebook
tags:
- meeting
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- research kickoff 2026-10-12
- surrogate ml accelerator kickoff
- jim tallman kickoff summary
- applied ml philosophy
date: 2026-10-12
attendees:
- Jim Tallman
- GE Vernova research team
- LTI cloud team
---

# Research Team Kickoff — 2026-10-12

> **TL;DR:** Jim Tallman's kickoff summary establishing the Surrogate ML Accelerator as a high-velocity research sandbox — researchers as "applied ML engineers", linear GPU scaling as the primary proof, and a flat, decentralized support model.
> **Use this for:** The research team's own framing of success, their six named deliverables, and the Day 0 action items.

Source: kickoff summary email from **Jim Tallman**, who leads the GE Vernova research team.

**Attendees:** not enumerated in the summary. Named as owners within it: Jim Tallman, Todd Shirback, Dave Garber, Mike (Russo), and the LTI "Cloud Team".

This is the **research-side** kickoff, distinct from the 2026-10-06 GE kickoff that covered scope and commercial structure (see [[Surrogate ML Accelerator - Electrification]]). It is the first document in which Jim Tallman's team states its own requirements directly rather than having them relayed — see [[GE Vernova ARC]] for his standing role.

> **A weekly recurring meeting is coming**, and a formal plan will follow. The action items below are explicitly interim — "just some initial action items until I get the formal plan in place".

## Core objective
Move from traditional siloed on-prem infrastructure to a cloud-native research sandbox:

- **Utilization: from the 60–70% industry standard on-prem to >90% in the cloud**, eliminating researcher "pend time"
- **Training time: from days to hours**, through linear scaling across multi-node GPU clusters
- A **"bulletin-board" compute architecture** that decouples jobs from specific hardware
- Positioned as a **pilot for a scalable "common job model"** to be blueprinted for the broader GE Vernova organization

## Key takeaways
- **"New future" for research** — a high-velocity sandbox that avoids the pitfalls of past DT4D efforts while keeping the scalable common-job-model vision. See [[2026-07-30 Discovery Meeting]] for the DT4D background.
- **The "applied ML" philosophy** — researchers are empowered as *applied machine learning engineers*. Success means they troubleshoot, configure and scale surrogate models **independently**, without waiting on production ticketing systems or formal deployment queues.
- **Linear scaling is the primary goal** — proving surrogate model training scales linearly across GPU clusters, moving from single-GPU workflows to multi-node HPC.
- **Computational efficiency** — decoupling jobs from hardware to eliminate pend time and beat on-prem utilization rates.
- **Flat, collaborative technical culture** — decentralized problem-solving, with the engineering team as a direct support layer for research. **No blocker should persist beyond 24 hours.**
- **Central learning** — a "Project Lab Notebook" documenting every technical configuration and scaling breakthrough, as a blueprint for enterprise-wide adoption.

## Strategic priorities
1. **Rapid enablement** — immediate, high-performance GPU access for the research team
2. **Scalability validation** — document linear scaling results to justify high-density compute
3. **Infrastructure agility** — **prioritize shell/SSH access over complex web UIs** for rapid iteration
4. **Knowledge capture** — maintain the living Project Lab Notebook

## Deliverables (as stated by the research team)
| # | Deliverable | Notes |
|---|---|---|
| 1 | **Architectural Reference Diagram** | Technical schematic of the **EKS / Ray / Argo** stack requirements, as defined by the research team |
| 2 | **Operational Sandbox Environment** | Fully provisioned high-density GPU environment, accessible via **Shell/SSH** |
| 3 | **Connectivity Bridge** | Secure, high-speed data path from on-prem storage to the sandbox |
| 4 | **Scaling Benchmark Report** | Performance data showing efficiency gain scaling from 1 to multiple GPUs |
| 5 | **Project Lab Notebook** | Central repository of configurations, library dependencies, and lessons learned |
| 6 | **SMaaS Foundation (Phase 2)** | Framework for "Surrogate Modeling as a Service" |

> **These six are a different framing from the SOW's D1–D8**, not a restatement of them. The mapping is approximate and unconfirmed — see [[Risks & Open Questions]].

## Action items (interim, per the summary)
| Action | Owner | Priority | Status / Notes |
|---|---|---|---|
| Provision laptops & accounts (Nam/Rick) | Todd / IT | Critical | **Day 0 blocker** |
| Initial architecture diagram | Cloud Team (LTI) | Critical | — |
| AWS GPU cluster capacity request | Mike (Russo) | Critical | **Single-AZ placement** |
| Finalize on-prem connectivity link | Dave Garber | Critical | — |
| Initiate "Project Lab Notebook" | Todd Shirback | Medium | — |

## What this changes
- **Application stack — a second answer, not a third.** The stack is now stated as **EKS / Ray / Argo**. Ray matches [[EKS Platform Replication Plan]]; **Argo is new**; the deck's Flyte / Dask / MLflow / Streamlit is absent. *(Java Spring / React, recorded at the [[2026-07-30 Discovery Meeting]], was never in contention here — it is DT4D's stack. Clarified 2026-10-19.)* Combined with "shell/SSH over complex web UIs", this suggests the app and frontend tier is **deprioritized for the sandbox** — which, if confirmed, materially shrinks the application-support exposure tracked in [[Risks & Open Questions]].
- **D7's acceptance test may have moved.** The SOW's D7 is *equivalent training* against the Alpharetta on-prem baseline; the research team's proof is *linear scaling from 1 to N GPUs*. These are different tests, and the kickoff still names no model, dataset or baseline metrics.
- **Phase 2 now carries build work.** "SMaaS Foundation (Phase 2) — **development** of the underlying framework" contradicts the 2026-09-14 reading that Phase 2 contains no build work, which was the premise for placing the burst build in D8 ([[Phase 1 Project Plan]] §2.1).
- **Single-AZ placement** is a new, concrete constraint on the GPU capacity request — consistent with placement groups and low-latency interconnect for multi-node training, and a deliberate trade of AZ resilience for performance.
- **A 24-hour blocker SLA** is now the stated support expectation, against an LTI team that is one full-time and two half-time engineers.
- **An immediate LTI deliverable:** the initial architecture diagram is owned by the Cloud Team and marked Critical.

## Open items raised here
- [ ] Is the **Todd** owning laptops and accounts the same **Todd Shirback** who owns the Lab Notebook, or a separate IT owner?
- [ ] The laptop/account action names **Nam and Rick only** — what about [[Chris Burke]]?
- [ ] How do the six research deliverables **map onto the SOW's D1–D8**, and which governs acceptance?
- [ ] How is **>90% utilization** measured, over what window, and who reports it?
- [ ] Does **Argo** mean Argo Workflows, Argo CD, or both?
- [ ] What is the **scope of the 24-hour unblock commitment** — business hours, on-call, and who carries it?

> Tracked in [[Risks & Open Questions]].

## Related
- [[Surrogate ML Accelerator - Electrification]]
- [[Phase 1 Project Plan]]
- [[EKS Platform Replication Plan]]
- [[2026-10 October]]
- [[GE Vernova ARC]]
