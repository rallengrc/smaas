---
title: Alternative Architecture — AWS Batch
description: AWS Batch-based architecture for the Surrogate ML Accelerator, the additional tooling it requires, and a head-to-head comparison against the Karpenter/Ray recommendation
keywords:
- AWS Batch
- multi-node parallel
- MNP
- gang scheduling
- EFA
- fair-share scheduling
- Karpenter comparison
- Ray
- Step Functions
- SMaaS
tags:
- architecture
- comparison
category: architecture
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- aws batch architecture
- batch instead of karpenter
- batch vs karpenter comparison
- batch mnp ray architecture
- alternative architecture batch
---

# Alternative Architecture — AWS Batch

> **TL;DR:** A Batch-based build is viable and in some respects *better* than the Karpenter design — it is a managed bulletin board with native fair-share scheduling, built-in gang scheduling, and native pend-time metrics, all with no scheduler to operate. It pays for that with the thing the kickoff ranked first: **the interactive loop**. Every iteration becomes a job submission with minutes of latency instead of seconds, Ray becomes hand-rolled, Spot is unavailable for multi-node jobs, and tri-environment parity is lost outright. **Recommendation: Karpenter/Ray for Phase 1 research velocity; revisit Batch for Phase 2 SMaaS multi-tenancy, where its strengths are decisive.**
> **Use this for:** Evaluating Batch against [[Recommended Architecture - Surrogate ML Accelerator]], and as the design to build from if Batch is mandated.

> ⚠️ **Requirements update, 2026-10-19.** [[2026-10-19 Research Workload Q&A - Deepak Akhare]] states **multi-server training is not currently required**, which **defuses this plan's defining risk**: spike S1 (EFA on Batch-on-EKS, undocumented) gated multi-node training, and without it there is no mid-phase pivot risk. Two further points cut both ways — jobs run for **days**, so the submit-and-wait penalty is noise against a three-day run though not during development; and the **CPU-heavy stages** (100–200 CPUs preprocessing, 150 for video) are work Batch handles well.

**Status: alternative design for comparison.** Read alongside [[Recommended Architecture - Surrogate ML Accelerator]] (the primary recommendation) and [[aws-batch-ecs-vs-karp-ray-flyte]] §6 (why Batch and Karpenter cannot be layered).

---

## 1. What necessarily changes

Batch is not a drop-in replacement for Karpenter. Three consequences follow from the service's design, all sourced in [[aws-batch-ecs-vs-karp-ray-flyte]] §6:

1. **Batch owns its nodes.** It scales, labels and taints them, and will not run jobs on nodes it does not manage. There is no configuration in which Karpenter scales Batch capacity.
2. **Batch submits podspecs, not CRDs.** KubeRay is unavailable. A Ray cluster must be bootstrapped by hand inside a multi-node parallel job (§4.2).
3. **The execution model inverts.** Karpenter/Ray gives a *persistent cluster you submit into*; Batch gives *a queue that materialises a cluster per job and destroys it*. Everything in §6 flows from this one difference.

---

## 2. Which Batch: on EKS, or on EC2/ECS?

