# Model zoo: strong and recent families per modality

This list is a **starting point**, written in 2026. New checkpoints appear every month, so always confirm the newest version, licence and size on the Hugging Face Hub or the official repository before choosing. Check each family against the competition's rules (some ban VLM, LLM or CLIP-style models, zero-shot use, or external weights).

## Contents
1. Tabular
2. Image classification and regression
3. Detection, segmentation, keypoints
4. Video and action recognition
5. Text (encoders) and LLMs
6. Time series
7. Audio
8. Graphs, molecules, recommendation
9. Practical fit on Kaggle GPUs

## 1. Tabular

| Family | When it shines | Notes |
|---|---|---|
| LightGBM, XGBoost, CatBoost | Default for almost all tabular data | GPU modes exist. CatBoost handles categoricals natively. Tune with Optuna on grouped CV. |
| TabPFN (v2 and later) | Small to medium tables (thousands of rows) | Foundation model for tabular data. Check row and feature limits of the current version. Strong ensemble member. |
| TabM, RealMLP, FT-Transformer | Medium and large data, as diversity for GBDT ensembles | Neural tabular models that have closed much of the gap to GBDT. |
| AutoGluon (tabular) | Strong automated stacking baseline | Good for a quick ceiling estimate. Watch the runtime. |

The main levers are feature engineering (aggregations, target encoding inside folds, lags for temporal data) and ensembling of GBDT plus neural models.

## 2. Image classification and regression

| Family | Notes |
|---|---|
| ConvNeXt V2, EfficientNet V2, NFNet | Reliable CNN fine-tuning workhorses in `timm`. |
| EVA-02, ViT and Swin V2, MaxViT, CAFormer | Strong transformers. Need more data or stronger pretraining. |
| DINOv2 and DINOv3 (self-supervised ViTs) | Excellent frozen features and fine-tuning starts. Check the licence of each release. |
| SigLIP 2, CLIP-style encoders | Very strong features, but they are vision-language models, which some competitions ban. |

Common levers: higher resolution, longer fine-tuning with EMA, strong but realistic augmentation (RandAugment, mixup or cutmix where labels allow), multi-resolution TTA.

## 3. Detection, segmentation, keypoints

| Task | Families |
|---|---|
| Detection | Ultralytics YOLO (11 and newer, AGPL licence), RT-DETR and DETR variants such as D-FINE, DEIM, RF-DETR |
| Semantic segmentation | U-Net or UNet++ with `timm` encoders (`segmentation_models_pytorch`), SegFormer, Mask2Former, nnU-Net for medical volumes |
| Promptable segmentation | SAM 2 and newer SAM releases, MedSAM for medical |
| Keypoints and pose | YOLO-pose, RTMPose and RTMO, ViTPose, MediaPipe (face mesh, hands) |

Fusion and post-processing: weighted boxes fusion for detection ensembles, mask thresholds plus minimum-area filtering for segmentation.

## 4. Video and action recognition

| Family | Notes |
|---|---|
| VideoMAE and VideoMAE V2 | Fine-tune from Kinetics or Something-Something checkpoints. SSv2 pretraining helps motion-centric tasks. Check the licence of the V2 weights. |
| V-JEPA 2 | Strong frozen video features. An attentive or temporal probe on top is cheap and strong. |
| UniFormerV2, TimeSformer, Video Swin | Alternatives with different inductive biases, useful for ensemble diversity. |
| InternVideo2, VideoCLIP-style models | Very strong, but they contain text towers, so they are banned where VLMs are banned. |
| X3D, MoViNet, 2D CNN + temporal pooling | Light options when runtime is tight. |
| Pose, gaze and hand streams (YOLO-pose, RTMPose, MediaPipe, Gaze-LLE) | Add structured cues for human-behaviour tasks. They often help less than expected, so measure the blend weight. |

Levers: person- or region-centred crops, clip length and sampling (respect "all frames" rules at test), multi-clip inference inside one sample, label boundary handling, ensembles across pretraining sources.

## 5. Text (encoders) and LLMs

| Family | Notes |
|---|---|
| DeBERTa-v3 (base, large) | Long-standing Kaggle workhorse for classification and regression on text. |
| ModernBERT and other recent encoders | Longer context and faster. Compare with DeBERTa on CV. |
| Multilingual: XLM-R, mDeBERTa, multilingual LLMs | For non-English data, including Indonesian. |
| Open-weight LLMs (Qwen, Llama, Gemma, Mistral, Phi families; check the newest release) | Fine-tune with LoRA or QLoRA (PEFT, Unsloth) when the rules allow LLMs. Use vLLM for fast inference. Distil into smaller models to fit the runtime. |

Levers: max length and truncation strategy, layer-wise learning-rate decay, multi-sample dropout, pseudo-labelling only when allowed, ensembles of different backbones, LLM-generated training data only when allowed.

## 6. Time series

| Family | Notes |
|---|---|
| GBDT with lag, rolling and calendar features | The usual winner on business forecasting. |
| N-BEATS, N-HiTS, PatchTST, TFT, iTransformer | Neural options with good diversity. |
| Foundation models: Chronos (and Chronos-Bolt), TimesFM, Moirai | Strong zero-shot and fine-tuned baselines. Check the rules on zero-shot use. |

Levers: validation by time with a gap, target transforms, hierarchical reconciliation, bias correction.

## 7. Audio

| Family | Notes |
|---|---|
| CNNs on log-mel spectrograms (EfficientNet, NFNet, RegNet) | The common BirdCLEF-style winner. Use sound-event-detection heads for weak labels. |
| PANNs, AST, BEATs, EfficientAT | Pretrained audio backbones. |
| Whisper or wav2vec2-class encoders | Speech tasks. |

Levers: mixup across clips, background-noise augmentation, pseudo-labelling on unlabelled soundscapes when allowed, ensembles across mel settings.

## 8. Graphs, molecules, recommendation

- **Graphs and molecules**: GBDT on fingerprints and descriptors, GNNs (GIN, GAT, MPNN), pretrained molecular models (Uni-Mol class). Use scaffold-split validation.
- **Recommendation and ranking**: candidate generation (co-visitation, two-tower), then a GBDT ranker (LightGBM lambdarank), validated on a time split.

## 9. Practical fit on Kaggle GPUs

- **T4 (16 GB, often two)**: fast with fp16 autocast. bf16 is not natively fast. Use gradient checkpointing for large backbones. Two GPUs need DDP or two parallel processes; DataParallel is the simple fallback.
- **P100 (16 GB)**: fp32 is often as fast as fp16, because it has no tensor cores.
- Keep weights under the dataset size limits and test offline loading early.
- Estimate runtime per epoch and per fold on a small slice before planning a full run.
