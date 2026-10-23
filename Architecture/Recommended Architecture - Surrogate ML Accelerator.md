---
title: Recommended Architecture — Surrogate ML Accelerator
description: Recommended tooling and architecture for the GE Vernova research sandbox, derived from the 2026-10-12 research kickoff vision, scope, and deliverables
keywords:
- recommended architecture
- Surrogate ML Accelerator
- EKS
- Ray
- KubeRay
- Karpenter
- Argo
- EFA
- FSx for Lustre
- linear scaling
- GPU utilization
tags:
- architecture
- recommendation
category: architecture
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- recommended architecture
- what stack should we build
- surrogate ml accelerator architecture
- sandbox architecture recommendation
- eks ray argo design
---

# Recommended Architecture — Surrogate ML Accelerator

> **TL;DR:** Build **one EKS cluster** carrying both a **CPU node pool** and a **GPU node pool**, Karpenter-managed against a 3-node reservation, with **Ray spanning the whole pipeline** — parallel preprocessing, single-node multi-GPU training, and parallel inference and rendering. Data stages from S3 to instance-store NVMe; FSx for Lustre is not needed. **§0 carries the revised reasoning**: after the 19 October workload answers, the case rests on pipeline unification and the development loop rather than on gang scheduling, and the margin over AWS Batch is narrow.
> **Use this for:** The Architectural Reference Diagram deliverable, the build sequence for Phase 1, and the decision list that must close before provisioning.

> ⚠️ **Requirements update, 2026-10-19.** [[2026-10-19 Research Workload Q&A - Deepak Akhare]] establishes that **multi-server training is not currently required** (4–8 GPUs on one server), that jobs run for **days**, that the pipeline needs a **substantial CPU tier** (100–200 CPUs preprocessing, 150 for video), and that the dataset is **30–100 GB in one HDF5**. Three consequences for this design: EFA and gang scheduling leave the critical path, **FSx for Lustre is probably unnecessary** in favour of staging to local NVMe (§3.5.1), and a **CPU node pool is now a first-class component** that §2 does not yet carry. The comparison in §6 is reopened — ECS was excluded on the gang-scheduling gap alone.

**Status: recommendation, not committed scope.** This responds to the [[2026-10-12 Research Team Kickoff]] and should be read against [[Phase 1 Project Plan]] and [[Risks & Open Questions]]. §8 lists what must be decided before anything is provisioned, and §6.6 flags where this design exceeds the SOW's literal Phase 1 wording.

---

## 0. Revised recommendation — 19 October 2026

**The recommendation stands: build on EKS + Karpenter + Ray — and the case is stronger, not weaker, once the new requirements are read correctly.**

> ### The framing that matters
>
> [[2026-10-19 Research Workload Q&A - Deepak Akhare]] describes **what the research team does today on constrained on-prem hardware** — not a specification for what to build. The project exists to give them something **better and more efficient**. Several answers therefore describe a *limit being worked around*:
>
> * *"Multi-server training is not currently required"* — because they cannot do it today. The kickoff names multi-node HPC as the destination.
> * *"Typical training jobs run for days"* — on today's hardware. **The kickoff's goal is days to hours.** If that succeeds, jobs become shorter and more numerous, and iteration latency matters **more**, not less.
> * *"One writer for the consolidated HDF5"* — Deepak flags this as a current implementation detail, not a constraint to design around.
>
> **Design for the destination without over-building for it.** Capabilities that are near-free now and costly to retrofit — EFA, cluster placement, multi-node readiness — go in. Capabilities with standing cost — FSx for Lustre — wait until the data demands them.

### 0.0 The dual mandate

Phase 1 has to satisfy two obligations at once, and they pull in different directions:

| Obligation | What it demands |
|---|---|
| **Support the work they do today** | Their existing pipeline must run **unchanged** on day one — the same HDF5, the same container, the same scripts. If researchers have to rewrite anything to get started, adoption stalls and the 24-hour unblock commitment becomes a support queue. |
| **Be demonstrably better than on-prem** | The project is not a lift-and-shift. It exists to remove the constraints that shaped the current practice: waiting for a free machine, single-node ceilings, days-long jobs, a serialised preprocessing stage. |

**Neither obligation alone gives the right design.** Build only for today and you reproduce Alpharetta in AWS at $92k/month. Build only for the destination and researchers arrive to an environment that does not run their code.

**The resolution is sequencing, not compromise:**

1. **Day one — parity.** Their current pipeline runs as-is: a GPU container, 4–8 GPUs on one node, HDF5 staged locally, logs and checkpoints persisted. Nothing to rewrite.
2. **Early wins — the constraints they feel.** Parallelise the single-writer preprocessing stage across 100–200 on-demand CPUs; give rendering its own CPU pool instead of queueing behind GPU work; make a GPU available in seconds instead of when a box frees up.
3. **Built in, proven later — the destination.** EFA, cluster placement and multi-node capability ship in Phase 1 but are demonstrated when a workload needs them. Capability is cheap now; retrofitting it is not.

This is why the architecture is judged on more than today's requirements — and why it must not be judged on the destination alone.

---

### 0.1 Day-one parity walkthrough

§0.0's first obligation — *their pipeline runs unchanged on day one* — is a claim that needs evidence, not assertion. This walks the pipeline described in [[2026-10-19 Research Workload Q&A - Deepak Akhare]] through this architecture, stage by stage.

| Stage | What they do today | How it runs here | Change required |
|---|---|---|---|
| **Preprocessing** | 5,000–10,000 VTU files → geometry, fields, point clouds → consolidated HDF5 + statistics. 100–200 CPUs | Karpenter CPU NodePool; one large CPU node, or several | ⚠️ **Depends on how it parallelises** — see C1 |
| **Training** | One model, 4–8 GPUs, one server, days. Container with GPU support | **A plain Kubernetes Job on one p5 node.** Their container, their entrypoint | ✅ **None** |
| **Data loading** | 8–16 CPUs per GPU | 24 vCPU per GPU available on a p5.48xlarge | ✅ None |
| **Dataset read** | Per-epoch iteration, shuffled simulation order, on-demand HDF5 reads | Staged S3 → local NVMe at job start, then read locally | ⚠️ **Path assumptions** — see C3 |
| **Checkpoints** | Written during training; post-processing reads them mid-run | Written to S3; post-processing reads from S3 while training continues | ⚠️ Path assumptions — see C3 |
| **Inference** | 1 GPU per concurrent case → predicted VTUs, metrics, plots | Single-GPU pods bin-packed on GPU nodes; 8 concurrent per p5 | ✅ None |
| **ParaView** | Researchers inspect VTUs | In-sandbox needs a POSIX view and a display; downloaded needs neither | ❓ **Location unknown** — see C4 |
| **Video generation** | Read VTUs → videos and slides. CPU-only headless, 150 CPUs | CPU NodePool, own capacity, no queueing behind GPU work | ⚠️ Depends on parallelisation — see C2 |

