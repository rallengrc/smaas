---
title: Phase 1 Execution Plan — Recommended Architecture Variant
description: Detailed Phase 1 execution plan if the EKS/Karpenter/KubeRay recommended architecture is adopted, with a workstream-level delta against the existing plan
keywords:
- Phase 1 execution plan
- recommended architecture
- EKS
- Karpenter
- KubeRay
- workstreams
- milestones
- acceptance criteria
tags:
- plan
- deliverable
category: planning
classification: 🔵🛡️ GE Vernova Proprietary
last_updated: '2026-10-19'
author: Claude Code (Opus 5) + Nam Park (LTI)
ai_search_aliases:
- phase 1 execution plan variant
- eks phase 1 plan
- recommended architecture delivery plan
- detailed execution plan
phase: 1
window: 2026-10-01 → 2026-11-30
variant_of: Phase 1 Project Plan.md
---

# Phase 1 Execution Plan — Recommended Architecture Variant

> **TL;DR:** A variation of [[Phase 1 Project Plan]] for the case where [[Recommended Architecture - Surrogate ML Accelerator]] is adopted. The headline change: **D8 stops being a late-phase risk**, because under this architecture the burst mechanism *is* the compute substrate rather than a separate build bolted on in week 7. Researchers reach a GPU in week 3, the scaling benchmark gets three weeks instead of one, and Thanksgiving stops sitting on the critical path. The cost is new scope exposure — the SOW describes static EC2 servers and explicitly excludes scheduling software.
> **Use this for:** Comparing delivery approaches before committing, and as the execution plan itself if this architecture is adopted.

**Status: variant, not a replacement.** [[Phase 1 Project Plan]] remains authoritative until GE Vernova decides. This document covers only what changes and the detail needed to execute it; anything not mentioned carries over unchanged. §1 is the delta; §3 onward is the plan itself.

**Decision required before this plan can start:** §9.1 — whether delivering an EKS cluster satisfies a SOW deliverable worded as "3 static servers," given Phase 1 excludes scheduling software.

---

## 1. What changes against the existing plan

### 1.1 The structural change

The existing plan sequences the phase as **static servers first, burst layer last**:

```
WS1 landing zone → WS2 three static EC2 GPU servers → WS3/4/5 → WS6 D7 demo → WS7 burst layer (wk 7-8)
                                                                                 ^^^^^^^^^^^^^^^^^^^^
                                                                      3-4 weeks of work, lands in
                                                                      Thanksgiving week, scope unconfirmed
```

Under the recommended architecture there is no separate burst build, because **Karpenter is how GPU nodes come into existence at all**:

```
WS1 landing zone → WS2 EKS + Karpenter GPU NodePool → WS7 KubeRay → researchers on GPUs (wk 3)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        D8 Reading B is satisfied here, structurally, in week 2
```

**This is the single largest schedule consequence.** D8 — the phase's largest unknown, 2–3 weeks of estimate variance, confirmation still outstanding — ceases to be a discrete deliverable with its own risk. You cannot build this environment *without* building the elastic layer.

### 1.2 Deliverable-by-deliverable delta

| # | SOW deliverable | Existing plan | This variant | Net |
|---|---|---|---|---|
| **D1** | 3 static servers / 24 GPUs | 3 × EC2 provisioned by Terraform, running | Karpenter NodePool against a **3-node ODCR** (settled 2026-10-19); nodes materialize on demand | ⚠️ **Wording risk** — see §9.1 |
| **D2** | File transfer on-prem ↔ AWS | DataSync/Transfer Family + FSx or EFS | Same, plus S3-first with FSx deferred pending the Ray Data path test | ✅ Simpler, possibly cheaper |
| **D3** | CLI/shell/script access | SSM vs bastion vs SSH decision | SSM Session Manager + `kubectl exec` + `ray job submit` | ✅ Decided, no open ports |
| **D4** | Stack parity with Alpharetta | Golden AMI via Packer | Container image in ECR + GPU AMI for driver layer | ✅ Reproducible, portable |
| **D5** | Cyber / auth requirements | IdP federation, blocked on unidentified IdP | IAM + SSM + EKS access entries; **IdP federation deferred to Phase 2** | ✅ Unblocks a blocked item |
| **D6** | Training packages | Installed onto AMI | Baked into the image, versioned | ✅ |
| **D7** | Equivalent multi-GPU training | Single test vs. on-prem baseline | **Two tests** — on-prem equivalence *and* 1→N linear scaling | ⚠️ More work, matches the kickoff |
| **D8** | Burstable infrastructure | WS7, weeks 7–8, scope unconfirmed | **Structural, week 2** | ✅ **Largest risk reduction** |

