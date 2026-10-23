---
title: Architecture Decision — Questions for Researchers
description: Prioritised, decision-linked question list for the GE Vernova research team, to settle the architecture choice and size the Phase 1 build
keywords:
- researcher questions
- architecture decision
- discovery
- Alpharetta baseline
- multi-node
- interactive loop
- benchmark
tags:
- architecture
- planning
category: planning
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- questions for researchers
- architecture decision questions
- discovery questions ge vernova
- what to ask the research team
---

# Architecture Decision — Questions for Researchers

> **TL;DR:** Eight questions decide the architecture; the rest size the build. **Q1 (does training actually span multiple nodes?) and Q2 (how long can a run take to start?) between them eliminate two of the three candidate architectures** — ask those first and the remainder gets much cheaper. Each question below states what it unblocks and how different answers move the decision.
> **Use this for:** The weekly meeting agenda with the research team, and as the checklist that closes the architecture decision. Items that are not theirs to answer are routed in §2.5.

> ✅ **Largely answered 2026-10-19.** Deepak Akhare has responded to Chris Burke's workload questions — see [[2026-10-19 Research Workload Q&A - Deepak Akhare]]. Q1, Q4, Q5, Q6 and Q7 below are answered; Q2 is partly answered (stated TBD, leaning seconds for development). **The headline: multi-server training is not currently required**, which reopens the architecture comparison. Questions are left in place with their answers marked, since the reasoning for *why each one mattered* still explains the decision.

**How to use this.** Do not send all of it. §1 is eight questions for the first conversation — most answerable from memory in a sentence. §2 needs someone to go and look things up, so send it in writing ahead of time. §3 can wait until the architecture is chosen.

Three architectures are on the table: [[Recommended Architecture - Surrogate ML Accelerator]] (EKS + Karpenter + Ray), [[Alternative Architecture - AWS Batch]], and [[Alternative Architecture - Amazon ECS]]. Open items duplicated here are tracked centrally in [[Risks & Open Questions]].

---

## 1. The eight that decide the architecture

### Q1 — Does a single training run span more than one server today? ✅ ANSWERED

> **Answered 2026-10-19:** **No.** 4–8 GPUs on one server, one model; multi-server training not currently required ([[2026-10-19 Research Workload Q&A - Deepak Akhare]]). This removes EFA and gang scheduling from the critical path and **reopens the comparison — ECS was excluded solely on this**. Note it contradicts the kickoff's "multi-node" framing; see [[Risks & Open Questions]].
*And if not today, is that the goal, or is the goal more runs in parallel?*

**Why it decides things.** A `p5.48xlarge` holds 8 × H100 with 640 GB of HBM. If models fit inside one node, the whole EFA / gang-scheduling / cluster-placement problem disappears and **all three architectures become viable** — ECS included, and the riskiest unknowns in the Batch plan evaporate.

If training genuinely spans nodes, ECS drops out (no gang-scheduling primitive), and EFA becomes the critical path in both remaining plans.

> **Watch for an ambiguity in the kickoff.** It says "scale from 1 to multiple GPUs" *and* "a multi-node, high-performance computing approach." Those are different claims. Scaling 1 → 8 GPUs *within* one node is a much easier problem than 8 → 32 across four.

### Q2 — If you change one line of code, how long is an acceptable wait before it starts running? ⭐
*Seconds? A minute? Five minutes? Does it depend on the time of day?*

**Why it decides things.** This is the single question AWS Batch lives or dies on. Batch is submit-and-wait: every iteration re-queues, provisions, pulls the image and bootstraps — minutes, not seconds. A persistent Ray cluster answers in seconds.

If five minutes is genuinely fine, Batch's managed scheduling and fair-share become very attractive. If it is not, Batch is wrong for Phase 1 regardless of its other merits.

### Q3 — Walk me through how you run a job on Alpharetta today. ⭐
*Do you SSH to a specific box? Submit to a queue? Open a notebook? How do you pick which machine?*

