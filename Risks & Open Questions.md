---
title: Risks & Open Questions — Burstable MLaaS
description: Tracked technical, operational, and contractual risks and open questions for the Burstable MLaaS project
keywords:
- risks
- open questions
- mitigations
- Burstable MLaaS
- dependencies
- GE Vernova
tags:
- log
category: planning
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- project risks
- open questions
- blockers
- risk log
---

# Risks & Open Questions

> **TL;DR:** Active register of technical uncertainties, team staffing considerations, scope boundaries, and delivery risks.
> **Use this for:** Tracking unresolved questions and assessing project blockers or risk mitigations.

## Risks
| Date raised | Risk | Impact | Mitigation | Status |
|---|---|---|---|---|
| 2026-10-12 | **Two competing deliverable sets** — the research team names six deliverables ([[2026-10-12 Research Team Kickoff]]); the SOW names D1–D8. They are different framings, not a restatement, and no mapping exists | Acceptance ambiguity on both sides: work can satisfy one set and miss the other. A "formal plan" is still coming from Jim Tallman | Produce an explicit mapping and get agreement on which set governs acceptance, before the formal plan lands and hardens the mismatch | **Open — new** |
| 2026-10-12 | **D7's acceptance test appears redefined** — the SOW proves *equivalent training* against the Alpharetta on-prem baseline; the research team's proof is *linear scaling from 1 to N GPUs* | Two different tests. Linear scaling can pass while on-prem equivalence fails, and vice versa. Still no model, dataset, baseline or tolerance named | Confirm which test constitutes D7 acceptance, and settle the benchmark definition that has been open since 2026-09-14 | **Open — new** |
| 2026-10-12 | **Phase 2 may contain build work** — "SMaaS Foundation (Phase 2): development of the underlying framework" contradicts the 2026-09-14 premise that Phase 2 has no build work | That premise is the stated reason D8's burst build sits in Phase 1. If Phase 2 builds, D8's scope reading may need revisiting; if it does not, SMaaS has nowhere to sit | Raise with Michael Russo alongside the still-open D8 scope question — they are now coupled | **Open — new** |
| 2026-10-12 | **24-hour blocker SLA against a 1.0 + 0.5 + 0.5 FTE team** — "no blockers persist beyond 24 hours", with engineering as a direct support layer for research | An unbounded reactive commitment landing on part-time engineers, competing directly with Phase 1 build milestones. Scope (hours, on-call, owner) undefined | Define the commitment's boundaries — business hours, named rotation, and what counts as a blocker — before researchers are onboarded | **Open — new** |
| 2026-10-12 | **Day 0 blocker: laptops and accounts for Nam and Rick not yet provisioned**, owned by Todd/IT and marked Critical. [[Chris Burke]] is not named in the action | Nothing starts without access; this compounds the already-open VNDLY onboarding gate and the AERO badging requirement | Chase Todd/IT this week; confirm explicitly whether Chris is covered by the same request | **Open — new, Day 0** |
| 2026-10-12 | **Single-AZ placement concentrates the GPU fleet in one AZ** | A single-AZ capacity shortfall or impairment stops all training. Also constrains the fallback region/family options already tracked below | Reasonable for a research sandbox and needed for low-latency multi-node training — record it as an accepted trade, and factor it into the capacity-reservation strategy | **Open — new (likely accepted trade)** |
| 2026-10-12 | **>90% utilization is a headline commitment with no measurement definition** — no metric, window, or reporting owner | A target that cannot be evidenced cannot be met; it is also the stated justification for high-density compute | Agree the definition (GPU-hours allocated vs. available? busy vs. idle?) and instrument it early, since it needs data from day one | **Open — new** |
| 2026-10-13 | **The QB blueprint may not demonstrate multi-node scaling.** [[QB Reference Architecture]] places p4d GPU nodes across **two AZs**, which is not how tightly-coupled distributed training is deployed — cross-AZ latency undermines NCCL collectives. The likeliest reading is single-node training and inference | GE Vernova is treating QB as the reference for a capability the reference may not contain. The linear-scaling proof has no precedent to copy, and estimates based on "QB already does this" would be unfounded | Confirm against the source diagram and with Dave Garber before the architecture review. QB stays a good model for the *platform*; it is not evidence for the *scaling claim*. See [[Recommended Architecture - Surrogate ML Accelerator]] §7.4 | **Open — new** |
| 2026-10-19 | **Multi-node: present practice versus destination.** [[2026-10-12 Research Team Kickoff]] states a "multi-node, high-performance computing approach" and scaling across GPU *clusters*; Deepak Akhare states **multi-server training is not currently required** ([[2026-10-19 Research Workload Q&A - Deepak Akhare]]) | The Scaling Benchmark Report cannot be designed until this is settled — 1 → 8 GPUs within one node and 1 → 24 across three are different proofs. It also decides whether EFA and gang scheduling are on the critical path at all, and therefore whether ECS remains excluded | **Not a conflict — Jim describes the destination, Deepak today's practice on constrained hardware.** The architecture should stay multi-node-capable regardless: EFA, cluster placement and a single-AZ GPU subnet are near-free now and costly to retrofit. What needs settling is narrower: **what the Phase 1 Scaling Benchmark Report measures.** 1 → 8 GPUs within a node is demonstrable today; 1 → 24 across three needs a workload that does not yet exist | **Open — new, high priority** |
| 2026-10-19 | **Day-one parity is asserted, not yet evidenced.** The training step and data path are low-risk — their container runs as a Kubernetes Job on one p5, and Ray is not required for it. The risk sits in the **CPU stages and filesystem assumptions**: how the 100–200 CPU preprocessing and 150 CPU rendering parallelise, whether scripts hardcode POSIX paths, and where ParaView runs | If any assumes a shared filesystem or shared-memory parallelism on one host, "no changes needed" becomes "some changes needed" — discovered during WS5 rather than before it | Confirmations C1–C4 in [[Recommended Architecture - Surrogate ML Accelerator]] §0.1, scheduled as WS5.0. Mountpoint for S3 mitigates the path case without code changes | **Open — new** |
| 2026-10-19 | **CPU capacity was not sized in any plan.** Preprocessing needs 100–200 CPUs, video generation 150, and training 8–16 per GPU ([[2026-10-19 Research Workload Q&A - Deepak Akhare]]) | A CPU tier is absent from all three architecture designs, which assumed a small platform node group. Running this work on p5 instances would be grossly uneconomic | Add a CPU node pool / capacity provider to whichever architecture is chosen; size it against the 150–200 CPU peak. This is also the clearest niche for Batch or ECS alongside the primary design | **Open — new** |
| 2026-10-15 | **SSM Session Manager may not be approved for remote access from GE laptops** — the recommended architecture's access plane assumed it. [[Chris Burke]] notes GE is restrictive here; the sanctioned patterns are **Gossamer** for AWS profile sessions and **PuTTY port tunnelling**, both SSO-backed | If SSM is refused late, the access plane needs redesigning mid-build | Low severity: `kubectl` from a laptop over Gossamer is already an established GE pattern, so the design's actual access path has precedent. Confirm the sanctioned route with GEV IT/InfoSec before WS3. See [[Recommended Architecture - Surrogate ML Accelerator]] §3.4 | **Open — new** |
| 2026-10-15 | **FSx for Lustre failed on SDM in this same GE Vernova estate** — the metadata server could not keep up, and per [[Chris Burke]] AWS never resolved it. Persistent_2 with additional metadata servers may have fixed it | FSx is the default choice for HPC I/O; an unverified metadata ceiling puts the training data path at risk, and file *count* drives it more than volume | Confirm Persistent_2 behaviour with the AWS account team. Settle the artifact-interaction question (Q6/Q7 of [[Architecture Decision - Questions for Researchers]]) before buying FSx: if workloads rarely read each other's outputs, write straight to S3 instead | **Open — new** |
| 2026-10-13 | **EFS is the most copyable mistake in the QB blueprint** — QB uses EFS for shared storage, which cannot feed eight H100s at training throughput | Adopting it by default because "QB does it" would starve the GPUs and sink the Scaling Benchmark Report for reasons that read as a platform failure | Use FSx for Lustre or the S3 + Ray Data path instead; see [[Recommended Architecture - Surrogate ML Accelerator]] §3.5.1 and §7.2 | **Open — new** |
| 2026-10-06 | ~~**Hardware spec conflict** — SOW deliverable D1 says **3 servers / 24 GPUs**; the funded Electrification plan says **4 × p5.48xlarge / 32 H100 GPUs**~~ | — | — | **RESOLVED 2026-10-19 — 3 × p5.48xlarge, 24 H100 GPUs total**, per the SOW's D1 wording. See [[Decisions Log]] |
| 2026-10-06 | **GPU funding not yet secured** — "Secure funding from business for GPU Servers" is listed as an open next step | Blocks D1 outright; servers cannot be landed without budget approval | Track with Mike Russo as a D1 predecessor; Electrification 2026 program money is the source | **Open — new** |
| 2026-10-06 | **GPU cost is substantial** — at the settled 3-server footprint, **~$91,609/month on-demand** (3 × $30,536.19), against the "tens of thousands" originally estimated | Material budget exposure, and the prepay decision is still worth roughly $450k over 15 months | **Updated 2026-10-19 for 3 servers.** The deck's totals ($1.83M on-demand / $1.23M prepay / $603,884 saving) were quoted for **four** servers; pro-rata for three they are ~$1.37M, ~$921k and ~$453k — **confirm with Mike Russo rather than relying on scaled figures.** Which option was chosen still matters, since a prepay removes the stop/start lever | **Open — cost basis restated** |
| 2026-10-06 | **New external gates: GWD via the CTO/HQ "Base" process, a ServiceNow "Business App" record, CTO/HQ-provisioned Git pipelines for IaC, and AERO badges for Nam and Rick to work on-site at 1RC** | Each has its own lead time and owner outside ARC; the MVP design must pass GWD | Add to the WS0 dependency list and request all four in week 1; AERO badging is on top of VNDLY | **Open — new** |
| 2026-10-06 | **Application stack uncertainty** — the Electrification deck's target shows **FastAPI, Flyte, Dask, MLflow, Streamlit**; [[2026-10-12 Research Team Kickoff]] states **EKS / Ray / Argo** | Mis-sized estimate for "deploy and support their application"; wrong assumptions in the EKS plan (which specifies Ray, not Dask) | Confirm the real target stack via the Architecture team | **Narrowed 2026-10-19.** **Java Spring / React is out** — it is DT4D's stack, not this project's ([[Decisions Log]]). Two Python candidates remain, and they may be complementary rather than competing: Ray and Argo are compute and orchestration, FastAPI and MLflow are serving and tracking. Argo remains unspecified (Workflows vs. CD). The kickoff's shell-over-web-UI priority hints the app tier may be out of sandbox scope — an inference, not a statement |
| 2026-10-04 | **Phase 2 extends past the executed SOW term** — Phase 2 now runs Dec 2026–**Feb 2027**; the signed term ends **2027-01-30** | The final month of committed support sits outside the contract | Confirm the actual term end at the GE kickoff; if it is still January, get an extension or follow-on SOW signed during January — not discovered in February. See [[2027-01 January]] | **Open — new** |
| 2026-10-04 | **Application/infrastructure/support boundary has shifted** — [[LTI Internal Kickoff Brief]] §5 has LTI deploying *and supporting* Jim Tallman's application and frontend; [[Build Analysis - Target Platform on AWS]] placed the app tier outside LTI's scope | Unplanned Phase 1 work (images, manifests, CI/CD) plus an on-call expectation across Phase 2's three months | Confirm and document the split at the GE kickoff, as the kickoff brief itself instructs. No application deployment materials have been supplied yet | **Open — new** |
| 2026-10-04 | **Thanksgiving falls in the D8 demo week** (Nov 26–27) | Two days lost from the week carrying Phase 1's last build milestone | Pull WS7 work forward from the week of Nov 9 if the burst build starts clean | Open |
| 2026-09-14 | **Phase 1 timeline** — 8 deliverables, ~2.0 FTE, and 3 external gates (VNDLY onboarding, GPU quota/capacity, Alpharetta inventory) outside LTI's control | Phase 1 slips into Phase 2's support window | Weekly status against the milestones in [[Phase 1 Project Plan]] §4; escalate at an M1/M2 miss, not in the final week | **Eased 2026-10-04** — the re-baseline gives 8.5 weeks starting at the kickoff, rather than 6.5 with the kickoff two-thirds through |
| 2026-09-14 | **D8 scope is ambiguous** — "infrastructure required to support the Burstable MLaaS offering" reads as either the supporting landing zone (~1–1.5 wks) or the elastic burst compute layer (3–4 wks) | 2–3 weeks of effort difference on the phase's largest unknown | Confirm with Michael Russo at the GE kickoff (2026-10-06) — see [[Phase 1 Project Plan]] §2.1. The available Karpenter reference config may shrink the estimate | **Open — highest priority** |
| 2026-09-14 | **GPU quota/capacity** for 8-GPU instance families may be unavailable in the chosen region; quota increases and capacity reservations have independent lead times | Blocks D1, and downstream D4/D6/D7 | Request quota in kickoff week; identify fallback family + region; evaluate On-Demand Capacity Reservations / ML Capacity Blocks | Open |
| 2026-09-14 | **"Equivalent training" (D7) has no agreed baseline** — no model, dataset, on-prem metrics, or tolerance defined | The phase's acceptance proof cannot be objectively passed or failed | Agree the benchmark with Jim Tallman's team before Nov 16 | Open |
| 2026-09-14 | **GPU cost exposure** — a 3-node, 8-GPU-per-node footprint run continuously is on the order of tens of thousands of dollars per month | Unbudgeted spend; possible mid-phase shutdown | Agree monthly budget, AWS Budgets alerts, and a stop/start policy before servers run continuously | Open |
| 2026-09-14 | **Elastic-scope clause** — the updated SOP explicitly permits redirecting LTI resources onto other AWS initiatives (e.g. Burstable HPC with THOR+) | Directly consumes already-tight Phase 1 capacity | Track diverted hours in status updates and restate Phase 1 impact at the time of diversion | Open |
| 2026-09-14 | **Team is three part-to-full-time people, not two full-timers** — [[Nam Park]] 100%, [[Chris Burke]] 50% (joined 2026-09-14), [[Rick Allen]] 50% (joined 2026-10-04, may increase) | Same ~2.0 FTE on paper, but more coordination overhead, two recent joiners, and only one person able to hold a continuous critical path | Nam on the access-dependent path; Chris on architecture-heavy tracks while his hours are front-loaded; Rick on interruption-tolerant tracks. Verify VNDLY onboarding for Chris **and Rick**. Confirm whether Exhibit A (2 resources) needs updating | **Open — updated 2026-10-04** |
| 2026-08-11 | Client (Michael Russo) has expressed intent for the LTI team to continue post-POC and for this to evolve into a production environment, but nothing is contractually committed beyond the current SOW term (ends 2027-01-30) | Possible resourcing/expectation mismatch if follow-on SOW isn't signed in time | Track as a renewal signal, not committed scope; revisit ahead of term end | Open |