#### Ray is not required for the training step

Worth stating plainly, because "EKS + Karpenter + Ray" implies more change than there is. They train **one model on 4–8 GPUs on one node** — that is `torchrun`/DDP in a container, which runs as an ordinary Kubernetes Job. **Ray earns its place in the CPU-parallel stages and in the multi-node destination, not in day-one training.** Nothing about adopting this architecture obliges them to rewrite a training script.

#### The hardware clears their stated needs

| Requirement | `p5.48xlarge` provides |
|---|---|
| 8–16 CPUs per GPU for data loading | **24 per GPU** (192 vCPU ÷ 8) |
| MGTrans holds a full simulation trajectory in memory | **2 TB RAM** |
| 30–100 GB dataset, read per epoch | **~30 TB local NVMe** — the dataset is ~0.3% of it |
| 100–200 CPUs preprocessing · 150 CPUs rendering | A single `c7i.48xlarge` is **192 vCPU**; Karpenter can also spread the work |

Staging 30–100 GB from S3 to NVMe is a few minutes once per job, against a run measured in days — after which every epoch reads from a local SSD, which should beat their current shared filesystem rather than merely match it.

#### Four confirmations before the parity claim is safe

None of these appear in Deepak's answers, and each could turn "no changes" into "some changes":

* **C1 — How is the 100–200 CPU preprocessing parallelised?** Shared-memory `multiprocessing` on one large box maps to a single big CPU instance; MPI or a job array maps differently. This decides whether preprocessing moves untouched.
* **C2 — The same question for the 150-CPU video rendering.**
* **C3 — Do the scripts assume a POSIX shared filesystem** for datasets and checkpoints? If paths are hardcoded to a mount, S3 implies a code change — avoidable with **Mountpoint for S3**, which presents a bucket at a filesystem path and leaves their code untouched.
* **C4 — Where does ParaView run?** In-sandbox needs a POSIX view and a remote display; downloading VTUs needs neither.

> **The honest summary: training and the data path are genuinely low-risk. The parity risk sits in the CPU stages and in filesystem assumptions** — not in the GPU work, which is where it is usually expected. C1–C4 belong in WS5 as confirmations before the image is built, not discovered during it.

---

### 0.2 What the original case rested on, and what survives

| Original argument | Status, read against *current practice vs. destination* |
|---|---|
| Multi-node gang scheduling and EFA demand a Kubernetes-native stack | ⏸ **Deferred, not gone.** Not needed for today's workload; still the stated destination, so stay capable |
| A seconds-long iteration loop is decisive | ✅ **Reinforced.** Deepak wants seconds for development, and "days to hours" means more iterations, not fewer |
| Bin-packing and fair-share drive >90% utilization | ⏸ **Deferred.** Few long jobs today; shorter jobs tomorrow bring this back |
| FSx for Lustre keeps the GPUs fed | ❌ **Genuinely unnecessary.** 30–100 GB in one HDF5 stages to local NVMe |
| The stack was named EKS / Ray / Argo at kickoff | ✅ **Unchanged** |
| Tri-environment parity is an invariant | ✅ **Unchanged** |

**Only one argument is actually retired — FSx.** The rest are deferred against today's workload and return as the environment does its job. A design that optimised for present constraints would fight the project's own purpose.

### 0.3 The new basis: this is a three-shape pipeline, not one workload

Deepak's answers describe three distinct compute profiles inside one pipeline:

| Stage | Shape | Resource |
|---|---|---|
| **Preprocessing** | Embarrassingly parallel across 5,000–10,000 VTU files and timesteps, with a serialising single-writer stage and a global statistics pass | **100–200 CPUs**, no GPU |
| **Training** | One model, one server, days, with heavy parallel data loading | **4–8 GPUs + 32–128 CPUs** |
| **Inference → video** | Parallel across test cases, then headless rendering | **1 GPU per case**, then **150 CPUs**, no GPU |

**Ray spans all three in one framework** — Ray Tasks for the parallel preprocessing and rendering, Ray Train for the single-node multi-GPU training, and Ray's object store for the checkpoint hand-off that post-processing consumes while training continues. Karpenter provisions the CPU and GPU node pools through the same mechanism.

**That unification is the argument now.** The alternative is operating a separate system for the CPU stages, which is a second thing to run for a team of one full-time and two half-time engineers.

### 0.4 Where AWS Batch now stands

**[[Alternative Architecture - AWS Batch]] fits *today's* job shapes well** — and that is precisely the limitation. It is an excellent fit for a workload the project is trying to change.

* Preprocessing and video rendering are **array jobs** — precisely what Batch is for.
* A days-long, single-node, 8-GPU training run is **exactly** the Batch model; start-up latency is irrelevant at that duration.
* The multi-node EFA spike that gated the Batch plan — a potential mid-phase architecture pivot — **no longer applies**.
* Nothing to operate, native pend-time metrics, and fair-share ready for Phase 2 SMaaS.

What still separates them:

1. **The development loop.** Deepak asks for start-up "within seconds" if development happens on AWS, and "optional live container access for development/debugging." Batch gives neither. This is the main remaining difference, and it concerns how researchers *work*, not how production jobs run.
2. **Pipeline unification.** Batch would need Step Functions or MWAA to sequence preprocess → train → infer → render; Ray expresses that in Python.
3. **Tri-environment parity**, which Batch forfeits entirely.
4. **The stated mandate** — EKS / Ray / Argo.

**The asymmetry that decides it:** Batch suits the current workload and does not grow into the destination — no interactive loop, no multi-node path that is not an undocumented EFA spike, no tri-environment parity. EKS + Ray suits both, at the cost of more to operate.

> **What would still tip the decision to Batch:** if the research team confirms that development happens **on-prem or locally**, with AWS used only to run finished jobs — *and* that multi-node training is genuinely not a destination. Both would have to be true. **Worth asking explicitly**, because one answer settles the architecture.

### 0.5 What changes in this design

1. **A CPU node pool is first-class** (§2) — sized to a 150–200 vCPU peak, Spot-eligible, and carrying more total compute hours than the GPU pool. This is real work regardless of how the GPU side evolves.
2. **EFA, cluster placement and the single-AZ GPU subnet stay in** (§3.3) — off the Phase 1 critical path, but built in. They are near-free now and costly to retrofit into a published benchmark.
3. **FSx for Lustre is dropped from the baseline** (§3.5.1). Stage the HDF5 to instance-store NVMe at job start; FSx remains a known upgrade path if datasets grow.
4. **The Phase 1 demonstration is 1 → 8 GPUs within one node** (§3.7), with multi-node as a Phase 2 proof once a workload needs it. The *capability* ships in Phase 1; the *demonstration* follows the workload.
5. **Checkpoint hand-off becomes an explicit requirement** — post-processing reads checkpoints while training continues; S3 serves this.
6. **Help remove the current bottlenecks, do not design around them.** The single-writer HDF5 stage and the global statistics pass are serialisation points in today's preprocessing. With 100–200 CPUs available on demand, parallelising them is a visible early win for the researchers.

