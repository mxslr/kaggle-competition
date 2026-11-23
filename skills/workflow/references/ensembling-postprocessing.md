# Ensembling and post-processing

## Contents
1. Blending
2. Stacking
3. Diversity
4. Test-time augmentation
5. Post-processing by metric

## 1. Blending

- **Weighted average on OOF.** Search weights on a simplex grid (step 0.1, fine for up to about 6 models) or with hill climbing with replacement (Caruana). Use `scripts/oof_tools.py blend`.
- **Rank averaging** for AUC-type metrics, or when models have different calibration.
- **Geometric mean** of probabilities for log loss and calibrated models.
- **Optimise the blend for a smooth metric** (AUC, log loss) and then set the threshold for F1-type metrics. Optimising F1 directly over weights overfits.
- **Drop zero-weight members** before the final run. They cost runtime and add dependencies without changing the predictions.

## 2. Stacking

- A level-2 model (logistic regression, ridge, small GBDT) trained on OOF predictions, plus optional meta-features.
- Use the **same folds** as level 1. Train level 2 out of fold too, or its CV is inflated.
- Stacking pays when models disagree in structured ways (for example per-class strengths). With 2 or 3 similar models, a weighted average is as good and safer.

## 3. Diversity

Rank of usefulness for an ensemble member:
1. a different architecture family or pretraining source (CNN versus transformer, different pretraining datasets);
2. a different input view (resolution, crop, modality, feature set);
3. a different target or loss (soft versus hard labels, ordinal versus classification);
4. different seeds of the same model (smallest gain, still useful at the end).

Check pairwise correlation of OOF predictions. Members above about 0.98 correlation add little.

## 4. Test-time augmentation

- Flips, multi-crop, multi-scale for images; multi-clip covering all frames for video; multiple windows or truncation offsets for text.
- Average TTA results only inside the same test row, and keep it compliant with "all inputs must be used" rules.
- Validate TTA on OOF. Some augmentations hurt (for example a horizontal flip when left and right matter).

## 5. Post-processing by metric

| Metric | Post-processing |
|---|---|
| Binary F1, macro F1 | Fold-averaged, smoothed threshold on OOF. Per-class offsets for multi-class. |
| AUC | None needed; rank averaging for blends. |
| Log loss | Clipping (for example to [0.01, 0.99] only if OOF says it helps), temperature scaling. |
| QWK and ordinal metrics | Optimised rounding thresholds on OOF (OptimizedRounder). |
| MAP@k, NDCG | Re-ranking, adding popular fallbacks, dedup. |
| Detection mAP | WBF or NMS parameters, score thresholds per class. |
| Segmentation Dice or IoU | Probability threshold, minimum area, hole filling, TTA averaging. |
| RMSE, MAE | Clipping to valid ranges, bias correction from OOF, blending in log space when targets are skewed. |

Every post-processing parameter is chosen on OOF data, never on the public LB.