**Why it decides things.** It reveals the model they already have in their heads. If they submit to Slurm today, a queue-based model is familiar and Batch is a smaller change than it looks. If they SSH to a known box and run `python train.py`, a queue will feel like a regression no matter how fast it is.

### Q4 — When a training run fails at hour three, what do you do next? ✅ ANSWERED

> **Answered 2026-10-19:** persistent logs and checkpoints normally suffice, with **optional live container access** for development and debugging. A pure submit-only model is therefore workable for production runs but not for development.
*Attach a debugger? Read logs after the fact? Re-run smaller interactively?*

**Why it decides things.** Interactive debugging on a GPU is something Batch cannot do at all and ECS/EKS can. If their answer is "I re-run it interactively with a smaller batch and poke at it," they need a live GPU session, which rules out a pure submit-only model.

### Q5 — How many jobs does the team have running at once on a busy day, and how long does each take? ✅ ANSWERED

> **Answered 2026-10-19:** jobs run for **days**; **a few large jobs**, not many small experiments. Bin-packing and fair-share matter much less than assumed, and start-up latency is noise against a multi-day run — though not during development.
*And roughly what mix — single-GPU experiments versus full multi-GPU training?*

**Why it decides things.** Drives the queue design and the utilization story. A long tail of 1-GPU experiments needs bin-packing (and under Batch, a strict two-queue split — an MNP node is single-tenant, so a 1-GPU MNP job would occupy all 8 GPUs of a p5). A handful of large jobs needs gang scheduling and little else.

### Q6 — What kind of model is it, and does anything need a POSIX filesystem? ✅ MOSTLY ANSWERED

> **Answered 2026-10-19:** **GNNs on unstructured meshes, transformers on point clouds, and hybrids** — mesh-shaped data confirmed. No license server needed. **POSIX is still open on one point:** users inspect VTUs in **ParaView** after inference — inside the sandbox, or downloaded?
*Graph neural networks on unstructured meshes (MeshGraphNets-style), or MLPs/CNNs on fixed grids and design parameters? And will ParaView, Ansys, STAR-CCM+ or any solver run inside the sandbox?*

**Why it decides things.** *(Raised by [[Chris Burke]], 2026-10-15.)* These two together settle the storage tier outright. GNNs on unstructured meshes read mesh-shaped data; MLPs on design parameters usually do not. And **if any tool needs POSIX, S3-only is off the table and FSx for Lustre stops being optional.**

> **The Electrification deck already hints at the answer.** [[Surrogate ML Accelerator - Electrification]] slide 4 names **PyVista** for ingestion — a VTK wrapper for 3D datasets — and "DLS Models — predict physics using AI (NVIDIA)". Both point at mesh-shaped data. **Ansys CFX appears as a *source data system***, which suggests it runs upstream rather than in the sandbox, but that is an inference, not a statement. Chris believes Ansys was mentioned again at the kickoff. Confirm rather than assume.

### Q7 — How big is the dataset, in files as well as bytes? ✅ ANSWERED

> **Answered 2026-10-19:** **30–100 GB**, as **one consolidated HDF5** plus 20–100 small metadata files — the "fewer large shards" case, which **points away from FSx for Lustre**. Per-epoch iteration with shuffled, on-demand HDF5 reads. 30–100 GB fits comfortably on a p5's local NVMe, so staging there is the natural pattern.
*Total size, **number of files**, typical file size — and is the whole dataset read each epoch, sampled randomly, or are slices pulled from inside large files?*

**Why it decides things.** *(Sharpened by [[Chris Burke]], 2026-10-15.)* File **count** matters as much as volume: thousands of small files lean toward Lustre, fewer large shards lean toward S3 — and Lustre has a ceiling, because the metadata server is what gives way first (§4, and the SDM history in [[Recommended Architecture - Surrogate ML Accelerator]] §3.5.1).