---

## 1. The tension this architecture has to resolve

The kickoff asks for two things that normally pull in opposite directions:

| Stated requirement | Pulls toward |
|---|---|
| Shell/SSH access, researchers self-sufficient, **"without waiting for production-level ticketing systems or formal deployment queues"** | Dedicated, long-lived, interactively-held machines |
| **>90% utilization** versus the 60–70% on-prem baseline, "eliminating pend time", jobs decoupled from hardware | Scheduling, bin-packing, preemption — i.e. a queue |

**Dedicated interactive boxes are precisely what produces 60–70% utilization on-prem.** A researcher holds a node while thinking, editing, and debugging; the GPUs idle. Handing out three p5 instances by SSH would reproduce the on-prem problem at roughly $92k/month.

The reconciliation is in the kickoff's own language: Jim Tallman asks for a **"bulletin-board" compute architecture** that decouples jobs from hardware. A bulletin board *is* a queue — what he is rejecting is **human approval queues** (ticketing, deployment gates), not **machine scheduling**. Those are different things, and the architecture must deliver the second while eliminating the first.

**Ray is the component that does both.** A researcher gets an interactive shell in a cheap CPU-side dev pod, writes ordinary Python, and submits with `ray job submit`. The GPUs attach to the *job*, not to the person, and release on completion. The experience is interactive and queue-free; the utilization behaves like a scheduled cluster.

> **This is the single most important design decision in this document.** Everything below follows from it.

---

## 2. Recommended stack

| Layer | Recommendation | Serves |
|---|---|---|
| **Account & network** | Dedicated AWS account in GEV ENT MasterPayer Org; Terraform; private subnets; S3 VPC endpoint | Landing zone, GWD review |
| **Compute substrate** | **Amazon EKS**, one cluster | EKS/Ray/Argo mandate; Phase 2 burst |
| **GPU capacity** | **3 × p5.48xlarge** (24 H100 GPUs), single-AZ, **cluster placement group**, **EFA enabled**, backed by an **ODCR / ML Capacity Block** | Linear scaling; capacity scarcity |
| **Node lifecycle** | **Karpenter**, with `capacityReservationSelectorTerms` targeting the ODCR | >90% utilization; scale-to-zero |
| **Job substrate** | **KubeRay** — a persistent `RayCluster` for interactive work, `RayJob` for batch and benchmarks | The bulletin board; days→hours |
| **Multi-node transport** | **NCCL over EFA** | The linear-scaling proof itself |
| **Access plane** | **SSM Session Manager** → dev pod / node shell; `ray job submit` from the laptop | Shell/SSH priority, no public SSH |
| **Data — bulk movement** | **AWS DataSync** over Direct Connect or Site-to-Site VPN; **S3 as system of record** | Connectivity Bridge deliverable |
| **Data — training path** | **FSx for Lustre**, linked to the S3 bucket as a data repository | Keeping GPUs fed; utilization |
| **Images** | One CUDA/Ray image per environment target, in **ECR** | Tri-environment parity; D7 |
| **Telemetry** | **DCGM exporter → Prometheus → Grafana** (managed services acceptable) | Evidencing >90%; benchmark report |
| **GitOps** | **Argo CD** for the platform itself | Lab Notebook as code; reproducibility |
| **Pipelines** | **Argo Workflows**, *deferred* until pipelines actually exist | Argo mandate, without blocking enablement |
| **Experiment tracking** | **MLflow** on EKS (S3 + RDS backends) | The run-level half of the Lab Notebook |
| **CPU tier** *(added 2026-10-19)* | **Karpenter CPU NodePool**, Spot-eligible, sized to a ~150–200 vCPU peak | Preprocessing, video rendering, data loading — see [[2026-10-19 Research Workload Q&A - Deepak Akhare]] §6.2 |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESEARCHER                                                                 │
│  laptop ──SSM──► dev pod (CPU, cheap, long-lived, shell)                    │
│                   └─ ray job submit ──┐                                     │
└───────────────────────────────────────┼─────────────────────────────────────┘
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EKS CLUSTER (single cluster, single region)                                │
│                                                                             │
│   KubeRay ── RayCluster (head + autoscaling GPU worker group)               │
│      │                                                                      │
│      │  pending Ray worker pods                                             │
│      ▼                                                                      │
│   Karpenter ──provisions──► p5.48xlarge  (single AZ, placement group, EFA)  │
│      │                      8 × H100 80GB each                              │
│      │                      capacity-type: reserved  ◄── ODCR               │
│      └──consolidates / scales to zero when the board is empty               │
│                                                                             │
│   Argo CD (platform GitOps)        Prometheus + DCGM (utilization truth)    │
│   Argo Workflows (deferred)        MLflow (run tracking)                    │
└──────────────┬──────────────────────────────────────────────────────────────┘
               │ NCCL over EFA between GPU nodes
               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA                                                                       │
│  FSx for Lustre  ◄──linked──►  S3 (system of record)  ◄──DataSync──►  on-prem│
│  (training throughput)                                      Alpharetta      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Why each choice

### 3.1 One EKS cluster, built immediately — not EC2 first

The SOW's D1 describes *static EC2 GPU servers*; the research team describes a Kubernetes sandbox. Building plain EC2 now and EKS later means **rebuilding on top of the scarcest resource in the project** — reserved p5 capacity — while researchers are already using it.

Against three to four nodes in a single AZ, EKS adds days, not weeks. Ray and Argo both require Kubernetes regardless, and the Phase 2 burst layer has no other home. Build it once.

The "static server" experience survives: a long-lived dev pod with a shell is indistinguishable from a login node, and is what §3.4 delivers.

### 3.2 Karpenter against a capacity reservation

