---
title: 2026-10-19 Research Workload Q&A — Deepak Akhare
description: Chris Burke's workload requirements questions to the GE Vernova research team and Deepak Akhare's answers, with the architectural implications
keywords:
- workload requirements
- Deepak Akhare
- GNN
- HDF5
- VTU
- preprocessing
- single-node training
- multi-node
- post-processing
tags:
- meeting
category: planning
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- deepak answers workload questions
- research workload requirements
- single node training confirmed
- hdf5 vtu preprocessing requirements
date: 2026-10-19
attendees:
- Chris Burke
- Deepak Akhare
---

# Research Workload Q&A — 2026-10-19

> **TL;DR:** The research team's **current on-prem workloads**, answered by **Deepak Akhare** — read as today's practice, not a target specification (see the caveat below). Today: **4–8 GPUs on one server**, jobs running **days**, a pipeline that is **heavily CPU-bound outside training** (100–200 CPUs preprocessing, 150 CPUs video), and a dataset of **a few large files** (30–100 GB in one HDF5). The project exists to improve on this, so the architecture should stay **multi-node-capable** even though multi-node is not used today.
> **Use this for:** The requirements basis for the architecture decision, and the source for the answered items now closed in [[Risks & Open Questions]].

**Source:** questions from [[Chris Burke]] to the research team; answers from **Deepak Akhare**, received 2026-10-19. Deepak is one of the ARC researchers named in [[Surrogate ML Accelerator - Electrification]].

> Deepak's framing: *"Below are my initial answers **based on our current workloads**. Some requirements are still evolving, but these should help with initial design decisions."*

> ## ⚠️ Read these as *current on-prem practice*, not as a target specification
>
> **This is the most important caveat in the document.** Deepak describes what the team does today on constrained on-prem hardware. The project exists to build something **better and more efficient** than that — so several answers describe a *limit being worked around*, not a requirement to design to:
>
> * **"Multi-server training is not currently required"** — they do not do it today. [[2026-10-12 Research Team Kickoff]] names multi-node HPC as the destination. Designing single-node-only would bake in the very constraint the project is meant to remove.
> * **"Typical training jobs run for days"** — on today's hardware. The kickoff's explicit goal is **days to hours**. If that succeeds, jobs get shorter and more numerous, which makes the iteration loop and scheduling matter *more*, not less.
> * **"Current implementation uses one writer for consolidated HDF5"** — Deepak flags this as a current implementation detail. A new environment is an opportunity to parallelise it, not a reason to design around it.
> * **"Startup tolerance is TBD"** — they have not had to think about it, because an always-on on-prem box has no start-up.
>
> **The design should serve the destination while not over-building for it.** Where a capability is cheap now and expensive to retrofit — EFA, cluster placement, multi-node readiness — build it in. Where it carries standing cost — FSx for Lustre — defer it until the data actually demands it.

---

## 1. How jobs will run

| Question | Answer |
|---|---|
| Does a run need anything besides its input data — a license server, other running jobs? | **A training container with GPU support. No license-server dependency.** |
| What scale do the biggest runs need? | **4–8 GPUs on one server, training one model**, with **8–16 CPUs per GPU** for data loading and preparation. Future scope includes multiple independent runs. **Multi-server training is not currently required.** |
| What start-up wait is acceptable? | **TBD.** If development happens on AWS, **start-up within seconds would be preferable.** |
| On failure, are logs enough, or do you need inside the running job? | **Persistent logs and checkpoints normally suffice**, with **optional live container access** for development and debugging. |
| Typical job duration, and job mix? | **Days.** A few large jobs rather than many small experiments. |

## 2. Pipeline

Preprocessing **must finish** generating data before training starts. Training produces **intermediate checkpoints that post-processing can consume while training continues**. Video generation follows completed inference outputs.

## 3. Preprocessing

