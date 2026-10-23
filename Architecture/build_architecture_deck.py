#!/usr/bin/env python3
"""
build_architecture_deck.py — Generate the Phase 1 architecture decision deck.

Builds "Architecture Options - Decision Deck.pptx" from the analysis in
Projects/Burstable MLaaS/Architecture/. Regenerate after changing any of:

  * Recommended Architecture - Surrogate ML Accelerator.md
  * Alternative Architecture - AWS Batch.md
  * Alternative Architecture - Amazon ECS.md

Content lives in CONTENT below so the deck stays editable without touching
layout code. Usage:

    python scripts/automation/build_architecture_deck.py [--out PATH]
"""
import argparse
import os
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_OUT = (WORKSPACE / "Projects" / "Burstable MLaaS" / "Architecture"
               / "Architecture Options - Decision Deck.pptx")

# ---------------------------------------------------------------- palette ---
INK = RGBColor(0x22, 0x27, 0x2E)
MUTED = RGBColor(0x6B, 0x72, 0x80)
PRIMARY = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0x2E, 0x8B, 0x8B)
GOOD = RGBColor(0x2E, 0x7D, 0x54)
WARN = RGBColor(0xB0, 0x76, 0x0B)
BAD = RGBColor(0xA4, 0x34, 0x3A)
PANEL = RGBColor(0xF4, 0xF6, 0xF8)
RULE = RGBColor(0xD8, 0xDE, 0xE5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Segoe UI"
W, H = Inches(13.333), Inches(7.5)

VERDICT_COLOR = {"+": GOOD, "~": WARN, "-": BAD}


# ---------------------------------------------------------------- helpers ---
def textbox(slide, x, y, w, h, text, size=14, bold=False, color=INK,
            align=PP_ALIGN.LEFT, space_after=6, line=1.15):
    """Add a text box; `text` may be a string or a list of paragraph strings."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = line
        run = p.add_run()
        run.text = ln
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = FONT
    return tb


def panel(slide, x, y, w, h, fill=PANEL, line=RULE):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line
    sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    sh.adjustments[0] = 0.04
    sh.text_frame.text = ""
    return sh


def slide_base(prs, title, kicker=None):
    """Blank slide with the standard header and footer rule."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if kicker:
        textbox(s, Inches(0.6), Inches(0.34), Inches(12), Inches(0.3),
                kicker.upper(), size=10, bold=True, color=ACCENT)
        ty = Inches(0.62)
    else:
        ty = Inches(0.45)
    textbox(s, Inches(0.6), ty, Inches(12.2), Inches(0.6), title,
            size=26, bold=True, color=PRIMARY)
    bar = s.shapes.add_shape(1, Inches(0.6), Inches(1.28), Inches(1.1), Pt(3))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    bar.shadow.inherit = False
    textbox(s, Inches(0.6), Inches(7.05), Inches(8), Inches(0.3),
            "GE Vernova Proprietary  ·  Surrogate ML Accelerator  ·  Phase 1 architecture decision",
            size=8, color=MUTED)
    return s


def table(slide, x, y, w, rows, col_w=None, header=True, size=10,
          header_size=10, row_h=Inches(0.32), verdict_cols=()):
    """Render `rows` (list of lists of str) as a table.

    Cells in `verdict_cols` are colour-coded by a leading +, ~ or - marker,
    which is stripped from the displayed text.
    """
    nrows, ncols = len(rows), len(rows[0])
    shape = slide.shapes.add_table(nrows, ncols, x, y, w, row_h * nrows)
    tbl = shape.table
    if col_w:
        for i, cw in enumerate(col_w):
            tbl.columns[i].width = cw
    for r, row in enumerate(rows):
        tbl.rows[r].height = row_h
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.07)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            colour = INK
            txt = val
            if r == 0 and header:
                cell.fill.fore_color.rgb = PRIMARY
                colour = WHITE
            else:
                cell.fill.fore_color.rgb = WHITE if r % 2 else PANEL
                if c in verdict_cols and txt[:1] in VERDICT_COLOR:
                    colour = VERDICT_COLOR[txt[:1]]
                    txt = txt[1:].lstrip()
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c in verdict_cols else PP_ALIGN.LEFT
            run = p.add_run()
            run.text = txt
            run.font.size = Pt(header_size if r == 0 and header else size)
            run.font.bold = (r == 0 and header) or (c in verdict_cols)
            run.font.color.rgb = colour
            run.font.name = FONT
    return tbl


def pros_cons(slide, pros, cons, y=Inches(1.65)):
    gap, colw = Inches(0.4), Inches(5.95)
    for i, (heading, items, accent) in enumerate(
            [("STRENGTHS", pros, GOOD), ("COSTS & LIMITATIONS", cons, BAD)]):
        x = Inches(0.6) + i * (colw + gap)
        panel(slide, x, y, colw, Inches(4.9))
        textbox(slide, x + Inches(0.25), y + Inches(0.22), colw - Inches(0.5),
                Inches(0.3), heading, size=11, bold=True, color=accent)
        textbox(slide, x + Inches(0.25), y + Inches(0.62), colw - Inches(0.5),
                Inches(4.0), ["•  " + t for t in items], size=11.5,
                space_after=9, line=1.12)


# ---------------------------------------------------------------- content ---
OPTIONS = ["EKS + Karpenter + Ray", "AWS Batch", "Amazon ECS"]

CONTENT = {
    "requirements": [
        ["Source", "Requirement"],
        ["Kickoff", "Rapid enablement — researchers productive on GPUs quickly"],
        ["Kickoff", "Linear scaling 1 → N GPUs; training from days to hours (multi-node)"],
        ["Kickoff", ">90% utilization, against a 60–70% on-prem baseline"],
        ["Kickoff", "Shell/SSH access prioritised over complex web UIs"],
        ["Kickoff", "Self-service — no ticketing systems or deployment queues"],
        ["Kickoff", "Flat support model; no blocker persists beyond 24 hours"],
        ["Kickoff", "Project Lab Notebook — configuration and lessons captured"],
        ["Kickoff", "SMaaS foundation for Phase 2 — a shared service across business units"],
        ["Kickoff", "Stack named as EKS / Ray / Argo"],
        ["SOW", "D7 — training equivalent to on-prem, across multiple GPUs"],
        ["SOW", "D8 — infrastructure supporting the Burstable MLaaS offering"],
        ["LTI", "Tri-environment parity — Mac, AWS, on-prem (our stated invariant)"],
    ],
    "glance": [
        ("EKS + Karpenter + Ray",
         "RECOMMENDED",
         ["Karpenter provisions p5 nodes when Ray", "workers are pending; researchers",
          "submit from a CPU dev pod and GPUs", "attach to the job, not the person."],
         PRIMARY),
        ("AWS Batch",
         "ALTERNATIVE",
         ["A managed queue materialises a cluster", "per job and destroys it. Gang",
          "scheduling and fair-share are built in;", "the interactive loop is not."],
         ACCENT),
        ("Amazon ECS",
         "ALTERNATIVE",
         ["ECS Managed Instances with AWS owning", "drivers and patching. Most managed,",
          "least controllable — and no gang", "scheduling primitive at all."],
         MUTED),
    ],
}