## Resolved / partially resolved
Per [[2026-08-11 Engagement Structure Email]]:
- [x] ~~When does the broader DT4D/AWS initiative actually kick off?~~ — Target timeline for the initial POC confirmed as **EOY 2026**, aligning with the SOW's Dec 2026 milestones.
- [~] Rebuild vs. extend Quantum Black's platform — the LTI team will use the previously-shared AWS design ([[QB Reference Architecture]]) as a **starting point for new infrastructure**, not extend Quantum Black's live platform. Reasonably resolved in spirit; no explicit IP/licensing statement yet.
- [~] App stack ownership — **Jim Tallman's team (GE Vernova)** owns the application/workload requirements as "the application team"; LTI owns cloud infrastructure. **Complicated 2026-10-04:** [[LTI Internal Kickoff Brief]] §5 also has LTI deploying and supporting that application in the new environment — see the risk above and [[Phase 1 Project Plan]] §2.3.

## Open Questions

**From [[2026-07-30 Discovery Meeting]] / [[2026-08-11 Engagement Structure Email]] (unresolved):**
- [ ] Has Michael Russo's business case been approved by leadership (funding for the "surrogate in a box" vision beyond this SOW)? Not addressed in the 2026-08-11 email.
- [x] ~~Who specifically builds/owns the Java Spring backend + React frontend?~~ — **moot from 2026-10-19: that tier belongs to DT4D, not this project.** Retained below for the ownership principle it settled. — *Partly answered 2026-10-04: Jim Tallman's team builds it; [[LTI Internal Kickoff Brief]] §5 has LTI **deploying and supporting** it in the new environment. The exact application / infrastructure / support split is a GE kickoff agenda item.*
- [ ] Is the "defined project deliverable" engagement model ([[2026-08-11 Engagement Structure Email]]) reflected in the SOW's actual commercial terms, or does the SOW's staff-aug-style Exhibit A (40 hrs/week, per-resource) contradict that framing?