| Question | Answer |
|---|---|
| What does it do? | Processes roughly **5,000–10,000 VTU files** — extracts geometry and physical fields, generates point clouds, writes **HDF5** plus statistics and metadata. Uses **100–200 CPUs** to accelerate. |
| Once per dataset, or every training run? | **Once per dataset/configuration**, reused across multiple training runs. |
| Can each case be processed independently? | Largely yes — parallel across timesteps and simulation cases. **But the current implementation uses a single writer for the consolidated HDF5 output, followed by global statistics aggregation.** Not every stage parallelises. |
| On-prem or in AWS? | **TBD.** |

## 4. Training data and models

| Question | Answer |
|---|---|
| Form on arrival? | **HDF5**, with JSON metadata/statistics and split files. **Raw VTUs would also need uploading if preprocessing moves to AWS.** |
| Model types? | **Graph neural networks on unstructured meshes, transformers on point clouds, and hybrid graph/transformer models.** |
| Dataset size, file count, file size? | **30–100 GB.** **One consolidated HDF5 file per dataset**, plus roughly **20–100 smaller metadata files**. |
| Read pattern? | Iterate over the data each epoch, **shuffling simulation order and reading HDF5 on demand** — not loading everything into RAM. MGTrans loads a **complete simulation trajectory at a time**, so memory depends on trajectory size and worker count. |

## 5. Post-processing

Two stages:

1. **Inference** — run the trained model on test cases **using GPUs**; export predicted VTUs, error metrics and 1D plots. Users then inspect VTUs in **ParaView**.
2. **Video generation** — read inference VTUs, produce videos and PowerPoint slides. **CPU-only, headless rendering; the current job requests 150 CPUs.**

Outputs from **many runs** are processed together. Inference needs **one GPU per concurrently processed case**. RAM and GPU-memory requirements are still to be measured.

---

## 6. What this changes

### 6.1 Multi-server training is not used *today* — what that does and does not change

This is **Q1** of [[Architecture Decision - Questions for Researchers]]. It describes present practice on constrained hardware, so it changes the **Phase 1 demonstration** without changing the **target architecture**:

* **What changes:** EFA and multi-node collectives move off the Phase 1 *critical path*. They no longer gate the benchmark, which removes the largest schedule risk from both the Karpenter and Batch plans — including the Batch plan's week-3 EFA spike, which could have forced a mid-phase pivot.
* **What does not change:** the architecture should remain **multi-node-capable**. EFA, a cluster placement group and a single-AZ GPU subnet are near-free to include now and costly to retrofit, and [[2026-10-12 Research Team Kickoff]] names multi-node HPC as the destination.
* **ECS is still the weakest fit.** Its gang-scheduling gap stops blocking *today's* workload, but it cannot grow into the multi-node destination without self-managed capacity on an undocumented EFA path — and it satisfies none of EKS / Ray / Argo.
* **The Phase 1 demonstration reframes** to **1 → 8 GPUs within one node**, with multi-node as a Phase 2 proof once a workload exists that needs it.

> **This is not a contradiction with the kickoff — it is present versus destination.** [[2026-10-12 Research Team Kickoff]] states a *"multi-node, high-performance computing approach"* and training that scales across GPU **clusters**. Deepak says multi-server training is not *currently* required. Both are true: Jim describes where the research is going, Deepak where it is today. **The architecture should therefore stay multi-node-capable** — EFA, cluster placement and a single-AZ GPU subnet cost nothing now and are expensive to retrofit. What still needs settling is narrower: **what the Scaling Benchmark Report measures in Phase 1** — 1 → 8 GPUs within a node is demonstrable today; 1 → 24 across three requires a workload that does not yet exist. Tracked in [[Risks & Open Questions]].

### 6.2 The pipeline is CPU-heavy outside training

The GPU-centric framing of the project understates the compute profile:

| Stage | Requirement |
|---|---|
| Training data loading | **8–16 CPUs per GPU** → 32–128 CPUs alongside a training run |
| Preprocessing | **100–200 CPUs** |
| Video generation | **150 CPUs**, CPU-only headless rendering |

