---
description: Prepare the final Kaggle submission - final pick by validation, reproducible from-scratch run inside the time limit, clean professional notebook, and the hand-in checklist.
argument-hint: <candidate runs or notebook versions, deadline, hand-in requirements>
---

Final-stage context:

> $ARGUMENTS

Load the `kaggle-competition:workflow` skill (Phase 5) and the `kaggle-competition:notebook` skill. Then:

1. Pick the final submission(s) from `comp_notes/EXPERIMENTS.md` by cross-validation, following the selection rules in `references/validation-and-selection.md`. When two picks are allowed, take the best validated run plus a robust, different one.
2. Confirm the final notebook reproduces the submission from scratch: every cached artifact can be rebuilt, the from-scratch runtime fits the limit with a safety margin, seeds are fixed, and inputs come only from allowed sources.
3. Run the `kaggle-competition:rules-gate` audit one last time on the exact notebook that will be handed in.
4. Polish the notebook text with the notebook skill: numbered sections, short professional explanations, every labelling rule and selection basis stated, no test analysis, and no claims the code does not support.
5. Produce the hand-in checklist: notebook version, models and weights, data and licence list, write-up, and any forms the organizers require. Ask the user before submitting or publishing anything.

Reply in the user's language.
