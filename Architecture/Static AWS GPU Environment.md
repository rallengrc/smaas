---
title: Static AWS GPU Environment Architecture
description: Phase 1 specification for standing up three fixed AWS EC2 GPU instances mirroring on-prem Alpharetta servers
keywords:
- static environment
- GPU
- EC2
- Phase 1
- Alpharetta
- NVIDIA
- CLI access
tags:
- architecture
category: architecture
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- static gpu environment
- phase 1 static environment
- ec2 gpu servers
- alpharetta replication
---

# Static AWS GPU Environment

> **TL;DR:** Specification for Phase 1 delivery of 3 static EC2 GPU servers (24 GPUs total) configured with shell/CLI access for GE Vernova researchers.
> **Use this for:** Reviewing Phase 1 hardware sizing, networking, access setup, and software configurations.

Phase 1 of [[SOW - Burstable MLaaS|Burstable MLaaS]]. Deliverable window: [[2026-10 October]] – [[2026-11 November]] *(re-baselined 2026-10-04)*. Delivery plan: [[Phase 1 Project Plan]].

Modeled after GE Vernova's existing on-premises MLaaS environment in Alpharetta.

## Target shape

> ✅ **Settled 2026-10-19: 3 × p5.48xlarge — 24 H100 GPUs total**, matching the SOW's D1 wording rather than the four servers costed in [[Surrogate ML Accelerator - Electrification]]. Quota, capacity reservation, cost basis and the D7 scaling sweep all size to 24 GPUs. See [[Decisions Log]].

- **3 static servers × p5.48xlarge, 24 total H100 GPUs**, one AWS data center (region still TBD)
- ~4 ARC researchers as initial users
- File transfer path between AWS and GE Vernova on-prem resources
- CLI / shell / script-based access (no scheduling/queuing software — self-managed by researchers)
- Technology stack aligned to the Alpharetta on-prem MLaaS environment
- Cybersecurity + authentication requirements (TBD — align with GE Vernova IT/security)
- Additional software/packages for surrogate model training

## Open design questions
- [x] ~~**How many servers and GPUs — 3/24 or 4/32?**~~ — **resolved 2026-10-19: 3 servers / 24 GPUs.**
- [ ] Which AWS region/data center is agreed upon?
- [x] ~~GPU instance type/family~~ — **p5.48xlarge (8 × H100 80GB)** per the Electrification plan. Still needs checking against Alpharetta's hardware generation for the D7 parity claim.
- [ ] Exact software stack parity list (CUDA/cuDNN versions, ML frameworks, drivers)
- [ ] File transfer mechanism (Direct Connect, VPN, S3 + on-prem sync, SFTP, etc.)
- [ ] Auth model (SSO/IdP integration, per-researcher accounts, key management)
- [x] ~~AWS account structure~~ — a dedicated account for this application, **inside the GEV ENT MasterPayer Org**, with QB-equivalent security and compliance controls.
- [ ] Cybersecurity requirements source (GE Vernova InfoSec policy doc?)

## Funding and demand
The environment is paid for from **Electrification 2026 Program** funds and positioned as a surrogate model accelerator for the Electrification business — see [[Surrogate ML Accelerator - Electrification]]. Costed at **~$122k/month on-demand** (4 servers), **$1.23M–$1.83M over 15 months**. Funding was still listed as *not yet secured* as of 2026-10-06.

## Related
- [[Surrogate ML Accelerator - Electrification]]
- [[Phase 1 Project Plan]]
- [[GE Vernova ARC]]
- [[Risks & Open Questions]]
- [[QB Reference Architecture]] — target end-state platform this static environment is the compute foundation for
- [[Build Analysis - Target Platform on AWS]] — gap analysis between this and the target platform
