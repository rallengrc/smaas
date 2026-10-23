---
title: Build Analysis — Target Platform on AWS
description: Gap analysis between SOW commitments and the full Quantum Black target architecture for GE Vernova ARC
keywords:
- build analysis
- AWS
- EKS
- QB reference architecture
- gap analysis
- Karpenter
- GPU
tags:
- architecture
- analysis
category: architecture
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- build analysis aws
- qb gap analysis
- target platform architecture
- eks build plan
---

# Build Analysis — Target Platform on AWS

> **TL;DR:** Detailed technical comparison detailing what it takes to build an ARC-owned equivalent of the Quantum Black platform on AWS versus current SOW scope.
> **Use this for:** Evaluating the technical gap, required AWS services, and scope boundary between static servers and burstable EKS.

What it takes to stand up an ARC-owned equivalent of [[QB Reference Architecture]] inside ARC's AWS environment, per the goals in [[2026-07-30 Discovery Meeting]], and how that relates to what [[SOW - Burstable MLaaS]] currently commits to delivering.

**Status: draft analysis, not a committed plan.** Several inputs (rebuild-vs-extend decision, app-stack ownership, business-case approval) are still open per the discovery meeting — this document exists to make the gap visible, not to lock in scope. Anything here that becomes committed scope should follow the SOW's Out of Scope Work / Work Scope Amendment process.

## 1. Where the SOW and the target architecture currently diverge

| Area | SOW commits to (Sept 2026, static env) | QB reference target | Gap |
|---|---|---|---|
| Compute | 3 static servers, 24 GPUs, CLI/shell/script access, self-managed scheduling | EKS cluster on EC2, mixed Node Group (fixed) + Karpenter Node Pool (dynamic/burstable) across 2 AZs | No orchestration layer, no burst-provisioning, no multi-AZ in current SOW scope |
| Access model | Basic CLI/shell/script access for ~4 researchers | ALB + OIDC via GE Identity Provider, internal HTTPS, IRSA roles | SOW has no web-facing app or IdP-integrated auth — it's direct server access |
| App layer | None (researchers run their own training scripts) | Java Spring backend + React frontend (per discovery meeting), serving the platform as a shared service | Entire app tier is out of current SOW scope and unowned (open question from discovery meeting) |
| Data/metadata | None specified | Aurora PostgreSQL Multi-AZ for metadata | Not started |
| Shared storage | File transfer to/from on-prem (mechanism TBD) | EFS (shared volumes) + S3 (images) | Different problem (bulk file transfer vs. live shared storage) — needs reconciling |
| External dataset access | Not mentioned | Read-only IAM role into a separate account's SDM S3 bucket for wind blade design data | Not started; needs a decision on which AWS account structure ARC will use |
| CI/CD | Not mentioned | GitHub Actions → ECR → EKS deploy pipeline | Not started |
| Secrets | "Cybersecurity and authentication requirements" (unspecified) | Secrets Manager, IRSA-scoped roles | SOW's security requirements aren't detailed enough yet to map |
| Observability | Not mentioned | CloudWatch + Fluent Bit/Logstash log shipping | Not started |
| Domain-specific software | Software/packages for surrogate model training (unspecified) | Ansys CFX implied as part of the surrogate modeling workflow | Needs a concrete package/license list |

**Read of this table:** the SOW as written buys the *compute foundation* (Phase 1) and *some* progress toward burstability (Phase 2, "milestones toward the On-Demand MLaaS POC"), but the QB reference diagram describes a full platform — app tier, orchestration, CI/CD, multi-tenant data layer — that is well beyond a "POC milestone." Either the On-Demand MLaaS POC's actual target is a **subset** of this diagram (e.g., prove Karpenter-based bursting under existing static servers, without the app/web tier), or the SOW will need a Work Scope Amendment once the business case is approved and the true scope is confirmed.

## 2. Decisions blocking a real build plan
These came out of the discovery meeting and haven't been answered yet — treat them as blockers, not just open questions:

- **Rebuild vs. extend** (raised by Earle Flynn at the [[2026-07-30 Discovery Meeting]]; he has since left the engagement — see [[Chris Burke]]): is LTI building a net-new platform from scratch, or extending/forking something from Quantum Black? This changes almost everything below — licensing, code ownership, how much of the QB diagram is actually reusable IP GE Vernova has rights to vs. needs to be redesigned.
- **App stack ownership** (Mike Young's question): who builds/owns the Java Spring backend + React frontend — LTI, GE Vernova ARC engineering, or a third party? The SOW's named resources ([[Nam Park]], [[Chris Burke]]) are Sr. Cloud Infrastructure Engineers, not app developers — if LTI owns the app tier too, that's likely additional scope/resourcing.
- **Business case / funding approval**: Michael Russo was to present to leadership for formal approval. Until that lands, the "surrogate in a box" multi-business-unit vision is aspirational, not funded scope.
- **Kickoff timing / resource contention**: Nam Park has competing project demands; the pace of any build beyond the SOW's static environment depends on his (and [[Chris Burke|Chris]]'s) actual availability — and Chris joined on 2026-09-14, so his VNDLY onboarding is not yet complete.

## 3. Proposed phasing if this proceeds

Mapped against the SOW's existing monthly cadence rather than inventing a new timeline:

**September 2026 (SOW-committed, unchanged)**
Static GPU environment as already scoped — 3 servers/24 GPUs, file transfer, CLI access, cybersecurity/auth, surrogate training parity with Alpharetta. No platform/app work yet.