**From the updated scope document (`SOW - Scope.pdf`, 2026-09-14) — see [[Phase 1 Project Plan]]:**
- [ ] Does `SOW - Scope.pdf` govern over the executed SOW, and if so should it be executed as a **Work Scope Amendment**? The two documents assign Phase 1/Phase 2 work differently ([[Phase 1 Project Plan]] §8.2).
- [ ] Does D8 mean the supporting landing zone, or the elastic burst compute layer? (§2.1 — **highest-priority open item**)
- [ ] What is the **Alpharetta environment inventory** — OS, NVIDIA driver, CUDA/cuDNN, frameworks, Python packages, licensed software, filesystem layout? D4/D6/D7 are undefined without it.
- [ ] What **surrogate model, dataset, on-prem baseline metrics, and tolerance** define "equivalent training" for D7?
- [x] ~~What are the **dataset size and transfer frequency**?~~ — **answered 2026-10-19** ([[2026-10-19 Research Workload Q&A - Deepak Akhare]]): **30–100 GB per dataset**, one consolidated HDF5 plus 20–100 metadata files; raw VTU input is 5,000–10,000 files *if* preprocessing moves to AWS. Transfer frequency still depends on where preprocessing runs.
- [ ] What **monthly GPU budget** applies, and is a scheduled/idle stop-start policy acceptable given "static servers" describes a fixed footprint rather than 24/7 runtime?
- [ ] Is **VNDLY onboarding** (background checks, drug tests, SSO) complete for Nam, Chris **and Rick**?
- [~] Which **GPU instance family**? — *Answered 2026-10-06: **p5.48xlarge (8 × H100 80GB)**. Still unverified against Alpharetta's hardware generation, which is what D7's "equivalent training" claim actually depends on.*