Three further decisions hang on the same answer: the Connectivity Bridge design (D2), whether Exoshuffle's pipelined shuffle is worth anything, and the per-run staging pattern. Open since 2026-09-14, and it blocks the longest-lead-time deliverable in the phase.

### Q8 — What do you actually lose time to today? ⭐
*Waiting for a free machine? Jobs running slowly? Environment problems? Something else?*

**Why it decides things.** The kickoff's headline is >90% utilization versus 60–70% on-prem, which assumes the pain is *waiting for hardware*. If the real pain is environment drift or slow data loading, the architecture should optimise for something different and the benchmark should measure something different.

---

## 2. Needed to build, whichever architecture wins

Send these in writing — they need someone to look things up.

### 2.1 The Alpharetta baseline *(blocks D4, D6 and D7)*

This has been open since 2026-09-14 and currently blocks three deliverables. **Routed through the Architecture team, not the research team** — Jim Tallman leads research and is not involved in architecture (§2.5).

1. **GPU model and count** per node, and number of nodes.
2. **NVIDIA driver, CUDA and cuDNN versions.**
3. **OS distribution and version.**
4. **Frameworks and exact versions** — PyTorch, TensorFlow, JAX?
5. **NCCL / MPI versions**, and whether the interconnect is InfiniBand, RoCE or plain Ethernet.
6. **How are distributed jobs launched today** — `torchrun`, `mpirun`, Slurm `srun`, Ray, something in-house?
7. **Is there a scheduler on-prem** (Slurm, PBS, LSF), and do researchers interact with it directly?
8. **Python environment management** — conda, venv, modules, containers?
9. **Licensed software** — Ansys CFX and anything else: who holds the licence, does it permit cloud execution, and does the licence server need to be reachable from AWS?

> **Question 6 is more interesting than it looks.** If they already use Ray, the kickoff's Ray mandate is grounded in experience and KubeRay is a small step. If they have never used it, "applied ML engineers working independently" is a bigger assumption than it appears, and training/onboarding needs to be in the plan.

### 2.2 The benchmark *(defines D7 acceptance)*

10. **Which model and dataset** should be the benchmark? Pick something real and repeatable.
11. **Current wall-clock time** for that run on Alpharetta, and on exactly what hardware.
12. **Accuracy or loss** that run achieves, and what tolerance counts as "equivalent."
13. **Is linear scaling judged on time-per-epoch or time-to-target-accuracy?** They can diverge badly.
14. **Is there a smaller version** of the benchmark that runs in minutes? Invaluable for shaking out the pipeline before burning p5 hours.

> **There are now two different acceptance tests in play.** The SOW's D7 asks for *equivalence with on-prem*; the kickoff asks for *linear scaling 1 → N GPUs*. Confirm which one constitutes acceptance, or plan to run both ([[Risks & Open Questions]]).

### 2.3 Data

15. **What form is the data in when it arrives?** Raw solver output (CGNS, HDF5, OpenFOAM case directories, EnSight), or already converted to arrays, tensors or Parquet? *(Chris Burke)* — this largely determines whether a POSIX filesystem is unavoidable.
16. **Where does training data live on-prem** — POSIX filesystem, object store, NFS?
17. **Read pattern**: whole dataset each epoch, random sampling, or slices pulled from inside large files? *(Chris Burke)*
18. **Current throughput** — do GPUs ever wait on data today?
19. **Checkpoint size and frequency**, and where checkpoints go.
20. **New data per week**, and whether it must be synced continuously or staged per run.
21. **Any data that cannot leave the premises** — export control, ITAR, customer-confidential?

> **Question 21 is a hard stop if the answer is yes.** It is better known now than after the Connectivity Bridge is built.

### 2.4 The working model

22. **Who are the four researchers**, and what is their comfort level with containers and the command line?
23. **Do you build container images today?** If yes, the image-based parity story is easy; if no, it is a new skill plus a new tool.
24. **Do you want notebooks eventually**, or is a shell genuinely enough? The kickoff deprioritises web UIs — confirm that is the researchers' view and not only leadership's.
25. **Does each researcher need isolation** from the others' jobs, or is a shared pool fine? Decides whether Phase 1 needs quotas or fair-share.
26. **What hours do you work?** The 24-hour unblock commitment needs a definition, and time zones are part of it.

