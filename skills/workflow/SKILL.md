---
name: workflow
description: "Complete playbook for competing in a Kaggle competition (or any leaderboard ML competition hosted on Kaggle) to get the best score the rules allow: rules and FAQ ledger as a hard gate, research of the newest strong models and past winning solutions, leak-free validation that tracks the leaderboard, a logged one-lever-at-a-time experiment loop, ensembling and robust thresholds, a reproducible notebook inside the runtime limit, and lessons carried to the next competition. Use it whenever the user mentions a Kaggle competition, kompetisi or lomba Kaggle, a Kaggle leaderboard or LB score, a competition FAQ, a code competition notebook, or asks to raise, boost or diagnose a competition score, even if they do not say the word workflow."
---

# Kaggle Competition Workflow

The goal is the highest **final (usually private) leaderboard** score that survives the organizers' verification. A disqualified 0.99 is worth zero, and a public-LB jump that does not generalise is worth less than a stable cross-validation gain. Everything below serves those two facts.

## Where the work runs

All heavy work runs on Kaggle, inside the competition notebook: data loading, EDA, preprocessing, feature extraction, training, validation, inference and ensembling. The user's own machine is not used for training or for processing competition data, and competition data or pretrained weights are not downloaded to it.

- Locally, only write the notebook source, build the `.ipynb` and run fast static checks (see the `kaggle-competition:notebook` skill).
- Deliver every version as an `.ipynb` file the user imports into Kaggle (send it with the file-sharing tool when one is available, otherwise give its path), together with the run instructions below.
- Results come back as outputs the user pastes, or by reading the finished Kaggle notebook's output page in the user's browser when they ask for it.
- Analyses that need data (EDA, error analysis, threshold or label checks) are written as notebook sections or as small CPU check cells that the user runs on Kaggle.

Reply in the user's language. When you give the user steps to run on Kaggle, always state: notebook name, inputs to attach, accelerator, internet on or off, whether to restart the session, expected runtime, the log lines to check, and exactly what to send back.

## Files this workflow keeps

Create `comp_notes/` in the project on first use, from the templates in `assets/`:

| File | Purpose |
|---|---|
| `COMPETITION.md` | task, data, metric, timeline, compute and runtime limits, submission limits, final-LB rule, hand-in requirements |
| `RULES.md` | the rules ledger: every rule and host FAQ answer with source and date, plus the decision for each technique (allowed, forbidden, unclear) |
| `RESEARCH.md` | research brief: closest past competitions, candidate methods, newest models, realistic ceiling |
| `EXPERIMENTS.md` | one row per run: id, date, change, CV, LB, runtime, decision, notes |

Cross-competition memory lives in `~/.claude/kaggle-competition/LESSONS.md` (create it when the first lesson is recorded). Seed lessons are in `references/lessons-learned.md`. Read both at the start of every competition, because most expensive mistakes repeat.

## Phase 0: Intake

1. Read every competition page: overview, data, evaluation, rules, timeline, code requirements, and the pinned discussion threads. If pages need sign-in, use the user's browser session or ask for pasted text. Never handle the user's Kaggle credentials yourself.
2. Fill `COMPETITION.md`. Pin down the details that silently decide the outcome:
   - exact metric definition and how ties, thresholds or rounding are handled;
   - public/private split size, so you know how noisy the public LB is (see `references/validation-and-selection.md`);
   - whether the final ranking uses the private LB only, and whether notebooks are re-run and verified;
   - runtime limit, internet on or off, GPU type, submission limits per day and their reset time;
   - what the unit of prediction is (row, image, clip, sequence) and whether each must be predicted independently.
3. Write down the deadline and a GPU-hour budget per remaining week. Kaggle quotas change, so check the current values on the user's account page rather than assuming.

## Phase 1: Rules ledger (hard gate)

Load the `kaggle-competition:rules-gate` skill and build `RULES.md` before any modelling. Re-run this step every time the user pastes a new FAQ batch. Every later idea is checked against the ledger first. When a rule is unclear, write the exact question to send to the organizers and treat the technique as forbidden until answered.

Typical traps: test-data analysis bans, "each row predicted independently", "all frames or rows must be used", VLM or LLM bans, pseudo-labelling bans, external-data rules, values that must be chosen from training data only, transparency requirements for labelling.

## Phase 2: Research before building

1. Read `~/.claude/kaggle-competition/LESSONS.md` and `references/lessons-learned.md`; list the lessons that apply.
2. Research with `references/research-playbook.md`: closest past competitions and their winning solutions, the newest strong models (`references/model-zoo.md`), current public notebooks and discussion threads, and papers on the exact sub-problem. Use the `kaggle-researcher` agent when the user allows subagents.
3. For the modality, read the matching section of `references/modality-playbooks.md`.
4. Write `RESEARCH.md`: candidate methods ranked by expected gain, cost and rule status, plus the realistic ceiling. Prefer methods that winners of similar competitions used and that fit the runtime limit.

## Phase 3: Validation and baseline