**From [[LTI Internal Kickoff Brief]] (2026-10-04):**
- [ ] **What is the actual SOW term end** — 2027-01-30 per the executed contract, or February 2027 per the kickoff brief's "current contract period"? Phase 2 depends on the answer.
- [ ] Does the **three-person 100/50/50 structure** need documenting against Exhibit A, which names two resources at 40 hrs/week?
- [ ] Obtain the **CloudFormation templates, YAML, and Karpenter scaling configuration** said to be available. Karpenter is the mechanism D8's burst layer proposes — a working reference config would materially de-risk it.
- [ ] The brief cites an **"August 5 follow-up email"**; the vault records a follow-up dated **2026-08-11** ([[2026-08-11 Engagement Structure Email]]). Different document, or a date error?
- [x] ~~Todd Shirbak vs. Shirback~~ — **resolved 2026-10-06**: the Electrification deck spells it **Shirback** and names him **Project Manager**.

**From [[Surrogate ML Accelerator - Electrification]] (shared 2026-10-06):**
- [x] ~~**3 servers / 24 GPUs or 4 servers / 32 GPUs?**~~ — **resolved 2026-10-19: 3 × p5.48xlarge, 24 H100 GPUs.** Quota, capacity reservation, cost basis and the D7 sweep all size to 24.
- [ ] **Has the business secured GPU funding yet?** Listed as an open next step in the deck.
- [ ] **Which costing option was chosen** — 15-month on-demand ($1.83M) or 12-month prepay + 3 months on-demand ($1.23M)? A prepay commitment removes the stop/start cost lever that [[Phase 1 Project Plan]] §WS2 proposes.
- [ ] **What is the GWD "Base" process**, what does it require from us, and when does the MVP design need to enter it?
- [ ] **Who raises the ServiceNow "Business App" record**, and is it a predecessor to account provisioning?
- [ ] **AERO badges for Nam and Rick at 1RC** — who sponsors them, and what is the lead time? This is on top of VNDLY.
- [ ] **Is the Python application tier FastAPI / Flyte / Dask / MLflow, or EKS / Ray / Argo — or both?** *(Java Spring / React removed 2026-10-19: DT4D's stack, not this project's.)* [[EKS Platform Replication Plan]] specifies Ray; the deck specifies Dask. The two sets may be complementary rather than alternatives.
- [ ] **Does the 15-month GPU costing horizon imply an intended engagement well past February 2027?** Relevant to the renewal signal already tracked below.
- [ ] Are **Deepak Akhare** and **Priyesh Kakka** among the "approximately four ARC researchers" in the SOW, and who is the fourth?