def build(out_path):
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H

    # ---------------------------------------------------------- 1. title ---
    s = prs.slides.add_slide(prs.slide_layouts[6])
    band = s.shapes.add_shape(1, 0, 0, W, Inches(3.1))
    band.fill.solid()
    band.fill.fore_color.rgb = PRIMARY
    band.line.fill.background()
    band.shadow.inherit = False
    textbox(s, Inches(0.9), Inches(1.0), Inches(11), Inches(0.4),
            "SURROGATE ML ACCELERATOR", size=12, bold=True,
            color=RGBColor(0x9F, 0xC6, 0xC6))
    textbox(s, Inches(0.9), Inches(1.45), Inches(11.5), Inches(0.9),
            "Architecture Options & Recommendation", size=38, bold=True, color=WHITE)
    textbox(s, Inches(0.9), Inches(2.35), Inches(11), Inches(0.4),
            "Three candidate architectures, evaluated against the project's stated needs",
            size=15, color=RGBColor(0xC9, 0xD6, 0xE4))
    textbox(s, Inches(0.9), Inches(3.5), Inches(11), Inches(1.2),
            ["GE Vernova ARC  ·  Logic Technology, Inc.",
             "Phase 1 decision input  ·  19 October 2026",
             "Footprint settled: 3 × p5.48xlarge — 24 H100 GPUs",
             "Prepared by the LTI cloud team"],
            size=13, color=INK, space_after=5)
    textbox(s, Inches(0.9), Inches(6.5), Inches(11), Inches(0.5),
            "GE Vernova Proprietary — not for external distribution",
            size=9, color=MUTED)

    # ------------------------------------------------ 2. what this decides --
    s = slide_base(prs, "What this deck decides", "purpose")
    panel(s, Inches(0.6), Inches(1.65), Inches(12.1), Inches(1.55))
    textbox(s, Inches(0.95), Inches(1.95), Inches(11.5), Inches(1.0),
            ["One decision: which compute architecture Phase 1 builds on.",
             "It gates the GPU capacity request, the build sequence, and the Architectural Reference Diagram deliverable."],
            size=15, space_after=8)
    textbox(s, Inches(0.6), Inches(3.5), Inches(5.9), Inches(0.35),
            "IN SCOPE", size=11, bold=True, color=ACCENT)
    textbox(s, Inches(0.6), Inches(3.9), Inches(5.9), Inches(2.4),
            ["•  The compute substrate and how jobs reach GPUs",
             "•  How researchers get a shell and submit work",
             "•  How the training data path is shaped",
             "•  What each option costs us in operations"],
            size=12.5, space_after=9)
    textbox(s, Inches(6.9), Inches(3.5), Inches(5.8), Inches(0.35),
            "DECIDED ELSEWHERE", size=11, bold=True, color=MUTED)
    textbox(s, Inches(6.9), Inches(3.9), Inches(5.8), Inches(2.4),
            ["•  Server count — settled: 3 × p5.48xlarge, 24 GPUs",
             "•  Costing option — on-demand or 12-month prepay",
             "•  Application tier — out of Phase 1 scope",
             "•  DT4D's Java/React stack — not this project's",
             "•  Region, and whether p5 capacity exists there"],
            size=12.5, space_after=9, color=MUTED)

    # --------------------------------- 3. requirements update (2026-10-19) --
    s = slide_base(prs, "How they work today — 19 October", "current practice, not a spec")
    textbox(s, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.35),
            "Deepak Akhare described how the team works TODAY on on-prem hardware — not a specification for what to build. Several answers describe a limit being worked around.",
            size=12, color=MUTED)
    items = [
        ("Multi-server training not used today", WARN,
         "Because on-prem cannot. The kickoff names multi-node as the destination, so EFA and cluster placement "
         "stay in the build — off the Phase 1 critical path, but near-free now and costly to retrofit."),
        ("Jobs run for days — today", WARN,
         "The kickoff's goal is days to hours. If we succeed, jobs get shorter and more numerous, "
         "and the iteration loop matters MORE, not less. Do not optimise for the current duration."),
        ("The pipeline is CPU-heavy outside training", GOOD,
         "100–200 CPUs preprocessing, 150 for rendering, 8–16 per GPU for loading. Real work either way — "
         "and a CPU pool is now first-class. No design carried one before."),
        ("A serialised preprocessing stage", GOOD,
         "One writer for the consolidated HDF5, then a global statistics pass. Flagged as a current implementation "
         "detail — an early win to parallelise across on-demand CPUs, not a constraint to design around."),
    ]
    y = Inches(1.88)
    for head, colour, body in items:
        panel(s, Inches(0.6), y, Inches(12.1), Inches(1.08))
        bar = s.shapes.add_shape(1, Inches(0.6), y, Pt(5), Inches(1.08))
        bar.fill.solid(); bar.fill.fore_color.rgb = colour
        bar.line.fill.background(); bar.shadow.inherit = False
        textbox(s, Inches(1.0), y + Inches(0.17), Inches(11.3), Inches(0.3),
                head, size=14, bold=True, color=PRIMARY)
        textbox(s, Inches(1.0), y + Inches(0.53), Inches(11.3), Inches(0.55),
                body, size=11, color=INK)
        y += Inches(1.21)
    textbox(s, Inches(0.6), Inches(6.62), Inches(12.1), Inches(0.33),
            "Read as a target spec, these answers would have us rebuild Alpharetta in AWS at $92k/month. Read as today's practice, they tell us what to fix first.",
            size=11.5, bold=True, color=PRIMARY)

    # ------------------------------------------- 4. the dual mandate -------
    s = slide_base(prs, "Two obligations, pulling different ways", "the dual mandate")
    cols = [("SUPPORT THE WORK THEY DO TODAY", ACCENT,
             ["Their pipeline must run unchanged on day one —",
              "same HDF5, same container, same scripts.",
              "",
              "If researchers have to rewrite anything to get",
              "started, adoption stalls and the 24-hour unblock",
              "commitment turns into a support queue."]),
            ("BE DEMONSTRABLY BETTER THAN ON-PREM", GOOD,
             ["This is not a lift-and-shift. It exists to remove",
              "the constraints that shaped current practice:",
              "",
              "waiting for a free machine · single-node ceilings ·",
              "days-long jobs · a serialised preprocessing stage",
              "· rendering queued behind GPU work."])]
    colw, gap = Inches(5.95), Inches(0.4)
    for i, (head, colour, lines) in enumerate(cols):
        x = Inches(0.6) + i * (colw + gap)
        panel(s, x, Inches(1.65), colw, Inches(2.5))
        bar = s.shapes.add_shape(1, x, Inches(1.65), colw, Pt(4))
        bar.fill.solid(); bar.fill.fore_color.rgb = colour
        bar.line.fill.background(); bar.shadow.inherit = False
        textbox(s, x + Inches(0.25), Inches(1.92), colw - Inches(0.5), Inches(0.3),
                head, size=11, bold=True, color=colour)
        textbox(s, x + Inches(0.25), Inches(2.32), colw - Inches(0.5), Inches(1.7),
                lines, size=11.5, space_after=3, line=1.12)
    textbox(s, Inches(0.6), Inches(4.35), Inches(12.1), Inches(0.35),
            "Neither alone gives the right design. Build only for today and we reproduce Alpharetta in AWS at $92k/month. "
            "Build only for the destination and researchers arrive to an environment that will not run their code.",
            size=12, bold=True, color=PRIMARY)
    steps = [("DAY ONE", "Parity", "Their pipeline runs as-is: GPU container, 4–8 GPUs on one node, HDF5 staged locally, logs and checkpoints persisted. Nothing to rewrite."),
             ("EARLY WINS", "The constraints they feel", "Parallelise the single-writer preprocessing across 100–200 on-demand CPUs. Give rendering its own CPU pool. A GPU in seconds, not when a box frees up."),
             ("BUILT IN, PROVEN LATER", "The destination", "EFA, cluster placement and multi-node capability ship in Phase 1, demonstrated when a workload needs them. Capability is cheap now; retrofitting is not.")]
    y = Inches(4.95)
    for tag, title_, body in steps:
        chip = s.shapes.add_shape(1, Inches(0.6), y, Inches(1.95), Inches(0.26))
        chip.fill.solid(); chip.fill.fore_color.rgb = PRIMARY
        chip.line.fill.background(); chip.shadow.inherit = False
        textbox(s, Inches(0.66), y + Inches(0.03), Inches(1.9), Inches(0.22),
                tag, size=8.5, bold=True, color=WHITE)
        textbox(s, Inches(2.75), y - Inches(0.02), Inches(2.6), Inches(0.28),
                title_, size=12.5, bold=True, color=PRIMARY)
        textbox(s, Inches(5.5), y - Inches(0.02), Inches(7.2), Inches(0.5),
                body, size=10.5, color=INK)
        y += Inches(0.66)

    # ------------------------------------- 5. the moving parts, plainly ----
    s = slide_base(prs, "The moving parts, in plain language", "orientation")
    textbox(s, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.35),
            "Skip this slide if the terms are already familiar.", size=11, color=MUTED)
    rows = [["Term", "What it actually is", "Why it matters here"],
            ["Kubernetes / EKS", "A cluster manager that runs containers across many machines",
             "The substrate Ray and Argo both require"],
            ["Karpenter", "Watches for work that has nowhere to run, then buys the right EC2 machine",
             "How a GPU server appears in 60 seconds and leaves when idle"],
            ["Ray", "A Python framework that spreads one program across many GPUs",
             "What turns 8 GPUs into one training run"],
            ["KubeRay", "The piece that runs Ray clusters on Kubernetes",
             "Makes Ray cluster lifecycle automatic rather than hand-rolled"],
            ["AWS Batch", "A managed job queue: submit work, AWS finds machines, runs it, tidies up",
             "No scheduler to operate — but you wait in line"],
            ["Amazon ECS", "AWS's own container service; simpler than Kubernetes",
             "Least to operate, but cannot start N machines as one unit"],
            ["Gang scheduling", "Starting N machines together, as a unit, so they can talk mid-job",
             "Mandatory for training that spans more than one server"],
            ["EFA", "A high-speed network card for server-to-server GPU traffic",
             "Without it, multi-node training does not scale"],
            ["p5.48xlarge", "One AWS server with 8 NVIDIA H100 GPUs (640 GB GPU memory)",
             "We are buying 3 of them: 24 GPUs, ~$91.6k/month"],
            ["FSx for Lustre", "A fast shared filesystem built for HPC workloads",
             "Needed only if jobs read each other's files, or meshes"]]
    table(s, Inches(0.6), Inches(1.85), Inches(12.1), rows,
          col_w=[Inches(2.1), Inches(5.9), Inches(4.1)], size=10.5, row_h=Inches(0.42))

    # -------------------------------------------------- 4. requirements ----
    s = slide_base(prs, "What we are evaluating against", "project needs")
    table(s, Inches(0.6), Inches(1.6), Inches(12.1), CONTENT["requirements"],
          col_w=[Inches(1.5), Inches(10.6)], size=11.5, row_h=Inches(0.37))
    textbox(s, Inches(0.6), Inches(6.55), Inches(12.1), Inches(0.4),
            "Sources: 2026-10-12 research kickoff (Jim Tallman) · SOW scope document · LTI architecture analysis",
            size=9.5, color=MUTED)

    # ------------------------------------------------ 4. three at a glance --
    s = slide_base(prs, "Three candidates", "at a glance")
    colw, gap = Inches(3.87), Inches(0.26)
    for i, (name, tag, lines, colour) in enumerate(CONTENT["glance"]):
        x = Inches(0.6) + i * (colw + gap)
        panel(s, x, Inches(1.7), colw, Inches(4.5))
        chip = s.shapes.add_shape(1, x + Inches(0.3), Inches(1.95),
                                  Inches(1.5), Inches(0.28))
        chip.fill.solid()
        chip.fill.fore_color.rgb = colour
        chip.line.fill.background()
        chip.shadow.inherit = False
        textbox(s, x + Inches(0.36), Inches(1.99), Inches(1.4), Inches(0.25),
                tag, size=9, bold=True, color=WHITE)
        textbox(s, x + Inches(0.3), Inches(2.45), colw - Inches(0.6),
                Inches(0.8), name, size=17, bold=True, color=PRIMARY)
        textbox(s, x + Inches(0.3), Inches(3.35), colw - Inches(0.6),
                Inches(2.4), lines, size=12, space_after=2, line=1.25)

    # --------------------------------------------------- 5-10. each option --
    opts = [
        ("EKS + Karpenter + Ray", "option a — recommended",
         [["Layer", "Choice"],
          ["Compute", "One EKS cluster; Karpenter-managed p5.48xlarge"],
          ["Capacity", "3 × p5.48xlarge = 24 H100 GPUs; single-AZ, placement group, EFA, ODCR"],
          ["Jobs", "KubeRay — persistent RayCluster, RayJob for batch runs"],
          ["Access", "kubectl exec into a CPU dev pod; ray job submit from the laptop"],
          ["Data", "S3 as system of record; FSx for Lustre if artifacts interact"],
          ["Platform", "Argo CD for GitOps; Argo Workflows deferred; MLflow"],
          ["Telemetry", "DCGM → Prometheus → Grafana"]],
         "Mechanism: Ray workers go pending → Karpenter provisions a p5 → the job runs → nodes consolidate away. GPUs attach to the job, never to a person.",
         ["Only option preserving a seconds-long iteration loop",
          "Satisfies the EKS / Ray / Argo stack as named at kickoff",
          "D8 is structural — the burst layer IS the compute substrate, built week 3",
          "Tri-environment parity: same image on Mac, AWS and on-prem",
          "Ray Data brings pipelined shuffle (Exoshuffle) for free",
          "Spot-eligible for interruption-tolerant work",
          "kubectl from a laptop is an established GE pattern (C. Burke)"],
         ["Largest operational surface — Karpenter and Ray are ours to tune",
          "Heaviest GWD review artifact of the three",
          "An unschedulable pod is harder for a researcher to self-diagnose",
          "Needs Kubernetes fluency across a 1.0 + 0.5 + 0.5 FTE team",
          "Phase 2 multi-tenancy must be hand-built (namespaces, quotas)",
          "Scope question: SOW says 'static servers', excludes scheduling software"]),

        ("AWS Batch", "option b — alternative",
         [["Layer", "Choice"],
          ["Compute", "EKS cluster + Batch managed compute environment"],
          ["Capacity", "3 × p5.48xlarge via launch template; ODCR targeting"],
          ["Jobs", "Two queues — regular container jobs, and MNP for multi-node"],
          ["Access", "Dev pods on a separate platform node group; no GPU shell"],
          ["Runtime", "torchrun / NCCL, or hand-bootstrapped Ray on MNP"],
          ["Scheduling", "Managed queues with fair-share scheduling policies"],
          ["Telemetry", "DCGM DaemonSet + native CloudWatch queue metrics"]],
         "Mechanism: submit to a queue → Batch materialises nodes → the job runs → everything is destroyed. A managed bulletin board.",
         ["Literally the 'bulletin board' the kickoff describes",
          "Nothing to operate — queues, priorities, retries, fair-share are AWS's job",
          "Pend time is emitted natively by CloudWatch, not instrumented by us",
          "Gang scheduling is built in and correct, with no extra components",
          "Strongest Phase 2 SMaaS foundation — fair-share across business units",
          "Smaller security-review surface than the EKS option"],
         ["The interactive loop dies — minutes per iteration, not seconds",
          "No GPU shell at all; debugging a live distributed job is not possible",
          "Ray reduces to a library, hand-bootstrapped from AWS_BATCH_JOB_* vars",
          "No Spot for MNP jobs — removes the main cost lever",
          "MNP nodes are single-tenant: a 1-GPU job occupies all 8 GPUs of a p5",
          "EFA on Batch-on-EKS is undocumented by AWS — a live build risk",
          "Tri-environment parity is lost; Argo becomes glue"]),

        ("Amazon ECS", "option c — alternative",
         [["Layer", "Choice"],
          ["Compute", "ECS cluster; Managed Instances capacity provider"],
          ["Capacity", "AWS owns AMI, NVIDIA drivers, patching, GPU auto-repair"],
          ["Jobs", "ECS tasks; Ray head/worker as long-lived ECS services"],
          ["Access", "ECS Exec — a real, audited shell into a running task"],
          ["Multi-node", "No primitive — needs self-managed capacity or Batch MNP"],
          ["Orchestration", "Step Functions or MWAA; no Flyte, no Argo"],
          ["Telemetry", "CloudWatch Container Insights + DCGM daemon service"]],
         "Mechanism: ECS schedules tasks onto AWS-managed instances. Simplest to operate — and the only option that cannot gang-schedule.",
         ["Genuinely zero Kubernetes — the only option that delivers this",
          "Most managed GPU fleet on AWS: drivers, patching, auto-repair",
          "Fractional GPU on G6f (to ⅛ of an L4) — unique among the three",
          "ECS Exec gives a real shell, serving the kickoff's shell priority",
          "A persistent Ray cluster is viable, so the interactive loop survives",
          "Smallest security-review surface of the three"],
         ["Karpenter, Flyte, Argo Workflows and Argo CD cannot run at all",
          "No gang-scheduling primitive — the capability the phase is graded on",
          "Managed Instances exposes no custom AMI, placement group or userdata",
          "…which removes EFA, host-mounted FSx and NVMe staging in one stroke",
          "Multi-node needs self-managed capacity on an undocumented EFA path",
          "No queue, so no native pend-time metric; no fair-share for Phase 2",
          "Tri-environment parity lost; satisfies none of EKS / Ray / Argo"]),
    ]

    def flow_slide():
        """Boxes-and-arrows view of the recommended architecture."""
        from pptx.enum.shapes import MSO_SHAPE
        s = slide_base(prs, "How the recommended option works", "option a — mechanism")
        boxes = [("Researcher", ["laptop", "edit code"], MUTED),
                 ("Dev pod", ["CPU only", "cheap, always on"], ACCENT),
                 ("Ray", ["schedules the job", "across GPUs"], PRIMARY),
                 ("Karpenter", ["buys a GPU server", "when work is pending"], PRIMARY),
                 ("p5 servers", ["3 nodes, 8 × H100 each", "24 GPUs, linked by EFA"], GOOD)]
        bw, bh, gap = Inches(2.17), Inches(1.45), Inches(0.33)
        x, y = Inches(0.6), Inches(2.0)
        for i, (title_, lines, colour) in enumerate(boxes):
            b = panel(s, x, y, bw, bh, fill=WHITE, line=colour)
            b.line.width = Pt(1.5)
            textbox(s, x + Inches(0.15), y + Inches(0.22), bw - Inches(0.3),
                    Inches(0.3), title_, size=14, bold=True, color=colour,
                    align=PP_ALIGN.CENTER)
            textbox(s, x + Inches(0.12), y + Inches(0.68), bw - Inches(0.24),
                    Inches(0.6), lines, size=10.5, color=INK,
                    align=PP_ALIGN.CENTER, space_after=2)
            if i < len(boxes) - 1:
                a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + bw + Inches(0.06),
                                       y + Inches(0.6), Inches(0.21), Inches(0.24))
                a.fill.solid(); a.fill.fore_color.rgb = RULE
                a.line.fill.background(); a.shadow.inherit = False
            x += bw + gap
        labels = ["", "ray job submit", "workers pending", "node joins in ~60s", ""]
        x = Inches(0.6)
        for i, lab in enumerate(labels):
            if lab:
                textbox(s, x - Inches(0.5), y + bh + Inches(0.1), bw + Inches(0.9),
                        Inches(0.3), "↑ " + lab, size=9.5, color=MUTED,
                        align=PP_ALIGN.CENTER)
            x += bw + gap
        panel(s, Inches(0.6), Inches(4.3), Inches(12.1), Inches(0.75),
              fill=RGBColor(0xEC, 0xF3, 0xF3), line=ACCENT)
        textbox(s, Inches(0.95), Inches(4.52), Inches(11.5), Inches(0.35),
                "Data:   Alpharetta  →  DataSync  →  S3 (system of record)  →  FSx for Lustre, only if jobs read each other's files",
                size=12, color=PRIMARY)
        notes = [("GPUs attach to the job, not the person",
                  "The researcher never holds a GPU while editing — which is exactly what caps on-prem at 60–70%."),
                 ("Idle means zero",
                  "When the board empties, Karpenter consolidates the nodes away. Nothing sits warm at $30.5k per server per month.")]
        for i, (h, b) in enumerate(notes):
            bx = Inches(0.6) + i * Inches(6.25)
            textbox(s, bx, Inches(5.35), Inches(5.9), Inches(0.3), h,
                    size=12.5, bold=True, color=GOOD)
            textbox(s, bx, Inches(5.72), Inches(5.9), Inches(0.8), b,
                    size=11, color=INK)

    for name, kicker, rows, mech, pros, cons in opts:
        s = slide_base(prs, name, kicker)
        table(s, Inches(0.6), Inches(1.6), Inches(12.1), rows,
              col_w=[Inches(2.0), Inches(10.1)], size=11.5, row_h=Inches(0.42))
        panel(s, Inches(0.6), Inches(5.35), Inches(12.1), Inches(1.0),
              fill=RGBColor(0xEC, 0xF3, 0xF3), line=ACCENT)
        textbox(s, Inches(0.95), Inches(5.6), Inches(11.5), Inches(0.6),
                mech, size=12.5, color=PRIMARY)

        if name.startswith("EKS"):
            flow_slide()

        s = slide_base(prs, name + " — strengths and costs", kicker)
        pros_cons(s, pros, cons)

    # ------------------------------------------------ 11. head-to-head -----
    s = slide_base(prs, "Head to head", "comparison")
    rows = [["Dimension", "EKS + Ray", "AWS Batch", "Amazon ECS"],
            ["Iteration loop", "+ Seconds", "- Minutes", "~ Seconds"],
            ["Shell on a GPU", "+ Yes", "- No", "+ Yes"],
            ["Gang scheduling", "+ Ray native", "+ MNP built in", "- No primitive"],
            ["Multi-node + EFA", "+ Documented", "~ Undocumented on EKS", "- Needs self-managed"],
            ["Scheduler to operate", "- Ours", "+ Managed", "~ None, but no queue"],
            ["GPU fleet operations", "- Ours", "~ AWS manages CE", "+ Most managed"],
            ["Fair-share / Phase 2", "~ Hand-built", "+ Native", "- Nothing"],
            ["Pend-time metric", "~ Build it", "+ Native", "- No queue"],
            ["Spot eligibility", "+ Yes", "- Not for MNP", "+ Yes"],
            ["Ray ecosystem", "+ Full", "- Execution only", "~ Partial"],
            ["Tri-environment parity", "+ Yes", "- AWS only", "- AWS only"],
            ["EKS / Ray / Argo mandate", "+ As named", "~ Partial", "- None"]]
    table(s, Inches(0.6), Inches(1.6), Inches(12.1), rows,
          col_w=[Inches(4.0), Inches(2.7), Inches(2.7), Inches(2.7)],
          size=11, row_h=Inches(0.38), verdict_cols=(1, 2, 3))

    # ------------------------------------------- 14. a day in the life -----
    s = slide_base(prs, "What it feels like to use", "a day in the life")
    textbox(s, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.35),
            "A researcher changes one line of code and runs it again. The same loop, twenty times a day.",
            size=12.5, color=MUTED)
    cols = [("EKS + Karpenter + Ray", GOOD,
             ["Edit the file in the dev pod",
              "ray job submit",
              "Runs on a live cluster — output",
              "starts within seconds",
              "Spot the bug, edit, resubmit",
              "", "≈ 20 iterations in an afternoon"]),
            ("AWS Batch", BAD,
             ["Edit the file in the dev pod",
              "aws batch submit-job",
              "RUNNABLE … wait. Nodes provision,",
              "image pulls, runtime bootstraps",
              "First log line after 3–6 minutes",
              "", "≈ 6 iterations in an afternoon"]),
            ("Amazon ECS", WARN,
             ["Edit the file in the dev pod",
              "ray job submit",
              "Live Ray service answers in",
              "seconds — same as EKS",
              "But multi-node needs a separate,",
              "self-managed path entirely",
              "≈ 20 iterations, single-node only"])]
    colw, gap = Inches(3.87), Inches(0.26)
    for i, (name, colour, lines) in enumerate(cols):
        x = Inches(0.6) + i * (colw + gap)
        panel(s, x, Inches(1.95), colw, Inches(4.0))
        bar = s.shapes.add_shape(1, x, Inches(1.95), colw, Pt(4))
        bar.fill.solid(); bar.fill.fore_color.rgb = colour
        bar.line.fill.background(); bar.shadow.inherit = False
        textbox(s, x + Inches(0.25), Inches(2.2), colw - Inches(0.5), Inches(0.35),
                name, size=14, bold=True, color=PRIMARY)
        textbox(s, x + Inches(0.25), Inches(2.72), colw - Inches(0.5), Inches(2.4),
                lines[:-1], size=11.5, space_after=5, line=1.1)
        textbox(s, x + Inches(0.25), Inches(5.35), colw - Inches(0.5), Inches(0.4),
                lines[-1], size=12.5, bold=True, color=colour)
    panel(s, Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.72),
          fill=RGBColor(0xEC, 0xF3, 0xF3), line=ACCENT)
    textbox(s, Inches(0.95), Inches(6.36), Inches(11.5), Inches(0.35),
            "This is the difference the kickoff was pointing at with \"no ticketing systems or formal deployment queues\" — not approvals, but waiting.",
            size=12, color=PRIMARY)

    # ------------------------------- 15. evaluation vs project requirements --
    s = slide_base(prs, "Evaluated against the project's needs", "requirements fit")
    rows = [["Requirement", "EKS + Ray", "AWS Batch", "Amazon ECS"],
            ["Rapid enablement", "+ GPUs in week 4", "~ Week 5, after spikes", "~ Week 5"],
            ["Linear scaling, multi-node", "+ Native path", "~ EFA unproven on EKS", "- Cannot gang-schedule"],
            [">90% utilization", "+ Jobs, not people, hold GPUs", "+ Queue-driven", "~ No queue to measure"],
            ["Shell over web UIs", "+ Dev pod + kubectl", "~ Shell, but not on a GPU", "+ ECS Exec"],
            ["No ticketing or queues", "+ Submit to a live cluster", "- Submit-and-wait", "+ Live Ray cluster"],
            ["24-hour unblock on 2 FTE", "- Most to operate", "+ Managed", "+ Least to operate"],
            ["Project Lab Notebook", "+ Argo CD makes it a by-product", "~ Split Terraform / Argo CD", "~ Terraform only"],
            ["SMaaS foundation (Phase 2)", "~ Build quotas", "+ Fair-share is the primitive", "- Nothing to build on"],
            ["EKS / Ray / Argo as named", "+ Exactly", "~ Partial", "- None of the three"],
            ["D7 — equivalent training", "+ Both tests runnable", "~ Gated on EFA spike", "- Multi-node blocked"],
            ["D8 — burstable infrastructure", "+ Structural, week 3", "+ Most literal reading", "~ Via Managed Instances"],
            ["Tri-environment parity", "+ Mac / AWS / on-prem", "- AWS only", "- AWS only"]]
    table(s, Inches(0.6), Inches(1.6), Inches(12.1), rows,
          col_w=[Inches(3.5), Inches(2.87), Inches(2.87), Inches(2.86)],
          size=10.5, row_h=Inches(0.37), verdict_cols=(1, 2, 3))

    # ---------------------------------------- 13. the deciding requirements --
    s = slide_base(prs, "Three requirements settle it", "what actually discriminates")
    items = [
        ("Multi-node linear scaling", BAD,
         "The headline deliverable. ECS has no gang-scheduling primitive and Managed Instances cannot supply EFA, a placement group or userdata.",
         "→ Rules out ECS"),
        ("Interactive iteration, no queues", BAD,
         "The kickoff's first and third priorities. Batch is submit-and-wait: minutes per iteration, and no GPU shell for debugging.",
         "→ Rules out Batch for Phase 1"),
        ("The stack named at kickoff", ACCENT,
         "EKS / Ray / Argo was stated by the research team. Only one option satisfies it as named; ECS satisfies none of the three.",
         "→ Confirms EKS + Ray"),
    ]
    y = Inches(1.7)
    for title_, colour, body, verdict in items:
        panel(s, Inches(0.6), y, Inches(12.1), Inches(1.5))
        bar = s.shapes.add_shape(1, Inches(0.6), y, Pt(5), Inches(1.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = colour
        bar.line.fill.background()
        bar.shadow.inherit = False
        textbox(s, Inches(1.0), y + Inches(0.2), Inches(7.6), Inches(0.35),
                title_, size=16, bold=True, color=PRIMARY)
        textbox(s, Inches(1.0), y + Inches(0.63), Inches(8.4), Inches(0.7),
                body, size=12, color=INK)
        textbox(s, Inches(9.7), y + Inches(0.55), Inches(2.8), Inches(0.5),
                verdict, size=13, bold=True, color=colour)
        y += Inches(1.72)

    # ------------------------------------------------ 14. recommendation ----
    s = slide_base(prs, "Recommendation", "decision")
    panel(s, Inches(0.6), Inches(1.6), Inches(12.1), Inches(1.35),
          fill=PRIMARY, line=PRIMARY)
    textbox(s, Inches(1.0), Inches(1.83), Inches(11.3), Inches(0.45),
            "Phase 1: build on EKS + Karpenter + Ray", size=22, bold=True, color=WHITE)
    textbox(s, Inches(1.0), Inches(2.35), Inches(11.3), Inches(0.4),
            "Revised 19 Oct: one framework across a three-shape pipeline, and the only option keeping a development loop. Margin over Batch is now narrow.",
            size=12.5, color=RGBColor(0xC9, 0xD6, 0xE4))
    textbox(s, Inches(0.6), Inches(3.2), Inches(12.1), Inches(0.35),
            "WHY", size=11, bold=True, color=ACCENT)
    textbox(s, Inches(0.6), Inches(3.6), Inches(12.1), Inches(1.9),
            ["•  The workload is three shapes, not one — 100–200 CPUs preprocessing, 4–8 GPUs training for days, then 150 CPUs rendering. Ray spans all three in one framework, and Karpenter provisions both node pools. The alternative is a second system to operate.",
             "•  It is the only option preserving a seconds-long development loop and live access into a running job — which is what Deepak asked for if development happens on AWS.",
             "•  D8 stops being a late-phase risk: the burst layer is the compute substrate, demonstrated in week 3 rather than built in Thanksgiving week.",
             "•  It is the stack the research team named, the only one preserving Mac / AWS / on-prem parity, and its access path — kubectl from a laptop — already works at GE."],
            size=11.5, space_after=8, line=1.1)
    textbox(s, Inches(0.6), Inches(5.6), Inches(12.1), Inches(0.35),
            "AND THE OTHER TWO", size=11, bold=True, color=MUTED)
    textbox(s, Inches(0.6), Inches(6.0), Inches(12.1), Inches(0.9),
            ["•  AWS Batch is now a CLOSE SECOND, not a clear no — it fits these job shapes well and its EFA pivot risk is gone.",
             "•  What would tip it: if development happens on-prem rather than on AWS, Batch becomes the better choice."],
            size=12, space_after=8)

    # ------------------------------ 15. what researchers actually do -------
    s = slide_base(prs, "What researchers actually do", "daily workflow")
    textbox(s, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.35),
            "The loop, under the recommended architecture. Nothing here requires them to learn Kubernetes.",
            size=12, color=MUTED)
    flow = [("laptop", ["gossamer →", "AWS session"], MUTED),
            ("dev pod", ["CPU, long-lived", "edit code here"], ACCENT),
            ("submit", ["mlaas submit", "train.py --gpus 8"], PRIMARY),
            ("GPU job", ["runs on one p5", "logs stream back"], GOOD),
            ("get inside", ["mlaas shell <run>", "live, while running"], GOOD)]
    bw, bh, gap = Inches(2.17), Inches(1.25), Inches(0.33)
    x, y = Inches(0.6), Inches(1.95)
    for i, (title_, lines, colour) in enumerate(flow):
        b = panel(s, x, y, bw, bh, fill=WHITE, line=colour)
        b.line.width = Pt(1.5)
        textbox(s, x + Inches(0.15), y + Inches(0.18), bw - Inches(0.3), Inches(0.3),
                title_, size=13, bold=True, color=colour, align=PP_ALIGN.CENTER)
        textbox(s, x + Inches(0.1), y + Inches(0.58), bw - Inches(0.2), Inches(0.55),
                lines, size=10, color=INK, align=PP_ALIGN.CENTER, space_after=2)
        if i < len(flow) - 1:
            from pptx.enum.shapes import MSO_SHAPE
            a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + bw + Inches(0.06),
                                   y + Inches(0.5), Inches(0.21), Inches(0.24))
            a.fill.solid(); a.fill.fore_color.rgb = RULE
            a.line.fill.background(); a.shadow.inherit = False
        x += bw + gap
    rows = [["Need", "What they type", "Note"],
            ["Edit code", "kubectl exec -it dev-<name> -- bash", "or VS Code Remote onto the dev pod"],
            ["Start a run", "mlaas submit train.py --gpus 8", "wrapper writes the Job; kubectl still works"],
            ["Watch it", "mlaas logs -f <run>", "kubectl logs underneath"],
            ["Get inside a running job", "mlaas shell <run>", "Deepak's \"optional live container access\""],
            ["Debug on a GPU", "mlaas shell --gpus 1 --ttl 2h", "time-boxed on purpose"]]
    table(s, Inches(0.6), Inches(3.5), Inches(12.1), rows,
          col_w=[Inches(2.9), Inches(4.6), Inches(4.6)], size=11, row_h=Inches(0.42))
    panel(s, Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.72),
          fill=RGBColor(0xEC, 0xF3, 0xF3), line=ACCENT)
    textbox(s, Inches(0.95), Inches(6.31), Inches(11.5), Inches(0.35),
            "Researchers should never write a Kubernetes manifest to start a run. The wrapper is about a day of work — and the biggest lever on whether this feels like a sandbox or a deployment pipeline.",
            size=12, color=PRIMARY)

    # ----------------------------------- 16. privileges: no root -----------
    s = slide_base(prs, "Access: no root, in three senses", "privilege model")
    rows = [["Scope", "Granted?", "Why"],
            ["Root on the node / host", "- Never", "Nodes are Karpenter-managed and immutable; node access is an operator function"],
            ["cluster-admin in Kubernetes", "- No", "Namespace-scoped: create and delete Jobs, exec into own pods, read logs"],
            ["Root inside their container", "- No, by design", "Non-root UID with a writable home and a virtualenv the researcher owns"]]
    table(s, Inches(0.6), Inches(1.6), Inches(12.1), rows,
          col_w=[Inches(3.3), Inches(2.1), Inches(6.7)], size=11.5,
          row_h=Inches(0.5), verdict_cols=(1,))
    textbox(s, Inches(0.6), Inches(3.5), Inches(12.1), Inches(0.35),
            "THE FRICTION — AND WHY IT MATTERS", size=11, bold=True, color=WARN)
    textbox(s, Inches(0.6), Inches(3.9), Inches(12.1), Inches(1.1),
            ["•  pip install works — into their own virtualenv, no root needed. That covers almost everything mid-project.",
             "•  apt-get does not. System packages are an image change — the discipline that makes stack parity reproducible.",
             "•  Friction is what sends people back to Alpharetta, so: a fast image rebuild, a generous base image, and a per-user overlay venv."],
            size=11.5, space_after=7)
    panel(s, Inches(0.6), Inches(5.2), Inches(12.1), Inches(1.6), fill=PANEL, line=BAD)
    bar = s.shapes.add_shape(1, Inches(0.6), Inches(5.2), Pt(5), Inches(1.6))
    bar.fill.solid(); bar.fill.fore_color.rgb = BAD
    bar.line.fill.background(); bar.shadow.inherit = False
    textbox(s, Inches(1.0), Inches(5.42), Inches(11.3), Inches(0.3),
            "Two exceptions to settle with GWD now, not in week six", size=13, bold=True, color=PRIMARY)
    textbox(s, Inches(1.0), Inches(5.82), Inches(11.3), Inches(0.9),
            ["•  GPU performance counters — NVIDIA restricts these to administrative users. Nsight profiling needs a driver setting or added capabilities, and a team chasing linear scaling will reach for it.",
             "•  CAP_SYS_PTRACE — for py-spy and gdb. Neither exception needs privileged containers, and neither should be cluster-wide."],
            size=11, space_after=6)

    # ------------------------------------------ 18. phasing: not rejected --
    s = slide_base(prs, "The other two are deferred, not rejected", "phasing")
    phases = [
        ("PHASE 1  ·  Oct – Nov 2026", "Research velocity", PRIMARY,
         ["EKS + Karpenter + Ray", "Four researchers, flat team, one shared pool.",
          "Judged on linear scaling and how fast researchers get moving."]),
        ("PHASE 2  ·  Dec 2026 – Feb 2027", "Shared service (SMaaS)", ACCENT,
         ["Revisit AWS Batch", "Many users across business units.",
          "Fair-share scheduling becomes the primitive that matters — and it is Batch's strongest card."]),
        ("ALONGSIDE  ·  either phase", "Specific workloads", MUTED,
         ["Amazon ECS", "Preprocessing and mesh generation; a Phase 2 inference tier.",
          "Fractional GPU on G6f suits small-model serving better than whole-GPU options."]),
    ]
    y = Inches(1.6)
    for header, theme, colour, lines in phases:
        panel(s, Inches(0.6), y, Inches(12.1), Inches(1.46))
        bar = s.shapes.add_shape(1, Inches(0.6), y, Pt(5), Inches(1.46))
        bar.fill.solid(); bar.fill.fore_color.rgb = colour
        bar.line.fill.background(); bar.shadow.inherit = False
        textbox(s, Inches(1.0), y + Inches(0.18), Inches(4.2), Inches(0.3),
                header, size=10, bold=True, color=colour)
        textbox(s, Inches(1.0), y + Inches(0.52), Inches(4.2), Inches(0.35),
                theme, size=15, bold=True, color=PRIMARY)
        textbox(s, Inches(5.5), y + Inches(0.2), Inches(7.0), Inches(0.3),
                lines[0], size=14, bold=True, color=colour)
        textbox(s, Inches(5.5), y + Inches(0.58), Inches(7.0), Inches(0.8),
                lines[1:], size=11, color=INK, space_after=3)
        y += Inches(1.62)
    textbox(s, Inches(0.6), Inches(6.55), Inches(12.1), Inches(0.4),
            "Each system is used where it is genuinely strongest, and the split matches the project's own phase boundary.",
            size=11.5, bold=True, color=PRIMARY)

    # ------------------------------- 19. what would change the answer ------
    s = slide_base(prs, "What would change this recommendation", "intellectual honesty")
    textbox(s, Inches(0.6), Inches(1.45), Inches(12.1), Inches(0.35),
            "Stated up front, so the decision can be revisited on evidence rather than argument.",
            size=12, color=MUTED)
    changes = [
        ("TRIGGERED 19 Oct — training fits on a single server",
         "This is no longer hypothetical. Deepak Akhare confirms 4–8 GPUs on one server, multi-server not currently required. Gang scheduling and EFA stop mattering, and all three options reopen — ECS included.",
         BAD),
        ("If a 5-minute wait is genuinely acceptable",
         "Batch's managed scheduling, fair-share and native pend-time metrics become close to free. The case against it rests almost entirely on iteration latency.",
         WARN),
        ("If Kubernetes is rejected organizationally",
         "If GWD or CTO/HQ will not accept an EKS cluster, the comparison becomes Batch versus ECS — and the answer depends on whether multi-node training is required.",
         WARN),
        ("If the team cannot carry the operations",
         "EKS has the largest operational surface of the three, against 1.0 + 0.5 + 0.5 FTE already holding a 24-hour unblock commitment. If that proves unrealistic, managed wins.",
         WARN),
    ]
    y = Inches(1.95)
    for head, body, colour in changes:
        panel(s, Inches(0.6), y, Inches(12.1), Inches(1.12))
        bar = s.shapes.add_shape(1, Inches(0.6), y, Pt(5), Inches(1.12))
        bar.fill.solid(); bar.fill.fore_color.rgb = colour
        bar.line.fill.background(); bar.shadow.inherit = False
        textbox(s, Inches(1.0), y + Inches(0.16), Inches(11.3), Inches(0.3),
                head, size=14, bold=True, color=PRIMARY)
        textbox(s, Inches(1.0), y + Inches(0.52), Inches(11.3), Inches(0.5),
                body.replace("**", ""), size=11, color=INK)
        y += Inches(1.28)

    # ------------------------------------------- 20. before we commit -------
    s = slide_base(prs, "What must be settled before we commit", "open questions")
    rows = [["Question", "Owner", "Why it blocks"],
            ["ANSWERED: no — single server, 4–8 GPUs", "Research team",
             "All three options reopen; see slide 3"],
            ["Start-up tolerance — stated TBD, leaning seconds", "Research team",
             "Matters for development, not for multi-day runs"],
            ["\"Argo\" — Workflows or CD?", "Architecture team",
             "Decides whether Flyte and Argo actually conflict"],
            ["ANSWERED: GNN/transformer on meshes. ParaView?", "Research team",
             "Only open point: does ParaView run in the sandbox?"],
            ["Python app tier: FastAPI/Flyte/Dask/MLflow, or EKS/Ray/Argo?", "Architecture team",
             "Sizes \"deploy and support their application\""],
            ["Multi-node: kickoff says yes, research says no", "Jim Tallman + research",
             "Decides what the Scaling Benchmark Report proves"],
            ["GPU funding, and on-demand vs 12-month prepay", "Michael Russo",
             "Prepay removes the stop/start cost lever"],
            ["Alpharetta environment inventory", "Architecture team",
             "D4, D6 and D7 are undefined without it"],
            ["Is SSM approved, or is Gossamer the path?", "GEV IT / InfoSec",
             "Shapes the access plane"],
            ["Does 'static servers' permit a cluster?", "Michael Russo",
             "SOW wording vs. what we would build"]]
    table(s, Inches(0.6), Inches(1.6), Inches(12.1), rows,
          col_w=[Inches(5.2), Inches(2.5), Inches(4.4)], size=11, row_h=Inches(0.44))
    textbox(s, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.4),
            "The first two carry the most weight: between them they can reopen or close the entire comparison.",
            size=11.5, bold=True, color=PRIMARY)

    # ------------------------------------------------- 16. next steps -------
    s = slide_base(prs, "Next steps", "if agreed")
    steps = [("1", "Confirm the architecture", "Weekly meeting with the research team"),
             ("2", "Close the two decisive questions", "Multi-node requirement, acceptable start latency"),
             ("3", "Place the capacity reservation", "Blocked on server count and funding"),
             ("4", "Enter the GWD Base process", "Submit the architecture for CTO/HQ review"),
             ("5", "Start the landing zone", "Terraform, single-AZ GPU subnet, placement group")]
    y = Inches(1.75)
    for num, title_, detail in steps:
        circ = s.shapes.add_shape(9, Inches(0.7), y, Inches(0.5), Inches(0.5))
        circ.fill.solid()
        circ.fill.fore_color.rgb = ACCENT
        circ.line.fill.background()
        circ.shadow.inherit = False
        textbox(s, Inches(0.7), y + Inches(0.1), Inches(0.5), Inches(0.3),
                num, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        textbox(s, Inches(1.45), y + Inches(0.02), Inches(5.0), Inches(0.35),
                title_, size=15, bold=True, color=PRIMARY)
        textbox(s, Inches(1.45), y + Inches(0.33), Inches(10.5), Inches(0.3),
                detail, size=12, color=MUTED)
        y += Inches(0.92)
    textbox(s, Inches(0.6), Inches(6.5), Inches(12.1), Inches(0.4),
            "Full analysis: Projects/Burstable MLaaS/Architecture/ — three architecture documents, two execution plans, and the researcher question list.",
            size=10.5, color=MUTED)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    return out_path, len(prs.slides.__iter__.__self__._sldIdLst)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    path, n = build(args.out)
    print(f"wrote {path} ({n} slides)")
