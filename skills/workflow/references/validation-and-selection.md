# Validation, leaderboard noise and final selection

## Contents
1. CV design that mirrors the test split
2. OOF discipline
3. Training labels versus evaluation labels
4. How noisy is the public LB?
5. Comparing two runs
6. Thresholds and calibration
7. Tracking CV against LB
8. Final selection

## 1. CV design that mirrors the test split

Ask: what differs between train and test? Split along exactly that.

| Data situation | Split |
|---|---|
| Rows share a person, patient, user, site, device, session | `GroupKFold` or `StratifiedGroupKFold` by that entity |
| Temporal data, forecasting | Time split, with a gap equal to the test horizon; walk-forward folds |
| Near-duplicates (images, texts) | Cluster duplicates first, then group by cluster |
| Small data | Repeated grouped K-fold to reduce variance |
| Imbalanced classes | Stratify inside the grouping |

Use 5 folds as the default. Fix the fold assignment once (seeded), store it, and reuse it for every model so out-of-fold (OOF) predictions are comparable and stackable.

## 2. OOF discipline

- Every model writes an OOF file (`id, fold, y, pred`) and a test file (`id, pred`) with the same ids and order. Blending and stacking only ever read these files.
- Fit every preprocessing step (scalers, encoders, feature selection, target encoding, normalisation statistics) inside the training part of each fold.
- When labels are derived (annotations, conventions), store the derivation config with the OOF files, so later reports know which labels they used.

## 3. Training labels versus evaluation labels

When the host's labelling convention is not directly observable (for example, coarse training labels with a finer test unit, or a host rule about which part of a sample counts), keep two label sets:
- **Training targets:** what the model can see. Low noise, for example annotated segments of the visible event.
- **Evaluation labels:** your best training-data-derived estimate of the host's convention, built from FAQ semantics and training annotations. Use these for metrics, blend weights and thresholds.

Derive the evaluation convention from training data and the host's text, not from LB probes. When the FAQ allows a choice between schemes "based on training validation", document the choice and its basis in the notebook.

## 4. How noisy is the public LB?

Run `oof_tools.py` where the OOF files live, normally a Kaggle CPU notebook with the run's output attached (upload the script as a utility script or dataset).

There are two different noise questions.

**How far can the public LB sit from the true score?** This is unpaired noise.
- With `n` public rows, the standard error of an accuracy-like metric is about `sqrt(p * (1 - p) / n)`. With n = 500 and p = 0.85, that is 0.016.
- For any metric, run `python scripts/oof_tools.py noise --oof <oof.csv> --n <public rows> --threshold <t>`. It resamples the OOF predictions at the public size and reports the spread. This also bounds how much public and private can differ.

**Is submission B really better than A on the public LB?** This is paired noise, and it is smaller.
- One changed prediction moves macro F1 by roughly `1 / n` to `2 / n`. With n = 500, that is about 0.002 to 0.004.
- Run `python scripts/oof_tools.py compare --a A.csv --b B.csv --n <public rows>` on the two runs' OOF files to see how often B beats A on a sample of that size.

Rule of thumb: ignore public-LB gaps that `compare --n` shows as unstable, and never expect the public LB to sit closer to the true score than the `noise` band. The private LB is usually larger and less noisy, and it decides the ranking.

## 5. Comparing two runs

- Compare on the same folds and the same evaluation labels.
- Use a paired bootstrap over rows (or over groups) of the metric difference: `python scripts/oof_tools.py compare --a run_a.csv --b run_b.csv`. Keep a change when the difference is positive in most resamples and larger than the fold-to-fold noise.
- Look at the per-fold deltas. A change that wins in 4 of 5 folds is more trustworthy than one big win in a single fold.

## 6. Thresholds and calibration

- Choose thresholds on OOF data only.
- Use a **fold-averaged, smoothed** threshold: compute the metric-versus-threshold curve per fold, average the curves, smooth over ±0.03, and take the argmax (`scripts/oof_tools.py blend` does this). It is more stable on unseen groups than the pooled argmax.
- For multi-class macro F1, tune per-class offsets or weights on OOF, with the same averaging.
- For log loss, use temperature or Platt scaling fitted on OOF.
- If train and test priors differ and the rules forbid looking at test, do not adjust for test priors. Rely on the evaluation-label convention instead.

## 7. Tracking CV against LB

Keep a table in `EXPERIMENTS.md` with CV and public LB for every submitted run.
- After 3 or more submissions, check the correlation.
- If CV and LB move together within the noise band, trust CV fully.
- If they disagree beyond noise, suspect, in this order:
  1. a validation split that does not mirror the test split;
  2. a label convention mismatch;
  3. preprocessing differences between the train and test paths;
  4. a test-time bug;
  5. a leak that other teams use.

## 8. Final selection

- Choose by CV, not by public LB, unless the two agree.
- With two picks: the best CV run, plus a robust and different run (for example a different model family, or a more conservative threshold). Do not pick two near-identical runs.
- Prefer the simpler of two runs with equal CV, because it reproduces more reliably.
- The final notebook must reproduce the pick from scratch inside the runtime limit, with only allowed inputs.
- Expect shake-up when the public share is small, the data are grouped, or many teams overfit public. A stable CV-chosen pick usually climbs.