**From [[2026-10-12 Research Team Kickoff]]:**
- [ ] **Which deliverable set governs acceptance** — the research team's six, or the SOW's D1–D8? How do they map? Jim Tallman's "formal plan" is still to come.
- [ ] **Is D7 proven by linear scaling (1→N GPUs) or by equivalence with Alpharetta on-prem?** The kickoff states the former; the SOW states the latter. Either way the benchmark model, dataset, baseline and tolerance remain undefined — open since 2026-09-14.
- [ ] **Does Phase 2 include development work?** "SMaaS Foundation (Phase 2): development of the underlying framework" cuts against the premise that Phase 2 has no build work.
- [ ] **Does "Argo" mean Argo Workflows, Argo CD, or both?** They are different tools with different infrastructure implications.
- [ ] **Is the app/frontend tier in or out of the sandbox?** "Prioritize shell/SSH over complex web UIs" suggests out; [[LTI Internal Kickoff Brief]] §5 has LTI deploying and supporting Jim's application and frontend. A direct answer here would close the longest-running open item in this register.
- [ ] **How is >90% utilization measured**, over what window, and who reports it?
- [ ] **What bounds the 24-hour blocker commitment** — business hours, named rotation, definition of "blocker"?
- [ ] **Is the "Todd / IT" owning laptops and accounts the same Todd Shirback** who owns the Lab Notebook, or a separate IT owner?
- [ ] **Are laptops and accounts being provisioned for [[Chris Burke]]?** The action item names only Nam and Rick.
- [ ] **Where does the Project Lab Notebook live**, and does LTI contribute to it directly? It overlaps substantially with this vault.
- [ ] **What is the single-AZ decision's fallback** if the chosen AZ cannot supply p5.48xlarge capacity?