### 1.3 Workstream delta

| Workstream | Status | Change |
|---|---|---|
| WS0 Access & onboarding | Unchanged | Still the Day-0 blocker |
| WS1 Landing zone | Extended | Adds EKS prerequisites: subnet tagging, OIDC provider, single-AZ GPU subnet, placement group |
| WS2 Static GPU compute | **Rewritten** | EKS + Karpenter + ODCR, replacing three fixed EC2 instances |
| WS3 Access & auth | **Simplified** | SSM + EKS RBAC; no bastion, no SSH, IdP work deferred |
| WS4 File transfer | Extended | Adds Ray object store sizing, `/dev/shm`, NVMe spill; FSx becomes conditional |
| WS5 Stack parity | **Re-based** | Container image rather than golden AMI |
| WS6 Training validation | Extended | Two acceptance tests instead of one |
| WS7 Burst infrastructure | **Absorbed into WS2** | Replaced by a new WS7 for the KubeRay job substrate |
| WS8 Documentation | Unchanged | — |
| **WS9 Observability** | **NEW** | DCGM → Prometheus → Grafana. The existing plan has no telemetry workstream, yet >90% utilization and the benchmark report both require it from day one |
| **WS10 GitOps** | **NEW** | Argo CD. Delivers a large part of the Project Lab Notebook as a by-product |

### 1.4 What gets harder

Honest accounting — this is not free:

1. **Kubernetes operational surface** on a 1.0 + 0.5 + 0.5 FTE team, against a 24-hour unblock commitment. Three EC2 instances are simpler to operate than an EKS cluster.
2. **GWD review of a cluster** is a larger artifact than a review of three instances. The MVP design must pass the CTO/HQ "Base" process; a Kubernetes architecture invites more questions.
3. **New scope exposure.** The SOW says static servers and excludes scheduling software (§9.1).
4. **A new failure mode for researchers.** A pod that will not schedule is harder to self-diagnose than a server that is up — which cuts against "applied ML engineers working independently."
5. **Two new workstreams** (WS9, WS10), ~7 person-days, that the existing plan does not carry.

### 1.5 What gets easier

1. **D8 risk dissolves** (§1.1) — the phase's largest estimate variance disappears.
2. **The unidentified corporate IdP stops blocking Phase 1.** No ALB, no OIDC, no web tier; IAM Identity Center + SSM suffices. The IdP question moves to Phase 2 where the SMaaS tier needs it.
3. **Thanksgiving leaves the critical path.** D8's demo no longer lands in the short week.
4. **Three weeks for the benchmark** instead of one, which matters because the scaling sweep is the deliverable the research team will judge the phase on.
5. **The footprint reads more naturally.** Settled 2026-10-19 at **3 × p5.48xlarge / 24 GPUs**. The deliverable becomes *24 GPUs of addressable reserved capacity* rather than *3 boxes that are always on* — which is also the more defensible reading of D1 (§9.2).

---

## 2. Execution model

### 2.1 Ownership

Allocation is unchanged (~620 person-hours, ~2.0 FTE nominal). Assignment follows the principle in [[Phase 1 Project Plan]] §4 — Nam holds the access-dependent critical path, Chris takes architecture-heavy work while his hours are front-loaded, Rick takes interruption-tolerant tracks.

| Workstream | Lead | Support | Est. person-days |
|---|---|---|---|
| WS0 Access & onboarding | [[Nam Park]] | — | 3 |
| WS1 Landing zone | [[Nam Park]] | [[Chris Burke]] | 5 |
| WS2 EKS + Karpenter + GPU | [[Chris Burke]] | [[Nam Park]] | 8 |
| WS3 Access plane | [[Nam Park]] | — | 4 |
| WS4 Data path | [[Rick Allen]] | [[Nam Park]] | 8 |
| WS5 Image & stack parity | [[Rick Allen]] | [[Chris Burke]] | 6 |
| WS6 Validation & benchmark | [[Chris Burke]] | [[Nam Park]] | 8 |
| WS7 KubeRay job substrate | [[Chris Burke]] | [[Rick Allen]] | 5 |
| WS9 Observability | [[Rick Allen]] | — | 4 |
| WS10 GitOps | [[Rick Allen]] | [[Nam Park]] | 3 |
| WS8 Documentation | [[Rick Allen]] | all | 5 |
| | | **Total** | **~59 person-days (~470 h)** |

~470 hours against ~620 available leaves roughly 25% for the 24-hour unblock commitment, GWD review cycles, and the elastic-scope clause that permits diversion to THOR+ work. **That buffer is not slack — it is already spoken for.**