**A separate CPU tier is now a first-class requirement, not an afterthought.** Running 150 CPUs of headless video rendering on a `p5.48xlarge` would consume a $30,536/month GPU server for work that needs no GPU at all. This is exactly the niche flagged in [[Alternative Architecture - Amazon ECS]] §8 and [[Alternative Architecture - AWS Batch]] §8 — and it is larger than either document assumed.

### 6.3 The data path simplifies — FSx for Lustre is probably unnecessary

Against [[Chris Burke]]'s criterion (2026-10-15), the answers point away from Lustre:

* **30–100 GB per dataset**, as **one consolidated HDF5** plus 20–100 small metadata files. This is the "fewer large shards" case, not the "thousands of small files" case that pressures a metadata server — the failure mode seen on SDM.
* **30–100 GB fits comfortably on a `p5.48xlarge`'s ~30 TB of local NVMe.** The natural pattern is **stage the HDF5 to local NVMe at job start and read from there**, which is faster than any network filesystem and removes a standing cost.
* **Raw VTU input is a different shape** — 5,000–10,000 files. If preprocessing runs in AWS, that volume lands in S3 and is read once per dataset, which S3 handles well.
* **One genuine shared-artifact requirement:** post-processing reads training checkpoints **while training is still running**. S3 serves this; it does not require POSIX.

**ParaView remains the open POSIX question.** Users inspect VTUs in ParaView after inference — if that happens inside the sandbox, a POSIX filesystem is needed; if VTUs are downloaded, it is not.

### 6.4 Days-long jobs change the utilization argument — but only for today

> **The kickoff's stated goal is to collapse training "from days to hours."** If the new environment succeeds, jobs become shorter and more numerous, and everything below inverts: iteration latency, queue behaviour and bin-packing all start to matter again. Design for the shorter-job future; do not optimise for the current duration.

A handful of multi-day jobs on three servers behaves nothing like a queue of short experiments:

* **Bin-packing and fair-share matter much less.** Queue depth will usually be zero or one.
* **Start-up latency matters much less for production training** — five minutes against a three-day run is noise. It still matters for **development**, which is where Deepak asks for seconds.
* **Scale-to-zero has fewer opportunities to fire** while a multi-day job holds a node.
* **>90% utilization becomes easier to achieve and less meaningful as a differentiator** — a few long jobs naturally produce high allocation.

### 6.5 Answers that close open items

| Previously open | Now |
|---|---|
| Does training span multiple servers? | **No, not currently** (§1) |
| Model type — GNN on unstructured meshes? | **Yes**, plus point-cloud transformers and hybrids (§4) |
| Dataset size and file count | **30–100 GB; one large HDF5 + 20–100 small files** (§4) |
| Read pattern | **Per-epoch iteration, shuffled, on-demand HDF5 reads** (§4) |
| Does a run need a license server? | **No** (§1) |
| Job duration and mix | **Days; a few large jobs** (§1) |
| Do jobs read each other's artifacts mid-flight? | **Yes — post-processing reads checkpoints during training** (§2) |

### 6.6 Still open

* **Start-up tolerance** — stated TBD, leaning seconds for development.
* **Preprocessing location** — on-prem or AWS. Decides whether 5,000–10,000 VTUs must be uploaded.
* **ParaView in the sandbox?** Decides whether POSIX is required (§6.3).
* **RAM and GPU-memory for inference and video generation** — not yet measured.
* **Multi-node: destination or non-requirement?** The kickoff and these answers disagree (§6.1).

---

## Related

* [[Architecture Decision - Questions for Researchers]] — the question set these answers close
* [[2026-10-12 Research Team Kickoff]] — Jim Tallman's framing, which §6.1 contradicts on multi-node
* [[Recommended Architecture - Surrogate ML Accelerator]] · [[Alternative Architecture - AWS Batch]] · [[Alternative Architecture - Amazon ECS]]
* [[Risks & Open Questions]] · [[Decisions Log]]