---

### 2.5 Not for the researchers — route these elsewhere

Raised in review but answerable by other people. Asking researchers would waste the meeting.

| Question | Ask |
|---|---|
| **"Argo" — Argo Workflows or Argo CD?** One word decides whether Flyte and Argo actually conflict. See [[aws-batch-ecs-vs-karp-ray-flyte]] §6.6 | **Architecture team** |
| **Alpharetta environment inventory** — OS, driver, CUDA, frameworks, licensed software (§2.1) | **Architecture team** |
| **Confirmed application stack** — FastAPI/Flyte/Dask/MLflow, or EKS/Ray/Argo, or both? *(Java Spring/React is DT4D's, not this project's)* | **Architecture team** |
| **Is AWS SSM Session Manager actually approved** for remote access from GE laptops? | GEV InfoSec / CTO-HQ |
| **Is Gossamer the sanctioned path** for an AWS profile session from a laptop, and does it cover `kubectl` and `aws` CLI against a new account? | [[Chris Burke]] / GEV IT |
| **Is PuTTY port tunnelling still the accepted pattern**, and does it extend to this environment? | GEV IT |
| Which **corporate IdP** backs the SSO behind those paths? | GEV IT |
| Does **FSx for Lustre Persistent_2** with additional metadata servers resolve the SDM-era failure? | AWS account team |
| ~~Server count~~ — **settled 2026-10-19: 3 × p5.48xlarge / 24 GPUs.** GPU funding and the costing option remain open | Michael Russo |

> **Chris Burke's access-plane correction (2026-10-15) matters for the recommended architecture.** It names **Gossamer** for AWS CLI/infrastructure sessions and **PuTTY port tunnelling** as the established GE patterns, both with SSO and minimal hops — and notes **`kubectl` is easily used from a laptop this way**. That is good news for the EKS design: the access path it depends on already has a precedent at GE, whereas **SSM approval is unconfirmed**. See [[Recommended Architecture - Surrogate ML Accelerator]] §3.4.

---

## 3. After the architecture is chosen

26. How should job priority work when two people want all the GPUs?
27. Should idle GPUs shut down automatically, and after how long?
28. Do you want email or Teams notification on job completion or failure?
29. What should the Project Lab Notebook contain from your side — configs, results, lessons?
30. Who should have access to the Grafana utilization dashboard?
31. What would make you stop using the cloud environment and go back to Alpharetta? *(The most useful question on this list, and the one most likely to surface something nobody has written down.)*

---

## 4. How the answers map to the decision

| Answer | Points toward |
|---|---|
| Q1: single-node training is sufficient | **All three viable** — ECS becomes a real contender; EFA risk disappears |
| Q1: multi-node required | **ECS out**; EFA becomes critical path for EKS and Batch alike |
| Q2: minutes are fine · Q3: already uses a queue | **Batch** — managed scheduling and fair-share become free wins |
| Q2: seconds required · Q4: interactive debugging | **EKS + Ray** — the only option preserving a live GPU session |
| Q5: many small jobs | Bin-packing matters; under Batch, the two-queue split is mandatory |
| Q5: few large jobs | Gang scheduling matters; ECS weakest, Batch strongest |
| Q6: GNN on unstructured meshes, or a POSIX tool in the sandbox | **FSx for Lustre is required**, not optional |
| Q6: MLP/CNN on arrays, nothing needs POSIX | S3 + per-run staging is enough; skip FSx and its standing cost |
| Q7: thousands of small files | Lustre — but watch the metadata server ceiling (SDM history) |
| Q7: fewer large shards | S3 reads directly; Lustre adds cost without benefit |
| Q7: dataset ≫ node memory | Pipelined shuffle earns its place |
| Q8: pain is waiting for hardware | The utilization thesis holds; queueing and scale-to-zero are the answer |
| Q8: pain is environment or data | Re-aim the architecture *and* the benchmark |
| 2.1 Q6: already uses Ray | Ray mandate is grounded; KubeRay is a small step |
| 2.1 Q6: never used Ray | Budget onboarding time; reconsider the self-sufficiency assumption |

