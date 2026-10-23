---
title: Phase 1 Execution Plan — AWS Batch Architecture Variant
description: Detailed Phase 1 execution plan if the AWS Batch alternative architecture is adopted, with a workstream delta against the existing plan and the Karpenter variant
keywords:
- Phase 1 execution plan
- AWS Batch
- multi-node parallel
- MNP
- fair-share scheduling
- EFA spike
- workstreams
- milestones
tags:
- plan
- deliverable
category: planning
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- phase 1 execution plan batch
- aws batch delivery plan
- batch variant execution plan
- batch phase 1 schedule
phase: 1
window: 2026-10-01 → 2026-11-30
variant_of: Phase 1 Project Plan.md
---

# Phase 1 Execution Plan — AWS Batch Architecture Variant

> **TL;DR:** A variation of [[Phase 1 Project Plan]] for the case where [[Alternative Architecture - AWS Batch]] is adopted. Like the Karpenter variant, **D8 is satisfied structurally** — Batch is burstable by construction. Unlike it, this plan carries a **hard decision gate in week 3**: EFA on Batch-on-EKS is undocumented, and if it fails the architecture must fall back to Batch on EC2/ECS, abandoning Kubernetes mid-phase. In exchange you get managed scheduling, native pend-time metrics, and a far better Phase 2 SMaaS foundation — at the cost of the interactive loop the research team ranked first.
> **Use this for:** Executing Phase 1 if Batch is mandated, and for comparing delivery risk against [[Phase 1 Execution Plan - Recommended Architecture]].

**Status: variant, not a replacement.** [[Phase 1 Project Plan]] remains authoritative. §1 is the delta; §2 is the decision gate that makes this plan different from either alternative; §4 onward is the plan itself.