### 2.2 Cadence

- **Weekly GE Vernova meeting** — Jim Tallman confirmed one is coming ([[2026-10-12 Research Team Kickoff]]). Use it for the §8 ask list, not status theatre.
- **Weekly written status** against §5 milestones. Escalate at an M1/M2 miss, not in the final week.
- **24-hour blocker SLA** — scope undefined (see [[Risks & Open Questions]]). Until bounded, treat it as business-hours best-effort and say so explicitly rather than implying on-call.
- **Project Lab Notebook** updated as work lands, not retrospectively. WS10 makes most of it a by-product of GitOps.

### 2.3 Conventions

- **Everything in Terraform**, from day one. Phase 2 is "support & enhance," which is materially harder against click-ops.
- **Cluster state in git, reconciled by Argo CD** (WS10). No `kubectl apply` from a laptop into the cluster except for break-glass, which gets logged.
- **One image, three targets** — the same container runs on KinD locally, EKS in AWS, and on-prem later. This is the tri-environment invariant from [[aws-batch-ecs-vs-karp-ray-flyte]] §5.
- **No long-lived credentials.** IRSA for workloads, SSM for humans.

---

## 3. Workstreams

### WS0 — Access & onboarding *(prerequisite, unchanged)*

Carried from [[Phase 1 Project Plan]] WS0 in full. Still the **Day-0 blocker**, and the kickoff action item names only Nam and Rick — confirm Chris is covered.

**Exit:** all three engineers run `aws sts get-caller-identity` against the target account.

---

### WS1 — Landing zone & network *(5 days)*

**Objective:** an Org member account with the network, identity and logging baseline that EKS requires, applied from a clean state by Terraform.

| # | Task | Owner | Est. |
|---|---|---|---|
| 1.1 | Terraform skeleton: remote state (S3 + DynamoDB lock), provider pinning, module layout, naming/tagging standard | Nam | 1d |
| 1.2 | VPC: private subnets for GPU nodes, public subnets for NAT egress, route tables | Nam | 1d |
| 1.3 | **Single-AZ GPU subnet + cluster placement group** — the GPU NodePool is constrained to one AZ for inter-node bandwidth (§3.3 of the architecture doc) | Chris | 0.5d |
| 1.4 | Subnet tagging for EKS discovery (`kubernetes.io/role/internal-elb`, `karpenter.sh/discovery`) | Chris | 0.5d |
| 1.5 | VPC endpoints: S3 gateway; ECR API, ECR DKR, STS, SSM, SSM Messages, EC2 Messages as interface endpoints | Nam | 1d |
| 1.6 | IAM: operator roles, researcher role, permission boundaries, no long-lived keys | Nam | 0.5d |
| 1.7 | CloudTrail, AWS Config, CloudWatch log groups with retention | Nam | 0.5d |

**Inputs required:** AWS region decision (§8); LTI's permission level in the account; confirmation the account sits inside the GEV ENT MasterPayer Org.

**Exit:** `terraform apply` from clean state produces the full baseline; `terraform plan` is then empty. SSM interface endpoints are present — **without them Session Manager fails in a private subnet**, which is the most common way WS3 breaks late.

---

### WS2 — EKS cluster & Karpenter GPU capacity *(8 days)* — **replaces the old WS2**

**Objective:** an EKS cluster where a GPU node appears on demand against reserved capacity, and disappears when idle.

| # | Task | Owner | Est. |
|---|---|---|---|
| 2.1 | EKS control plane via Terraform; pin the Kubernetes version; private endpoint access | Chris | 1d |
| 2.2 | System managed node group (2 × small on-demand, multi-AZ) for platform workloads — **must not be Karpenter-managed**, or Karpenter cannot run | Chris | 0.5d |
| 2.3 | EKS access entries for the three LTI engineers and the researcher role (preferred over `aws-auth` ConfigMap) | Nam | 0.5d |
| 2.4 | Karpenter install (Helm, pinned), controller IAM role via IRSA, interruption queue | Chris | 1d |
| 2.5 | `EC2NodeClass` for GPU: AMI family with NVIDIA drivers, instance profile, **single-AZ subnet selector**, placement group, block device mapping | Chris | 1d |
| 2.6 | **`capacityReservationSelectorTerms` targeting the ODCR**; NodePool permits `karpenter.sh/capacity-type: reserved`. Karpenter does **not** support open matching — every ODCR must be named explicitly | Chris | 1d |
| 2.7 | NVIDIA device plugin + EFA device plugin DaemonSets; verify `nvidia.com/gpu` and `vpc.amazonaws.com/efa` are advertised | Chris | 1d |
| 2.8 | Instance-store NVMe: RAID-0, format, mount via node bootstrap — the target for Ray object spilling (WS4) | Nam | 1d |
| 2.9 | Consolidation and disruption policy; `expireAfter`; validate scale-to-zero | Chris | 1d |