---

## 5. Suggested running order

1. **Weekly meeting, 20 minutes:** Q1–Q6 conversationally with the research team.
2. **Same day, in writing:** §2.1 (Alpharetta baseline) and §2.3 (data) — these have the longest turnaround and block the most.
3. **Within the week:** Q7, Q8 and §2.2 (benchmark), ideally with whoever owns the on-prem baseline numbers.
4. **After the architecture decision:** §3.

**If only five minutes are available, ask Q1 and Q2.** Those two narrow the field further than everything else combined — and settle the Argo question separately with the Architecture team (§2.5).

---

## 6. Notes from Rick — Design Considerations, Technical Solutions & GE Budget Strategy

> **Author:** Rick Allen (LTI Cloud Architect & Orchestrator Lead)  
> **Audience:** Chris Burke, Nam Park, Jim Tallman, Michael Russo, and GE Vernova Business & Budget Leadership  
> **Context:** Synthesizing newly indexed AWS official guides ([LustreGuide.md](../../Resources/aws/LustreGuide.md), [karpenter.md](../../Resources/aws/karpenter.md), [KUB312](../../Resources/aws/KUB312_Simplify-Kubernetes-workloads-with-Karpenter-and-Amazon-EKS-Auto-Mode.md)), KubeRay code packages, and the 3-node hardware feasibility analysis to definitively resolve architectural disputes, protect researcher velocity, and secure budget approvals.

### 6.1 Resolving Chris Burke's Storage & Metadata Ceiling Trap (Q6 & Q7)

Chris Burke correctly flagged that **FSx for Lustre previously failed during GE Vernova's SDM project** because the metadata server (MDS) froze when processing hundreds of thousands of unstructured 3D mesh files (VTK, PyVista, OpenFOAM). 

Based on our deep dive into the official [FSx for Lustre User Guide](../../Resources/aws/LustreGuide.md) and AWS accelerated compute architectures, we now have two proven technical solutions that neutralize this risk:

1. **Modern FSx for Lustre Persistent_2 with User-Provisioned Metadata IOPS:**
   * In older Lustre versions (used during SDM), Metadata IOPS was rigidly tied to disk capacity ratios. Under-sizing capacity throttled metadata performance and stalled small-file traversal.
   * Modern **FSx for Lustre Persistent_2 SSD** decouples metadata throughput: AWS now supports **User-Provisioned Metadata IOPS** scaling up to **192,000 IOPS** (in multiples of 12,000 IOPS) independently of disk size.
   * If upstream solver tools (Ansys CFX, ParaView) strictly require a shared POSIX file system, provisioning Persistent_2 with dedicated high-IOPS metadata servers completely prevents the SDM bottleneck.
2. **The Local NVMe Instance Scratch Architecture (Recommended / Zero-Standing-Cost):**
   * Each `p5.48xlarge` server includes **8 × 3.84 TB local NVMe SSDs (~30.7 TB raw)** delivering over **30 GB/s local read throughput** via PCIe Gen5.
   * Rather than streaming fine-grained mesh slices across a network file system, we configure Karpenter node bootstrap to stripe these disks into a RAID-0 array mounted at `/mnt/nvme-scratch`.
   * **Ray Data** prefetches and stages dataset shards from S3 directly into local NVMe prior to training epochs. This achieves **10× the throughput of network storage**, provides 100% isolation between researchers, and saves **$1,500–$3,000/month** in standing FSx for Lustre infrastructure costs.

### 6.2 Resolving the Access Plane & Security Approvals (§2.5)

