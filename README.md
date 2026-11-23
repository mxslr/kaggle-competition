# kaggle-competition

A Claude Code plugin for competing in Kaggle competitions to get the best score the rules allow, and to keep it through the organizers' verification.

## What it does

- **Triggers automatically** whenever a prompt mentions a Kaggle competition. Phrases include "kaggle competition", "kompetisi kaggle", "lomba kaggle", a Kaggle leaderboard, or a `kaggle.com/competitions/...` link. A `UserPromptSubmit` hook adds a short instruction to load the workflow skill and read the lessons file.
- **Rules first.** It builds a `comp_notes/RULES.md` ledger from the rules page and every FAQ answer. Every technique is checked against it, and unclear points become questions for the organizers.
- **Research before building.**
  - It finds the closest past competitions and their winning solutions.
  - It finds the newest strong models for the modality, with licence, runtime fit and rule status.
  - It reads current public notebooks and discussions.
- **Validation that tracks the leaderboard.**
  - Cross-validation is grouped and time-aware.
  - Training targets are kept separate from evaluation labels.
  - It estimates public-LB noise and selects by cross-validation, not LB.
- **One lever at a time.**
  - Error budgets come from out-of-fold data, and the next experiment is ranked by expected gain, cost and rule risk.
  - Every run is logged in `comp_notes/EXPERIMENTS.md`.
- **Ensembling and post-processing.** Simplex or hill-climbing blends, stacking, and metric-specific post-processing, all chosen on out-of-fold data.
- **Everything runs on Kaggle.** Claude writes the notebook and hands you the `.ipynb` to import. Training, feature extraction, EDA and inference never run on your machine.
- **Reproducible notebooks.**
  - The notebook is built from a percent-format source with numbered sections and short professional text.
  - Stage caches are keyed by config fingerprints, a time-budget guard protects the session limit, and a debug mode runs the whole notebook on a small subset in minutes.
- **Learns across competitions.** Lessons go to `~/.claude/kaggle-competition/LESSONS.md`, and the plugin ships general seed lessons. Competition-specific details stay in that private file and are never published.
- **Technique catalog.** It lists techniques that are banned in some competitions but often allowed in others, such as pseudo-labelling, adversarial validation, VLM features, cross-row features and test-time adaptation. Each comes with the question to ask the organizers.

## Components

| Type | Name | Purpose |
|---|---|---|
| Skill | `workflow` | The phased playbook: intake, rules, research, validation, iteration, final, post-mortem |
| Skill | `rules-gate` | Rules and FAQ ledger, technique decisions, audits, transparency section |
| Skill | `notebook` | Professional, reproducible notebook authoring and run instructions |
| Command | `/kaggle-start` | Start a competition from zero |
| Command | `/kaggle-next` | Diagnose the latest run and pick the next experiment |
| Command | `/kaggle-audit` | Compliance audit of a notebook or pipeline |
| Command | `/kaggle-final` | Final pick, reproducible run, hand-in checklist |
| Command | `/kaggle-lessons` | Record lessons for the next competition |
| Agent | `kaggle-researcher` | Research sweep: past winners, newest models, papers |
| Agent | `rules-auditor` | Independent compliance audit |
| Agent | `error-analyst` | Out-of-fold error budget and next lever |
| Hook | `UserPromptSubmit` | Auto-trigger on Kaggle competition prompts |
| Script | `skills/workflow/scripts/oof_tools.py` | LB noise, paired comparison, robust threshold, blending |
| Script | `skills/notebook/scripts/build_nb.py` | Percent-format source to `.ipynb` with checks |
| Template | `skills/notebook/assets/nb_template.py` | Runnable notebook skeleton |

## Install

The hook needs Node.js on PATH (Claude Code already requires it). Building notebooks locally needs Python with `nbformat`. `oof_tools.py` is meant to run inside a Kaggle notebook next to the OOF files.

From GitHub:

```
claude plugin marketplace add mxslr/kaggle-competition
claude plugin install kaggle-competition@kaggle-competition-marketplace
```

From a local clone:

```
claude plugin marketplace add <path-to-this-folder>
claude plugin install kaggle-competition@kaggle-competition-marketplace
```

Restart Claude Code after installing.

## Principles

- A disqualified 0.99 is worth zero. The rules ledger is a hard gate.
- Cross-validation decides; the public LB is a noisy check.
- Every chosen constant has a training-data basis that the notebook states.
- All compute runs on Kaggle; Claude delivers importable notebooks with run instructions.
- The user owns every outward action: downloads, submissions, pushes and posts happen only on their go-ahead.