1. Design cross-validation that mirrors how the test set differs from train (by group, subject, time, source, site). Follow `references/validation-and-selection.md`. A validation that does not track the LB is the most common reason teams plateau.
2. Implement the metric exactly as the host defines it, and check it on a toy case.
3. Build the simplest strong baseline first (for example GBDT for tabular, one fine-tuned pretrained backbone for images or video, one DeBERTa-class or small LLM for text). Log it as run 0.
4. Engineer for the runtime limit from day one: config fingerprints for cached stages, a time-budget guard, a debug mode that runs the whole notebook on a small subset in minutes on Kaggle, and a notebook built from a source file. See `references/runtime-engineering.md` and the `kaggle-competition:notebook` skill.
5. Make one early LB submission to calibrate CV against LB. From then on, CV decides.

## Phase 4: Iteration loop

Repeat until the deadline or until the expected gains fall inside the noise:

1. **Diagnose** the last run on out-of-fold data only, from the tables the notebook prints or from a CPU check cell the user runs on Kaggle (`error-analyst` agent when the files are at hand): error budget by bucket, per-model contribution, threshold stability, learning curves. Find the bucket with the largest "score if fixed".
2. **Pick one lever** that targets that bucket. Rank candidates by expected gain, GPU hours and rule risk. Check it against `RULES.md` and `references/technique-catalog.md`.
3. **Run it cheaply first** on Kaggle: reuse caches, retrain only the affected heads, use fewer folds or epochs for a directional check, then commit to the full run. Hand over each version as an `.ipynb` with run instructions.
4. **Decide with CV**, using the noise rules in `references/validation-and-selection.md`. Keep a change only if CV improves beyond noise; record the LB but do not select on it, especially when the FAQ forbids using test information.
5. **Log** the row in `EXPERIMENTS.md` with the decision and the reason.
6. Every few iterations, re-run the research step for the current bottleneck; new public notebooks and papers appear during a competition.

Levers that usually pay most, roughly in order: better validation and labels, stronger or newer pretrained backbones, input representation (resolution, crops, context length, frames), augmentation matched to the test shift, loss and target design for the metric, ensembling diverse models, threshold and post-processing. See `references/ensembling-postprocessing.md`.

## Phase 5: Final submission

1. Choose the final pick(s) by CV and robustness (`references/validation-and-selection.md`, final-selection section). With two picks, take the best validated run and a different, robust one.
2. Make sure the exact notebook reproduces the submission from scratch inside the runtime limit with margin, with only allowed inputs.
3. Run the `rules-gate` audit and the `rules-auditor` agent on the final notebook.
4. Polish the notebook text with the `kaggle-competition:notebook` skill: every labelling rule, threshold and selection basis stated honestly, no test analysis, no claim the code does not support.
5. Prepare the hand-in checklist. Ask the user before any submission, publication or form.

## Phase 6: Post-mortem

After the private LB is out (or after the final hand-in), append reusable lessons to `~/.claude/kaggle-competition/LESSONS.md`: what worked, what failed, rule surprises, CV versus public versus private, and what the winners did differently. Keep personal data and private competition data out of it.

## Non-negotiables

- **Compute stays on Kaggle.** Never train, extract features or run the competition pipeline on the user's machine. Hand over notebooks to import instead.
- **Rules beat score.** Never use a technique the ledger marks forbidden or unclear. Never build on a leak the rules ban, such as reconstructing shuffled test sequences when each row must be predicted independently.
- **No test peeking when banned.** Do not print, plot or summarise test inputs or predictions; do not pick constants, thresholds or label conventions from LB probes when the FAQ says values must come from training data.
- **Honest ceilings.** Compute what the current validation says is reachable and say it plainly. Leaderboards often have leak-driven tops that disappear at verification.
- **Evidence before claims.** Only report a result after seeing the output. Separate measured numbers from estimates.
- **The user owns outward actions.** Ask before downloading competition data, submitting, pushing notebooks or datasets, or posting in discussions. Never read or print API keys or tokens.

## Reference map

| Need | Read |
|---|---|
| Rule types, ledger, compliance gate | `kaggle-competition:rules-gate` skill |
| Techniques that are banned in some competitions and allowed in others | `references/technique-catalog.md` |
| How to research methods and past winners | `references/research-playbook.md` |
| Newest model families per modality | `references/model-zoo.md` |
| Per-modality recipes | `references/modality-playbooks.md` |
| CV design, LB noise, thresholds, final selection | `references/validation-and-selection.md` |
| Blending, stacking, TTA, post-processing | `references/ensembling-postprocessing.md` |
| Runtime limits, caching, time guards, smoke tests | `references/runtime-engineering.md` |
| Lessons from past competitions | `references/lessons-learned.md` and `~/.claude/kaggle-competition/LESSONS.md` |
| Writing the notebook | `kaggle-competition:notebook` skill |
| OOF blending, robust threshold, LB noise tools | `scripts/oof_tools.py` (copy into a Kaggle CPU cell or upload it as a utility script; run with `--help`) |
