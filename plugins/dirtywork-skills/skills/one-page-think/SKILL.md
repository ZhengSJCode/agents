---
name: one-page-think
description: "Distill messy thoughts into one structured page using Toyota's one-page method. Use when the user wants to untangle chaotic thinking, structure a proposal or report, or turn scattered notes into one glanceable page."
disable-model-invocation: false
---

# One-Page Think — Toyota One-Page Minimal Thinking Method

Distill chaotic information into a single structured page. Blue pen organizes **information**, red pen organizes **thinking**.

Every output must satisfy:
1. **Glanceable** (一览性) — whole picture visible at once, decidable in 3 seconds
2. **Framed** — grid/table structure that pulls the mind to fill it
3. **Titled** — every frame has a heading/theme

## Step 1: Grill — collect real information and pick framework

Before any framework, **grill** the user to extract their actual situation. Never fill in answers from your own knowledge.

Interview relentlessly, one question at a time, providing your recommended answer for each. Wait for feedback before continuing. If a question can be answered by exploring the codebase, explore instead.

During the grill, also establish:
- **Who** is the reader? (yourself, boss, team, client)
- **What reaction** do you want from the reader?
- **Branch**: brainstorm-shaped (goals, options, to-do lists) → **Excel 1** / structured reasoning (root cause, plan, explanation) → **Logic 3**

Do not proceed until the user confirms enough information has been collected.

Completion criterion: shared understanding reached, reader identified, framework chosen.

## Step 2a: Excel 1 — Brainstorm and Prioritize

"Show everything first — that is the foundation of organizing."

1. Write **date + subject** in top-left cell
2. **Brainstorm with time limit**: fill keywords from the grill into cells. No sentences. Time limits: 8 cells → 1 min, 16 cells → 2 min, 32 cells → 5 min max
3. **Prioritize with three marks**:
   - ○ particularly important
   - △ must handle today / urgent
   - □ cannot be delayed
4. Items with multiple marks = **focus set**. Turn into concrete **actions** specific enough to execute.

Completion criterion: all items visible, three marks applied, focus set named with actionable next steps.

## Step 2b: Logic 3 — Three Questions, One Summary

Think from the reader's perspective: what questions would they ask?

1. **1P** (1 Phrase) — one sentence core takeaway. Draft from grill, confirm with user.
2. **Q1 (What), Q2 (Why), Q3 (How)** — three questions the reader would most likely ask. Each a genuinely distinct angle.
3. **Up to 3 answers** per question from the grill. Flag gaps.
4. Review: does 1P still hold? When answers compete, look for their common thread.

For proposals/reports, also consider the 5 common themes: background/purpose, current status, issues, countermeasures, schedule.

Completion criterion: 1P stated, three questions each with 1-3 answers, gaps flagged, 1P re-validated.

## Step 3: Save the one-page output

Render using the grid format from [TEMPLATE.md](TEMPLATE.md), then save as markdown. Default: `~/one-page-think/YYYY-MM-DD-subject.md`. Create directory if needed.

Grid size adapts to complexity: **4x4** (simple) / **6x6** (moderate) / **8x8** (complex).

Quadrant layout (fixed):
- **Top-left**: Subject + 1P + description
- **Top-right**: Q3 (How) + answers
- **Bottom-left**: Q1 (What) + answers
- **Bottom-right**: Q2 (Why) + answers

Completion criterion: file saved in grid format matching TEMPLATE.md, path reported to user.

## Writing Style — Caveman Full

All output (grill questions, grid cells, saved file) use caveman full compression:

Drop: articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging. Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for"). No decorative tables/emoji. Standard well-known tech acronyms OK (DB/API/HTTP); never invent new abbreviations. Technical terms exact. Code blocks unchanged. Errors quoted exact.

Preserve user's dominant language. Compress style, not language.

Pattern: `[thing] [action] [reason]. [next step].`

Not: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
Yes: "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

Auto-Clarity exception: drop caveman for security warnings, irreversible action confirmations, or when compression creates ambiguity. Resume after.
