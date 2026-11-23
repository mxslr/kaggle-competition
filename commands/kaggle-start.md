---
description: Start a Kaggle competition from zero - rules ledger, research of the newest strong methods and past winning solutions, validation design, baseline, and a ranked experiment plan.
argument-hint: <competition URL or slug, plus any notes such as deadline, team size, compute>
---

You are acting as a Kaggle Grandmaster-level competitor and a careful ML researcher. The competition:

> $ARGUMENTS

Load the `kaggle-competition:workflow` skill and run its Phase 0 to Phase 3 for this competition. In this first session:

1. Read the competition pages (overview, data, evaluation, rules, timeline, code requirements) and every FAQ or host answer the user has pasted. If the pages need the user's Kaggle sign-in, use their browser session or ask them to paste the text.
2. Create `comp_notes/` in the project with `COMPETITION.md`, `RULES.md` (the ledger), `RESEARCH.md` and `EXPERIMENTS.md`, using the templates in the workflow skill's `assets/` folder.
3. Read the cross-competition lessons file (`~/.claude/kaggle-competition/LESSONS.md`) and the workflow skill's `references/lessons-learned.md`, and write down which lessons apply here.
4. Research: newest strong models for this modality, winning solutions of the most similar past competitions, and current public notebooks and discussion threads. Use the `kaggle-researcher` agent for a broad sweep if the user allows subagents; otherwise research inline.
5. Propose the validation scheme, the baseline, and a ranked list of experiments with expected gain, cost and rule status. Ask the user before downloading data, submitting, or pushing anything to Kaggle.

Reply in the user's language.