**Inputs required:** GPU funding confirmation, region, and the ODCR or ML Capacity Block in place for **3 × p5.48xlarge**. *(Server count settled 2026-10-19 — see [[Decisions Log]].)*

**Exit / verification:**
```
kubectl get nodes                         # system nodes only, at rest
kubectl apply -f gpu-smoke-pod.yaml       # requests nvidia.com/gpu: 8
kubectl get nodes -w                      # a p5 node joins, carrying
                                          #   karpenter.k8s.aws/capacity-reservation-id
kubectl exec gpu-smoke -- nvidia-smi       # 8 × H100 visible
kubectl delete -f gpu-smoke-pod.yaml      # node drains and terminates
```
**D8 Reading B is satisfied at this point** — elastic GPU capacity, provisioned on demand, torn down automatically, with cost guardrails. Capture evidence here for the deliverable rather than rebuilding a demo in week 8.

---

### WS3 — Access plane *(4 days)*

**Objective:** every researcher reaches a shell and submits work under their own identity, with no inbound network exposure.

| # | Task | Owner | Est. |
|---|---|---|---|
| 3.1 | SSM Session Manager: instance profile, session logging to S3/CloudWatch, session document with idle timeout | Nam | 1d |
| 3.2 | Per-researcher dev pod: **CPU-only, long-lived**, home directory on a PVC, image from WS5 | Nam | 1d |
| 3.3 | Kubernetes RBAC: researcher Role/RoleBinding scoped to their namespace; `kubectl exec` permitted, cluster-admin not | Nam | 0.5d |
| 3.4 | `ray job submit` path from the laptop to the Ray head, authenticated | Nam | 0.5d |
| 3.4a | **Submission wrapper CLI** — `mlaas submit / logs / shell`, generating Job manifests so researchers never write Kubernetes YAML ([[Recommended Architecture - Surrogate ML Accelerator]] §3.4.1) | Nam | 1d |
| 3.4b | **Privilege model**: non-root container UID, user-owned venv, namespace-scoped RBAC; scope the profiling and ptrace exceptions for GWD ([[Recommended Architecture - Surrogate ML Accelerator]] §3.4.2) | Nam | 0.5d |
| 3.5 | Encryption at rest (KMS CMKs for EBS/S3), in transit; MFA on the IAM path | Nam | 0.5d |
| 3.6 | Cyber requirements review against the GEV standard, with the named approver | Nam | 0.5d |

**Dev pods are CPU-only by design.** Letting a researcher hold a GPU node to edit files reproduces the on-prem 60–70% utilization problem the project exists to fix.

**Inputs required:** the GE Vernova cybersecurity requirements document and a named approver — unstated since 2026-09-14 and still blocking D5 acceptance.

**Exit:** four named researchers each open a shell, submit a run **without writing a Kubernetes manifest**, get inside a running job, and see their session in the audit log. **No security group permits inbound 22 from anywhere, and no researcher holds root on a node, cluster-admin, or root in their container.**

---

### WS4 — Data path *(8 days)*

**Objective:** data moves between Alpharetta and AWS through an approved path, and arrives at the GPUs fast enough not to starve them.

| # | Task | Owner | Est. |
|---|---|---|---|
| 4.1 | **Open the network/InfoSec approval request in week 1** — historically the slowest external gate in the phase | Rick | 0.5d |
| 4.2 | Obtain dataset size and transfer frequency from Jim's team; size the mechanism against real numbers | Rick | 0.5d |
| 4.3 | S3 buckets: datasets, checkpoints, artifacts. Lifecycle policy, versioning, KMS, bucket policy | Rick | 1d |
| 4.4 | DataSync task over Direct Connect or Site-to-Site VPN; scheduled and on-demand modes; validate both directions | Rick | 2d |
| 4.5 | **Ray object store sizing** — `/dev/shm` as an `emptyDir` with `medium: Memory`, sized deliberately. K8s defaults to 64 MB; left wrong, shuffle silently degrades to disk | Nam | 0.5d |
| 4.6 | **Ray spill to instance-store NVMe** (from 2.8), not overlay fs or EBS | Nam | 0.5d |
| 4.7 | **Benchmark the S3 + Ray Data path** at training I/O rates; measure GPU idle while loading | Rick | 1.5d |
| 4.8 | **FSx for Lustre only if 4.7 proves insufficient** — S3-linked data repository association | Rick | 1.5d |