| | **Batch on EKS** | **Batch on EC2/ECS** |
|---|---|---|
| Kubernetes retained | Yes — Argo, MLflow, dev pods still have a home | No |
| MNP support | Yes, [GA July 2024](https://aws.amazon.com/about-aws/whats-new/2024/07/aws-batch-gang-scheduling-eks-multi-node-parallel-jobs/) | Yes, long-standing |
| **EFA** | **Not documented by AWS** (§4.3) | **Documented** ([Batch EFA guide](https://docs.aws.amazon.com/batch/latest/userguide/efa.html)) |
| GPU monitoring | DaemonSets explicitly permitted on Batch nodes | CloudWatch agent / custom |
| Honours the EKS mandate | Yes | No |

**Recommendation: Batch on EKS**, subject to resolving the EFA question in §4.3. It preserves the EKS/Argo half of the kickoff mandate and keeps a home for the platform services Batch itself does not provide. Batch on EC2/ECS is simpler and has the documented EFA path, but abandons Kubernetes entirely — and with it Argo, the dev-pod tier, and any pretence of on-prem parity.

Note that choosing Batch on EKS does **not** remove the need for Kubernetes expertise. You operate both systems.

---

## 3. The Batch stack

| Layer | Component | Notes vs. the Karpenter design |
|---|---|---|
| **Compute substrate** | EKS cluster | Unchanged |
| **GPU capacity** | **AWS Batch managed compute environment**, p5.48xlarge, single-AZ, cluster placement group | Replaces Karpenter NodePool |
| **Scheduling** | **Batch job queues + scheduling policies** (share identifiers, weights) | New — replaces Ray's scheduler |
| **Multi-node jobs** | **Batch MNP jobs**, gang-scheduled | Replaces KubeRay RayCluster |
| **Single-node jobs** | **Regular Batch container jobs** (bin-packed, see §4.4) | Replaces Ray worker pods |
| **Distributed runtime** | **torchrun / NCCL**, or hand-bootstrapped Ray (§4.2) | Replaces KubeRay |
| **Platform node group** | Small **EKS managed node group** (not Batch-managed) | New — Batch nodes cannot host platform services |
| **Interactive tier** | **Dedicated CPU dev pods** on the platform node group + SSM | New requirement — Batch has no interactive mode |
| **Pipelines** | **Step Functions** or **MWAA**, or Argo Workflows calling `SubmitJob` | Argo integration becomes glue |
| **Data** | S3 + FSx for Lustre + DataSync | Unchanged |
| **Telemetry** | DCGM DaemonSet on Batch nodes + **CloudWatch queue metrics** | Queue metrics are a genuine gain |
| **Tracking** | MLflow on the platform node group | Unchanged |
| **GitOps** | Argo CD for the platform; Batch resources via Terraform | Batch is not a Kubernetes object |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESEARCHER                                                                 │
│  laptop ──SSM──► dev pod (CPU, platform node group)                         │
│                   └─ aws batch submit-job ──┐   ← NOT an interactive loop   │
└─────────────────────────────────────────────┼───────────────────────────────┘
                                              ▼
                                   ┌──────────────────────┐
                                   │  AWS BATCH           │
                                   │  job queue           │
                                   │  + scheduling policy │
                                   │  (fair-share)        │
                                   └──────────┬───────────┘
                                              │ materialises per job
┌─────────────────────────────────────────────▼───────────────────────────────┐
│  EKS CLUSTER                                                                │
│                                                                             │
│  ┌── Batch-managed nodes (tainted, Batch-scaled) ──────────────────────┐    │
│  │   MNP job: node 0 (main) ── NCCL/EFA ── node 1 ── node 2 ── …       │    │
│  │   torchrun, or ray start --head / --address bootstrap               │    │
│  │   DCGM DaemonSet (permitted on Batch nodes)                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌── Platform managed node group (NOT Batch-managed) ──────────────────┐    │
│  │   dev pods · Argo CD · MLflow · Prometheus/Grafana                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└──────────────┬──────────────────────────────────────────────────────────────┘
               ▼
    FSx for Lustre ◄──► S3 ◄──DataSync──► Alpharetta
```

---

## 4. The four things that need solving

### 4.1 Interactive access — the hardest problem

Batch is fire-and-forget. It has no interactive mode, no attach, no persistent session. The kickoff's **first strategic priority is Rapid Enablement** and its third is "prioritize shell/SSH access over complex web UIs" — Batch serves both worst.

The mitigation is a **separate always-on interactive tier**: CPU dev pods on the platform node group where researchers edit, with `aws batch submit-job` as the run command. That is workable, and it is honestly not far from how HPC users already work with Slurm. But note what it costs:

* **Iteration latency goes from seconds to minutes.** A persistent Ray cluster executes a changed function immediately. A Batch job re-queues, provisions nodes, pulls the image, bootstraps the runtime, runs, and tears down — every time.
* **No GPU-backed interactive debugging.** Attaching a debugger to a live distributed job is not a Batch workflow.
* Researchers who want a GPU shell will ask for one, and the only answer is a dedicated GPU dev instance outside Batch — which reintroduces exactly the idle-GPU pattern that caps on-prem utilization at 60–70%.

### 4.2 Ray on MNP — the bootstrap

If Ray is retained, it is hand-rolled. Batch MNP provides [four environment variables](https://docs.aws.amazon.com/batch/latest/userguide/mnp-env-vars.html) that make this tractable:

| Variable | Use |
|---|---|
| `AWS_BATCH_JOB_MAIN_NODE_INDEX` | Compare against node index to identify the head |
| `AWS_BATCH_JOB_NODE_INDEX` | This node's index, 0-based |
| `AWS_BATCH_JOB_NUM_NODES` | Total nodes requested |
| `AWS_BATCH_JOB_MAIN_NODE_PRIVATE_IPV4_ADDRESS` | Head address — **set only on child nodes** |

The container entrypoint branches: head nodes run `ray start --head`, children `ray start --address=$AWS_BATCH_JOB_MAIN_NODE_PRIVATE_IPV4_ADDRESS:6379`, then the main node runs the workload and exits, which terminates the job.

**What is lost:** the Ray Dashboard as a persistent service, autoscaling worker groups, Ray actors and Serve, heterogeneous pipelines, and the whole interactive `ray job submit` model. You keep Ray's *distributed execution* and discard its *platform*.

> **Worth considering honestly:** if the architecture is Batch, Ray may not be worth retaining. For pure distributed training, **`torchrun` with NCCL over EFA is simpler, better documented, and loses nothing** that Batch has not already taken away. Ray's value is concentrated in exactly the capabilities Batch negates. Retaining Ray here is largely about honouring the stated mandate rather than engineering merit.

### 4.3 EFA — an unresolved build risk

Linear scaling past one node depends on EFA. AWS documents EFA for Batch on the **ECS/EC2 path only** — [the Batch EFA guide](https://docs.aws.amazon.com/batch/latest/userguide/efa.html) specifies:

* an AMI with the EFA driver loaded;
* a security group allowing **all inbound and outbound traffic to and from itself**;
* **all instances in the same cluster placement group**;
* a job definition `devices` member with `hostPath` set to `/dev/infiniband/uverbs0`.

Every example given is `containerProperties` / `nodeRangeProperties` — i.e. the ECS/EC2 shape. EKS has its own EFA mechanism entirely (the [EFA device plugin or DRA driver](https://docs.aws.amazon.com/eks/latest/userguide/device-management-efa.html), requesting `vpc.amazonaws.com/efa` in a podspec).

**I could not find AWS documentation for EFA on Batch-on-EKS.** It may well work by requesting the resource in the job definition's podspec, but it is undocumented. **Treat this as a required spike before committing** — the Scaling Benchmark Report depends on it, and failing it forces a fallback to Batch on EC2/ECS, which abandons Kubernetes.

### 4.4 MNP is single-tenant per instance

[MNP job nodes are single-tenant](https://docs.aws.amazon.com/batch/latest/userguide/multi-node-parallel-jobs.html): *"only a single job container is run on each Amazon EC2 instance."* On p5.48xlarge that means **a 1-GPU MNP job occupies all 8 GPUs of a node** — catastrophic for the utilization target.

The fix is a two-queue design:

* **Regular container jobs** for single-node work (≤ 8 GPUs). Batch bin-packs these by resource requirement, so eight 1-GPU jobs can share a node.
* **MNP jobs** for multi-node training only.

This must be explicit in researcher guidance, or the utilization headline fails for the most common job shape.

---

## 5. Additional tooling Batch requires

Beyond the Karpenter design's components, a Batch build needs:

| Need | Tool | Why Batch creates this need |
|---|---|---|
| Interactive tier | EKS managed node group + dev pods + SSM | Batch has no interactive mode (§4.1) |
| Platform hosting | Same node group | Batch nodes are tainted; platform services cannot run on them |
| Ray bootstrap | Custom entrypoint using `AWS_BATCH_JOB_*` | No KubeRay (§4.2) |
| DAG orchestration | **Step Functions** (native Batch integration) or **MWAA/Airflow** (`BatchOperator`); Argo Workflows only as `SubmitJob` glue | Batch jobs are not Kubernetes objects, so Argo cannot drive them natively |
| Multi-tenancy | **Batch scheduling policies** — share identifiers, weight factors | Replaces namespace quotas; a genuine Batch strength |
| Infrastructure as code | **Terraform** for queues, compute environments, job definitions | Batch resources are not reconciled by Argo CD |
| Queue telemetry | **CloudWatch** job-state metrics | Native pend-time measurement; a genuine Batch gain |
| GPU telemetry | **DCGM exporter as a DaemonSet** on Batch nodes | AWS explicitly permits DaemonSets on Batch-managed nodes |
| Capacity targeting | ODCR via **launch template** capacity reservation specification | Batch has no equivalent of Karpenter's `capacityReservationSelectorTerms` — **verify** |

Unchanged from the Karpenter design: S3, FSx for Lustre, DataSync, ECR, MLflow, Prometheus/Grafana, Argo CD for the platform.

---

## 6. Head-to-head

| Dimension | Karpenter + Ray | AWS Batch | Winner |
|---|---|---|---|
| **Interactive iteration** | Persistent cluster, seconds | Job submission, minutes | **Karpenter** — decisively |
| **Shell/SSH priority** | Dev pod + live cluster | Dev pod + fire-and-forget | **Karpenter** |
| **Scheduler operations** | Ray + Karpenter tuning is yours to own | Fully managed | **Batch** — decisively |
| **Gang scheduling** | Via KubeRay; needs care | Built into MNP | **Batch** |
| **Fair-share / multi-tenancy** | Namespace quotas, hand-built | Native scheduling policies | **Batch** — decisively |
| **Pend-time measurement** | Build it from Prometheus | Native CloudWatch queue metrics | **Batch** |
| **Utilization, single-node jobs** | Fine-grained pod packing | Bin-packed regular jobs | Tie |
| **Utilization, multi-node jobs** | Fractional node use possible | Single-tenant whole nodes (§4.4) | **Karpenter** |
| **Spot eligibility** | Yes, for interruptible work | **Not available for MNP** | **Karpenter** |
| **Scale-to-zero** | Karpenter consolidation | Native, `minvCpus: 0` | Tie |
| **EFA / linear scaling** | Documented EKS path | Documented on ECS/EC2; **undocumented on EKS** | **Karpenter** |
| **Ray ecosystem** | Full (Dashboard, Tune, Train, actors) | Execution only (§4.2) | **Karpenter** |
| **Training input pipeline** | Ray Data / Exoshuffle, pipelined shuffle | Framework data loaders only | **Karpenter** |
| **Tri-environment parity** | Mac / AWS / on-prem | **AWS only** | **Karpenter** — decisively |
| **Honours EKS/Ray/Argo mandate** | Natively | Partially; Argo becomes glue | **Karpenter** |
| **Security review surface** | More cluster components | Fewer; managed service | **Batch** |
| **Operational load on 2 FTE** | Two systems to tune | One managed, but still two platforms | **Batch**, slightly |

---

## 7. Pros and cons

### Batch — genuine advantages
* **It is literally the bulletin board** Jim Tallman described. Jobs decouple from hardware by construction.
* **Nothing to operate.** Queues, priorities, retries, fair-share and scale-to-zero are the service's job, not the team's — material against a 1.0 + 0.5 + 0.5 FTE team carrying a 24-hour unblock commitment.
* **Pend time is measured natively.** The metric the kickoff wants driven to zero is emitted by the service.
* **Gang scheduling is free and correct.** No partial-allocation deadlocks, no Kueue or Volcano.
* **The best available answer to Phase 2 SMaaS.** Fair-share scheduling across share identifiers is exactly the primitive a shared service across business units needs.
* **Smaller security-review surface** for GWD.

### Batch — real costs
* **The interactive loop dies** — the kickoff's first priority, served worst.
* **Ray is reduced to a library**, hand-bootstrapped, with its platform discarded (§4.2).
* **Ray Data's shuffle goes with it.** [[Exoshuffle An Extensible Shuffle Architecture|Exoshuffle]] is built on Ray's distributed futures and shared-memory object store, so it is unavailable to a `torchrun`-based Batch job. That costs the measured **2.4× end-to-end training speedup from pipelining shuffle with training on fixed hardware**, and the full per-epoch shuffle that converges to higher accuracy than the windowed shuffle memory-bound data loaders fall back to. See [[Recommended Architecture - Surrogate ML Accelerator]] §3.5.1 — and note this is a *throughput* loss independent of GPU count, so it directly erodes the linear-scaling headline.
* **No Spot for MNP** — removes the main cost lever against ~$92k/month (3 servers, settled 2026-10-19).
* **One instance type per MNP job**, limiting heterogeneous pipelines.
* **Single-tenant MNP nodes** waste GPUs on small jobs unless the two-queue discipline holds (§4.4).
* **EFA on Batch-on-EKS is undocumented** (§4.3) — a live risk to the headline deliverable.
* **Tri-environment parity is gone.** [[aws-batch-ecs-vs-karp-ray-flyte]] §5 lists this as an architectural *invariant*; Batch violates it outright.
* **Argo becomes glue**, or is replaced by Step Functions — further from the stated mandate.
* **You operate both platforms anyway** on Batch-on-EKS; the "no Kubernetes" saving is not real.

---

## 8. Recommendation

**Keep Karpenter/Ray for Phase 1.** The kickoff's stated priorities are, in its own order: rapid enablement, scalability validation, infrastructure agility (shell/SSH over UIs), knowledge capture. Batch serves the first and third worst, and those are where the project will be judged in its first eight weeks.

**Revisit Batch for Phase 2 SMaaS.** The moment the environment stops being four researchers in a flat team and becomes a shared service across Electrification, wind and power, the requirements invert: fair-share scheduling, queue isolation, cost attribution per business unit, and no-touch operations. Those are precisely Batch's strengths and precisely Ray's weaknesses. "SMaaS Foundation (Phase 2)" may well be a Batch-shaped problem even though Phase 1 is not.

That phasing is not a compromise — it uses each system where it is genuinely stronger, and it matches the project's own phase boundary.

**If Batch is mandated for Phase 1 anyway**, build §3 as written, and set expectations explicitly on three points: iteration latency (§4.1), the two-queue discipline (§4.4), and the EFA spike (§4.3) landing before any scaling commitment.

---

## 9. Spikes required before committing to Batch

1. **Does EFA work on Batch-on-EKS MNP jobs?** Undocumented. Blocks linear scaling. (§4.3)
2. **Can a Batch compute environment target the ODCR** via launch template capacity reservation specification?
3. **Measured iteration latency** — submit-to-first-log for a 2-node p5 MNP job, cold and warm. This number decides whether researchers accept the model.
4. **Does FSx for Lustre mount cleanly** into Batch-on-EKS job pods?
5. **Does the Ray-on-MNP bootstrap survive node failure** mid-job, and what is the retry behaviour?

---

## 10. Related

* [[Recommended Architecture - Surrogate ML Accelerator]] — the primary recommendation this is measured against
* [[Alternative Architecture - Amazon ECS]] — the third option; ECS converges on this design for multi-node work, and §6 there carries the three-way comparison
* [[aws-batch-ecs-vs-karp-ray-flyte]] — §6 on why Batch and Karpenter cannot be layered
* [[2026-10-12 Research Team Kickoff]] — the vision and priorities both designs serve
* [[Risks & Open Questions]] — cost options, capacity conflict, stack contradictions

**External sources (verified 2026-10-12):**
* [AWS Batch on Amazon EKS](https://docs.aws.amazon.com/batch/latest/userguide/eks.html) — node ownership, taints, podspec translation, DaemonSet exception
* [Multi-node parallel jobs](https://docs.aws.amazon.com/batch/latest/userguide/multi-node-parallel-jobs.html) — gang scheduling, single-tenant nodes
* [MNP environment variables](https://docs.aws.amazon.com/batch/latest/userguide/mnp-env-vars.html) — the Ray/torchrun bootstrap contract
* [MNP compute environment considerations](https://docs.aws.amazon.com/batch/latest/userguide/mnp-ce.html) — no Spot, one instance type, single-AZ placement group
* [Elastic Fabric Adapter with AWS Batch](https://docs.aws.amazon.com/batch/latest/userguide/efa.html) — ECS/EC2 requirements; no EKS coverage
* [Manage EFA devices on Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/device-management-efa.html) — the separate EKS mechanism
* [Gang scheduling on EKS announcement, July 2024](https://aws.amazon.com/about-aws/whats-new/2024/07/aws-batch-gang-scheduling-eks-multi-node-parallel-jobs/)
* [Leveraging EFA to run HPC and ML workloads on AWS Batch](https://aws.amazon.com/blogs/compute/leveraging-efa-to-run-hpc-and-ml-workloads-on-aws-batch/)