p5 capacity is scarce enough that the kickoff made the capacity request a Critical action item. Reserved capacity and elastic scaling are not in conflict — [Karpenter models ODCRs as a distinct `reserved` capacity type](https://karpenter.sh/docs/tasks/odcrs/), selected via `capacityReservationSelectorTerms` on the `EC2NodeClass`, and **prioritizes reserved capacity during both provisioning and consolidation**, modelling it as free because it is pre-paid.

Practical consequences:

* Reserved nodes carry `karpenter.k8s.aws/capacity-reservation-id`; the NodePool must permit `karpenter.sh/capacity-type: reserved`.
* **Karpenter does not support open matching** — every ODCR to be used must be named explicitly in `capacityReservationSelectorTerms`.
* Scale-to-zero still works mechanically, but **a prepaid reservation removes its financial benefit**. If the business takes the 12-month prepay option ([[Risks & Open Questions]]), idle-time savings disappear and the utilization target becomes a *throughput* argument, not a *cost* argument. That changes how >90% should be sold internally.

### 3.3 Single AZ, cluster placement group, EFA — now optional

> **Revised 2026-10-19:** with multi-server training not currently required, none of this is load-bearing. **Keep the single-AZ GPU subnet and the placement group anyway** — they cost nothing, and they preserve the multi-node option that the kickoff's framing still implies. **Treat EFA as deferred**, not dropped: it is cheap to enable later on a fresh node pool, and expensive to retrofit into a benchmark already published.

The original reasoning, which still applies if multi-node returns:

The kickoff already requests single-AZ placement, which is correct and worth recording as deliberate: multi-node training is latency- and bandwidth-bound, so GPU nodes belong in one AZ inside a **cluster placement group**, with **EFA** enabled and NCCL configured to use it. p5.48xlarge provides substantial EFA bandwidth precisely for this.

This trades AZ resilience for performance. For a research sandbox that is the right trade, but it should be a recorded decision rather than an accident — a single-AZ capacity event stops all training.

### 3.4 Shell access without a public SSH surface

"Shell/SSH" is a requirement about **ergonomics**, not about port 22. Opening SSH on GPU nodes in a GE Vernova account invites a security review that will cost more time than the feature is worth, and the environment must pass GWD.

> **Correction, 2026-10-15 ([[Chris Burke]]).** This section originally assumed SSM Session Manager was available. **It may not be approved** — GE is restrictive about remote access from laptops. The established patterns are **Gossamer**, which creates the AWS profile session for CLI and infrastructure work, and **PuTTY port tunnelling**; both use SSO and keep hops minimal, and **`kubectl` is routinely driven from a laptop this way**.
>
> That is good news for this design rather than bad: the access path it depends on — `kubectl exec` into a dev pod, `ray job submit` against the cluster — **already has a working precedent at GE**, and does not require SSM approval to proceed. Treat SSM as an optimisation to seek, not a dependency. Confirm the sanctioned path before WS3 starts (§8).

Recommended, in order of preference:

* **Gossamer-issued AWS profile session + `kubectl` from the laptop** — the path GE already sanctions, giving `kubectl exec` into dev pods and authenticated `ray job submit` with no new approval.
* **AWS Systems Manager Session Manager** for node-level shells, *if approved* — no bastion, no key distribution, IAM-controlled, fully audited.
* **`kubectl exec`** into a per-researcher dev pod for container-level shells. Precise terminology matters here: SSM gives a *node* shell, `kubectl exec` gives a *container* shell. The researcher experience is the same.
* **`ray job submit`** from the laptop against an authenticated Ray endpoint, so the laptop becomes the editing surface and the cluster the execution surface.

Dev pods should be **CPU-only and long-lived**. Letting a researcher hold a GPU node to edit files is the exact behaviour that caps on-prem at 60–70%.

If literal SSH is non-negotiable, an SSM-brokered SSH tunnel satisfies it without any inbound exposure.

### 3.4.1 What a researcher actually does each day

Connecting is settled above. This is the loop itself.

```
laptop                          dev pod (CPU, long-lived)        GPU node (per job)
  │                                    │                               │
  ├─ gossamer → AWS session            │                               │
  ├─ kubectl exec -it dev-deepak ──────┤                               │
  │                                edit code                           │
  │                                    ├─ mlaas submit train.py --gpus 8
  │                                    │                      ──────►  │ Job starts
  │                                    ├─ mlaas logs -f run42 ◄────────┤
  │                                    └─ mlaas shell run42  ──────►   │ exec into the
  │                                                                    │ running job
```

**Researchers should not write Kubernetes manifests.** Asking them to author a `Job` YAML to start a training run is infrastructure homework, and it contradicts the kickoff's "applied ML engineers … without waiting for formal deployment queues." The submission path should be **a thin wrapper CLI** that generates the manifest from a few flags — GPUs, image tag, dataset, run name — with `kubectl` available underneath as the escape hatch for anyone who wants it.

That wrapper is perhaps a day of work in WS3 and is the single largest lever on whether the environment feels like a research sandbox or like a deployment pipeline.

| Need | Command | Notes |
|---|---|---|
| Edit code | `kubectl exec -it dev-<name> -- bash`, or VS Code Remote attached to the dev pod | Dev pod is **CPU-only and long-lived** |
| Start a run | `mlaas submit train.py --gpus 8` | Wrapper writes the Job; `kubectl apply` still works |
| Watch it | `mlaas logs -f <run>` | `kubectl logs -f` underneath |
| **Get inside a running job** | `mlaas shell <run>` → `kubectl exec` into the training pod | This is Deepak's "optional live container access" |
| Debug on a GPU interactively | `mlaas shell --gpus 1 --ttl 2h` | **Time-boxed deliberately** — an untimed GPU shell is how on-prem reaches 60–70% |

### 3.4.2 Privileges — researchers do not need root

The answer is no in three distinct senses, and the distinction matters for the GWD submission.

| Scope | Granted? | Reasoning |
|---|---|---|
| **Root on the host / node** | ❌ **Never** | Nodes are Karpenter-managed and treated as immutable. Node-level access is an operator function, through SSM if approved. |
| **`cluster-admin` in Kubernetes** | ❌ **No** | Namespace-scoped RBAC is enough: create and delete Jobs, `exec` into their own pods, read logs, read their own secrets. |
| **Root inside their own container** | ❌ **No, by design** | The image runs as a **non-root UID** with a writable home and a virtualenv the researcher owns. |

**The container case is the one that creates friction, so plan for it.** Running as non-root means:

* ✅ `pip install` works — into a user-owned virtualenv, no root required. This covers the overwhelming majority of what researchers need mid-project.
* ❌ `apt-get install` does not. System packages are an **image change**, not a runtime action.

That is good discipline — it is what makes D4 stack parity reproducible rather than aspirational — but it is friction, and friction is what drives people back to Alpharetta. Mitigate it:

1. **A fast image path.** `mlaas build` rebuilds the image and pushes to ECR in minutes, so a missing system package costs a coffee rather than a ticket.
2. **Pre-install generously.** The heavy common set — CUDA, frameworks, VTK/PyVista, HDF5 tooling — ships in the base image.
3. **A per-user overlay venv** mounted into jobs, so a researcher's own packages survive between runs without an image rebuild.

#### Two privilege exceptions to settle *before* the security review

Both are normal for ML work and both will surprise a reviewer if they surface late:

* **GPU profiling.** Nsight Systems and Nsight Compute read GPU performance counters, which NVIDIA restricts to administrative users by default. Enabling them needs either a driver-level setting on the node (`NVreg_RestrictProfilingToAdminUsers=0`) or added container capabilities. **Decide deliberately** — profiling is exactly what a team chasing linear scaling will reach for.
* **Process attachment.** `py-spy`, `gdb` and similar need `CAP_SYS_PTRACE` to attach to a running process. Common in ML debugging, and a narrower grant than root.

Neither requires `privileged: true`, and neither should be granted cluster-wide. Both belong in the GWD submission as named, scoped exceptions rather than as discoveries in week six.

### 3.5 Data: the part most likely to cap utilization

A p5 node reading training data directly from S3 will starve its GPUs. The pattern that works:

* **S3** as the system of record for datasets, checkpoints and artifacts.
* **FSx for Lustre** linked to the S3 bucket via a data repository association, presenting a POSIX filesystem at the throughput multi-GPU training needs. Load on demand, write results back to S3.
* **AWS DataSync** over Direct Connect (preferred) or Site-to-Site VPN for the Alpharetta bridge — the **Connectivity Bridge** deliverable, owned by Dave Garber on the GE side.

**Sizing is unknown and blocking.** Dataset size and transfer frequency have been open since 2026-09-14. The bridge cannot be designed without them, and this is the deliverable with the longest external lead time.

#### 3.5.1 The training input path — Ray Data and Exoshuffle

Ray Data's shuffle is [[Exoshuffle An Extensible Shuffle Architecture|Exoshuffle]], shipped as a library on Ray's distributed futures rather than as a separate system — the paper's own ML evaluation notes that *"Ludwig 0.4.1 uses Exoshuffle offered through Ray Data."* **Nothing needs adopting: it arrives with KubeRay.** Using `ray.data` for the training input pipeline, instead of framework-native loaders, is the whole integration at the API level.

The work is in the node spec, and two details decide whether it performs:

* **Object store sizing, and the `/dev/shm` trap.** Exoshuffle rests on Ray's shared-memory object store for zero-copy on-node reads (paper §4.3.1). Ray defaults the object store to roughly 30% of node memory — about 600 GB on a 2 TB p5.48xlarge — but **a Kubernetes pod gets 64 MB of `/dev/shm` by default**. Worker pods need an `emptyDir` with `medium: Memory`, sized deliberately. Left wrong, shuffle silently degrades to disk and only a benchmark reveals it.
* **Spill to the instance-store NVMe.** Spilling is transparent, coalesces small objects into larger files, and streams spilled objects directly from disk to remote node managers (§4.3.2). p5.48xlarge carries roughly 30 TB of local NVMe, which is the correct target. Point Ray's spill directory at a RAID-0 of the instance store during node bootstrap — **not** the container overlay filesystem and not EBS.

> ✅ **Largely settled 2026-10-19.** [[2026-10-19 Research Workload Q&A - Deepak Akhare]] reports **30–100 GB per dataset as one consolidated HDF5** plus 20–100 small metadata files — the "fewer large shards" case, not the small-file case that broke SDM's metadata server. That volume fits comfortably on a p5's ~30 TB local NVMe, so **stage the HDF5 at job start and read from there**: faster than any network filesystem, and no standing cost. **FSx for Lustre is probably unnecessary.** Two caveats remain — whether ParaView runs in the sandbox (POSIX), and whether preprocessing runs in AWS (5,000–10,000 raw VTUs landing in S3).

**This may reduce what FSx for Lustre is for.** If Ray Data reads Parquet from S3 and handles per-epoch shuffle in the object store with NVMe spill, the training loop may not need a POSIX filesystem at all, leaving FSx serving raw CFD mesh files only. FSx is a standing cost and a second storage system to operate — **test the S3 + Ray Data path before committing to it.**

> **Sharpened 2026-10-15 by [[Chris Burke]], who has operational history here.** FSx for Lustre is the natural choice for HPC loads, but it failed badly on **SDM** — the same GE Vernova estate ([[QB Reference Architecture]] references `sdm-v5-s3-project-storage-prod`). Those workloads were far harder on the filesystem and **the metadata server could not keep up; AWS was stumped and never resolved it**. **Persistent_2** filesystems, which allow additional metadata servers to be provisioned, may since have addressed it — worth confirming with the AWS account team before relying on Lustre at scale.
>
> **The decision criterion is artifact interaction, not dataset size.** If workloads rarely read each other's outputs, generate artifacts locally and write them straight to S3 when done. That breaks down the moment there is a **post-processing step that reads everything produced upstream, or any mesh requirement** — in which case put the dependency artifacts on Lustre with DataSync and send only final outputs to S3.
>
> **Two signals suggest the mesh case applies here.** [[Surrogate ML Accelerator - Electrification]] slide 4 names **PyVista** for ingestion — a VTK wrapper for 3D datasets — alongside "DLS Models — predict physics using AI (NVIDIA)". And **file count matters as much as volume**: thousands of small files pressure the metadata server, which is exactly where SDM gave way. Q6 and Q7 of [[Architecture Decision - Questions for Researchers]] exist to settle this.

Note that shuffle traffic is **not** NCCL traffic: EFA accelerates GPU collectives, while Ray's object transfers use the normal network path. Both benefit from the single-AZ placement group, but EFA will not speed up shuffle.

### 3.6 Argo — both of them, in the right order

"Argo" remains ambiguous (Workflows or CD — see [[2026-10-12 Research Team Kickoff]]). The recommendation does not need the answer, because both have a place:

* **Argo CD now**, for the platform itself. Every cluster change lands through git. This also quietly delivers a large part of the **Project Lab Notebook**: configurations become version-controlled artifacts rather than prose.
* **Argo Workflows later**, when multi-step pipelines actually exist. On day one researchers have single training jobs, and a DAG engine adds operational surface without serving the Rapid Enablement priority. Argo Workflows submits `RayJob` resources cleanly when the time comes.

[[Risks & Open Questions]] still carries the Flyte-vs-Argo split — the Electrification deck says Flyte, the kickoff says Argo, and `hello-mlaas-burst` is built on Flyte. Deferring the orchestrator buys time to settle it without stalling the build. See §6.6 of [[aws-batch-ecs-vs-karp-ray-flyte]].

### 3.7 Measuring >90% — define it before claiming it

A headline number with no definition cannot be evidenced. Two very different metrics are both called "utilization":

| Metric | Meaning | Typical value |
|---|---|---|
| **Allocation** | GPU-hours assigned to a job ÷ GPU-hours available | What 60–70% on-prem almost certainly refers to |
| **SM occupancy** | GPU actually computing, via DCGM | Routinely 40–70% even in healthy training |

**The >90% target is achievable as allocation and is not a realistic SM-occupancy figure.** Stating which one is meant, early, prevents a benchmark report that appears to miss its headline target while the platform is working correctly.

Instrument from day one with **DCGM exporter → Prometheus → Grafana**, tracking allocation, SM occupancy, queue wait ("pend time"), and job duration. The same telemetry produces the **Scaling Benchmark Report**.

> **Revised 2026-10-19:** the sweep is now **1 → 2 → 4 → 8 GPUs within one node**, not 1 → 24 across three. Single-node scaling is dominated by NVLink and the data pipeline rather than by network fabric, which makes the input-path caveat below *more* important, not less.

**The scaling curve is only partly about GPUs.** The kickoff frames speedup entirely as 1 → N GPU scaling, but **input-pipeline starvation is the most common cause of sublinear scaling**. If data loading is the bottleneck, adding GPUs produces a flat curve, and the benchmark reads as a failure for reasons unrelated to the cluster, Karpenter or EFA.

[[Exoshuffle An Extensible Shuffle Architecture|Exoshuffle]] measured a **2.4× end-to-end training speedup from pipelining shuffle with training — on fixed hardware**, plus faster per-epoch convergence to higher accuracy, because a full per-epoch shuffle beats the windowed shuffle that memory-bound data loaders fall back to. Getting the input path right (§3.5.1) is therefore a *precondition* for the linear-scaling claim being measurable, not an optimization to revisit later.

Caveat on magnitude: that result came from a 7.5 GB dataset on g4dn instances. The benefit scales with the dataset-to-memory ratio, so if GEV's training sets fit comfortably inside one p5's 2 TB, the gain shrinks toward nothing. **Dataset size decides this** — the same open item that blocks the Connectivity Bridge design (§3.5).

### 3.8 Images carry the parity contract

[[aws-batch-ecs-vs-karp-ray-flyte]] treats tri-environment portability (Mac / AWS / on-prem) as an invariant. The practical carrier is the **container image**: one CUDA + driver + framework + Ray stack, built once, run on KinD locally, EKS in AWS, and on-prem later.

This is also where **D7 lives or dies**. "Equivalent training" against Alpharetta requires matching its driver, CUDA, framework and library versions — and the **Alpharetta inventory is still unanswered**. It gates the benchmark more tightly than any infrastructure item.

---

## 4. Deliverable mapping

The research team's six deliverables are a different framing from the SOW's D1–D8. This architecture serves both; the mapping is proposed, not agreed.

| Research deliverable | Architecture component | Approx. SOW |
|---|---|---|
| Architectural Reference Diagram | §2 of this document | — (new) |
| Operational Sandbox Environment | EKS + Karpenter + p5 + SSM access plane | D1, D3 |
| Connectivity Bridge | DataSync + Direct Connect/VPN + S3 + FSx | D2 |
| Scaling Benchmark Report | Ray + NCCL/EFA + DCGM telemetry | D7 |
| Project Lab Notebook | Argo CD git repo + MLflow + this vault | — (new) |
| SMaaS Foundation (Phase 2) | Namespaces, quotas, self-service templates | D8 / Phase 2 |

---

## 5. Build sequence

Aligned to Phase 1 (October–November 2026). Week 1 is the week access lands — **nothing starts until laptops and accounts exist**, which the kickoff marks a Day 0 blocker.

| Week | Milestone | Serves |
|---|---|---|
| **1** | Landing zone in Terraform; ODCR/capacity request filed; GWD, ServiceNow, Git pipelines requested | Unblocking |
| **2** | EKS cluster; system node pool; Argo CD bootstrapped; **first GPU node up** | Rapid Enablement |
| **3** | KubeRay installed; dev pods + SSM access; **first researcher trains on one GPU** | Rapid Enablement |
| **4** | S3 + DataSync bridge one direction; **Ray Data input path — object store, `/dev/shm`, NVMe spill (§3.5.1)**; FSx only if the S3 path proves insufficient | Connectivity Bridge |
| **5** | Multi-node Ray with EFA/NCCL; **2 → 4 → 8 GPU scaling runs**; **shuffle spike: epoch time and convergence, full vs. windowed** | Scalability Validation |
| **6** | Bridge bidirectional; DCGM dashboards live | Knowledge Capture |
| **7** | Full scaling sweep to 24 GPUs (3 nodes); benchmark report drafted | Scalability Validation |
| **8** | Hardening, runbooks, Lab Notebook consolidated | Handover |

**The week-3 milestone is the one that matters politically.** "Rapid enablement" is the first strategic priority, and a researcher training on a GPU in week 3 buys the latitude to build the rest properly.

---

## 6. What this architecture deliberately avoids

### 6.1 AWS Batch — now a close second, not a clear no

> **Revised 2026-10-19.** With multi-server training not required and jobs running for days, Batch fits these job shapes well and its EFA pivot risk is gone. See §0.4 for the narrowed margin and the question that would tip the decision. The structural points below still hold but no longer carry the argument.

Covered in detail in [[aws-batch-ecs-vs-karp-ray-flyte]] §6. Batch manages its own tainted nodes, so it cannot sit under Karpenter; and it submits podspecs rather than CRDs, so **it cannot run Ray at all** through KubeRay. It would add a second scaling system and AWS lock-in in exchange for managed queuing nobody requested.

**A full Batch-based design, with its additional tooling and a head-to-head comparison, is worked out in [[Alternative Architecture - AWS Batch]].** In short: Batch is genuinely stronger on managed scheduling, fair-share multi-tenancy and pend-time measurement, and genuinely weaker on the interactive loop the kickoff ranked first. Its strengths line up with **Phase 2 SMaaS** rather than Phase 1 research velocity.

### 6.2 A web portal or UI first
Explicitly deprioritized by the kickoff ("prioritize shell/SSH access over complex web UIs"). The Electrification deck's Streamlit frontend and the earlier Java Spring/React stack both belong to a later conversation. A Grafana dashboard is the only UI Phase 1 needs.

### 6.3 Amazon ECS

> **Revised 2026-10-19.** ECS was excluded on the gang-scheduling gap; with single-node training that objection falls away. It remains behind on pipeline unification, tri-environment parity and the stated mandate, and it has no queue — but it is no longer disqualified. See [[2026-10-19 Research Workload Q&A - Deepak Akhare]] §6.1.

Worked through in [[Alternative Architecture - Amazon ECS]]. ECS cannot run Karpenter, Flyte or Argo at all. Its genuine strengths (fully managed GPU fleet, fractional GPU, a real shell via ECS Exec) sit on axes this phase is not graded on. Best use here is a preprocessing tier or a Phase 2 inference tier, alongside rather than instead of this design.

### 6.4 Slurm
The natural instinct for HPC researchers, and genuinely good at gang scheduling. Rejected because the research team named EKS/Ray/Argo, and running Slurm alongside Kubernetes means two schedulers competing for the same GPUs. Ray provides gang scheduling within the Kubernetes model already.

### 6.5 Flyte, for now
Not rejected — deferred. See §3.6.

### 6.6 Scope caveat
The SOW's Phase 1 describes static EC2 servers and **explicitly excludes scheduling/queuing software**. This design delivers a Kubernetes cluster with a job substrate. [[Build Analysis - Target Platform on AWS]] already flags standing up EKS as new scope. **The research team's deliverables cannot be met within the SOW's literal Phase 1 wording** — that gap needs settling with Michael Russo rather than being absorbed quietly.

---

## 7. Relationship to the Quantum Black reference

GE Vernova is rebuilding internally using Quantum Black's platform as a reference blueprint ([[2026-07-30 Discovery Meeting]]). This design is **a deliberate subset of [[QB Reference Architecture]] plus two genuine technical disagreements** — worth stating explicitly, because "use QB as the model" otherwise invites copying choices that do not transfer.

### 7.1 Head-to-head

| | **Quantum Black** | **This design** | Driver |
|---|---|---|---|
| **Access** | Route 53 → WAF → ALB + ACM → OIDC vs corporate IdP → **JupyterHub** per-user pods | SSM + `kubectl exec` + `ray job submit`; no ALB, no OIDC, no notebooks | Kickoff: shell/SSH over web UIs |
| **AZ strategy** | Multi-AZ (App az-1 / az-2), Aurora Multi-AZ | **Single-AZ**, cluster placement group, EFA | Availability vs. training locality |
| **Node provisioning** | **Two systems** — SA-managed EKS Node Group (p4d + m4) *and* app-team Karpenter NodePool | Karpenter for GPU; small managed group for platform only | QB's split is organizational, not technical |
| **Ray's role** | One workload among pooled workspace pods (Layer E) | **The substrate** everything runs through | Jobs, not notebooks, at the centre |
| **Training storage** | **EFS** (NFS) + EBS + S3 | **FSx for Lustre**, or S3 + Ray Data (§3.5.1) | Real disagreement — §7.2 |
| **Database** | Aurora PostgreSQL, Multi-AZ, for app metadata | None in Phase 1 | No app tier |
| **Orchestration** | Argo Workflows / Flyte present from the start | Argo CD now, Workflows deferred (§3.6) | No pipelines exist yet |
| **GPU family** | p4d.24xlarge (A100) | p5.48xlarge (H100) | Funded plan |
| **IRSA, KMS, ECR, GitHub Actions → Argo CD, Prometheus/Grafana, VPC endpoints** | Yes | Yes | **No difference** |

### 7.2 The two real disagreements

**EFS is the wrong storage for this workload.** QB uses EFS as shared storage, which suits notebook home directories and application assets. It is **not fast enough to feed eight H100s**. Copying that choice because QB is the blueprint would starve the GPUs and sink the scaling benchmark for reasons that look like a platform failure. This is the most copyable mistake in the reference architecture — see §3.5 and §3.5.1 for the alternative.

**Single-AZ inverts QB's availability posture deliberately.** QB spans two AZs because it serves a business application where uptime matters more than inter-node bandwidth. A research sandbox has the opposite priority. Both are correct for their purpose; this one should be recorded as a conscious deviation rather than discovered later as an oversight (§3.3, §9).

### 7.3 Everything else is sequencing, not disagreement

The components dropped here — the whole edge and auth stack, JupyterHub, Aurora, Argo Workflows — are not rejected. QB is a multi-tenant product serving the wind business; this is four researchers in a flat team. **QB's architecture is a reasonable preview of the SMaaS Foundation**, and those components return in Phase 2 when non-ARC users arrive and per-user isolation, federated auth and metadata persistence become real requirements. [[Build Analysis - Target Platform on AWS]] already sizes that gap.

**One QB pattern worth adopting now:** QB reads wind design data from the `sdm-v5` S3 bucket **cross-account and read-only, without copying it into the platform's own storage**. The Connectivity Bridge here assumes DataSync replication from Alpharetta. If any Electrification source data already lives in an AWS account, the QB pattern removes a deliverable's worth of work — worth one question to Dave Garber.

### 7.4 What QB may not demonstrate

QB places p4d GPU nodes across **two Availability Zones**. Tightly-coupled multi-node training is not run that way — cross-AZ latency would undermine NCCL collectives. The likeliest reading is that QB's platform runs **single-node training and inference**, not distributed multi-node training.

If that is right, then **the capability Jim Tallman's team most wants to prove — linear scaling across a GPU cluster — is not something the reference blueprint actually demonstrates.** QB remains a good model for the *platform*; it is not evidence for the *scaling claim*. Confirm against the source diagram before the architecture review, because it changes what "use QB as the model" means in practice. Tracked in [[Risks & Open Questions]].

---

## 8. Decisions required before provisioning

Ordered by lead time. The first four block the build.

> **Added 2026-10-19, and now the highest-value question on the list:** **does development happen on AWS, or on-prem/locally with AWS used only to run finished jobs?** If the latter, the interactive argument disappears and [[Alternative Architecture - AWS Batch]] becomes the better choice (§0.3).

1. **On-demand or 12-month prepay?** Worth roughly $450k at the 3-server footprint, and it determines whether scale-to-zero has any financial meaning (§3.2).
2. **Which region and AZ**, and is p5 capacity actually available there?
3. **Is GPU funding secured?** Still listed as an open next step in the Electrification deck.
4. **Alpharetta inventory** — driver, CUDA, frameworks, licensed software. Gates the image and D7.
5. **Dataset size and transfer frequency.** Gates the bridge design (§3.5).
6. **Does ">90%" mean allocation or SM occupancy?** (§3.7)
7. **Argo Workflows or Argo CD?** (§3.6)
8. **Does the SOW's "no scheduling software" exclusion survive the kickoff?** (§6.5)

All are tracked in [[Risks & Open Questions]].

---

## 9. Risks this architecture accepts

| Accepted risk | Why it is acceptable | Watch for |
|---|---|---|
| Single AZ for all GPU capacity | Required for multi-node training performance; research sandbox, not production | A capacity event stops all training |
| One cluster, no multi-tenancy in Phase 1 | ~4 researchers, flat team, speed prioritized | Becomes untenable as SMaaS onboards other business units |
| EKS operational surface on a part-time team | Unavoidable — Ray and Argo both require it | The 24-hour unblock commitment against 1.0 + 0.5 + 0.5 FTE |
| FSx for Lustre adds a second storage system | GPU starvation is the likelier utilization cap | Cost; lifecycle of scratch data |
| Deferring the orchestrator | Enablement outranks pipelines in the kickoff's own priority order | Slipping past Phase 2 planning |

---

## 10. Notes from Rick — Technical Solutions, Closing Decisions & GE Budget Strategy

> **Author:** Rick Allen (LTI Cloud Architect & Orchestrator Lead)  
> **Audience:** Nam Park, Chris Burke, Jim Tallman, Michael Russo, and GE Vernova Stakeholders  
> **Context:** Translating newly verified AWS guides ([LustreGuide.md](../../Resources/aws/LustreGuide.md), [karpenter.md](../../Resources/aws/karpenter.md), [KUB312](../../Resources/aws/KUB312_Simplify-Kubernetes-workloads-with-Karpenter-and-Amazon-EKS-Auto-Mode.md)), KubeRay operator patterns, and the 3-node hardware analysis into decisive closures for §8 provisioning decisions.

### 10.1 Closing Decision 1 & 4: 3 Servers (24 GPUs) Eliminates the Funding Blocker

* **Contractual Reality:** Signed [SOW - Burstable MLaaS.md](../SOW/SOW%20-%20Burstable%20MLaaS.md) Deliverable D1 literally specifies: *"Establish access to 3 static servers with 24 total GPUs within an agreed-upon AWS data center for ~4 ARC researchers."*
* **Budget Impact for Michael Russo:** Budgeting for 4 nodes ($122,145/month) generated an artificial $1.83M 15-month exposure that exceeded GE's available Phase 1 funding. Restoring the contractual baseline of **3 × `p5.48xlarge` (24 GPUs)** costs **$91,608/month**, saving **~$30,536/month ($366,434/year)**.
* **Collective Scaling Proof:** PyTorch DDP and NCCL Ring AllReduce do not require powers of two. In Ring AllReduce, bus efficiency scales as $\frac{N-1}{N}$. At 24 GPUs, efficiency is $\frac{23}{24} = 95.83\%$, compared to $96.87\%$ for 32 GPUs. The difference is mathematically negligible (<1.04%), while the 3-node topology provides a clean 5-point scaling curve (1, 2, 8, 16, 24 GPUs) for Jim Tallman's scaling benchmark report.

### 10.2 Closing Decision 6 & Overcoming the SDM Metadata Ceiling (§3.5.1)

Chris Burke noted in §3.5.1 that FSx for Lustre failed on GE's SDM project because the metadata server froze on high file counts. Our analysis of the newly indexed [FSx for Lustre User Guide](../../Resources/aws/LustreGuide.md) resolves this:
* **The Root Cause:** SDM used older Lustre Scratch/Persistent_1 tiers where Metadata IOPS was statically locked to capacity ratios. Small file systems with hundreds of thousands of mesh slices starved the metadata server (MDS).
* **The Fix in Persistent_2:** Modern **FSx for Lustre Persistent_2 SSD** introduces **User-Provisioned Metadata IOPS** mode, supporting up to **192,000 Metadata IOPS** independently of storage size.
* **The Zero-Cost Alternative (Local NVMe Scratch):** Each `p5.48xlarge` includes **8 × 3.84 TB NVMe SSDs (~30.7 TB raw local scratch)** delivering over **30 GB/s local read throughput**. Karpenter userdata formats these into `/mnt/nvme-scratch` via RAID-0. Using **Ray Data** to prefetch S3 shards directly into local NVMe bypasses network storage entirely, eliminates the Lustre metadata risk, and saves an additional **$1,500–$3,000/month** in standing filesystem costs.

### 10.3 Closing Decision 8: Clarifying Argo CD vs. Flyte (§3.6)

* There is no conflict between Argo and Flyte:
  * **Argo CD** is adopted strictly as the Kubernetes GitOps engine to maintain cluster state, KubeRay operator deployments, and Karpenter CRDs.
  * **Flyte** is the workflow orchestration engine (macro-DAGs, data caching, lineage, Pythonic `@task` authoring) that delegates GPU training jobs to Ray actors.

### 10.4 Closing Decision 5: De-Risking SOW D7 Acceptance

* SOW D7 ("equivalence with on-prem MLaaS") has been blocked since Sept 14 awaiting Alpharetta baseline metrics.
* We decouple Phase 1 acceptance from the missing baseline by developing a synthetic 3D Physics-GNN / mesh benchmark (MeshGraphNet on Ray Train). This benchmark demonstrates linear scaling across 1 to 24 GPUs on Day 1, fulfilling Jim Tallman's Deliverable 4, and serves as an immutable benchmark to compare against Alpharetta whenever GE provides the on-prem dataset.

### 10.5 Spot Interruption & Karpenter Capabilities

* Using official [karpenter.md](../../Resources/aws/karpenter.md) and [KUB312](../../Resources/aws/KUB312_Simplify-Kubernetes-workloads-with-Karpenter-and-Amazon-EKS-Auto-Mode.md), we configure Karpenter EventBridge/SQS interruption queues. For single-node hyperparameter sweeps and inference tests, Karpenter can leverage EC2 Spot instances with automated 2-minute checkpointing before reclamation, cutting compute costs by up to 65% for non-distributed jobs.

---

## 11. Related

* [[2026-10-12 Research Team Kickoff]] — the vision, scope and deliverables this responds to
* [[aws-batch-ecs-vs-karp-ray-flyte]] — why Batch is excluded (§6), Flyte vs. Argo (§6.6)
* [[EKS Platform Replication Plan]] — the fuller platform build this is a sandbox-scoped subset of
* [[Phase 1 Project Plan]] — committed scope, workstreams, milestones
* [[Static AWS GPU Environment]] — the SOW's literal D1 description
* [[Surrogate ML Accelerator - Electrification]] — funding, instance family, cost options
* [[Exoshuffle An Extensible Shuffle Architecture]] — the shuffle architecture inside Ray Data; source for §3.5.1 and the input-pipeline caveat in §3.7
* [[Risks & Open Questions]] — every open item referenced above

**External sources (verified 2026-10-12):**
* [Karpenter — On-Demand Capacity Reservations](https://karpenter.sh/docs/tasks/odcrs/) — `reserved` capacity type, selector terms, consolidation behaviour
* [Karpenter ODCR design](https://github.com/aws/karpenter-provider-aws/blob/main/designs/odcr.md)
* [EKS best practices — AI/ML compute](https://docs.aws.amazon.com/eks/latest/best-practices/aiml-compute.html)
* [EKS — ML node pools with Karpenter](https://docs.aws.amazon.com/eks/latest/userguide/ml-node-pools.html)