**4.7 is a go/no-go gate on 4.8.** FSx is a standing cost and a second storage system to operate; buying it before measuring is a decision made in the dark. See [[Recommended Architecture - Surrogate ML Accelerator]] §3.5.1.

**Exit:** a researcher moves a real dataset both directions through an approved path, and a training job sustains GPU utilization without input stalls.

---

### WS5 — Image & stack parity *(6 days)*

**Objective:** one versioned container image that matches Alpharetta closely enough for D7 to mean something, and runs identically on a laptop.

| # | Task | Owner | Est. |
|---|---|---|---|
| 5.0 | **Parity confirmations C1–C4** ([[Recommended Architecture - Surrogate ML Accelerator]] §0.1): how preprocessing and rendering parallelise; whether scripts assume a POSIX filesystem; where ParaView runs | Rick | 0.5d |
| 5.1 | **Obtain the Alpharetta inventory** — OS, NVIDIA driver, CUDA/cuDNN, frameworks, MPI/NCCL, Python manifest, licensed software, filesystem layout | Rick | 0.5d |
| 5.2 | Base image: CUDA + cuDNN + NCCL + EFA libs matching the host driver on the GPU AMI | Rick | 1.5d |
| 5.3 | Ray + framework layer, pinned; Ray version aligned with KubeRay | Rick | 1d |
| 5.4 | Surrogate training packages; Ansys CFX if cloud-licensed | Rick | 1d |
| 5.5 | ECR repository, image scanning, immutable tags, lifecycle policy | Rick | 0.5d |
| 5.6 | **KinD parity check** — same image runs on a laptop with CPU fallback | Chris | 0.5d |
| 5.7 | Multi-GPU plumbing: NCCL all-reduce on 8 GPUs single-node, then across nodes over EFA | Chris | 1d |

**Driver/container split matters.** The NVIDIA driver lives on the host AMI; CUDA and frameworks live in the image. A mismatch fails at runtime, not at build, and usually in week 7.

**Blocking input:** the Alpharetta inventory. Open since 2026-09-14. **D4, D6 and D7 are all undefined without it** — if unanswered by **Friday 2026-10-23**, build to a documented assumed stack and flag the assumption in that week's status.

**Exit:** a reproducible, versioned image whose stack the Architecture team confirms matches Alpharetta, **and C1–C4 answered** so the day-one parity claim rests on evidence rather than assumption ([[Recommended Architecture - Surrogate ML Accelerator]] §0.1).

---

### WS6 — Validation & scaling benchmark *(8 days)* — **two tests, not one**

**Objective:** evidence for both acceptance definitions, which are not the same test.

| # | Task | Owner | Est. |
|---|---|---|---|
| 6.1 | **Agree the benchmark**: model, dataset, on-prem baseline (accuracy *and* wall-clock), tolerance | Chris | 0.5d |
| 6.2 | **Test A — on-prem equivalence** (SOW D7): same model/dataset, compare against the Alpharetta baseline, document deltas and causes | Chris | 2d |
| 6.3 | **Test B — linear scaling** (kickoff): 1 → 2 → 4 → 8 → 16 → 24 GPUs (1 → 3 nodes); wall-clock, throughput, scaling efficiency | Chris | 3d |
| 6.4 | Input-pipeline check at each scale point — confirm the curve bends for compute reasons, not data-loading stalls | Rick | 1d |
| 6.5 | Shuffle spike: epoch time and convergence, Ray Data full shuffle vs. windowed | Rick | 0.5d |
| 6.6 | Scaling Benchmark Report, with method, raw data and caveats | Chris | 1d |

**A flat scaling curve usually means a starved input pipeline, not a bad cluster.** 6.4 exists so that a disappointing result is diagnosed rather than mis-attributed to the architecture.

**Exit:** a written report accepted by GE Vernova, covering both tests. **This is what the phase will be judged on — protect its schedule.**

---

### WS7 — KubeRay job substrate *(5 days)* — **new; replaces the old burst workstream**

**Objective:** the bulletin board. Researchers submit; GPUs attach to jobs, not people.

