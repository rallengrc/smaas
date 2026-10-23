---
title: Third-Party Documentation Source URLs
description: Original source URLs for the third-party documents stored under Resources/, grouped by vendor folder (aws, flyte, ray, docker-k8s, copilot)
keywords:
- source URLs
- third-party documentation
- AWS docs
- Flyte docs
- Ray whitepaper
- Docker
category: reference
classification: 🟢🛡️ General
last_updated: '2026-10-19'
author: GitHub Copilot (VS Code) + Rick Allen (LTI)
ai_search_aliases:
- doc source urls
- where did this doc come from
- original documentation links
---

# Third-Party Documentation Source URLs

> **TL;DR:** Where each file under `Resources/<vendor>/` came from, so the PDFs and book content do not have to be redistributed. Categories mirror the `Resources/` folders.
> **Use this for:** Re-downloading a document, checking the latest version, or deciding whether a file can be shared.

**Status key:** ✅ = HTTP 200 on 2026-10-19 · 🔒 = publisher blocks automated requests (HTTP 403), URL taken from a search result and not fetched · ❌ = no public URL found.
Where the local file records its own `source_url` / `Source:` line, that URL is used. Otherwise the URL is the matching official page and the PDF/HTML name follows the AWS docs pattern. The AWS PDF builds are rolling; the local copy is a snapshot.

---

## `Resources/aws/`

### Service guides (PDF builds on docs.aws.amazon.com)

