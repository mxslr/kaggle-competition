# Lessons learned

Seed lessons that transfer across competitions. Competition-specific lessons, with their numbers and details, go to the private file `~/.claude/kaggle-competition/LESSONS.md` on the user's machine, not here. That file survives plugin updates and is never published with the plugin.

## Contents
1. Rules, labels and the leaderboard
2. Validation and selection
3. Modelling
4. Engineering and runtime
5. Planning

## 1. Rules, labels and the leaderboard

**Leaderboard tops can be leaks.** When a band of teams sits near a perfect score while the rest cluster far lower, suspect a leak, for example reconstructing shuffled test chunks into their original sequences.
- Estimate the honest ceiling from your own validation.
- Read every host answer about row independence.
- Expect verification to remove leak-based scores.

**The host's labelling convention can differ from what is visible.** Training labels may be coarse (per video, per document, per session), while the test unit has its own labelling rule (for example "dominant behaviour", or "preparation steps count"). Then the test labels can sit where the model cannot see them.
- Separate **training targets** (what is visible, low noise) from **evaluation labels** (your training-data-based estimate of the host's convention).
- Select thresholds and blend weights on the evaluation labels.
- Training directly on widened labels tends to raise false alarms.

**Derive every convention value from training data.** Hosts can rule that time values, label schemes and thresholds must come from training data only.
- Choose these values from training annotations and FAQ semantics.
- Document the basis in the notebook.
- Record LB scores without selecting on them.
- Probing the LB for test statistics, such as an all-ones submission to read prevalence, is risky even when it seems harmless.

**Input rules apply to feature extraction too.** "Every frame or row must be used" can also forbid subsampling plus interpolation inside pose, gaze or embedding extractors.
- The usual compliant pattern: multi-clip or interleaved splits that feed every input to the model, merged only inside the same test row.
- Re-check every stage that touches test inputs.

**No test analysis means no test statistics anywhere.** This includes resolution or colour checks, detection rates, predicted-label counts and score histograms on test. Keep the test path inference-only and keep its outputs silent.

**AI-assisted annotation of training data can be allowed, but only after the host confirms it.** Once confirmed:
- annotate from frame or sample sheets under one written rule;
- cross-check independent views or annotators;
- re-check a sample at finer resolution;
- document the process in the notebook.

## 2. Validation and selection

- **Trust CV that mirrors the test split.** Group by the entity that differs between train and test: subject, patient, site, user, time. Shuffle-split CV on grouped data inflates scores and picks the wrong models.
- **Once the labels match the host's convention, OOF tracks the LB.** When it does not, check the label convention before anything else.
- **Public LB is a small, noisy sample.**
  - Compute what one error is worth and the noise band before reading any LB delta.
  - Shake-ups punish teams that tuned on public.
  - Pick final submissions by CV, plus one diverse robust pick when allowed.
- **Fold-averaged, smoothed thresholds** are more stable on unseen groups than the pooled argmax.
- **Ambiguous boundaries.** When labels are uncertain near event boundaries, try ignoring those samples in the loss (weight 0) before trying soft or widened labels. Verify the change on OOF under the evaluation labels.

## 3. Modelling

- **Read the winning write-ups of the 3 closest past competitions before writing code.** Most winning ideas are re-used ideas.
- **Newer and larger pretrained backbones are often the biggest single gain**, as long as they fit the runtime limit and the rules allow them. A second pretraining source (a different dataset or objective) often adds more than a second seed.
- **Diversity beats more seeds of the same model.** Ensembles gain most from different architectures, input views or targets.
- **Check blend weights early.** Auxiliary streams (pose, gaze, handcrafted features) often end up with zero weight. Drop zero-weight members before the final run to save runtime and dependencies.
- **Post-processing tuned to the metric is cheap and often worth a lot**: thresholds for F1, rank averaging for AUC, clipping for log loss, rounding for QWK.
- **Leakage hides in preprocessing**: scalers, target encoding, feature selection or augmentation statistics fit on all data. Fit them inside each fold.

## 4. Engineering and runtime

- **Stage caches keyed by config fingerprints** stop interactive sessions from reusing stale artifacts. Excluding new config fields from the key while they sit at neutral defaults keeps old caches valid.
- **A time-budget guard** that skips folds which would overrun keeps the hand-in run inside the session limit.
- **A local smoke test with tiny fake models** on CPU catches most bugs before any GPU hour is spent.
- **Build the notebook from a percent-format source file**, and never hand-edit the `.ipynb`.
- **Code competitions with internet off** need wheels and weights uploaded as Kaggle datasets in advance. Test the offline install path early.

## 5. Planning

- **Plan GPU hours backwards from the deadline.** Leave the last 2 to 3 days for the reproducible final run and the hand-in. Never start the only full run on the last day.
- **Write the experiment log as you go.** Without it, teams re-run ideas they already rejected and forget why the current config was chosen.
- **Run cheap directional experiments first**, for example retraining only the affected heads on cached features. Spend long runs only on levers that already showed a gain.