**October–December 2026 ("milestones toward the On-Demand MLaaS POC")**
This is where the QB reference architecture should inform scope, in roughly increasing order of platform maturity:
1. **Burst compute proof point** — introduce Karpenter (or equivalent) node-pool provisioning alongside the existing static Node Group, on top of the already-deployed GPU servers, to prove on-demand GPU scaling. This is the most direct interpretation of "Burstable MLaaS" and doesn't require the app tier.
2. **Auth foundation** — decide whether OIDC/IdP integration (mirroring the ALB + GE Identity Provider pattern) is needed for the POC or deferred to a later, fully-funded phase.
3. **Data layer decision** — determine whether the POC needs its own metadata DB (Aurora) and shared storage (EFS/S3), or whether the static environment's file-transfer mechanism is sufficient for POC scope.
4. **App tier: explicitly out of scope for the POC** unless the "app stack ownership" question resolves in favor of LTI building it and a Work Scope Amendment is signed — do not assume Java Spring/React work is included in the current SOW.
5. **External dataset access (SDM S3)** — only relevant once there's an actual application layer consuming wind blade design data; not a POC-blocking item.

## 4. Open questions this analysis surfaces (beyond the discovery meeting's three)
- [ ] Does "On-Demand MLaaS POC" mean bursting the *existing 3 static servers' GPU capacity*, or standing up a new EKS-based environment? The SOW text and the QB diagram suggest different things.
- [ ] Which AWS account(s) will ARC's new environment use — one new account (per the diagram's "New account" label), and how does it relate to the existing `geren-eu-dwf-sdm-prod` account if cross-account data access is ever needed?
- [ ] Is eu-west-1 the intended region for ARC's build, or was that specific to Quantum Black's deployment (wind business, possibly EU-data-residency driven)? The SOW says "an agreed-upon AWS data center" without naming one.
- [ ] What's the actual license/package list for Ansys CFX and other surrogate-modeling software, and who holds those licenses (GE Vernova or LTI)?

Track these in [[Risks & Open Questions]] and resolve high-impact ones (rebuild vs. extend, app ownership, POC's real target) before committing further build effort past the static environment.

## 5. Notes from Rick — Closing Architectural Gaps, Eliminating Web Bloat & GE Budget Alignment

> **Author:** Rick Allen (LTI Cloud Architect & Orchestrator Lead)  
> **Audience:** Nam Park, Chris Burke, Jim Tallman, Michael Russo, and GE Vernova Stakeholders  
> **Context:** Resolving the open questions and blockers raised in this analysis using current AWS guides, KubeRay patterns, and the 3-node hardware baseline.

### 5.1 Resolving App Stack Ownership (The "Web UI Bloat" Elimination)

> **Clarified 2026-10-19:** the **Java Spring backend and React frontend belong to DT4D**, the predecessor system. This engagement reuses DT4D's *concepts* and builds a wholly new cloud architecture for MLaaS — that tier was never in contention here. The exclusion below therefore still holds, but it excludes something that was never in scope rather than removing something that was. See [[Decisions Log]].

* **The Blocker:** §2 asked who builds the Java Spring backend + React frontend, raising risks of scope explosion and resource misallocation.
* **The Resolution:** In the October 12 research kickoff, Jim Tallman explicitly directed:
  > *"Prioritize shell/SSH access over complex web UIs for rapid iteration... Researchers are empowered as applied machine learning engineers."*
* We completely **remove the Java Spring and React tiers from Phase 1**. LTI will not build, deploy, or maintain web portals in Phase 1. Instead, researchers receive lightweight interactive CPU dev pods on EKS accessible via Gossamer/SSH. They interact with the cluster via the **Ray Bulletin Board** pattern (`ray job submit`), which provides an instant queue-free research sandbox while KubeRay and Karpenter manage GPU bin-packing under the hood.

### 5.2 Rebuild vs. Extend & The Quantum Black (QB) Anti-Patterns
* **The Finding:** QB was built as a multi-tenant business application for wind turbine engineering. As noted in [[Recommended Architecture - Surrogate ML Accelerator]] §7.4, QB spans **two Availability Zones using Amazon EFS**.
* **Why QB Cannot Be Directly Replicated for Surrogate ML:** Cross-AZ network latency breaks NCCL inter-node ring communication, and Amazon EFS throughput (~tens to hundreds of MB/s) severely starves 8 × H100 GPUs during distributed training.
* **The Architecture:** We build a purpose-tailored, single-AZ EKS cluster equipped with an EC2 Cluster Placement Group and 3200 Gbps EFA fabric. Instead of EFS, we deploy **Local NVMe Instance Scratch** (30.7 TB per node at >30 GB/s) with Ray Data S3 prefetching, keeping FSx for Lustre Persistent_2 as an optional POSIX mount only if upstream tools (Ansys CFX) require it.

### 5.3 3 Nodes (24 GPUs) Contractual Alignment & GE Budget Approval
* **Budget Alignment for Michael Russo:** SOW Deliverable D1 specifies **3 servers with 24 total GPUs**. Moving away from the 4-node assumption saves **~$30,536/month ($366,434/year)**, reducing on-demand spend from $122,145 to **$91,608/month**.
* **Scaling Parity:** NCCL Ring AllReduce efficiency across 24 GPUs is 95.83% (within 1% of 32 GPUs). A 3-node cluster natively supports the required 5-point linear scaling progression (1, 2, 8, 16, 24 GPUs) to complete Jim Tallman's Scaling Benchmark Report on time.

---

## Related
- [[QB Reference Architecture]]
- [[Static AWS GPU Environment]]
- [[On-Demand MLaaS POC]]
- [[2026-07-30 Discovery Meeting]]
- [[Decisions Log]]