| Local file | Source URL | Status |
|---|---|---|
| `eks-ug.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/eks/latest/userguide/eks-ug.pdf | ✅ |
| `eks-bpg.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/eks/latest/best-practices/eks-bpg.pdf | ✅ |
| `amazon-eks-observability-best-practices.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/amazon-eks-observability-best-practices/amazon-eks-observability-best-practices.pdf | ✅ |
| `AmazonEksEksctlDocs.pdf` / `.md` | https://docs.aws.amazon.com/eks/latest/eksctl/ (HTML only; eksctl.io redirects here. Schema: https://schema.eksctl.io/) | ✅ |
| `karpenter.md` | https://docs.aws.amazon.com/eks/latest/best-practices/karpenter.html. The original page `…/eks/latest/userguide/karpenter.html` now redirects to the guide index. Project docs: https://karpenter.sh/ | ✅ |
| `ec2-ug.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/AWSEC2/latest/UserGuide/ec2-ug.pdf | ✅ |
| `ec2-types.pdf` / `.md` | https://docs.aws.amazon.com/ec2/latest/instancetypes/instance-types.html (no PDF build found) | ✅ |
| `ecs-dg.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/AmazonECS/latest/developerguide/ecs-dg.pdf | ✅ |
| `efs-ug.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/efs/latest/ug/efs-ug.pdf | ✅ |
| `LustreGuide.pdf` / `.md` (FSx for Lustre) | https://docs.aws.amazon.com/pdfs/fsx/latest/LustreGuide/LustreGuide.pdf | ✅ |
| `Amazon SageMaker.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/sagemaker/latest/dg/sagemaker-dg.pdf | ✅ |
| `next-generation-sagemaker-ug.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/next-generation-sagemaker/latest/userguide/next-generation-sagemaker-ug.pdf | ✅ |
| `AmazonBedrock_UserGuide.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/bedrock/latest/userguide/bedrock-ug.pdf | ✅ |
| `bedrock-api.pdf` / `.md` | https://docs.aws.amazon.com/pdfs/bedrock/latest/APIReference/bedrock-api.pdf | ✅ |

### Blog posts and articles

| Local file | Source URL | Status |
|---|---|---|
| `introducing-new-ray-capabilities-sagemaker-hyperpod.md` | https://aws.amazon.com/blogs/machine-learning/introducing-new-ray-capabilities-on-sagemaker-hyperpod/ | ✅ |
| `how-vannevar-labs-cut-ml-inference-costs-45-percent-ray-eks.md` | https://aws.amazon.com/blogs/containers/how-vannevar-labs-cut-ml-inference-costs-by-45-using-ray-on-amazon-eks/ | ✅ |
| `building-reliable-scalable-genai-infrastructure-aws-ray-anyscale.md` | https://aws.amazon.com/blogs/apn/building-reliable-and-scalable-generative-ai-infrastructure-on-aws-with-ray-and-anyscale/ | ✅ |
| `run-multi-node-inference-ray-llm-deep-learning-containers.md` | https://aws.amazon.com/blogs/machine-learning/run-multi-node-inference-workloads-using-ray-llm-deep-learning-containers/ | ✅ |
| `scaling-ai-ml-workloads-ray-aws.md` | https://aws.amazon.com/blogs/opensource/scaling-ai-and-machine-learning-workloads-with-ray-on-aws/ | ✅ |
| `build-ai-workflows-on-amazon-eks-with-union-ai-and-flyte.md` | https://aws.amazon.com/blogs/machine-learning/build-ai-workflows-on-amazon-eks-with-union-ai-and-flyte/ | ✅ |
| `run-kubernetes-clusters-for-less-with-amazon-ec2-spot-and-karpenter.md` | https://builder.aws.com/content/2dhlDEUfwElQ9mhtOP6D8YJbULA/run-kubernetes-clusters-for-less-with-amazon-ec2-spot-and-karpenter | ✅ |

### Conference session

| Local file | Source URL | Status |
|---|---|---|
| `KUB312_Simplify-Kubernetes-workloads-with-Karpenter-and-Amazon-EKS-Auto-Mode.pdf` / `.md` (AWS re:Invent KUB312 slide deck) | No public slide URL found. Related official pages: https://docs.aws.amazon.com/eks/latest/best-practices/karpenter.html and https://docs.aws.amazon.com/eks/latest/best-practices/automode.html | ❌ |

---

## `Resources/flyte/`

Flyte 2 open-source docs, served by Union.ai. Every page is also available as Markdown by appending `.md`. Full index: https://www.union.ai/docs/v2/flyte/llms.txt (✅). Single-file dump: https://www.union.ai/docs/v2/flyte/llms-full.txt (✅).

| Local file | Source URL | Status |
|---|---|---|
| `get-started.md` | https://www.union.ai/docs/v2/flyte/user-guide/get-started | ✅ |
| `tasks.md` | https://www.union.ai/docs/v2/flyte/user-guide/tasks | ✅ |
| `apps.md` | https://www.union.ai/docs/v2/flyte/user-guide/apps | ✅ |
| `triggers.md` | https://www.union.ai/docs/v2/flyte/user-guide/triggers | ✅ |
| `agents.md` | https://www.union.ai/docs/v2/flyte/user-guide/agents | ✅ |
| `system-one-types.md` | https://www.union.ai/docs/v2/flyte/user-guide/system-one-types | ✅ |
| `software-development-lifecycle.md` | https://www.union.ai/docs/v2/flyte/user-guide/software-development-lifecycle | ✅ |
| `scale-your-runs.md` | https://www.union.ai/docs/v2/flyte/user-guide/run-scaling | ✅ |
| `advanced-project.md` | https://www.union.ai/docs/v2/flyte/user-guide/advanced-project | ✅ |
| `llms-full.md` | https://www.union.ai/docs/v2/flyte/llms-full.txt | ✅ |

Commercial superset docs (Union.ai): https://www.union.ai/docs/v2/union/llms.txt (✅).

---

## `Resources/ray/`

| Local file | Source URL | Status |
|---|---|---|
| `RayV2Architecture.pdf` / `.md` (Ray v2 Architecture whitepaper) | https://docs.ray.io/en/latest/ray-contribute/whitepaper.html (the official page; the whitepaper itself is embedded there) | ✅ |
| `Exoshuffle An Extensible Shuffle Architecture.html` / `.md` (SIGCOMM 2023) | Preprint: https://arxiv.org/abs/2203.05072 · Published: https://doi.org/10.1145/3603269.3604848 | ✅ arXiv · 🔒 ACM |

---

## `Resources/docker-k8s/`

| Local file | Source URL | Status |
|---|---|---|
| `docker_cheatsheet.pdf` / `docker-cheatsheet.md` | https://docs.docker.com/get-started/docker_cheatsheet.pdf | ✅ |
| Docker Desktop reference (linked from `docker-cheatsheet.md`) | https://docs.docker.com/desktop/ | ✅ |
| `9781807301095_ColorImages.pdf` / `operational-ai-with-docker-color-images.md` (Packt, *Operational AI with Docker*, Ajeet Singh Raina and Harsh Manvar, 2026) | Book page: https://www.packtpub.com/en-us/product/operational-ai-with-docker-9781807301088 · O'Reilly: https://www.oreilly.com/library/view/operational-ai-with/9781807301095/ | 🔒 |
| `images/packt/ocr/*` (OCR of figures from the book) | Derived from the book above | 🔒 |

The color-images PDF is a Packt companion download. No direct public URL was found; it is distributed with the book purchase. It is not redistributable.

---

## `Resources/copilot/`

Mostly in-house design docs with no external source. Third-party items:

| Local file | Source | Status |
|---|---|---|
| `stanford-llm-creativity/stanford-llm-creativity.txt` | Medium article by Adham Khaled, "Stanford Just Killed Prompt Engineering With 8 Words". No URL recorded in the file and none was searched for. | ❌ |
| `stanford-llm-creativity/` (underlying paper cited by `LTI-Killed-Prompt-Engineering.md`) | https://arxiv.org/abs/2510.01171 | ✅ |

---

## Not covered

| Path | Reason |
|---|---|
| `Resources/visualization/`, `Resources/Templates/` | In-house diagrams and templates. |
| `Resources/eksctl-karpenter.md`, `Resources/vi-cheatsheet.md`, `Resources/self-referential.md` | In-house notes; no external source recorded in the files. |
| `Resources/aws/*.chunks/`, `*.assets/` | Derived from the PDFs above (chunked markdown and extracted images). |
