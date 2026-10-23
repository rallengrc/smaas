---
title: Surrogate ML Accelerator — Electrification
description: Domain background and computational workflow analysis for GE Vernova wind blade and electrification surrogate models
keywords:
- surrogate modeling
- ML accelerator
- electrification
- CFD
- Ansys CFX
- wind blade
- GE Vernova
tags:
- architecture
- stakeholder
- funding
category: architecture
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- surrogate ml accelerator
- electrification ml
- wind blade surrogate model
- ansys cfx ml
source: Surrogate ML Accelerator - Electrification Project.pptx
shared: 2026-10-06
shared-by: Mike Russo
---

# Surrogate ML Accelerator — Electrification Project

> **TL;DR:** Domain overview of surrogate ML workflows that replace expensive CFD/Ansys simulations with accelerated deep learning models.
> **Use this for:** Understanding the scientific and machine learning workloads running on the GPU infrastructure.

Parsed from `Surrogate ML Accelerator - Electrification Project.pptx`, shared by **Mike Russo at the GE kickoff on 2026-10-06**.

**This is the business case, funding vehicle, and target application architecture sitting above [[SOW - Burstable MLaaS|our SOW]].** It is the first time the vault has seen who is paying, what the hardware actually is, and what the application layer is meant to look like. Several of its facts **contradict** what [[Phase 1 Project Plan]] and [[LTI Internal Kickoff Brief]] currently assume — see §4.

Slide 3 is the same Quantum Black EKS diagram already parsed as [[QB Application-Level Architecture (EKS)]]; slide 2 is a Confluence link. Both are redundant.

---

## 1. What it is trying to achieve

> **Objective (verbatim):** "Bring burstable ML/GPU dense compute capabilities to **GEVAR** leveraging the AWS cloud — building a scalable solution which can be leveraged as a surrogate model accelerator for the **Electrification business**."

The "surrogate in a box" vision from [[2026-07-30 Discovery Meeting]] has found its **first paying business unit: Electrification.** That reframes the engagement:

- ARC/GEVAR is building the shared capability.
- **Electrification is the first customer and the funding source** — "Paid for by Electrification 2026 Program $'s."
- The deliverable the business cares about is a *surrogate model accelerator* — faster design iteration on airfoils and turbine blades — not "a GPU environment."

This is the demand signal behind our infrastructure work. It also explains the urgency: the money is 2026 program money.

## 2. Current state (slide 1)

### Infrastructure
- **(4) p5.48xlarge — 32 GPUs** — deployed in an AWS account **hosted in the GEV ENT MasterPayer / Org**, with all security/compliance controls in place, "like QB set up."
- Paid for by **Electrification 2026 Program** funds.
- Leveraging the **QB design as reference architecture**, plus an understanding of how the business uses the on-prem environment today, to design and build the cloud environment for Electrification's needs.
- **ENG engagement open with CTO/HQ** to work with their Solution Architecture team — required for **GWD**, via the process called **"Base."**
- **ServiceNow record** required for "Business App."
- **Discussion with AWS underway to secure P5 instances** in the planned account.

### Teams
| Group | People |
|---|---|
| **ARC DT** | **Mike Russo** — Sponsor / Block Breaker · **Todd Shirback** — Project Manager · **Dave Garber** — On-prem ↔ Cloud · [[Nam Park]], [[Rick Allen]], [[Chris Burke]] — Cloud Engineers *(all marked "TBD")* |
| **Researchers / Business** | **Jim Tallman** · **Deepak Akhare** · **Priyesh Kakka** |

> Two new researcher names — **Deepak Akhare** and **Priyesh Kakka** — join Jim Tallman. The SOW's "approximately four ARC researchers" now has three named people against it.
>
> The spelling here is **"Shirback"**, matching the 2026-08-11 email signature and settling the Shirbak/Shirback question left open by [[LTI Internal Kickoff Brief]].
>
> All three LTI engineers are listed "TBD" — read as allocation/assignment not yet locked on the client side, consistent with the 100/50/50 split in the kickoff brief.

