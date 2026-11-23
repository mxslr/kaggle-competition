# Modality playbooks

Each playbook covers four things: a strong first baseline, the levers ranked roughly by how often they pay off in winning solutions, typical pitfalls, and the usual post-processing. Pick model families from `model-zoo.md`.

## Contents
1. Tabular
2. Images (classification, regression)
3. Detection and segmentation
4. Video and human behaviour
5. Text and LLM competitions
6. Time series and forecasting
7. Audio
8. Multimodal

## 1. Tabular

- **Baseline:** LightGBM with default-ish parameters on raw features, grouped or time CV, early stopping per fold.
- **Levers:**
  1. Features: aggregates by entity, ratios, counts, target encoding inside folds, lags and rolling windows for temporal data.
  2. Matching CV to the split.
  3. GBDT diversity (LightGBM, XGBoost, CatBoost).
  4. A neural tabular model or TabPFN for ensemble diversity.
  5. Optuna tuning late, not early.
  6. Seed averaging.
- **Pitfalls:** target leakage in features, encoders fit on all rows, duplicated rows across folds, using IDs that do not transfer.
- **Post-processing:** clipping, rounding for ordinal metrics, thresholds for F1.

## 2. Images (classification, regression)

- **Baseline:** a `timm` pretrained ConvNeXt or EfficientNet at a moderate resolution, AdamW with cosine schedule, light augmentation, 5-fold stratified (grouped if images share a source).
- **Levers:**
  1. Resolution.
  2. A stronger or newer backbone.
  3. Augmentation matched to the test conditions.
  4. Longer training with EMA.
  5. Loss for the metric (focal or class weights for imbalance, ordinal losses for grades).
  6. TTA.
  7. Ensembles across backbones and resolutions.
- **Pitfalls:** near-duplicate images across folds, leakage through patient or site, resizing that destroys small signals (crop the region of interest instead).

## 3. Detection and segmentation

- **Baseline:** a YOLO or DETR-family detector, or a U-Net with a `timm` encoder for segmentation. Use the competition's exact metric for validation (mAP at the right IoU, Dice, F-beta).
- **Levers:** input size, multi-scale training, mosaic or copy-paste augmentation, longer schedules, model ensembles fused with weighted boxes fusion (detection) or probability averaging (segmentation), tiling for large images.
- **Pitfalls:** metric mismatch (mAP@0.5 versus mAP@0.5:0.95), label format errors, and the AGPL licence of some detectors when prizes need open licences.
- **Post-processing:** confidence thresholds, NMS or WBF parameters, minimum-area filters, morphology.

## 4. Video and human behaviour

- **Baseline:** fine-tune a pretrained video transformer on person- or region-centred crops. A light probe on a strong frozen video encoder is a cheap second model.
- **Levers:**
  1. Correct labels in time. Clip-level labels inside long videos need temporal annotation or multiple-instance learning (MIL), and the host's labelling convention decides the evaluation labels.
  2. Crops around the person or the hands.
  3. Clip sampling that covers all required frames at test (multi-clip, averaged inside the sample).
  4. Careful handling of ambiguous label boundaries.
  5. A second pretraining source for ensemble diversity.
  6. Pose, gaze or hand streams, measured by their blend weight.
- **Pitfalls:**
  - Subject leakage, so use group k-fold by subject.
  - Frame-rate differences between train and test.
  - Train/test resolution mismatch; downscale train the same way when the rules allow it.
  - Rules about using every frame.
  - Banned VLM video models.
- **Post-processing:** a fold-averaged threshold for F1, and averaging across clips inside the same sample only.

## 5. Text and LLM competitions

- **Baseline:** DeBERTa-v3-base or a recent encoder with mean pooling, a max length chosen from the token-length distribution, grouped CV if texts share authors or prompts.
- **Levers:**
  1. A larger backbone (large-size encoders or LoRA-tuned LLMs where allowed).
  2. Max length and head design.
  3. Layer-wise LR decay.
  4. Adversarial training (AWP, FGM).
  5. Pseudo-labelling or extra data where allowed.
  6. Distilling an LLM ensemble into a smaller model to fit the runtime.
  7. Ensembles across backbones.
- **LLM-specific:** prompt format consistency, quantised inference (4- or 8-bit) to fit T4s, vLLM batching, answer-extraction robustness, self-consistency when the metric rewards it.
- **Pitfalls:** prompt or topic leakage across folds, the tokenizer truncating the important part, runtime blow-ups at inference.

## 6. Time series and forecasting

- **Baseline:** LightGBM on lag, rolling and calendar features, with a time-based validation that leaves the same gap as the test horizon.
- **Levers:** target transforms (log, differencing), global versus local models, neural forecasters and foundation models for diversity, hierarchical reconciliation, external calendars (holidays) if allowed.
- **Pitfalls:** using future information in features, random CV on time series, misaligned horizons.
- **Post-processing:** clip to valid ranges, bias correction measured on validation.

## 7. Audio

- **Baseline:** log-mel spectrogram plus a pretrained CNN, with sound-event-detection heads for weak labels.
- **Levers:** mel parameters, mixup, background noise and gain augmentation, longer context windows, pseudo-labels on unlabelled audio when allowed, ensembles across mel settings and backbones.
- **Pitfalls:** recording-site leakage, and class priors that differ between train and test.

## 8. Multimodal

- **Baseline:** a strong single-modality model per modality, then late fusion (averaging or a small stacker on OOF predictions).
- **Levers:** cross-modal attention fusion only after late fusion is strong; per-modality dropout so the model survives a missing modality.
- **Pitfalls:** a stronger modality drowning a weaker one in joint training. Check each branch alone and use auxiliary losses.
