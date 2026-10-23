---
title: Phase 1 Project Plan — Burstable MLaaS
description: Authoritative delivery plan for Phase 1 static environment build, testing, and deployment (Oct-Nov 2026)
keywords:
- Phase 1 plan
- deliverables
- project plan
- static environment
- milestones
- GE Vernova
tags:
- plan
- deliverable
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- phase 1 project plan
- delivery plan
- phase 1 milestones
- static environment plan
phase: 1
window: 2026-10-01 → 2026-11-30
source: SOW - Scope.pdf (re-baselined 2026-10-04)
updated: 2026-10-04
---

# Phase 1 Project Plan — Design, Build & Deploy

> **TL;DR:** Authoritative plan for Phase 1, detailing the 8 specific deliverables required to deploy the static AWS GPU environment.
> **Use this for:** Tracking deliverable completion, validation criteria, and schedule baselines.

Plan for the **first deliverable** of [[SOW - Burstable MLaaS|Burstable MLaaS]], as defined by **Phase 1** in the SOW scope document.

**Window:** **October 1 – November 30, 2026** *(re-baselined 2026-10-04 from the previous September–October window)*.
**As of 2026-10-04, ~8.5 weeks remain** — effectively 8 working weeks plus Nov 30, with US Thanksgiving taking two days from the week of Nov 23.

**Resources** (per [[LTI Internal Kickoff Brief]]):

| Resource | Allocation | Notes |
|---|---|---|
| [[Nam Park]] | **100%** | The only full-time engineer — holds the access-dependent critical path |
| [[Chris Burke]] | **50%** | More hours initially, per AWS architecture + HPC expertise |
| [[Rick Allen]] | **50%** | May increase as his other project winds down |

~2.0 FTE nominal, **~620 person-hours** across the window before leave and onboarding time.

> **Kickoffs held: internal Monday 2026-10-05, GE Tuesday 2026-10-06.** At the GE kickoff Mike Russo shared the Electrification business case — see [[Surrogate ML Accelerator - Electrification]], which **answers several open questions and contradicts others** (hardware count, account placement, cost, application stack). Read §2.4 before acting on WS2.
>
> This plan supersedes the September–October framing. All timeline notes have been updated to match.

---

## 0. What the updated scope document changed

### Re-baselined dates (2026-10-04)

| | Previous | **Current SOW** |
|---|---|---|
| **Phase 1 — Design, Build & Deploy** | September – October 2026 | **October – November 2026** |
| **Phase 2 — Support & Enhance** | November – December 2026 | **December 2026 – February 2027** |

Deliverables are unchanged in both phases — only the calendar moved, by one month for Phase 1 and by one-to-two months for Phase 2 (which also gained a third month). This resolves what looked like an impossible schedule: a GE kickoff on 6 October against a Phase 1 ending 31 October. Phase 1 now begins at the kickoff rather than two-thirds of the way through.

> ⚠️ **Phase 2 now runs one month past the executed SOW's term end of 2027-01-30.** See §8.

### Scope changes (carried from the earlier scope update)

| | Original project docs | Current SOW scope |
|---|---|---|
| **Phase 1 window** | September 2026 only | **October – November 2026** |
| **Phase 1 deliverables** | 7 | **8** — adds *"Design, build, and deploy the infrastructure required to support the Burstable MLaaS offering for ARC"* |
| **Burstable / on-demand build** | Phase 2 work (Oct–Dec), framed as *"milestones toward an On-Demand MLaaS POC"* | **Pulled into Phase 1** |
| **Phase 2** | On-Demand MLaaS POC build | **Support & Enhance** (Dec 2026 – Feb 2027) — troubleshoot user issues, enhance per app-team requirements, support ongoing development |
| **Cyber wording** | "Implement required cybersecurity and authentication requirements" | "**Configure the environment to meet applicable** GE Vernova cybersecurity and authentication requirements" |
| **Engagement framing** | Burstable MLaaS specific | Broader **"Cloud Infrastructure Engineering services"**; deliverables explicitly *"not intended to limit"* LTI's support of other AWS work, naming **Burstable HPC with THOR+** as a possible additional initiative |

**Two consequences worth naming up front:**

1. **Phase 1 carries the whole build.** Both the static environment *and* the burstable infrastructure. Phase 2 contains no build line items at all — so if the burstable infrastructure isn't built in Phase 1, the SOW has nowhere else to put it.
2. **The elastic-scope paragraph cuts both ways.** It gives GE Vernova room to redirect the LTI team onto THOR+ or other AWS work mid-phase. Any such redirect consumes Phase 1 capacity — track it explicitly rather than absorbing it silently.
3. **Phase 2 grew from two months to three**, and now ends in February 2027. That is more support runway than before, but it extends past the executed SOW's term — see §8.