| # | Task | Owner | Est. |
|---|---|---|---|
| 7.1 | KubeRay operator install, pinned, via Argo CD | Chris | 0.5d |
| 7.2 | `RayCluster`: head on the system node group, GPU worker group with autoscaling, resource requests, tolerations matching the GPU NodePool | Chris | 1.5d |
| 7.3 | Two-level autoscaling validation: pending Ray workers → Karpenter provisions → workers schedule → idle → both scale down | Chris | 1d |
| 7.4 | `RayJob` template for batch and benchmark runs | Rick | 0.5d |
| 7.5 | Ray Dashboard reachable through port-forward or SSM tunnel — **not** a public ALB | Rick | 0.5d |
| 7.6 | Gang-scheduling behaviour under contention; confirm no partial-allocation deadlock | Chris | 1d |

**Exit:** a researcher runs `ray job submit` from a dev pod; GPU nodes appear, the job runs, nodes disappear; a second concurrent job queues and runs without deadlock.

---

### WS9 — Observability *(4 days)* — **new**

**Objective:** make >90% utilization provable, and give the benchmark its instrumentation.

| # | Task | Owner | Est. |
|---|---|---|---|
| 9.1 | DCGM exporter DaemonSet on GPU nodes | Rick | 0.5d |
| 9.2 | Prometheus (or Amazon Managed Prometheus) with retention sized for the phase | Rick | 1d |
| 9.3 | Grafana dashboards: allocation, SM occupancy, queue wait, job duration, cost/day | Rick | 1.5d |
| 9.4 | **Agree the utilization definition in writing** — allocation vs. SM occupancy — before any number is reported | Rick | 0.5d |
| 9.5 | AWS Budgets + alarms; cost allocation tags per researcher/project | Rick | 0.5d |

**9.4 is small and disproportionately important.** Allocation and SM occupancy are both called "utilization"; >90% is achievable as allocation and is **not** a realistic SM-occupancy figure. Undefined, the benchmark report will appear to miss its headline while the platform works correctly.

**Exit:** a dashboard showing per-GPU utilization and queue wait, with the metric definition agreed and written down.

---

### WS10 — GitOps & Project Lab Notebook *(3 days)* — **new**

| # | Task | Owner | Est. |
|---|---|---|---|
| 10.1 | Argo CD install, bootstrapped from the CTO/HQ-provisioned git repo | Rick | 1d |
| 10.2 | App-of-apps: KubeRay, device plugins, DCGM, Prometheus, Grafana | Rick | 1d |
| 10.3 | Lab Notebook structure — configuration lives in git; prose for lessons learned; link it to this vault | Rick | 1d |

**The Lab Notebook is largely a by-product.** Every configuration becomes a version-controlled artifact rather than a screenshot in a document. Todd Shirback owns the notebook itself ([[2026-10-12 Research Team Kickoff]]); this provides its technical half.

---

### WS8 — Documentation & Phase 2 readiness *(5 days, unchanged in intent)*

Researcher quick-start (connect, move data, submit a job, read the dashboard); operator runbook (rebuild, patch, common failures, escalation); as-built diagram; Terraform and Argo CD repo READMEs; Phase 1 closeout summary.

**Exit:** a second engineer could operate the environment from the documentation alone.

---

## 4. Schedule

Eight working weeks plus a final Monday, same window as [[Phase 1 Project Plan]].

| Week | Focus | Milestone |
|---|---|---|
| **Oct 5–9** | Kickoffs held. **File every long-lead request**: GPU quota + ODCR, Alpharetta inventory, cyber requirements, network/InfoSec approval, GWD entry, ServiceNow record, AERO badges, git pipelines. Settle server count and funding | **M0 — every external dependency formally requested** |
| **Oct 12–16** | WS0 closed out. WS1 landing zone applied. Region and instance family locked. ODCR placed | **M1 — landing zone applied; capacity reserved** |
| **Oct 19–23** | WS2 EKS + Karpenter + GPU NodePool. **First GPU node provisioned and torn down.** WS10 Argo CD bootstrapped | **M2 — D8 evidence captured: elastic GPU capacity demonstrated** |
| **Oct 26–30** | WS7 KubeRay. WS3 dev pods + SSM. WS5 image build. **First researcher trains on one GPU** | **M3 — D1 + D3: researchers on GPUs** |
| **Nov 2–6** | WS4 S3 + DataSync both directions; 4.7 input-path benchmark → FSx go/no-go. WS9 dashboards live | **M4 — D2: data moves both directions** |
| **Nov 9–13** | WS5 stack parity confirmed; WS3 cyber sign-off; multi-node NCCL/EFA validated | **M5 — D4 + D5 + D6** |
| **Nov 16–20** | WS6 Test A and Test B; scaling sweep to 24 GPUs | **M6 — D7: both acceptance tests run** |
| **Nov 23–27** | Benchmark report; WS8 documentation — **short week, Thanksgiving 11/26–27** | **M7 — Scaling Benchmark Report delivered** |
| **Nov 30** | Closeout and Phase 2 handover | **Phase 1 complete** |

