---
description: Diagnose the latest Kaggle run (CV, OOF, logs, LB) and pick the next experiment by expected gain versus cost, without breaking the rules.
argument-hint: <paste the run's metrics, logs or LB score, or point to the files>
---

Latest results from the user:

> $ARGUMENTS

Load the `kaggle-competition:workflow` skill and run its Phase 4 iteration loop:

1. Log the run in `comp_notes/EXPERIMENTS.md` (id, change, CV, LB, runtime, decision).
2. Compare CV against LB using the noise estimate from `references/validation-and-selection.md`. Do not chase public-LB differences smaller than the noise band, and never select settings from LB scores when the rules or FAQ forbid using test information.
3. Do the error analysis on out-of-fold predictions only, from the tables the user pasted or by writing a CPU check cell for them to run on Kaggle: error buckets, per-class and per-group scores, calibration, and which component of the ensemble drags. Never analyse test data when the rules forbid it.
4. Re-read `comp_notes/RULES.md` and the newest FAQ, then rank the next levers by expected gain, GPU hours and rule risk. Recommend one main experiment, plus one cheap side experiment when it can run in parallel.
5. State the honest ceiling: how far the current validation says the score can still move.
6. Deliver the next experiment as an updated `.ipynb` with full Kaggle run instructions. Nothing runs on the user's machine.

Reply in the user's language.