---

## 1. Phase 1 deliverables

| # | Deliverable (from SOP) | Workstream | Depends on |
|---|---|---|---|
| **D1** | Establish access to 3 static servers with 24 total GPUs within an agreed-upon AWS data center for ~4 ARC researchers ✅ *settled 2026-10-19 — 3 × p5.48xlarge, see §2.4* | WS2 | WS0, WS1, **server count + funding (§2.4)**, quota |
| **D2** | Enable file transfer between the AWS environment and GE Vernova on-premises resources | WS4 | WS1, GEV network/security approval |
| **D3** | Provide basic command-line, shell, and script-based access | WS3 | D1, auth model decision |
| **D4** | Configure the static servers with the technology stack required to align with the Alpharetta on-premises MLaaS environment | WS5 | **Alpharetta stack inventory (GEV)** |
| **D5** | Configure the environment to meet applicable GE Vernova cybersecurity and authentication requirements | WS3 | **GEV InfoSec requirements doc**, IdP decision |
| **D6** | Install additional software and packages required for surrogate model training | WS5 | D4, **package + license list (GEV)** |
| **D7** | Demonstrate successful surrogate model training equivalent to on-prem MLaaS, across multiple GPUs | WS6 | D1, D4, D6, **agreed benchmark + baseline (GEV)** |
| **D8** | Design, build, and deploy the infrastructure required to support the Burstable MLaaS offering for ARC | WS1, WS7 | Scope confirmation (see §2.1) |

---

## 2. Critical path and blockers

### 2.1 Blocker — D8 scope is ambiguous and must be confirmed in writing

"The infrastructure required to support the Burstable MLaaS offering" admits two readings:

- **Reading A (narrow, ~1–1.5 weeks):** the supporting AWS foundation around the static servers — account/landing zone, VPC and subnets, IAM, storage, transfer path, access tier, logging/monitoring, all under Terraform. This is largely implied by D1–D7 anyway.
- **Reading B (broad, 3–4 weeks):** the *elastic* compute layer that makes the offering "Burstable" — on-demand GPU capacity beyond the fixed 3 servers (EKS + Karpenter, or ASG-based), with cost guardrails. This is what [[On-Demand MLaaS POC]] and [[EKS Platform Replication Plan]] previously held in Phase 2.

Since the updated Phase 2 contains no build work, **Reading B is the more likely intent** — and it is the difference between a comfortable Phase 1 and an over-committed one.

**Recommended position, pending confirmation:** commit to Reading A as the baseline, plus a **time-boxed Reading B foundation** — a burst-capable design (ADR) and one working burst proof point on the same landing zone. Explicitly exclude the app tier (Java Spring / React), multi-tenancy, JupyterHub/Argo platform services, and CI/CD, per [[Build Analysis - Target Platform on AWS]]; those remain Work Scope Amendment territory.

> **Action:** confirm D8 scope with Michael Russo **at the GE kickoff on 2026-10-06**. This is the single highest-leverage open item in the phase.

**Helpful development:** [[LTI Internal Kickoff Brief]] §5 says GE Vernova has **CloudFormation templates and YAML files available, including Karpenter scaling configuration**. Karpenter is exactly the mechanism WS7 proposes for the burst layer. A working reference configuration materially de-risks Reading B — get these files at or before the kickoff, and reassess the 3–4 week estimate once you've seen them.

### 2.2 Critical path

```
WS0 onboarding (VNDLY, SSO, AWS access)
   → WS1 landing zone (account, region, VPC, IAM, Terraform)
      → GPU quota / capacity reservation request   ← LONG LEAD, start immediately
         → D1 servers up
            → D4 stack parity → D6 packages → D7 multi-GPU training demo   ← acceptance proof
      → D2 file transfer (parallel, own GEV approval track)
      → D3/D5 access + cyber (parallel)
      → D8 burst layer (starts once landing zone is stable)
```

Three items gate everything and all three are **outside LTI's direct control**:

| Gate | Why it's critical | Lead time | Owner |
|---|---|---|---|
| **VNDLY onboarding + SSO** | Background checks/drug tests are required before any LTI engineer gets GE environment access ([[2026-08-11 Engagement Structure Email]]). No access, no build. **[[Chris Burke]] joined 2026-09-14 and [[Rick Allen]] 2026-10-04** — confirm both are through, and do not assume. | Days–weeks | Michael Russo / GEV |
| **GPU service quota + capacity** | 8-GPU instance families (P4d/P5 class) routinely require quota increases *and* capacity reservations. Requests can take days; capacity in a given AZ is not guaranteed. | Days–weeks | LTI to request, AWS to grant |
| **Alpharetta stack inventory** | D4, D6 and D7 are all undefined without it — "align with Alpharetta" is untestable without knowing what Alpharetta runs. | GEV-dependent | Architecture team |

**All three should be formally requested at or immediately after the GE kickoff on 2026-10-06.** If any is not moving by Friday 2026-10-16, the November 30 date is at risk and should be raised in that week's status update rather than at the end of the phase.

### 2.3 Blocker — the application/infrastructure/support boundary has shifted

[[Build Analysis - Target Platform on AWS]] and [[EKS Platform Replication Plan]] both place the Java Spring / React application tier **outside** LTI's scope, on the strength of the role split in [[2026-08-11 Engagement Structure Email]]: Jim's team owns the application, LTI owns infrastructure.

[[LTI Internal Kickoff Brief]] §5 states something different — LTI will "work with **Jim Tallman** and his engineering team to **deploy their application and frontend into the new environment, then support it**."

Deploying and supporting an application someone else builds is not the same as building it, but it is more than the pure-infrastructure boundary the earlier analysis assumed, and it carries real work: container images, Helm/manifests, CI/CD into the cluster, runtime troubleshooting, and an on-call expectation extending into Phase 2.

> **Action:** the kickoff brief itself says to "confirm the division of application, infrastructure, and support responsibilities at kickoff." **Do that on 2026-10-06 and write the answer down.** Note that no application service deployment materials have been provided yet — only infrastructure templates.

### 2.4 Blocker — hardware settled; funding still open

> ✅ **Resolved 2026-10-19: 3 × p5.48xlarge — 24 H100 GPUs total**, per D1's wording rather than the four servers costed in [[Surrogate ML Accelerator - Electrification]]. The service-quota request, capacity reservation, landing-zone sizing and D7 demo design all size to **24 GPUs across 3 nodes**, and the on-demand run rate becomes **~$91,609/month** (3 × $30,536.19) rather than the ~$122k quoted for four.

Compounding it: the deck lists **"Secure funding from business for GPU Servers" as an open next step**. The money is Electrification 2026 program money and it is not yet committed. D1 cannot complete without it, which makes funding a predecessor to the phase's first milestone.

> **Action:** confirm the server count and the funding status with Mike Russo this week. These two together are now the most schedule-critical open items in the phase, ahead of the D8 scope question.

---

## 3. Workstreams

### WS0 — Access & onboarding *(prerequisite)*
- Confirm VNDLY records, background checks, drug tests complete for **all three** of Nam, Chris and Rick. Chris joined 2026-09-14 and Rick 2026-10-04 — verify rather than assume.
- Handover from Earle Flynn: AWS/account context, any in-flight work, and the DT4D/Quantum Black documentation review he carried.
- **AERO badges for [[Nam Park]] and [[Rick Allen]]** to work on-site at **1RC**, part-time — a *separate* requirement from VNDLY, with its own sponsor and lead time ([[Surrogate ML Accelerator - Electrification]]).
- **ServiceNow "Business App" record** — confirm who raises it and whether it gates account provisioning.
- **GWD via the CTO/HQ "Base" process** — a formal architecture review with CTO/HQ's Solution Architecture team. An **MVP design for Jim Tallman must pass through it**; find out what it requires from us and when.
- **Git pipelines for IaC deployments** must be set up with CTO/HQ SA/ENG — our Terraform delivery path depends on another team's schedule.
- Obtain GE Vernova SSO credentials and VPN/network access.
- AWS account path is **partly answered** by [[LTI Internal Kickoff Brief]] §5: a **dedicated account for this application only**, standalone, with **no integration** with the GE Vernova Enterprise Master Payer account that hosts the existing environment. Still confirm what IAM permissions LTI holds vs. what requires a GEV administrator.
- **Exit:** all three engineers can authenticate to the target AWS account and run `aws sts get-caller-identity`.