**Two decisions required before this plan can start:** §10.1 (does Batch satisfy a deliverable worded "3 static servers"?) and §10.2 (is the research team's stated iteration experience negotiable?).

---

## 1. What changes against the existing plan

### 1.1 The structural change — same direction, different mechanism

The existing plan builds static servers first and the burst layer last, in weeks 7–8. Batch, like Karpenter, removes that sequencing problem — but more literally:

```
WS1 landing zone → WS2 Batch compute environment + job queues → researchers submitting (wk 4)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        D8 is satisfied here. AWS Batch IS a managed
                        burstable compute offering — arguably the most
                        literal possible reading of the deliverable.
```

**D8 arguably reads better under Batch than under any other option.** "Design, build, and deploy the infrastructure required to support the Burstable MLaaS offering" is satisfied by a managed, queue-driven, scale-to-zero GPU service. If the goal is the least contestable D8 evidence, this is it.

### 1.2 Deliverable-by-deliverable delta

| # | SOW deliverable | Existing plan | This variant | Net |
|---|---|---|---|---|
| **D1** | 3 static servers / 24 GPUs | 3 × EC2, running | Batch compute environment, `minvCpus` holding a warm floor against an ODCR | ⚠️ Wording risk (§10.1), eased by the warm floor |
| **D2** | File transfer | DataSync + FSx/EFS | Same; **FSx mount into Batch-on-EKS pods is a spike** (§2) | ⚠️ Unproven |
| **D3** | CLI/shell/script access | SSM vs bastion vs SSH | SSM → **dev pods on a separate platform node group** | ⚠️ Shell, but **not a shell on a GPU** |
| **D4** | Stack parity | Golden AMI | Container image in ECR | ✅ |
| **D5** | Cyber / auth | IdP federation, blocked | IAM + SSM + Batch IAM; IdP deferred to Phase 2 | ✅ Unblocks |
| **D6** | Training packages | Installed on AMI | Baked into the image | ✅ |
| **D7** | Equivalent multi-GPU training | One test | **Two tests**, and Test B depends on the EFA spike | ⚠️ Gated |
| **D8** | Burstable infrastructure | WS7, weeks 7–8 | **Structural, week 4 — and the most literal reading** | ✅ Strongest D8 evidence of the three plans |

### 1.3 Workstream delta

| Workstream | Status | Change |
|---|---|---|
| WS0 Access & onboarding | Unchanged | Still the Day-0 blocker |
| **WS-S Spikes** | **NEW, front-loaded** | Five unknowns that gate the architecture (§2) |
| WS1 Landing zone | Extended | EKS prerequisites plus a single-AZ subnet and cluster placement group for MNP |
| WS2 Static GPU compute | **Rewritten** | Batch compute environment, queues, scheduling policies, job definitions |
| WS3 Access & auth | **Split in two** | A separate always-on interactive tier, because Batch has no interactive mode |
| WS4 File transfer | Extended | Adds the FSx-into-Batch-pods spike |
| WS5 Stack parity | **Re-based** | Container image; adds the MNP entrypoint contract |
| WS6 Training validation | Extended | Two tests; Test B gated on the EFA spike |
| WS7 Burst infrastructure | **Absorbed into WS2** | Replaced by a distributed-runtime workstream |
| WS8 Documentation | Extended | Must cover the submit-and-wait model, which is new to researchers |
| **WS9 Observability** | **NEW, partly free** | DCGM DaemonSet on Batch nodes; **CloudWatch already emits queue depth and pend time** |
| **WS10 IaC & Lab Notebook** | **NEW, Terraform-weighted** | Batch resources are not Kubernetes objects, so Argo CD covers only the platform tier |

### 1.4 Against the Karpenter variant

For direct comparison with [[Phase 1 Execution Plan - Recommended Architecture]]:

| | Karpenter variant | **Batch variant** |
|---|---|---|
| Researchers on a GPU | Week 4 | **Week 4–5** (interactive tier first, then queue) |
| D8 evidence | Week 3 | **Week 4**, but a stronger reading |
| Architecture-pivot risk | None | **Week 3 gate — EFA spike can force a rebuild** |
| Iteration loop | Seconds (persistent Ray cluster) | **Minutes** (submit → provision → bootstrap → run) |
| Scheduler to operate | Ray + Karpenter, yours | **Managed, none** |
| Pend-time evidence | Build it from Prometheus | **Native CloudWatch** |
| Phase 2 SMaaS foundation | Namespaces and quotas, hand-built | **Fair-share scheduling policies, built in** |
| Total estimate | ~59 person-days | **~62 person-days** |

---

## 2. The decision gate — spikes first *(this plan's defining feature)*

Five unknowns sit under this architecture, and one of them can invalidate it. **All five run in weeks 2–3, before any dependent build starts.**

| # | Spike | Why it gates | Owner | Est. | Deadline |
|---|---|---|---|---|---|
| **S1** | **Does EFA work on Batch-on-EKS MNP jobs?** AWS documents EFA for Batch only on the ECS/EC2 path (`linuxParameters.devices`, `/dev/infiniband/uverbs0`); EKS has a separate mechanism (`vpc.amazonaws.com/efa` device plugin). The combination is undocumented | **Blocks linear scaling — the headline deliverable.** Failure forces Batch on EC2/ECS, abandoning Kubernetes, Argo and the dev-pod tier | Chris | 3d | **2026-10-23** |
| **S2** | Can a Batch compute environment target the ODCR via launch-template capacity reservation targeting? | Without it, reserved capacity goes unused and cost assumptions break | Nam | 1d | 2026-10-23 |
| **S3** | **Measured iteration latency** — submit-to-first-log for a 2-node p5 MNP job, cold and warm | Decides whether researchers accept the model at all (§10.2) | Chris | 1d | 2026-10-23 |
| **S4** | Does FSx for Lustre mount cleanly into Batch-on-EKS job pods? | Gates the training data path | Rick | 1d | 2026-10-30 |
| **S5** | Does the Ray-on-MNP bootstrap survive mid-job node failure, and what is the retry behaviour? | Only if Ray is retained (§5, WS7) | Chris | 1d | 2026-10-30 |

### Gate outcomes

| S1 result | Consequence |
|---|---|
| **Works** | Proceed as written. Kubernetes retained; Argo, dev pods and MLflow keep their home |
| **Fails** | **Fall back to Batch on EC2/ECS.** EFA is documented there. Cost: no Kubernetes at all — the platform tier moves to plain EC2 or ECS, Argo Workflows has no home, the dev-pod design is rebuilt on EC2 + SSM, and the EKS/Ray/Argo mandate from the kickoff is abandoned outright. **Estimated rework: 6–8 person-days, landing in week 4** |

> **This gate is the single most important difference between this plan and either alternative.** Neither the existing plan nor the Karpenter variant carries a mid-phase architecture-pivot risk. Budget for it explicitly rather than discovering it in November.

**If S1 has not returned a clear answer by 2026-10-23, escalate rather than proceeding on optimism.** A pivot decided in week 3 is recoverable; the same pivot discovered in week 6 is not.

---

## 3. Execution model

### 3.1 Ownership

| Workstream | Lead | Support | Est. person-days |
|---|---|---|---|
| WS0 Access & onboarding | [[Nam Park]] | — | 3 |
| **WS-S Spikes** | [[Chris Burke]] | [[Nam Park]], [[Rick Allen]] | 7 |
| WS1 Landing zone | [[Nam Park]] | [[Chris Burke]] | 5 |
| WS2 Batch compute & queues | [[Chris Burke]] | [[Nam Park]] | 8 |
| WS3a Interactive tier | [[Nam Park]] | — | 4 |
| WS3b Access & auth | [[Nam Park]] | — | 3 |
| WS4 Data path | [[Rick Allen]] | [[Nam Park]] | 8 |
| WS5 Image & MNP contract | [[Rick Allen]] | [[Chris Burke]] | 6 |
| WS6 Validation & benchmark | [[Chris Burke]] | [[Nam Park]] | 8 |
| WS7 Distributed runtime | [[Chris Burke]] | [[Rick Allen]] | 4 |
| WS9 Observability | [[Rick Allen]] | — | 3 |
| WS10 IaC & Lab Notebook | [[Rick Allen]] | [[Nam Park]] | 3 |
| WS8 Documentation | [[Rick Allen]] | all | 5 |
| | | **Total** | **~67 person-days (~536 h)** |

~536 hours against ~620 available leaves **~13% buffer — materially tighter than the Karpenter variant's 25%**, and that is *before* the 6–8 day pivot contingency in §2. If S1 fails, this plan is over capacity and scope must be cut; the honest candidate is WS7's Ray retention (§5, WS7).

### 3.2 Cadence

As [[Phase 1 Execution Plan - Recommended Architecture]] §2.2, with one addition: **a go/no-go review on 2026-10-23** covering S1–S3, minuted, with the pivot decision recorded in [[Decisions Log]] either way.

### 3.3 Conventions

- **Terraform owns Batch.** Compute environments, queues, scheduling policies and job definitions are AWS resources, not Kubernetes objects — Argo CD cannot reconcile them. This splits the IaC story across two tools, which WS10 must document clearly.
- **Two queues, always** (§4, WS2) — single-node work never goes through MNP.
- **One image, two execution shapes** — the same container runs as a regular job and as an MNP node, branching on `AWS_BATCH_JOB_NODE_INDEX`.

---

## 4. Workstreams

### WS0 — Access & onboarding *(prerequisite, unchanged)*

Carried from [[Phase 1 Project Plan]] WS0 in full. Still the Day-0 blocker.

---

### WS1 — Landing zone & network *(5 days)*

Identical to [[Phase 1 Execution Plan - Recommended Architecture]] WS1, with two Batch-specific additions:

| # | Task | Owner | Est. |
|---|---|---|---|
| 1.1–1.7 | As the Karpenter variant: Terraform skeleton, VPC, single-AZ GPU subnet, EKS subnet tagging, VPC endpoints, IAM, logging | Nam | 4d |
| 1.8 | **Cluster placement group** — required for MNP, not merely advisable: AWS states MNP jobs need a cluster placement group in a single AZ | Chris | 0.5d |
| 1.9 | **Security group permitting all inbound and outbound traffic to and from itself** — an explicit EFA requirement | Chris | 0.5d |

**Exit:** `terraform apply` from clean state produces the baseline; placement group and self-referencing security group in place before any MNP spike runs.

---

### WS2 — Batch compute environment & queues *(8 days)* — **replaces the old WS2**

**Objective:** a managed GPU queue that scales from zero, honours the reservation, and never wastes a p5 on a one-GPU job.

| # | Task | Owner | Est. |
|---|---|---|---|
| 2.1 | EKS control plane; **platform managed node group** (2 × small, on-demand, multi-AZ) for dev pods, Argo CD, MLflow, Prometheus. **Must not be Batch-managed** | Chris | 1d |
| 2.2 | Batch service and instance roles; EKS access entry for Batch; RBAC per the AWS Batch on EKS guide | Nam | 1d |
| 2.3 | Managed compute environment: p5.48xlarge, single-AZ subnet, placement group, launch template with EFA driver AMI | Chris | 1.5d |
| 2.4 | **ODCR targeting via launch template** capacity reservation specification *(gated on S2)* | Nam | 0.5d |
| 2.5 | **`minvCpus` warm floor** — keeps a reserved node warm so D1 reads as "servers available" and cold-start latency drops. Tune against the S3 latency result | Chris | 0.5d |
| 2.6 | **Two job queues**: `gpu-single` (regular container jobs, bin-packed) and `gpu-mnp` (multi-node, gang-scheduled) | Chris | 1d |
| 2.7 | **Scheduling policy** with share identifiers per researcher or project, weight factors, compute reservation | Chris | 1d |
| 2.8 | Job definitions: regular (GPU resource requirements) and MNP (`nodeRangeProperties`, EFA device passthrough) | Chris | 1d |
| 2.9 | Validate scale-to-zero above the warm floor; confirm retries and timeouts | Chris | 0.5d |

**Why two queues is not optional.** MNP job nodes are single-tenant — AWS states *"only a single job container is run on each Amazon EC2 instance."* On a p5.48xlarge a one-GPU MNP job therefore occupies **all eight GPUs**. Regular container jobs bin-pack by resource requirement, so eight single-GPU jobs can share a node. Without the split, the utilization headline fails on the most common job shape.

**Exit / verification:**
```
aws batch submit-job --job-queue gpu-single --job-definition train-1gpu   # bin-packs
aws batch submit-job --job-queue gpu-mnp    --job-definition train-mnp \
    --node-overrides numNodes=2                                           # gang-scheduled
aws batch describe-jobs --jobs <id>          # RUNNABLE -> STARTING -> RUNNING
# confirm the node carries the capacity reservation, not on-demand
```
**Capture D8 evidence here**: queue-driven provisioning, scale-to-zero, cost guardrails active.

---

### WS3a — Interactive tier *(4 days)* — **new, and required**

**Objective:** give researchers somewhere to work, because Batch cannot.

| # | Task | Owner | Est. |
|---|---|---|---|
| 3a.1 | Per-researcher dev pod on the platform node group: **CPU-only, long-lived**, PVC home directory, WS5 image | Nam | 1.5d |
| 3a.2 | AWS CLI + Batch submit helpers pre-installed; a `submit` wrapper hiding job-definition boilerplate | Nam | 1d |
| 3a.3 | Log tailing: CloudWatch Logs streamed back to the dev pod so researchers see output without the console | Nam | 1d |
| 3a.4 | Job status helper — queue position, pend time, failure reason — surfacing what researchers will ask about most | Nam | 0.5d |

**This workstream exists only because Batch has no interactive mode.** The kickoff's first strategic priority is Rapid Enablement and its third is shell access over web UIs; Batch serves both worst, and 3a.2–3a.4 are the mitigation. Treat them as deliverable work, not polish — without them the model feels like the ticketing system the kickoff explicitly rejected.

**Exit:** a researcher edits code in a shell, submits with one command, watches logs stream back, and sees why a job is waiting.

---

### WS3b — Access & authentication *(3 days)*

| # | Task | Owner | Est. |
|---|---|---|---|
| 3b.1 | SSM Session Manager with session logging; no inbound 22 | Nam | 1d |
| 3b.2 | IAM: per-researcher submit rights scoped to their queue and share identifier | Nam | 1d |
| 3b.3 | Encryption at rest and in transit; MFA; cyber review with the named GEV approver | Nam | 1d |

**Smaller in-cluster surface than the Karpenter variant** — no Karpenter, no KubeRay operator — which should make the GWD submission marginally easier to defend.

**Exit:** four researchers authenticate, submit under their own identity, and every session and submission is attributable.

---

### WS4 — Data path *(8 days)*

As [[Phase 1 Execution Plan - Recommended Architecture]] WS4, with two changes:

| # | Task | Owner | Est. |
|---|---|---|---|
| 4.1–4.4 | InfoSec request week 1; dataset sizing; S3 buckets; DataSync both directions | Rick | 4d |
| 4.5 | **FSx for Lustre mount into Batch-on-EKS job pods** *(gated on S4)* — volumes in the job definition's podspec | Rick | 2d |
| 4.6 | Per-job data staging pattern: S3 → local NVMe → train → results to S3 | Rick | 1.5d |
| 4.7 | Measure GPU idle during data loading at MNP scale | Rick | 0.5d |

**No Ray object store here.** Without Ray's shared-memory object store and distributed futures, [[Exoshuffle An Extensible Shuffle Architecture|Exoshuffle]] is unavailable — so there is no pipelined shuffle, and the `/dev/shm` and spill tuning from the Karpenter variant does not apply. Staging through local NVMe is the substitute, and 4.7 exists because the input path has fewer ways to hide a stall.

---

### WS5 — Image & MNP entrypoint contract *(6 days)*

| # | Task | Owner | Est. |
|---|---|---|---|
| 5.1 | **Obtain the Alpharetta inventory** — still the blocking input for D4/D6/D7 | Rick | 0.5d |
| 5.2 | Base image: CUDA + cuDNN + NCCL + **EFA libs and `libfabric`**, matching the launch-template AMI driver | Rick | 1.5d |
| 5.3 | Framework layer (PyTorch), pinned; `torchrun` entrypoint | Rick | 1d |
| 5.4 | **MNP entrypoint contract** — branch on `AWS_BATCH_JOB_NODE_INDEX` vs `AWS_BATCH_JOB_MAIN_NODE_INDEX`; children reach the head via `AWS_BATCH_JOB_MAIN_NODE_PRIVATE_IPV4_ADDRESS`; world size from `AWS_BATCH_JOB_NUM_NODES` | Chris | 1.5d |
| 5.5 | Training packages; Ansys CFX if cloud-licensed | Rick | 1d |
| 5.6 | ECR repository, scanning, immutable tags | Rick | 0.5d |

**Note `AWS_BATCH_JOB_MAIN_NODE_PRIVATE_IPV4_ADDRESS` is set only on child nodes**, not the main node — the single most common MNP bootstrap bug.

**Exit:** one image runs correctly as both a single-node job and an MNP node, with NCCL over EFA verified across two nodes.

---

### WS6 — Validation & scaling benchmark *(8 days)*

| # | Task | Owner | Est. |
|---|---|---|---|
| 6.1 | Agree the benchmark: model, dataset, on-prem baseline, tolerance | Chris | 0.5d |
| 6.2 | **Test A — on-prem equivalence** (SOW D7) via a single-node job | Chris | 2d |
| 6.3 | **Test B — linear scaling** 1 → 2 → 4 → 8 → 16 → 24 GPUs (1 → 3 nodes) via MNP *(gated on S1)* | Chris | 3d |
| 6.4 | Input-pipeline check at each scale point | Rick | 1d |
| 6.5 | **Pend-time and utilization pull from CloudWatch** — queue metrics are emitted by the service | Rick | 0.5d |
| 6.6 | Scaling Benchmark Report | Chris | 1d |

**6.5 is cheaper here than in the Karpenter variant.** Batch emits queue depth and job-state transitions natively, so "pend time" — the metric the kickoff wants driven to zero — is a CloudWatch query rather than something to instrument.

---

### WS7 — Distributed runtime *(4 days)*

**Objective:** decide and implement what actually runs inside an MNP job.

| # | Task | Owner | Est. |
|---|---|---|---|
| 7.1 | **Decision: `torchrun` or hand-bootstrapped Ray.** Record in [[Decisions Log]] | Chris | 0.5d |
| 7.2 | `torchrun` + NCCL over EFA path, validated at 2 and 4 nodes | Chris | 2d |
| 7.3 | *If Ray is retained:* head/child bootstrap, readiness wait, teardown on main-node exit *(gated on S5)* | Chris | 1.5d |

> **Recommendation: drop Ray in this architecture.** Ray's value is the persistent cluster, interactive submission, autoscaling worker groups, actors, the dashboard and Ray Data's shuffle — every one of which Batch has already removed. What remains is distributed execution, which `torchrun` does more simply and with far better documentation. Retaining Ray here honours the kickoff's stated stack but buys little engineering value, and it is the first scope to cut if §2's pivot consumes the buffer. **This is a conversation to have with Jim Tallman explicitly, not a decision to make quietly** — he named Ray.

---

### WS9 — Observability *(3 days)* — **partly free**

| # | Task | Owner | Est. |
|---|---|---|---|
| 9.1 | **DCGM exporter DaemonSet on Batch-managed nodes.** AWS explicitly permits DaemonSets there — they are the documented exception to the "no other workloads on Batch nodes" rule | Rick | 0.5d |
| 9.2 | Prometheus + Grafana on the platform node group | Rick | 1d |
| 9.3 | **CloudWatch dashboard: queue depth, RUNNABLE→STARTING duration (pend time), job outcomes** | Rick | 0.5d |
| 9.4 | **Agree the utilization definition in writing** — allocation vs. SM occupancy | Rick | 0.5d |
| 9.5 | Budgets, alarms, cost allocation tags by share identifier | Rick | 0.5d |

One day cheaper than the Karpenter variant, because queue metrics come from the service.

---

### WS10 — IaC & Project Lab Notebook *(3 days)*

| # | Task | Owner | Est. |
|---|---|---|---|
| 10.1 | Terraform modules for compute environments, queues, scheduling policies, job definitions | Rick | 1.5d |
| 10.2 | Argo CD for the **platform tier only** — dev pods, MLflow, Prometheus, DCGM | Rick | 1d |
| 10.3 | Lab Notebook structure; **document the two-tool split** so Phase 2 support knows what lives where | Rick | 0.5d |

**The split IaC story is a real support cost.** Half the platform reconciles through git and Argo CD; the other half changes only through `terraform apply`. Phase 2 is "support & enhance," and an engineer who does not know which half they are touching will reach for the wrong tool.

---

### WS8 — Documentation *(5 days)*

As the Karpenter variant, plus one addition that matters: **the submit-and-wait model is new to these researchers.** Document expected pend times, how to read queue position, why a job is `RUNNABLE` but not `STARTING`, and the two-queue rule. Most Phase 2 support tickets will come from this.

---

## 5. Schedule

| Week | Focus | Milestone |
|---|---|---|
| **Oct 5–9** | Kickoffs. **File every long-lead request** incl. GPU quota + ODCR. Settle server count and funding. Open the InfoSec request | **M0 — external dependencies requested** |
| **Oct 12–16** | WS0 closed out. WS1 landing zone, placement group, EFA security group. **Spikes S1–S3 begin** | **M1 — landing zone applied; spikes underway** |
| **Oct 19–23** | Spikes S1–S3 complete. **Go/no-go review Thu 10/23.** WS2 compute environment and queues begin | **M2 — architecture gate passed (or pivot decided)** |
| **Oct 26–30** | WS2 queues and scheduling policies. WS3a interactive tier. WS5 image + MNP entrypoint. S4, S5 | **M3 — D8 evidence: queue-driven GPU capacity** |
| **Nov 2–6** | WS3a/3b complete; **first researcher submits and trains**. WS4 S3 + DataSync both directions | **M4 — D1 + D3: researchers running jobs** |
| **Nov 9–13** | WS4 FSx and staging; WS5 parity confirmed; cyber sign-off; NCCL/EFA validated at 2–4 nodes | **M5 — D2 + D4 + D5 + D6** |
| **Nov 16–20** | WS6 Test A and Test B; scaling sweep to 24 GPUs | **M6 — D7: both tests run** |
| **Nov 23–27** | Benchmark report; WS8 documentation — **short week, Thanksgiving 11/26–27** | **M7 — Scaling Benchmark Report** |
| **Nov 30** | Closeout and Phase 2 handover | **Phase 1 complete** |

**Compared with the Karpenter variant**, researchers reach a GPU roughly a week later (week 5 vs. week 4), because weeks 2–3 are spent proving the architecture rather than building on it. The back half is otherwise similar — unless S1 fails, in which case weeks 4–5 absorb a 6–8 day pivot and **M4 slips to the week of Nov 9**, leaving no slack before the benchmark.

---

## 6. Milestones & acceptance gates

| ID | Gate | Evidence | Latest acceptable |
|---|---|---|---|
| M0 | External dependencies requested | Written requests with owners and dates | 2026-10-09 |
| M1 | Landing zone + spikes underway | `terraform plan` empty; placement group live | 2026-10-16 |
| **M2** | **Architecture gate** | S1–S3 results; go/no-go minuted in [[Decisions Log]] | **2026-10-23 — hard** |
| M3 | Queue-driven GPU capacity *(D8)* | Submit → provision → run → scale-to-zero transcript | 2026-10-30 |
| M4 | Researchers running jobs *(D1, D3)* | Four researchers, own identities, completed jobs | 2026-11-06 |
| M5 | Data, stack, cyber, packages *(D2, D4, D5, D6)* | Round-trip dataset; parity confirmed; approver sign-off | 2026-11-13 |
| M6 | Both acceptance tests *(D7)* | Raw results, Test A and Test B | 2026-11-20 |
| M7 | Benchmark report | Accepted by GE Vernova | 2026-11-27 |

**M2 is the one that matters.** Miss it, or pass it on an unclear answer, and every date after it is fiction.

---

## 7. Definition of done

**Against the SOW (D1–D8)** — as [[Phase 1 Execution Plan - Recommended Architecture]] §6, with D1 read as *"the agreed GPU count available through the queue, with a warm floor"* (§10.1).

**Against the research team's deliverables** — as the Karpenter variant, with one caveat: the *Operational Sandbox Environment* is delivered as **a shell plus a queue**, not a shell on a GPU. If the research team's expectation is interactive GPU work, this will not meet it however well it is built (§10.2).

**Operational**
- [ ] Two-queue discipline documented and enforced in job definitions
- [ ] Scheduling policy live, with per-researcher share identifiers
- [ ] Pend-time dashboard from CloudWatch; utilization metric defined in writing
- [ ] Terraform/Argo CD split documented for Phase 2 support
- [ ] Measured iteration latency published, so expectations are set by data

---

## 8. Risks — delta from the existing plan

**Retired or reduced**

| Risk | Why |
|---|---|
| D8 scope ambiguity | Batch is a managed burstable offering — the most literal D8 reading available |
| Thanksgiving on the critical path | D8 lands week 4 |
| Unidentified corporate IdP | No web tier in Phase 1 |
| Scheduler operations | Managed by AWS — no Karpenter or Ray tuning to own |

**New or increased**

| Risk | Impact | Mitigation |
|---|---|---|
| **S1 EFA failure forces an architecture pivot** | 6–8 person-days of rework in week 4; Kubernetes, Argo and dev pods abandoned | Spike by 2026-10-23; pre-agree the fallback so the decision is executed, not debated (§2) |
| **Iteration latency rejected by researchers** | The project is judged on researcher velocity; a model they resent is a failed sandbox regardless of uptime | Measure in S3 and publish; invest in WS3a wrappers; set expectations at the weekly meeting early |
| **MNP single-tenancy wastes GPUs** | A one-GPU MNP job consumes eight; the utilization headline fails | Two-queue design (WS2.6), enforced in job definitions and documented for researchers |
| **No Spot for MNP jobs** | Removes the main cost lever against ~$122k/month | Factor into the prepay decision; use Spot for single-node and preprocessing queues only |
| **Capacity buffer is ~13%, before the pivot contingency** | No room for the 24-hour unblock commitment plus a pivot | Pre-agree what gets cut: WS7 Ray retention first (§4, WS7) |
| **Split IaC (Terraform + Argo CD)** | Phase 2 support reaches for the wrong tool | WS10.3; make it the first page of the runbook |
| **Ray retained for mandate reasons rather than engineering ones** | Hand-rolled bootstrap, fragile under node failure, little benefit | Raise with Jim Tallman explicitly — do not drop it quietly |

**Carried unchanged:** GPU quota/capacity, VNDLY onboarding, Alpharetta inventory, benchmark baseline, cost exposure and the prepay decision, Ansys licensing, THOR+ diversion, Phase 2 past the signed term.

---

## 9. What LTI needs from GE Vernova

Items 1–20 of [[Phase 1 Project Plan]] §7 carry over. This variant **adds**:

21. **Decision on the architecture** — Batch or the Karpenter/Ray recommendation.
22. **Written position on §10.1** — does a Batch compute environment satisfy "3 static servers," given Phase 1 excludes scheduling software? **Harder to argue here than in the Karpenter variant**, since Batch *is* a scheduler.
23. **ODCR placed**, with its ID, before WS2.
24. **Acceptance of the iteration model** (§10.2) — the research team should see the S3 latency number and say whether it is workable, before the back half is built on the assumption that it is.
25. **Position on Ray** — retain it hand-bootstrapped on MNP, or drop it for `torchrun`? Jim Tallman named Ray.
26. **Utilization metric definition** — allocation or SM occupancy.
27. **Dataset size** — bridge sizing and staging design.
28. **GWD submission window.**

**21–24 are start-blocking.**

---

## 10. Contract and scope consequences

### 10.1 — "Static servers" versus a managed queue

The same deliverable-wording problem as the Karpenter variant, **with one point in each direction**:

- **Easier:** `minvCpus` holds a warm floor, so reserved nodes genuinely sit available — closer to "static servers" than a scale-to-zero cluster.
- **Harder:** Phase 1 **explicitly excludes scheduling/queuing software**, and AWS Batch is unambiguously a scheduler with job queues. The Karpenter variant can at least argue Ray is a library; that argument is unavailable here.

**Get a written position before WS2.** A Work Scope Amendment started in November does not fit inside the phase.

### 10.2 — The experience gap is a scope question, not a build-quality question

The kickoff asks for researchers working "without waiting for production-level ticketing systems or formal deployment queues." This architecture delivers a job queue. The distinction between a *human approval* queue and a *machine scheduling* queue is real and defensible — but it is a distinction the research team has to accept, not one LTI can assert on their behalf.

**Put the S3 latency measurement in front of Jim Tallman's team and get an explicit answer.** If the number is unacceptable, that is better known in week 3 than discovered in the Phase 1 review.

### 10.3 — Carried forward unchanged

§8.1, §8.2 and §8.3 of [[Phase 1 Project Plan]] apply unchanged.

---

## Related

- [[Phase 1 Project Plan]] — the authoritative plan this varies from
- [[Phase 1 Execution Plan - Recommended Architecture]] — the Karpenter/Ray variant, for comparison
- [[Alternative Architecture - AWS Batch]] — the architecture this executes, and its sourcing
- [[aws-batch-ecs-vs-karp-ray-flyte]] §6 — why Batch and Karpenter cannot be layered
- [[2026-10-12 Research Team Kickoff]] — the vision this must satisfy
- [[Risks & Open Questions]] · [[Decisions Log]]
- Timeline: [[2026-10 October]] · [[2026-11 November]]