**Three differences from the existing schedule worth noting:**

1. **D8 evidence lands in week 3, not week 8.** The phase's largest unknown is retired before November.
2. **Researchers reach a GPU in week 4**, against week 3 in the existing plan. One week later — the cost of building a cluster rather than three instances — but against a structurally de-risked back half.
3. **Thanksgiving week carries documentation, not a build milestone.** In the existing plan it carries the D8 demo.

---

## 5. Milestones & acceptance gates

| ID | Gate | Evidence | Latest acceptable |
|---|---|---|---|
| M0 | External dependencies requested | Written requests with dates and owners | 2026-10-09 |
| M1 | Landing zone + reserved capacity | `terraform plan` empty; ODCR active | 2026-10-16 |
| M2 | Elastic GPU capacity *(D8)* | Scale-up/down transcript; `capacity-reservation-id` on the node | 2026-10-23 |
| M3 | Researchers on GPUs *(D1, D3)* | Four named researchers, session logs, a completed job | 2026-10-30 |
| M4 | Data path *(D2)* | Round-trip of a real dataset; input-path benchmark | 2026-11-06 |
| M5 | Stack, cyber, packages *(D4, D5, D6)* | Jim's team confirms parity; named GEV approver signs off | 2026-11-13 |
| M6 | Both acceptance tests *(D7)* | Raw results for Test A and Test B | 2026-11-20 |
| M7 | Benchmark report | Written report accepted by GE Vernova | 2026-11-27 |

**Escalate on an M1 or M2 miss.** Both are early enough to recover; M5 onward is not.

---

## 6. Definition of done

Phase 1 is complete when all are true and evidenced:

**Against the SOW (D1–D8)**
- [ ] Agreed GPU count reachable by four named ARC researchers *(D1 — see §9.1 on wording)*
- [ ] Security-approved file transfer exercised both directions with real data *(D2)*
- [ ] Shell/CLI/script access per researcher under their own identity, session-logged *(D3)*
- [ ] Stack confirmed by GE Vernova as matching Alpharetta *(D4)*
- [ ] Configuration confirmed by a named GEV approver *(D5)*
- [ ] Training packages installed and licensed *(D6)*
- [ ] Accepted validation report: on-prem equivalence **and** linear scaling *(D7)*
- [ ] Elastic GPU infrastructure deployed via IaC and demonstrated *(D8)*

**Against the research team's deliverables** ([[2026-10-12 Research Team Kickoff]])
- [ ] Architectural Reference Diagram accepted
- [ ] Operational Sandbox reachable by shell
- [ ] Connectivity Bridge live
- [ ] Scaling Benchmark Report delivered
- [ ] Project Lab Notebook established and populated

**Operational**
- [ ] Runbook and researcher guide published; Terraform and Argo CD repos handed over
- [ ] Cost guardrails active; budget agreed; utilization metric defined in writing
- [ ] Scale-to-zero verified when the board is empty

---

## 7. Risks — delta from the existing plan

**Retired or materially reduced**

| Risk | Why |
|---|---|
| D8 scope ambiguity | The burst layer is structural; Reading A vs. B stops being a 2–3 week swing (§1.1) |
| Thanksgiving on the critical path | D8 moves to week 3 |
| Unidentified corporate IdP blocking D5 | No web tier in Phase 1; federation deferred to Phase 2 |

**New or increased**

| Risk | Impact | Mitigation |
|---|---|---|
| **EKS is arguably new scope** — the SOW says static servers and excludes scheduling software | Rework, or a Work Scope Amendment mid-phase | Settle in writing before WS2 starts (§9.1) |
| **Kubernetes operational load** on 1.0 + 0.5 + 0.5 FTE under a 24-hour unblock commitment | Support work displaces build milestones | Bound the SLA (§2.2); Argo CD so recovery is `git revert`; runbook written as you go, not at the end |
| **GWD review of a cluster** is a larger artifact than of three instances | Entry delay; possible redesign | Enter the Base process in week 1 with the architecture doc as the submission |
| **EFA on the GPU NodePool is unproven here** | Multi-node scaling — the headline deliverable — fails late | Validate in WS5.7 by **2026-11-13**, not in the benchmark week |
| **Researcher-facing failure modes are less obvious** — an unschedulable pod is harder to self-diagnose than a down server | Cuts against "applied ML engineers working independently" | A troubleshooting page in the quick-start; surface `kubectl describe` and the Ray dashboard early |
| **ODCR + Karpenter reserved capacity is a newer code path** | Nodes fall back to on-demand, silently costing more | Assert on `karpenter.k8s.aws/capacity-reservation-id` in the M2 evidence; alarm on on-demand GPU nodes |

