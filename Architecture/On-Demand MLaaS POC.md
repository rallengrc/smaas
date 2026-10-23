---
title: On-Demand MLaaS POC Architecture
description: Phase 2 proof-of-concept design for dynamic burstable GPU capacity on AWS using Karpenter and EKS
keywords:
- on-demand
- POC
- burstable GPU
- Karpenter
- AWS
- EKS
- auto-scaling
tags:
- architecture
category: architecture
classification: 🟢🛡️ General
last_updated: '2026-10-11'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- on-demand poc
- burstable gpu poc
- phase 2 poc
- karpenter burst architecture
---

# On-Demand MLaaS POC

> **TL;DR:** Architecture plan for transitioning from static GPU servers to dynamic, on-demand GPU capacity on AWS during Phase 2.
> **Use this for:** Understanding proof-of-concept scaling goals, burst triggers, cost controls, and milestone criteria.

Phase 2 of [[SOW - Burstable MLaaS|Burstable MLaaS]] — the "burstable" part of Burstable MLaaS. Built out incrementally across [[2026-10 October]], [[2026-11 November]], and [[2026-12 December]] alongside ongoing support of the [[Static AWS GPU Environment]].

## Goal
Move from a fixed 3-server/24-GPU footprint toward GPU capacity that can scale up/down on demand — a proof of concept, not full production, through end of 2026.

[[QB Reference Architecture]] (Quantum Black's current platform) is the reference blueprint for what GE Vernova ultimately wants — an ARC-owned "surrogate in a box" shared service, per [[2026-07-30 Discovery Meeting]]. It is **not** the POC's literal target for December 2026 — see [[Build Analysis - Target Platform on AWS]] for the gap between the two and a proposed narrower phasing.

## Open design questions
- [ ] What triggers a burst — job submission, queue depth, manual request?
- [ ] Since scheduling/queuing software is explicitly excluded from the static environment, does the POC introduce one, or does bursting stay manual/self-service?
- [ ] Cost controls / auto-shutdown policy for on-demand GPU instances
- [ ] How this POC's auth/security model relates to the static environment's

## Milestones
Track monthly milestones in the corresponding timeline notes:
- [[2026-10 October]]
- [[2026-11 November]]
- [[2026-12 December]]

## Related
- [[Decisions Log]]
- [[Risks & Open Questions]]