### Next steps (as listed)
- Kick-off call with **Jim / the business for intake** — *note: still pending as of this deck*
- **Secure funding from the business** for the GPU servers — *not yet secured*
- **Land servers** in the destination account
- Get **Nam and Rick AERO badges** to work at **1RC** (part-time)
- **Design of MVP for Jim, to GWD**
- Meetings with CTO/HQ SA/ENG to get **Git pipelines set up for IaC deployments**

## 3. Target application architecture (slide 4)

A McKinsey-authored, "ILLUSTRATIVE" view of the **DLS** stack. This is the *application* target — the layer above our infrastructure — and it is **materially different from [[QB Application-Level Architecture (EKS)]]** in several components.

| Layer | Components |
|---|---|
| **Source data systems** | **Ansys CFX** — aerodynamics models of 2D airfoils and 3D turbine blades · **Dassault Systèmes SimPack** — iterative load and mass analysis of blades against external conditions · **LoopMaster** — internal solver engine for system optimization · **Polar Engine** — ~4,800 sets of polar data for experimentally-tested airfoils. *(A footnote marks one of these "to be deprecated.")* |
| **Data ingestion** | **PyVista** (open source, ingests open 3D datasets) · **proprietary connectors** for enterprise formats |
| **Analytics** | **DLS Models** — predict physics using AI (NVIDIA) · **Design Modules** — generate geometries programmatically (Blender) · **Optimization** — iteratively improve design through genetic evolution |
| **Serving** | **FastAPI** REST APIs · **Keycloak** auth *(shown greyed out)* |
| **Orchestration & observability** | **Flyte** — orchestrate workflows and tasks · **Dask** — distribute data and jobs · **MLflow** — manage experiments |
| **Platform** | K8s Service · Container Registry · Blob Storage · **GPU Nodepool** |
| **DevOps** | **GitHub** — version control and CI/CD · **Helm + Terraform** — infrastructure as code |
| **Technical users** | DLS DS (data scientist) · DLS DE (data engineer) · DLS Infra |
| **Consumption** | **React** and **Streamlit** client-facing apps and APIs → Leadership, Clients |

**Our scope is the bottom two rows.** Platform (K8s, registry, storage, GPU node pool) and DevOps (Git, IaC) are infrastructure. Everything above — ingestion, analytics, serving, orchestration — is the application layer that Jim Tallman's team owns, and that [[Phase 1 Project Plan]] §2.3 says we may be asked to *deploy and support*.

**Note the vocabulary:** "K8s Service," "Container Registry," **"Blob Storage"** are cloud-agnostic (and Azure-flavoured) labels, not AWS service names. Treat this diagram as a logical reference, not an AWS design — the AWS mapping is [[QB Reference Architecture]] and [[QB Application-Level Architecture (EKS)]].

---

## 4. Conflicts with what our plan currently assumes

**These are the reason this deck matters.** Each needs resolving before the affected work starts.

| Item | [[SOW - Burstable MLaaS]] / [[Phase 1 Project Plan]] | This deck |
|---|---|---|
| **Hardware** | **3 servers, 24 total GPUs** (D1, verbatim SOW deliverable) | **4 × p5.48xlarge, 32 GPUs** (H100) |
| **Account placement** | "Dedicated account, standalone, **no integration** with the GEV Enterprise Master Payer account" ([[LTI Internal Kickoff Brief]] §5) | Account **hosted in the GEV ENT MasterPayer / Org**, QB-style security and compliance controls |
| **Who pays** | Open question — "monthly GPU budget" unresolved | **Electrification 2026 Program** — and funding is listed as *not yet secured* |
| **Backend** | ~~Java Spring~~ — **DT4D's stack, not this project's** *(clarified 2026-10-19)*; recorded at the [[2026-07-30 Discovery Meeting]] | **FastAPI** (Python) |
| **Distributed compute** | **Ray / KubeRay** ([[EKS Platform Replication Plan]] Layer E) | **Dask** |
| **Orchestrator** | "Argo Workflows and/or Flyte — pick one" | **Flyte** |
| **Experiment tracking** | Not mentioned | **MLflow** |
| **Frontend** | React | **React + Streamlit** |
| **Horizon** | SOW runs Oct 2026 – Feb 2027 (5 months) | GPU costs modelled over **15 months** |
| **Beneficiary** | "~4 ARC researchers" | **Electrification business**; 3 named researchers |