### WS1 — Landing zone & network *(D8 Reading A)*
- **Account placement is settled:** a dedicated account for this application, **inside the GEV ENT MasterPayer Org**, with QB-equivalent security and compliance controls ([[Surrogate ML Accelerator - Electrification]]). *(This corrects the earlier "standalone, no integration" reading — that referred to the existing environment, not the account hierarchy.)* Design the landing zone as an Org member account inheriting SCPs and central guardrails, not as an isolated account.
- Confirm **region** — still unresolved ([[Static AWS GPU Environment]]). `eu-west-1` appears in the Quantum Black reference but may be specific to the wind business's data residency. Region choice drives P5 availability, cost, and latency to on-prem.
- VPC design: subnets (private for GPU nodes, public/NAT for egress), route tables, security groups, NACLs.
- Connectivity to on-prem: Direct Connect vs. Site-to-Site VPN vs. transit through existing GEV networking — decide alongside D2 (WS4).
- IAM: roles for researchers, roles for LTI operators, permission boundaries, no long-lived keys.
- VPC endpoints (S3 gateway; ECR/STS/SSM interface) to keep traffic off the public internet.
- CloudWatch logging, CloudTrail, AWS Config baseline.
- **Everything under Terraform from day one** — Phase 2 is "support & enhance," which is materially harder against click-ops infrastructure.
- **Exit:** `terraform apply` from a clean state produces the full network/IAM/logging baseline.

### WS2 — Static GPU compute *(D1)*
- **Instance selection.** 24 GPUs / 3 servers = 8 GPUs per server, which maps cleanly onto AWS's 8-GPU instances:

  | Instance | GPUs | Notes |
  |---|---|---|
  | `p3.16xlarge` | 8× V100 16GB | Oldest; closest to legacy on-prem hardware if Alpharetta is V100-era |
  | `p4d.24xlarge` | 8× A100 40GB | NVLink + EFA; common ML training baseline |
  | `p4de.24xlarge` | 8× A100 80GB | Larger HBM for bigger models |
  | `p5.48xlarge` | 8× H100 80GB | Highest performance; tightest capacity |
  | `g5.48xlarge` | 8× A10G 24GB | Cheaper; no NVLink — weaker for multi-GPU training |
  | `g6e.48xlarge` | 8× L40S 48GB | Cost/perf middle ground |

  **Effectively decided: `p5.48xlarge` (8 × H100 80GB)** — named in [[Surrogate ML Accelerator - Electrification]], with AWS capacity discussions for P5 already underway.

  **But the selection criterion for D7 is Alpharetta parity, not raw performance.** D7 asks for *equivalent* training, and H100 is several generations newer than typical on-prem hardware — a generation mismatch changes numerics, framework/driver requirements, and achievable batch sizes. Confirm Alpharetta's GPU model and decide explicitly how "equivalent" is judged against newer silicon.
- **Request service quota increases immediately** for the chosen family in the chosen region; evaluate On-Demand Capacity Reservations or ML Capacity Blocks if standard capacity is unavailable.
- Provision 3 instances via Terraform; attach EBS (gp3/io2) and shared storage (FSx for Lustre or EFS — see WS4).
- **Cost — now quantified.** [[Surrogate ML Accelerator - Electrification]] prices 4 × p5.48xlarge with a 24% GEV discount at **~$122,145/month on-demand** ($30,536.19 per server per month): **$1,832,171.52 over 15 months** on-demand, or **$1,228,287.79** with a 12-month prepay plus 3 months on-demand — a **$603,883.73** saving.
- **Two consequences.** First, this is an order of magnitude above the "tens of thousands per month" this plan previously assumed. Second, **a 12-month prepay removes the stop/start lever** — if the business takes Option 2, idle-shutdown saves nothing on the committed servers, and the cost argument for it disappears. Find out which option was chosen before designing a scheduling policy.
- Still agree with GE Vernova: a monthly budget ceiling, AWS Budgets alerts, and — if the footprint stays on-demand — a scheduled or idle-triggered stop/start policy. "Static servers" describes the *fixed footprint*, not a requirement that they run 24/7.
- **Exit:** **3 instances running / 24 GPUs** (settled 2026-10-19, §2.4), all GPUs visible via `nvidia-smi`, reachable by the named researchers.

### WS3 — Access & authentication *(D3, D5)*
- **Obtain the actual GE Vernova cybersecurity requirements document.** D5 says "applicable ... requirements" without naming them; LTI cannot self-certify against an unstated standard. Request the controlling policy/standard and the named GEV security approver.
- Auth model decision: AWS SSM Session Manager (no open SSH ports, fully audit-logged — recommended default) vs. SSH via bastion vs. direct SSH over VPN.
- Identity: federate researcher access through GE Vernova's corporate IdP where possible. **The IdP is still unidentified** and it blocks any OIDC/SAML work here and downstream in D8 — resolve early.
- Per-researcher accounts/home directories, sudo policy, session logging, MFA.
- Encryption at rest (KMS CMKs for EBS/S3/EFS) and in transit.
- Patching/AMI baseline and vulnerability scanning per GEV standard.
- **Exit:** all 4 researchers authenticate with their own identity, run shell and script workloads, and every session is logged. A named GEV security contact confirms the configuration meets their requirements.