- [ ] **Does development happen on AWS, or on-prem/locally with AWS used only to run finished jobs?** Added 2026-10-19 and **now the highest-value open question**: it is what separates the recommended architecture from [[Alternative Architecture - AWS Batch]], whose other objections fell away with single-node training. See [[Recommended Architecture - Surrogate ML Accelerator]] §0.4.

**From SOW/architecture work:**
- [ ] Which AWS region/data center is agreed upon for the static environment? ([[Static AWS GPU Environment]])
- [ ] What exact cybersecurity/authentication requirements apply, which standard governs, and who is the named GEV approver? ([[Static AWS GPU Environment]])
- [ ] Which **corporate IdP** does GE Vernova run? Blocks federated auth in D5 and any OIDC work in D8.
- [ ] What does "on-demand" mean operationally, given scheduling/queuing software is excluded from Phase 1? ([[On-Demand MLaaS POC]])

**From [[Build Analysis - Target Platform on AWS]] (gap analysis vs. [[QB Reference Architecture]]):**
- [ ] Does the On-Demand MLaaS POC mean bursting the existing static servers' GPU capacity, or standing up a new EKS-based environment?
- [x] ~~Which AWS account(s) will ARC's build use?~~ — **resolved 2026-10-06**: a dedicated account for this application, hosted **inside the GEV ENT MasterPayer Org** with QB-equivalent security and compliance controls ([[Surrogate ML Accelerator - Electrification]]). *(This corrects the 2026-10-04 reading of "standalone, no integration" — that referred to the existing environment, not the account hierarchy.)* Relationship to `geren-eu-dwf-sdm-prod` still unaddressed.
- [ ] Is eu-west-1 the intended region for ARC's own build, or specific to Quantum Black's (wind business) deployment?
- [ ] What's the concrete license/package list for Ansys CFX and other surrogate-modeling software, and who holds those licenses?

Anything that turns into a scope change should follow the Out of Scope Work process in [[SOW - Burstable MLaaS]] (written proposal → 14-day response → signed Work Scope Amendment).

---

## Notes from Rick — Status & Resolution of Critical Open Risks and Questions

> **Author:** Rick Allen (LTI Cloud Architect & Orchestrator Lead)  
> **Audience:** Nam Park, Chris Burke, Jim Tallman, Michael Russo, and GE Vernova Stakeholders  
> **Context:** Definitive status updates and technical mitigations resolving key open questions in the register based on official AWS user guides, KubeRay patterns, and the 3-node hardware feasibility analysis.