**Carried unchanged:** GPU capacity/quota, VNDLY onboarding, Alpharetta inventory, benchmark baseline, cost exposure and the prepay decision, Ansys licensing, THOR+ diversion, Phase 2 running past the signed term.

---

## 8. What LTI needs from GE Vernova

Items 1–20 of [[Phase 1 Project Plan]] §7 carry over. This variant **adds**:

21. **Decision on the architecture itself** — does GE Vernova adopt this approach? Everything here depends on it. *(Server count settled 2026-10-19: 3 × p5.48xlarge / 24 GPUs.)*
22. **Written position on §9.1** — does an EKS cluster satisfy a deliverable worded "3 static servers," given Phase 1 excludes scheduling software?
23. **ODCR or ML Capacity Block placed for 3 × p5.48xlarge**, with its ID, before WS2 starts.
24. **Utilization metric definition** — allocation or SM occupancy (WS9.4).
25. **Dataset size** — now needed for three separate decisions: bridge sizing, FSx go/no-go, and expected shuffle benefit.
26. **Argo Workflows or Argo CD?** The one-word answer decides whether Flyte and Argo conflict at all.
27. **GWD submission window** for a Kubernetes-based MVP design.

**Items 21–23 are start-blocking.** The rest can run in parallel with WS0/WS1.

---

## 9. Contract and scope consequences

### 9.1 — "Static servers" versus a cluster *(new, and start-blocking)*

SOW deliverable D1 reads *"establish access to 3 static servers with 24 total GPUs."* Phase 1 also **explicitly excludes scheduling/queuing software** — researchers were to self-manage job scheduling.

This architecture delivers an EKS cluster with Karpenter and a Ray job substrate. Capacity is reserved for a fixed footprint, but nodes are created and destroyed on demand, and Ray schedules the work.

Two defensible readings:

- **Compliant:** the funded footprint is reserved and continuously available; researchers get GPU access and shell access; D8 explicitly asks for burstable infrastructure, which requires exactly this. "Static" describes the *funded footprint*, not a prohibition on orchestration.
- **Non-compliant:** "static servers" means persistent instances, and "no scheduling software" excludes a job scheduler, which is what Ray is.

**The second reading is survivable only if nobody raises it late.** Get a written position from Michael Russo before WS2 begins. If it needs a Work Scope Amendment, the SOW's Out of Scope Work process is a written proposal, a 14-day response window, and a signed amendment — **which does not fit inside this phase if started in November.**

### 9.2 — The server count is settled, and it reads in our favour

**Resolved 2026-10-19: 3 × p5.48xlarge, 24 H100 GPUs** — matching D1's wording rather than the four servers costed in the Electrification deck. Two consequences:

* **The D1 wording risk in §9.1 narrows.** The footprint now matches the deliverable exactly; the only remaining question is whether *"static servers"* permits an orchestrated cluster, not how many there are.
* **Under a reserved-capacity model the deliverable reads as "24 GPUs of addressable reserved capacity"** rather than "3 boxes that are always on" — which shifts the conversation from footprint to utilization, the conversation the research team wants to have anyway.

The on-demand run rate falls to **~$91,609/month** (3 × $30,536.19). The 15-month and prepay totals in [[Surrogate ML Accelerator - Electrification]] §5 were quoted for four servers; scaled pro rata they are roughly $1.37M, $921k and a $453k saving — **confirm with Michael Russo rather than relying on scaled figures.**

### 9.3 — Carried forward unchanged

§8.1 (Phase 2 past the signed term), §8.2 (which document governs), and §8.3 (Exhibit A names two resources) from [[Phase 1 Project Plan]] apply unchanged.

---

## Related

- [[Phase 1 Project Plan]] — the authoritative plan this varies from
- [[Recommended Architecture - Surrogate ML Accelerator]] — the architecture this executes
- [[Alternative Architecture - AWS Batch]] — the rejected alternative, and why
- [[2026-10-12 Research Team Kickoff]] — the six research deliverables and the vision
- [[EKS Platform Replication Plan]] — deeper technical detail for WS2 and WS7
- [[Build Analysis - Target Platform on AWS]] — scope boundary against the QB target
- [[Static AWS GPU Environment]] — the SOW's literal D1 description
- [[Risks & Open Questions]] · [[Decisions Log]]
- Timeline: [[2026-10 October]] · [[2026-11 November]]