### WS4 — File transfer, on-prem ↔ AWS *(D2)*
- Decide the mechanism against actual dataset size and frequency — **ask Jim's team for both numbers first**:
  - **AWS DataSync** over Direct Connect/VPN — best for scheduled bulk transfer of large datasets.
  - **AWS Transfer Family (SFTP)** — best if researchers expect a familiar SFTP endpoint.
  - **S3 + CLI/sync** — simplest, good for ad-hoc researcher-driven movement.
  - **Storage Gateway / FSx** — if on-prem needs a live mounted view.
- Pair with in-cloud shared storage so all 3 nodes see the same data: **FSx for Lustre** (high-throughput training I/O, S3-linked) or **EFS** (simpler, lower throughput).
- Security review of the chosen path with GEV network/InfoSec — this is likely to be the **slowest external approval in the phase**; open the request in week 1.
- **Exit:** a researcher moves a real dataset in both directions and it lands intact, through an approved path.

### WS5 — Software stack parity & training packages *(D4, D6)*
- **Request the Alpharetta environment inventory via the Architecture team** — OS/distro and version, NVIDIA driver and CUDA/cuDNN versions, ML frameworks and versions (PyTorch/TensorFlow), MPI/NCCL, Python environment and package manifest, Ansys CFX and any other licensed software, scheduler configuration (noting Phase 1 explicitly excludes scheduling software), and filesystem layout conventions.
- Build a golden AMI (Packer) or a documented bootstrap so the stack is reproducible, not hand-installed — this directly serves Phase 2 support.
- **Resolve licensing:** who holds Ansys CFX and similar licenses, and does the license model permit cloud/EC2 execution? License servers may need on-prem reachability, which folds back into WS4's network path. Still open per [[Risks & Open Questions]].
- Validate multi-GPU plumbing: NCCL all-reduce across 8 GPUs on one node, and across nodes if multi-node training is expected.
- **Exit:** a documented, reproducible stack whose versions are confirmed by the Architecture team as matching Alpharetta.

### WS6 — Training validation *(D7 — the acceptance proof)*
- **Agree the benchmark with Jim's team before building toward it.** "Equivalent to the on-premises MLaaS environment" needs: a specific surrogate model, a specific dataset, an on-prem baseline result (accuracy/loss *and* wall-clock runtime), and an agreed tolerance. Without these, D7 cannot be passed or failed.
- Run single-GPU, then multi-GPU (8 GPUs on one node), then multi-node if in scope.
- Compare against the baseline; document deltas and their causes (GPU generation, framework version, data path).
- **Exit:** a written validation report, accepted by GE Vernova, showing an equivalent training result across multiple GPUs. **This is the deliverable that demonstrates Phase 1 succeeded — protect the schedule for it.**

### WS7 — Burstable MLaaS infrastructure *(D8, pending §2.1 confirmation)*
- **Architecture Decision Record** for the burst mechanism: EKS + Karpenter GPU node pool (aligns with [[QB Reference Architecture]] and [[EKS Platform Replication Plan]]) vs. a simpler EC2 Auto Scaling Group vs. AWS Batch / ParallelCluster. Recommend the simplest option that satisfies the actual burst trigger.
- **Define the burst trigger** — still an open question in [[On-Demand MLaaS POC]]. With scheduling/queuing software excluded from Phase 1, the honest near-term answer is likely *researcher-initiated, self-service* rather than queue-depth-driven autoscaling. Confirm rather than assume.
- Cost controls **as a build requirement, not a follow-up**: max node caps, TTL/idle termination, Spot where interruption is tolerable, budget alarms.
- Build and demonstrate one burst proof point: additional GPU capacity provisioned on demand beyond the 3 static servers, running a real workload, then torn down automatically.
- **Explicitly out of scope** for Phase 1 unless a Work Scope Amendment says otherwise: the application tier, multi-tenancy for "surrogate in a box," platform services, and application CI/CD. See [[Build Analysis - Target Platform on AWS]] §1.
- **Note the application target is Python, not the DT4D stack.** [[Surrogate ML Accelerator - Electrification]] slide 4 shows **FastAPI, Flyte, Dask, MLflow, Streamlit**, and **Dask rather than the Ray/KubeRay** in [[EKS Platform Replication Plan]]. *(Java Spring/React, assumed by several earlier documents, belongs to DT4D — clarified 2026-10-19.)* Confirm before sizing any platform work.
- **Exit:** ADR accepted, burst mechanism deployed via Terraform, one demonstrated scale-up/scale-down cycle with cost guardrails active.