### 1. Hardware Baseline & GPU Budget Conflict (Resolved: 3 Nodes / 24 GPUs)
* **Open Item:** SOW D1 says 3 servers (24 GPUs); Electrification pitch deck said 4 servers (32 GPUs).
* **Resolution:** We formalize **3 × `p5.48xlarge` (24 NVIDIA H100 GPUs)** as the contractual and technical baseline per signed SOW D1.
* **Financial Impact:** Sizing for 3 servers reduces on-demand monthly spend from $122,145 to **$91,608**, saving **~$30,536/month ($366,434/year)**. This completely resolves the "unsecured funding" risk for Michael Russo.
* **Technical Parity:** In NCCL Ring AllReduce, bus efficiency at 24 ranks is $\frac{23}{24} = 95.83\%$ (compared to $96.87\%$ at 32 ranks). The efficiency variance is $<1.04\%$, while providing a clean 5-point benchmark progression (1, 2, 8, 16, 24 GPUs) across single-node NVLink and multi-node EFA.

### 2. FSx for Lustre Metadata Ceiling / SDM History (Resolved: Two Working Paths)
* **Open Item:** Chris Burke reported FSx for Lustre failed during GE's SDM project because metadata servers froze on high file counts (unstructured meshes).
* **Resolution Path A (Modern Persistent_2):** The official [FSx for Lustre User Guide](../../Resources/aws/LustreGuide.md) confirms that modern **Persistent_2 SSD** file systems support **User-Provisioned Metadata IOPS** up to **192,000 IOPS** (in multiples of 12,000 IOPS), decoupled from storage capacity. This prevents the metadata starvation that caused the SDM freeze.
* **Resolution Path B (Local NVMe Scratch — Recommended):** Each `p5.48xlarge` has **8 × 3.84 TB NVMe SSDs (~30.7 TB raw)** delivering **>30 GB/s local read throughput**. Striping these via RAID-0 at `/mnt/nvme-scratch` and using **Ray Data** to stream S3 shards directly into local NVMe eliminates the Lustre metadata risk entirely, provides 10× faster training I/O, and saves **$1,500–$3,000/month** in standing filesystem costs.

### 3. Remote Access Plane & InfoSec Approval (Resolved: Gossamer + PuTTY)
* **Open Item:** AWS SSM Session Manager approval from GE laptops is unconfirmed.
* **Resolution:** Chris Burke confirmed that **Gossamer** (for AWS profile sessions) and **PuTTY port tunnelling** are pre-approved GE Vernova enterprise patterns. Researchers can run `kubectl` and `ray job submit` from GE laptops over Gossamer SSO directly to the EKS cluster without waiting on SSM InfoSec exceptions.

### 4. Argo vs. Flyte Tooling Conflict (Resolved: Separation of Concerns)
* **Open Item:** Electrification deck specifies Flyte; kickoff specifies Argo.
* **Resolution:** **Argo CD** is used strictly for GitOps platform deployment (managing EKS manifests, Karpenter CRDs, and KubeRay operators). **Flyte** is the macro-DAG orchestrator (data lineage, pipeline caching, Pythonic `@task` definitions) that dispatches GPU training tasks to KubeRay. There is zero conflict.

### 5. D7 Acceptance Test Divide (Resolved: Synthetic Physics-GNN Benchmark)
* **Open Item:** SOW D7 requires "equivalence with on-prem MLaaS" (blocked awaiting Alpharetta baseline metrics since Sept 14); kickoff requires "linear scaling 1 to N GPUs".
* **Resolution:** We de-risk Phase 1 signoff by constructing a synthetic 3D Physics-GNN / mesh benchmark (MeshGraphNet on Ray Train) that demonstrates linear scaling from 1 to 24 GPUs over EFA 3200 Gbps. This delivers Jim Tallman's Scaling Benchmark Report on time and establishes an immutable baseline that can be verified against Alpharetta whenever GE provides the on-prem data.

### 6. Application Tier Scope Creep (Resolved: Shell-First Ray Bulletin Board)
* **Open Item:** ~~Who builds the Java Spring / React web frontend?~~ — **closed 2026-10-19: that tier is DT4D's, not in scope here.**
* **Resolution:** Jim Tallman explicitly directed: *"Prioritize shell/SSH access over complex web UIs for rapid iteration."* We deploy lightweight CPU dev pods on EKS accessible via Gossamer/SSH. Researchers submit jobs via `ray job submit` directly to the KubeRay head, which prompts Karpenter to dynamically provision GPU workers. This delivers an interactive "bulletin board" Day 1 and defers complex web portals to Phase 2 (SMaaS).