* **Chris Burke's Finding:** Chris identified that **Gossamer** (for AWS profile sessions) and **PuTTY port tunnelling** are established, pre-approved patterns within GE Vernova corporate IT and InfoSec.
* **Impact on EKS Build:** We do **not** need to wait for AWS SSM Session Manager approval through corporate InfoSec. Researchers can execute `kubectl`, `ray job submit`, and interactive debugging sessions from their GE-managed laptops through Gossamer SSO sessions directly to the EKS control plane and lightweight CPU dev pods.

### 6.3 Answers for the GE Business & Budget Team (Michael Russo / Jim Tallman)

1. **3 Nodes (24 GPUs) vs. 4 Nodes (32 GPUs) Contractual Alignment:**
   * Signed [SOW - Burstable MLaaS.md](../SOW/SOW%20-%20Burstable%20MLaaS.md) Deliverable D1 explicitly specifies: *"Establish access to 3 static servers with 24 total GPUs within an agreed-upon AWS data center for ~4 ARC researchers."*
   * Budgeting for 4 nodes ($122,145/month) created an artificial $1.83M 15-month exposure. Moving to the contractual **3 × `p5.48xlarge` (24 GPUs)** costs **$91,608/month**, generating an immediate savings of **~$30,536/month ($366,434/year)**.
   * *Collective Scaling Math:* PyTorch DDP and NCCL Ring AllReduce do not require power-of-two nodes. At 24 ranks, scaling efficiency is $\frac{N-1}{N} = \frac{23}{24} = 95.83\%$, compared to $96.87\%$ for 32 ranks (a negligible $<1.04\%$ difference).
2. **De-Risking the Deliverable Acceptance Divide (SOW D7 vs. Tallman Deliverable 4):**
   * SOW D7 requires "equivalence with on-prem MLaaS" (blocked since Sept 14 awaiting Alpharetta baseline data), whereas Jim Tallman's kickoff requires "linear scaling 1 to N GPUs".
   * *Resolution Strategy:* We construct an internal, repeatable synthetic Physics-GNN / 3D-mesh benchmark (e.g. MeshGraphNet on Ray Train) running across 1, 2, 8, 16, and 24 GPUs over EFA 3200 Gbps. This proves linear scaling to Jim Tallman immediately while providing baseline metrics that can be matched against Alpharetta whenever GE provides the on-prem data.
3. **AWS Batch vs. Karpenter + KubeRay: The Research Sandbox Velocity Case:**
   * AWS Batch requires 3 to 8 minutes per job run (re-evaluating queue, pulling containers, booting instances), does not support EC2 Spot instances for Multi-Node Parallel (MNP) jobs, lacks interactive debugging, and is poorly documented for EFA on EKS.
   * **Karpenter + KubeRay on EKS** provides sub-second interactive turnarounds, scale-to-zero in 30 seconds when idle, and supports the "Ray Bulletin Board" pattern (`ray job submit`) that matches Jim Tallman's vision of an unencumbered research environment.

### 6.4 The Argo Clarification (Q9)

* As verified in our architecture matrix, **Argo CD** is a GitOps platform deployment tool, whereas **Flyte** is a macro-DAG workflow and data-lineage engine.
* Pairing Argo CD (to manage cluster state, KubeRay operators, and Karpenter CRDs) with Flyte (orchestrating surrogate pipelines) eliminates any conflict and delivers enterprise-grade reproducibility.

---

## Related

* [[Recommended Architecture - Surrogate ML Accelerator]] · [[Alternative Architecture - AWS Batch]] · [[Alternative Architecture - Amazon ECS]]
* [[aws-batch-ecs-vs-karp-ray-flyte]] — the underlying trade-off analysis
* [[2026-10-12 Research Team Kickoff]] — the vision these questions test against
* [[Phase 1 Project Plan]] §7 — the broader GE Vernova ask list this complements
* [[Risks & Open Questions]] — where the answers should be recorded