### WS8 — Documentation & Phase 2 readiness
- Researcher quick-start: how to connect, move data, run training, request burst capacity.
- Operator runbook: build/rebuild, patch, common failures, escalation path — Phase 2 is "support & troubleshoot," and it will be run against this document.
- As-built architecture diagram and Terraform repo README.
- Phase 1 closeout summary for GE Vernova.
- **Exit:** a second engineer could operate the environment from the documentation alone.

---

## 4. Schedule

Eight working weeks plus a final Monday. Sequenced so external lead-time items start at the kickoff and the D7 demo is not compressed against the deadline.

| Week | Focus | Target milestone |
|---|---|---|
| **Oct 5–9** | **Internal kickoff Mon 10/5, GE kickoff Tue 10/6.** Confirm the application/infrastructure/support split (§2.3). Obtain the CloudFormation / YAML / Karpenter reference configs. **File all long-lead requests**: GPU quota, Alpharetta inventory, cyber requirements doc, network/transfer approval. | **M0 — kickoffs held; every external dependency formally requested** |
| **Oct 12–16** | WS0 onboarding closed out; WS1 landing zone in Terraform; region and instance family decided; WS4 mechanism decided | Landing zone applied; region + instance type locked |
| **Oct 19–23** | WS2 provision the 3 GPU servers; WS3 access model stood up | **M1 — D1 + D3: 24 GPUs reachable by researchers** |
| **Oct 26–30** | WS4 transfer path live; WS5 stack build to Alpharetta parity begins | **M2 — D2: data moves both directions** |
| **Nov 2–6** | WS5 stack parity complete; training packages installed | **M3 — D4 + D6: stack matches, packages in** |
| **Nov 9–13** | WS3 cyber configuration reviewed and signed off with GEV; WS7 burst build starts | **M4 — D5: security-approved** |
| **Nov 16–20** | WS6 training validation runs; WS7 burst build continues | **M5 — D7: multi-GPU training demo accepted** |
| **Nov 23–27** | WS7 burst demo; WS8 documentation — **short week, US Thanksgiving 11/26–27** | **M6 — D8: burst mechanism demonstrated** |
| **Nov 30** | Phase 1 closeout and handover to Phase 2 | **Phase 1 complete** |

**The re-baseline bought real float.** The previous window left 6.5 weeks for eight deliverables with the kickoff two-thirds of the way through; this one gives 8.5 weeks starting *at* the kickoff. The schedule above holds roughly a week of slack before D7 and another before closeout.

Two things still want watching: **Thanksgiving week** is where D8's demo lands, so pull that work forward if WS7 starts clean; and **the three 50%/100% allocations** mean parallel workstreams compete for Nam's full-time attention more than a two-full-timer plan would. Give Chris the architecture-heavy tracks (WS1 design, WS7) where his front-loaded hours land, and Rick the tracks that tolerate interruption (WS4 analysis, WS5 packaging, WS8 documentation).

---

## 5. Definition of done

Phase 1 is complete when all of the following are true and evidenced:

- [ ] 3 servers, 24 GPUs, running in the agreed AWS region, reachable by 4 named ARC researchers *(D1)*
- [ ] A working, security-approved file transfer path exercised in both directions with real data *(D2)*
- [ ] CLI/shell/script access for every researcher under their own identity, with session logging *(D3)*
- [ ] Software stack confirmed by GE Vernova as matching Alpharetta *(D4)*
- [ ] Configuration confirmed against the named GE Vernova cybersecurity/authentication requirements by a named GEV approver *(D5)*
- [ ] Surrogate-model training packages installed and licensed *(D6)*
- [ ] **Accepted validation report** showing equivalent multi-GPU training vs. the on-prem baseline *(D7)*
- [ ] Burstable MLaaS infrastructure designed, deployed via IaC, and demonstrated, per the confirmed §2.1 scope *(D8)*
- [ ] Runbook + researcher guide published; Terraform repo handed over *(WS8)*
- [ ] Cost guardrails active with an agreed monthly budget and stop/start policy

