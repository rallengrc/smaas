---
title: Alternative Architecture — Amazon ECS
description: ECS-based architecture for the Surrogate ML Accelerator, its limitations, and a three-way comparison against the Karpenter/Ray and AWS Batch designs
keywords:
- Amazon ECS
- ECS Managed Instances
- fractional GPU
- ECS Exec
- gang scheduling
- EFA
- three-way comparison
- Karpenter
- AWS Batch
tags:
- architecture
- comparison
category: architecture
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- ecs architecture
- ecs managed instances architecture
- three way architecture comparison
- ecs vs batch vs karpenter
- can we use ecs instead
---

# Alternative Architecture — Amazon ECS

> **TL;DR:** ECS is the most *operationally* appealing of the three options and the worst fit for what this project has to prove. It gives genuinely zero Kubernetes, the most managed GPU fleet in AWS, fractional GPUs, and — unlike Batch — a real interactive shell and a viable persistent Ray cluster. But **ECS Managed Instances exposes no custom AMI, no placement group and no userdata**, which removes EFA, host-mounted FSx and NVMe staging; and ECS has **no gang-scheduling primitive at all**. Multi-node training therefore needs self-managed capacity or Batch MNP underneath. **Recommendation: not for Phase 1.** Its real niche is single-node work — preprocessing, and a Phase 2 inference tier.
> **Use this for:** Evaluating ECS against [[Recommended Architecture - Surrogate ML Accelerator]] and [[Alternative Architecture - AWS Batch]], and §6 for the three-way comparison.

> ⚠️ **Requirements update, 2026-10-19 — this option is no longer disqualified.** [[2026-10-19 Research Workload Q&A - Deepak Akhare]] states **multi-server training is not currently required**. ECS was ruled out in §1 and §8 on the absence of a gang-scheduling primitive; if single-node training is the Phase 1 target, that objection falls away, as do the EFA and placement-group limitations of Managed Instances (§2.1). Its strengths — zero Kubernetes, the most managed GPU fleet, fractional GPU, and a real shell — now apply against a workload it can actually serve. **The §8 recommendation should be re-read in that light**, and the CPU-heavy preprocessing and video stages are squarely in its wheelhouse.

**Status: third alternative, for comparison.** See [[aws-batch-ecs-vs-karp-ray-flyte]] §6.7 for the underlying analysis of why the proposed stack cannot be relocated to ECS.

---

## 1. What necessarily changes

ECS is not EKS with a different control plane. Three components of the recommended architecture do not survive the move:

| Component | On ECS | Why |
|---|---|---|
| **Karpenter** | ❌ **Cannot run** | It watches *unscheduled pods* through the Kubernetes API and is configured entirely through CRDs (`NodePool`, `EC2NodeClass`). ECS has no pods, no Kubernetes API, no CRDs. |
| **Flyte** | ❌ **Cannot run in production** | [FlytePropeller is "a Kubernetes native operator"](https://github.com/flyteorg/flytepropeller) that executes workflows by creating Kubernetes resources. `pyflyte run` is a local dev loop, not a deployment target. |
| **Argo (either)** | ❌ **Cannot run** | Argo Workflows and Argo CD are both Kubernetes controllers. The kickoff's EKS/Ray/Argo mandate cannot be satisfied on ECS at all. |
| **Ray** | ⚠️ **Runs, hand-rolled** | Ray is processes over IP. See §3.2 — it fares *better* here than under Batch. |

**The decisive structural gap is gang scheduling.** Starting N tasks together, as a unit, with inter-node communication, is not an ECS primitive — which is exactly why AWS Batch multi-node parallel jobs exist. For tightly-coupled multi-node training you either build gang scheduling yourself or run Batch MNP on top of ECS, at which point this becomes [[Alternative Architecture - AWS Batch]].

---

## 2. Which ECS — and the fork that decides everything

ECS offers two capacity models, and **the choice is not cosmetic**.

### 2.1 ECS Managed Instances

GA across commercial regions since October 2025. AWS owns instance provisioning, **NVIDIA driver management**, AMI updates, patching and scaling; [GPU health monitoring and auto-repair](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ecs-gpu-auto-repair/) is on by default, [fractional GPU scheduling on G6f](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecs-fractional-gpu/) is available, and AWS publishes a [scale-to-zero GPU pattern](https://aws.amazon.com/blogs/containers/run-gpu-batch-inference-on-amazon-ecs-managed-instances-with-scale-to-zero/).

**What the capacity provider actually exposes** ([the API](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-capacity-provider-managed-instances.html)) is a short list: `instanceRequirements` (vCPU, memory, instance types, CPU manufacturer, accelerator type and count), `networkConfiguration` (subnets, security groups), `storageConfiguration` (`storageSizeGiB`), an instance profile, and monitoring level.

**What it does not expose is the problem:**

| Not configurable | Consequence for this workload |
|---|---|
| **Custom AMI** | No EFA-enabled AMI with a driver stack you control |
| **Cluster placement group** | No low-latency placement for multi-node collectives |
| **Instance userdata** | No RAID/mount of instance-store NVMe; no host-mounted FSx for Lustre |

So **ECS Managed Instances cannot do multi-node distributed training**, and cannot stage data on the p5's ~30 TB of local NVMe. For single-node GPU work it is excellent — arguably the most managed GPU compute on AWS.

### 2.2 ECS with self-managed capacity (ASG-backed capacity provider)

You supply the launch template: custom EFA-enabled AMI, cluster placement group, userdata for NVMe and FSx. **This is the only ECS path that can do multi-node training.**

The cost is everything Managed Instances was giving you: you own the AMI, the NVIDIA drivers, patching and node health, and scaling reverts to ASG evaluation loops (minutes, with cooldowns) rather than the managed model.

### 2.3 The resulting shape

| | Managed Instances | Self-managed ASG |
|---|---|---|
| Single-node GPU training | 🏆 Excellent | Works |
| **Multi-node training** | ❌ **Impossible** | Possible, undocumented (§4.2) |
| Fleet operations | AWS owns it | You own it |
| Scaling latency | Managed, scale-to-zero | ASG loops + cooldown |
| Fractional GPU | ✅ G6f | — |

**A realistic ECS build uses both**: Managed Instances for CPU and single-node GPU work, self-managed capacity for anything multi-node. Two capacity models to operate, which erodes the "simplicity" argument that motivates ECS in the first place.

---

## 3. The ECS stack

| Layer | Component | Note |
|---|---|---|
| **Cluster** | One ECS cluster | — |
| **CPU + single-node GPU** | **Managed Instances** capacity provider, `accelerator type: gpu` | Scale-to-zero, AWS-managed drivers |
| **Multi-node GPU** | **Self-managed ASG** capacity provider: EFA AMI, placement group, userdata | Only if multi-node is required (§4.2) |
| **Interactive** | Long-lived CPU **ECS service** + **ECS Exec** | A genuine shell — ECS's `kubectl exec` equivalent |
| **Distributed runtime** | **Ray cluster as ECS services** (head + workers), or `torchrun` per task | §3.2 |
| **Service discovery** | **Cloud Map / ECS Service Connect** | How Ray workers find the head |
| **Orchestration** | **Step Functions** (native `RunTask` integration) or **MWAA** | No Flyte, no Argo |
| **Data** | S3 + DataSync; FSx for Lustre **only on self-managed capacity** | §4.3 |
| **Images** | ECR | Unchanged |
| **Telemetry** | **CloudWatch Container Insights** + **DCGM exporter as a DAEMON service** | Container Insights is native |
| **IaC** | **Terraform throughout** | No Argo CD; CI/CD via CodePipeline or GitHub Actions |
| **Tracking** | MLflow as an ECS service | Unchanged |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESEARCHER                                                                 │
│  laptop ──SSM/ECS Exec──► dev task (CPU, long-lived, real shell)            │
│                            └─ ray job submit ──┐  ← interactive loop intact │
└────────────────────────────────────────────────┼────────────────────────────┘
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ECS CLUSTER                                                                │
│                                                                             │
│  ┌── Managed Instances capacity provider ─────────────────────────────┐     │
│  │   Ray head service + Ray worker service (long-lived)               │     │
│  │   single-node GPU tasks · preprocessing · fractional GPU (G6f)     │     │
│  │   AWS owns AMI, drivers, patching, GPU auto-repair                 │     │
│  │   ✗ no custom AMI · ✗ no placement group · ✗ no userdata           │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌── Self-managed ASG capacity provider (only if multi-node) ─────────┐     │
│  │   EFA AMI · cluster placement group · NVMe + FSx via userdata      │     │
│  │   gang scheduling: build it, or run Batch MNP here                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  DCGM daemon service · Container Insights · MLflow · Step Functions         │
└──────────────┬──────────────────────────────────────────────────────────────┘
               ▼
    S3 ◄──DataSync──► Alpharetta      (FSx Lustre only on self-managed)
```

### 3.2 Ray on ECS fares better than Ray on Batch

Worth stating plainly, because it is the strongest point in ECS's favour:

**ECS services are long-lived.** A Ray head service plus a Ray worker service, with Cloud Map discovery, gives a **persistent Ray cluster** — so `ray job submit` works against a live cluster, iteration stays in seconds, and the Ray Dashboard is a running service. That is precisely the interactive loop AWS Batch destroys (see [[Alternative Architecture - AWS Batch]] §4.1).

Two caveats keep it honest:

1. **No ECS node provider exists for the Ray autoscaler.** Scaling the worker service is manual, or custom Application Auto Scaling against a metric you define. KubeRay's autoscaling worker groups have no equivalent.
2. **Ray tolerates elastic membership**, so ECS's missing gang scheduling hurts Ray far less than it hurts `torchrun`/MPI. Ray Train waits for its placement group before starting. Pre-scale the worker service, then submit.

**If Ray is retained anywhere outside EKS, ECS is the better host of the two alternatives.**

---

## 4. The four things that need solving

### 4.1 Gang scheduling — there is no primitive

ECS can start N tasks; it cannot start them *as a unit*, guarantee co-scheduling, pass peer addresses, or fail them together. Options:

- **Build it** — a controller that launches N tasks, waits for all `RUNNING`, distributes peer IPs via Cloud Map, and tears down on partial failure. This is re-implementing AWS Batch MNP.
- **Run Batch MNP on ECS compute environments** — supported and documented, and converges on [[Alternative Architecture - AWS Batch]].
- **Avoid multi-node entirely** — a p5.48xlarge holds 8 × H100 (640 GB HBM). If the surrogate models fit, single-node training sidesteps all of this. **But the kickoff explicitly calls for "a multi-node, high-performance computing approach"**, so this is a scope conversation, not an engineering shortcut.

### 4.2 EFA — undocumented on ECS, and blocked on Managed Instances

AWS publishes no ECS-specific EFA guide. The mechanism almost certainly works the same way Batch documents it for its ECS-style job definitions — a `linuxParameters.devices` passthrough of `/dev/infiniband/uverbs0`, an EFA-enabled AMI, and a security group allowing all traffic to and from itself — because Batch-on-ECS jobs *are* ECS tasks underneath.

But all three of those requirements need the launch template, **so EFA is unavailable on Managed Instances entirely** (§2.1). Multi-node training on ECS therefore requires self-managed capacity *and* an undocumented configuration. **Treat as a required spike.**

### 4.3 Storage — no host mounts on Managed Instances

FSx for Lustre on ECS is mounted on the host and bind-mounted into tasks, which needs userdata. On Managed Instances that is unavailable, leaving:

- **Mountpoint for Amazon S3** inside the container, or
- direct S3 reads with in-container staging to the EBS root volume (`storageSizeGiB`).

Neither reaches FSx throughput, and the p5's local NVMe cannot be RAIDed or mounted. **The data path is the second casualty of the Managed Instances model**, after EFA.

### 4.4 Interactive access — ECS's genuine strength

`aws ecs execute-command` gives a real shell inside a running task, audited through SSM, with no inbound ports. Combined with a long-lived CPU dev service, this satisfies the kickoff's "shell/SSH over complex web UIs" priority **better than Batch and comparably to EKS**.

---

## 5. Additional tooling ECS requires

| Need | Tool | Why |
|---|---|---|
| DAG orchestration | **Step Functions** (native ECS integration) or **MWAA** | Flyte and Argo Workflows are both Kubernetes |
| GitOps | **Terraform + CodePipeline / GitHub Actions** | Argo CD is Kubernetes |
| Service discovery | **Cloud Map / Service Connect** | How Ray workers find the head |
| Gang scheduling | **Custom controller, or Batch MNP** | No ECS primitive (§4.1) |
| Multi-node capacity | **Self-managed ASG capacity provider** | Managed Instances cannot (§2.1) |
| Shared storage | **Mountpoint for S3**, or FSx on self-managed capacity | §4.3 |
| GPU telemetry | **DCGM exporter as a DAEMON-strategy service** | ECS supports daemon scheduling |
| Multi-tenancy (Phase 2) | **Build it** — ECS has no queue or fair-share primitive | Weaker than Batch here |

Unchanged from the other designs: S3, DataSync, ECR, MLflow, CloudWatch, Prometheus/Grafana.

---

## 6. Three-way comparison

| Dimension | **Karpenter + Ray** | **AWS Batch** | **Amazon ECS** |
|---|---|---|---|
| **Interactive loop** | 🏆 Seconds, persistent cluster | ❌ Minutes, submit-and-wait | 🥈 Seconds via persistent Ray services |
| **Shell access** | 🏆 `kubectl exec` + dev pods | 🥈 Dev pods, but no GPU shell | 🏆 **ECS Exec** — real shell, audited |
| **Gang scheduling** | 🏆 Ray/KubeRay native | 🏆 **MNP, built in** | ❌ **No primitive at all** |
| **Multi-node training** | 🏆 EFA documented on EKS | 🥈 EFA on EKS undocumented; documented on ECS path | ⚠️ Needs self-managed capacity + undocumented config |
| **EFA on managed capacity** | ✅ Karpenter `EC2NodeClass` | ✅ Batch launch template | ❌ **Not on Managed Instances** |
| **Custom AMI / placement group / userdata** | ✅ Full control | ✅ Launch template | ❌ **None on Managed Instances** |
| **Local NVMe staging** | ✅ Node bootstrap | ✅ Launch template | ❌ Not on Managed Instances |
| **FSx for Lustre** | ✅ | ✅ (spike) | ⚠️ Self-managed capacity only |
| **Scheduler operations** | ❌ Ray + Karpenter, yours | 🏆 Fully managed | 🥈 None, but no scheduler either |
| **GPU fleet operations** | ❌ Drivers, AMIs, health yours | 🥈 AWS manages the CE | 🏆 **Most managed** — auto-repair default |
| **Fractional GPU** | ❌ Whole GPUs | ❌ Whole GPUs | 🏆 **G6f, down to ⅛ L4** |
| **Fair-share multi-tenancy** | ❌ Hand-built quotas | 🏆 **Native scheduling policies** | ❌ **Nothing** — build it |
| **Pend-time metrics** | ❌ Build from Prometheus | 🏆 **Native CloudWatch** | ⚠️ No queue, so no queue metric |
| **Spot eligibility** | 🏆 Yes | ❌ Not for MNP | 🏆 Yes |
| **Scale-to-zero** | ✅ Consolidation | ✅ `minvCpus: 0` | ✅ Managed Instances |
| **Ray** | 🏆 KubeRay, full platform | ❌ Hand-bootstrapped, execution only | 🥈 Persistent cluster, no autoscaler |
| **Flyte** | ✅ Native | ❌ Impossible | ❌ Impossible |
| **Argo (mandate)** | ✅ Both | ⚠️ CD only, on the EKS path | ❌ **Neither** |
| **Tri-environment parity** | 🏆 Mac / AWS / on-prem | ❌ AWS only | ❌ AWS only |
| **Kubernetes expertise needed** | ❌ Yes | ⚠️ Yes, on Batch-on-EKS | 🏆 **Genuinely none** |
| **Security review surface** | ❌ Largest | 🥈 Moderate | 🏆 **Smallest** |
| **Phase 2 SMaaS fit** | 🥈 Build namespaces + quotas | 🏆 **Fair-share is the primitive** | ❌ Weakest — nothing to build on |
| **Fit to the kickoff mandate** | 🏆 EKS/Ray/Argo as stated | ⚠️ Partial | ❌ Satisfies none of the three |

### What the table says

- **Karpenter + Ray** wins research velocity, the stated mandate, and portability.
- **AWS Batch** wins managed scheduling, fair-share and Phase 2 multi-tenancy.
- **ECS** wins operational simplicity, GPU fleet management, fractional GPU and shell ergonomics — and loses precisely where this project's headline deliverable lives.

**ECS is strongest on the axes nobody is grading and weakest on the one they are.** The phase is judged on linear multi-node scaling; that is the single thing ECS cannot do without either self-managed capacity on an undocumented EFA path, or Batch MNP underneath.

---

## 7. Pros, cons and limitations

### Genuine advantages
* **No Kubernetes at all** — the only option of the three that truly delivers this. Batch-on-EKS still requires an EKS cluster. Real for a 1.0 + 0.5 + 0.5 FTE team under a 24-hour unblock commitment.
* **The most managed GPU fleet on AWS** — AWS owns AMIs, NVIDIA drivers, patching, and GPU health with auto-repair enabled by default.
* **Fractional GPU on G6f** — down to ⅛ of an L4. Unique among the three, and genuinely useful for dev boxes and small-model experimentation.
* **ECS Exec gives a real, audited shell**, satisfying the kickoff's third strategic priority.
* **A persistent Ray cluster is viable** (§3.2), so the interactive loop survives — unlike Batch.
* **Smallest security-review surface** for GWD: no cluster components, no operators, no CRDs.
* **Native Container Insights**, and scale-to-zero on Managed Instances.

### Costs and hard limitations
* **Karpenter, Flyte, Argo Workflows and Argo CD cannot run.** The kickoff named EKS, Ray and Argo; ECS satisfies none of the three.
* **No gang-scheduling primitive** (§4.1) — the capability the project exists to demonstrate.
* **Managed Instances exposes no custom AMI, placement group or userdata**, which removes EFA, host-mounted FSx and NVMe staging in one stroke (§2.1).
* **EFA on ECS is undocumented by AWS** and requires self-managed capacity (§4.2).
* **Two capacity models** to operate if multi-node is required, undermining the simplicity argument.
* **No Ray autoscaler integration** — worker scaling is manual or custom.
* **No queue, therefore no pend-time metric** — the number the kickoff wants driven to zero has no native source here, unlike Batch.
* **No fair-share primitive**, making ECS the weakest of the three for Phase 2 SMaaS multi-tenancy.
* **Tri-environment parity is gone** — no Mac, no KinD, no on-prem, violating the invariant in [[aws-batch-ecs-vs-karp-ray-flyte]] §5.

---

## 8. Recommendation

**Do not adopt ECS for Phase 1.** It cannot deliver the Scaling Benchmark Report without either self-managed capacity on an undocumented EFA path or Batch MNP underneath — and in the second case you have chosen the Batch architecture with extra steps.

**Where ECS genuinely earns a place:**

1. **A preprocessing and mesh-generation tier.** Large numbers of independent single-container CFD runs, scale-to-zero, no gang scheduling needed, AWS managing the fleet. This is ECS at its best and could sit alongside either primary architecture.
2. **A Phase 2 inference tier.** Fractional GPU on G6f is a strong fit for serving trained surrogate models cheaply — the whole-GPU granularity of the other two options is wasteful for inference.
3. **A fallback if Kubernetes is rejected organizationally.** If GWD or CTO/HQ will not accept an EKS cluster, ECS is the better of the two non-Kubernetes paths for *interactive* work, and Batch the better one for *throughput*.

**If ECS is mandated for Phase 1 anyway**, the honest plan is: Managed Instances for everything single-node, self-managed ASG capacity for the multi-node benchmark, Ray as persistent ECS services, Step Functions for DAGs — and spike S1 and S3 below before committing to a date.

---

## 9. Spikes required before committing

1. **Does EFA work on ECS tasks at all**, via `linuxParameters.devices` passthrough with a self-managed EFA AMI and placement group? Undocumented. **Blocks multi-node training.**
2. **Confirm Managed Instances cannot supply a custom AMI, placement group or userdata** — this document reads that from the capacity-provider API surface; verify against the live API before designing around it.
3. **Measured single-node 8-GPU performance** — if the surrogate models fit in 640 GB HBM, §4.1's third option becomes a legitimate scope conversation.
4. **Ray-as-ECS-services**: head/worker discovery via Cloud Map, worker scaling, and behaviour when a worker task is replaced mid-job.
5. **Mountpoint for S3 throughput** at training I/O rates, since FSx is unavailable on Managed Instances.

---

## 10. Related

* [[Recommended Architecture - Surrogate ML Accelerator]] — the primary recommendation
* [[Alternative Architecture - AWS Batch]] — the second alternative; ECS converges on it for multi-node work
* [[aws-batch-ecs-vs-karp-ray-flyte]] §6.7 — why the proposed stack cannot be relocated to ECS
* [[2026-10-12 Research Team Kickoff]] — the EKS/Ray/Argo mandate ECS cannot satisfy
* [[Risks & Open Questions]] · [[Decisions Log]]

**External sources (verified 2026-10-15):**
* [Creating a capacity provider for ECS Managed Instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-capacity-provider-managed-instances.html) — the configurable surface, and what it omits
* [Amazon ECS Managed Instances](https://aws.amazon.com/ecs/managed-instances/) · [GA across commercial regions](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-ecs-managed-instances-commercial-regions/)
* [GPU health monitoring and auto repair](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ecs-gpu-auto-repair/)
* [Fractional GPU scheduling with G6f](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecs-fractional-gpu/)
* [GPU batch inference on ECS Managed Instances with scale to zero](https://aws.amazon.com/blogs/containers/run-gpu-batch-inference-on-amazon-ecs-managed-instances-with-scale-to-zero/)
* [Elastic Fabric Adapter with AWS Batch](https://docs.aws.amazon.com/batch/latest/userguide/efa.html) — the ECS-style device passthrough this infers from
* [FlytePropeller](https://github.com/flyteorg/flytepropeller) — "a Kubernetes native operator"