### New dependencies not currently in our plan
- **GWD via the CTO/HQ "Base" process** — a formal architecture review gate with a Solution Architecture team outside ARC. An **MVP design for Jim must go through it.**
- **ServiceNow "Business App" record.**
- **Git pipelines for IaC deployments must be set up with CTO/HQ SA/ENG** — so CI/CD is both partly in our scope *and* gated on another team's schedule.
- **AERO badges for Nam and Rick** to work on-site at **1RC**, part-time. This is a physical-access requirement **on top of** VNDLY onboarding, with its own lead time.
- **AWS capacity negotiation for P5 instances** is already in progress — confirming the GPU-capacity risk in [[Phase 1 Project Plan]] is real, and that someone is working it.

---

## 5. Cost (slide 5) — answers our open GPU budget question

Two options for **4 servers / 32 H100 GPUs**, both with a **24% GEV customer discount**:

| | Structure | Total |
|---|---|---|
| **Option 1** | On-demand for 15 months, billed quarterly | **$1,832,171.52** |
| **Option 2** | 12-month all-up-front + 3 months on-demand | **$1,228,287.79** |
| | **Option 2 saving** | **$603,883.73** |

Working figures:
- On-demand list: **$40,179.20 per server per month** → **$30,536.19** after discount
- On-demand run rate: **~$122,145 / month** for all 4 servers · **$366,434.30 / quarter**
- 12-month all-up-front: $1,134,017.74 list → **$861,853.48** after discount ≈ **$71,821 / month equivalent**

> **This corrects [[Phase 1 Project Plan]] §WS2**, which estimated "tens of thousands of dollars per month." The real on-demand figure is **~$122k/month** — the plan assumed 3 servers of unspecified family; this is 4 servers of the most expensive family (H100).
>
> **The 15-month horizon is a signal.** The SOW runs five months, to February 2027. The hardware is being costed to roughly January 2028 — consistent with Michael Russo's stated intent for this to become a production environment, and relevant to the renewal tracked in [[Risks & Open Questions]].

---

## 6. What to do about it

1. **Resolve 3×24 vs 4×32 before ordering anything.** The SOW deliverable D1 says three servers and 24 GPUs; the funded plan says four and 32. Either D1 is superseded or the deck is aspirational. This changes quota requests, capacity reservations, cost, and the D7 multi-GPU demo design.
2. **Correct the account-placement note.** The environment sits *inside* the GEV ENT MasterPayer Org — a dedicated account within it, with QB-equivalent controls. "Standalone with no integration" was a misreading of the kickoff brief and should not drive the landing-zone design.
3. **Instance family is effectively decided: p5.48xlarge (8× H100).** Confirm it against Alpharetta parity anyway — [[Phase 1 Project Plan]] §WS2 flags that a GPU-generation mismatch affects D7's "equivalent training" claim, and H100 is several generations newer than much on-prem hardware.
4. **Raise the funding status.** "Secure funding from business for GPU servers" is an open next step. We cannot land servers we have no budget approval for, and it blocks D1.
5. **Add GWD, ServiceNow, Git-pipeline, and AERO badge items to the plan** as external dependencies with their own lead times.
6. **Take the FastAPI / Dask / Flyte / MLflow stack as the current application target** when sizing what "deploy and support their application" means ([[Phase 1 Project Plan]] §2.3) — it is a Python stack, not the Java Spring one every earlier document assumed.

## Related
- [[Phase 1 Project Plan]] · [[LTI Internal Kickoff Brief]]
- [[QB Application-Level Architecture (EKS)]] · [[QB Reference Architecture]] · [[EKS Platform Replication Plan]]
- [[Build Analysis - Target Platform on AWS]]
- [[GE Vernova ARC]] · [[Risks & Open Questions]] · [[Decisions Log]]