---

## 6. Risks

| Risk | Impact | Mitigation | Status |
|---|---|---|---|
| **D8 scope ambiguity** — Reading A vs. Reading B differ by ~2–3 weeks of work | Over- or under-delivery on the phase's largest unknown | Confirm at the GE kickoff 2026-10-06 (§2.1); the available Karpenter reference config may shrink the estimate | **Open — highest priority** |
| **Application/infrastructure/support boundary** — the kickoff brief has LTI deploying *and supporting* Jim Tallman's application and frontend, which earlier analysis placed outside LTI's scope | Unplanned work in Phase 1 (images, manifests, CI/CD) and an on-call expectation running through Phase 2's three months | Confirm and document the split at the GE kickoff, as the kickoff brief itself instructs (§2.3). No app deployment materials have been supplied yet | **Open — new 2026-10-04** |
| **GPU capacity/quota unavailable** in the chosen region | Blocks D1, and therefore D4/D6/D7 | Request quota week 1; identify a fallback instance family and region; evaluate Capacity Reservations | Open |
| **Onboarding (VNDLY/SSO) delay** | Blocks all build work; consumes float directly | Escalate to Michael Russo week 1; confirm status before assuming it's done | Open |
| **Team is three part-to-full-time people, not two full-timers** — [[Nam Park]] 100%, [[Chris Burke]] 50% (joined 2026-09-14), [[Rick Allen]] 50% (joined 2026-10-04, may increase) | Same 2.0 FTE on paper, but more coordination overhead, two recent joiners, and only one person able to hold a continuous critical path | Nam on the access-dependent path; Chris on architecture-heavy tracks while his hours are front-loaded; Rick on interruption-tolerant tracks. Verify VNDLY onboarding for Chris and Rick rather than assuming. Confirm whether Exhibit A (2 resources) needs updating | **Open — updated 2026-10-04** |
| **Alpharetta inventory not supplied** | D4/D6/D7 are undefined and unverifiable | Formal written request week 1; if unanswered by Sep 25, build to a documented assumed stack and flag the assumption in status | Open |
| **"Equivalent training" has no agreed baseline** | D7 cannot be objectively accepted | Agree model + dataset + baseline metrics + tolerance with Jim's team before Oct 19 | Open |
| **Cyber requirements unstated** | D5 unverifiable; late-surfacing controls force rework | Obtain the controlling standard and a named approver; schedule the review for mid-October, not the final week | Open |
| **GPU cost overrun** | Budget exposure in the tens of thousands per month | Budget + alerts + stop/start policy agreed before servers run continuously | Open |
| **Ansys CFX licensing blocks cloud execution** | D6/D7 blocked late in the phase | Confirm license holder and cloud-execution terms week 1; check whether a license server needs on-prem reachability (affects WS4) | Open |
| **Scope diversion to THOR+/other AWS work** | Directly consumes Phase 1 capacity | The SOP permits it; track diverted hours in status updates and restate Phase 1 impact when it happens | New — from updated SOP |
| **Timeline** — 8.5 weeks, 8 deliverables, ~2.0 FTE, 3 external gates, Thanksgiving in the D8 demo week | Phase 1 slips into Phase 2's support window | Weekly status against the §4 milestones; escalate at M1/M2 misses, not in the final week; pull D8 work forward out of Thanksgiving week if WS7 starts clean | Open — **eased** by the 2026-10-04 re-baseline |
| **Phase 2 extends past the executed SOW term** — Phase 2 now ends February 2027; the signed SOW term ends 2027-01-30 | The final month of committed support sits outside the contract | Raise with Michael Russo at the GE kickoff; likely needs a term extension or new SOW signed well before January (§8) | **Open — new 2026-10-04** |

---

## 7. What LTI needs from GE Vernova

Consolidated ask list — **all of these belong on the GE kickoff agenda for 2026-10-06**:

1. **Application / infrastructure / support split** confirmed and written down (§2.3) — *Michael Russo, Jim Tallman*
2. **The CloudFormation templates, YAML, and Karpenter scaling configuration** referenced in [[LTI Internal Kickoff Brief]] §5 — *Michael Russo*
3. **D8 scope confirmation** (§2.1) — *Michael Russo*
4. **Alpharetta MLaaS environment inventory** — OS, drivers, CUDA, frameworks, packages, licensed software, filesystem layout — *Architecture team*
5. **Cybersecurity/authentication requirements document** + the named security approver — *GEV InfoSec*
6. **Corporate IdP identity** and federation path — *GEV IT*
7. **AWS region decision** and LTI's permission level in the dedicated account — *GEV cloud team* *(the account question is partly answered: dedicated, standalone, no Enterprise Master Payer integration)*
8. **Surrogate training benchmark**: model, dataset, on-prem baseline metrics, acceptance tolerance — *Jim Tallman's team*
9. **Dataset size and transfer frequency**, to size the D2 mechanism — *Jim Tallman's team*
10. **Ansys CFX / software license** holder and cloud-execution terms — *GEV*
11. **The 4 named researchers** and their access requirements — *ARC*
12. **Monthly GPU budget** and approval of a stop/start policy — *Michael Russo*
13. **VNDLY onboarding status** for Nam, Chris and Rick — *Michael Russo*
14. **Term coverage for February 2027** — Phase 2 now ends a month after the signed term (§8) — *Michael Russo*
15. ~~**Server count: 3/24 or 4/32?**~~ — **settled 2026-10-19: 3 servers / 24 GPUs**
16. **GPU funding status** — is Electrification's 2026 program money committed? (§2.4) — *Michael Russo*
17. **Which costing option** — 15-month on-demand, or 12-month prepay? It decides whether a stop/start policy is worth building — *Michael Russo*
18. **GWD "Base" process** requirements and timing for the MVP design — *CTO/HQ Solution Architecture*
18a. **Two scoped privilege exceptions for the GWD submission** — GPU performance counters for Nsight profiling, and `CAP_SYS_PTRACE` for `py-spy`/`gdb`. Neither needs `privileged: true`; both will surprise a reviewer if raised late ([[Recommended Architecture - Surrogate ML Accelerator]] §3.4.2) — *CTO/HQ Solution Architecture*
19. **AERO badge sponsorship** for Nam and Rick at 1RC — *Michael Russo / Todd Shirback*
20. **Confirmed application stack** — FastAPI/Flyte/Dask/MLflow, or EKS/Ray/Argo, or both? *(Java Spring/React is DT4D's, not this project's — clarified 2026-10-19.)* — *Architecture team*

---

## 8. Contract discrepancies to resolve

**8.1 — Phase 2 now runs past the signed term.** The SOW scope puts Phase 2 at **December 2026 – February 2027**. The executed SOW ([[SOW - Burstable MLaaS]], effective 2026-08-12) has a term ending **2027-01-30**. February 2027 is committed support falling outside the contract.

This is consistent with [[LTI Internal Kickoff Brief]] §4, which describes "the current contract period, which runs through February" — suggesting the term has moved and the vault's record is simply behind. **Confirm the actual term end**, and if it is still January, get an extension or follow-on SOW signed well before then rather than discovering the gap in late January.

**8.2 — Which document governs the deliverables.** `SOW - Scope.pdf` is a **scope document**, not the executed contract. The executed SOW (`Burstable MLaaS - SOW - 2026 (Shareable).pdf`, effective 2026-08-12) describes Phase 1 as a September static environment and Phase 2 as the On-Demand MLaaS POC. The scope document reassigns work between the phases *and* moves both calendars. If that is intended to change the contractual deliverables, it should be executed as a **Work Scope Amendment** per the SOW's Out of Scope Work process (written proposal → 14-day response → signed amendment). This plan proceeds on the scope document as directed, with that flagged.

**8.3 — Exhibit A names two resources; the team is three.** Exhibit A lists two Sr. Cloud Infrastructure Engineers at 40 hrs/week. Delivery is staffed 100/50/50 across [[Nam Park]], [[Chris Burke]] and [[Rick Allen]] — and Chris replaced Earle Flynn, who is the name in the signed document. Same nominal capacity, different structure and different people. Confirm whether a documented substitution or amendment is needed.

> Logged in [[Risks & Open Questions]] and [[Decisions Log]].

---

## Related
- [[SOW - Burstable MLaaS]] — executed contract
- [[Static AWS GPU Environment]] — D1–D7 architecture notes
- [[On-Demand MLaaS POC]] — prior home of the burst work now in D8
- [[Build Analysis - Target Platform on AWS]] — scope boundary vs. the QB target platform
- [[EKS Platform Replication Plan]] — technical detail for WS7 if D8 resolves to Reading B
- [[QB Reference Architecture]] · [[QB Application-Level Architecture (EKS)]]
- [[Risks & Open Questions]] · [[Decisions Log]]
- Timeline: [[2026-09 September]] · [[2026-10 October]] · [[2026-11 November]] · [[2026-12 December]]
