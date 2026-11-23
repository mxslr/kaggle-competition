# Technique catalog: rule-gated techniques

Many of the strongest Kaggle tricks are allowed in one competition and disqualifying in the next. Use this catalog to remember what to ask, and use the competition's `RULES.md` ledger to decide. A technique is used only when the ledger marks it **allowed** for this competition.

## Contents
1. Never allowed (any competition)
2. Data and labels
3. Test-time and transductive techniques
4. Cross-row context and leaks
5. Model families and external services
6. Leaderboard use
7. Template questions for organizers

Status words used below: **often allowed**, **often restricted**, **often banned**. They describe common practice only. The rules of the current competition always decide.

## 1. Never allowed (any competition)

- Multiple Kaggle accounts or submissions beyond the team's daily limit.
- Private sharing of code or data outside the team. Sharing publicly in the forum is allowed when the rules allow it.
- Hand-labelling test data, or using test labels obtained from anywhere.
- Hiding how a result was produced from organizers who verify notebooks.

These are not tactics. Leave them out of every plan.

## 2. Data and labels

| Technique | Typical gain | Status | Ask or check | Notes |
|---|---|---|---|---|
| External public datasets | Large on small data | Often allowed if public, free and disclosed (often in a dedicated thread) | Is dataset X allowed? Must it be posted? | Check licence, and check for overlap with test (leak risk). |
| Pretrained weights and foundation models | Usually the biggest single gain | Often allowed; some competitions ban families such as VLM or LLM | Are pretrained weights allowed? Any banned families? | Record source, licence and date. Offline competitions need the weights uploaded as a dataset. |
| Pseudo-labelling of **test** rows | +0.5 to +3 points in many CV and NLP competitions | Often allowed on Kaggle, banned when test is "inference only" | Is pseudo-labelling the test set allowed? | Use confident rows, soft labels, and a full retrain. Keep pseudo-labelled rows out of validation folds. |
| Pseudo-labelling **unlabelled external** data | Medium to large | Often allowed when the external data itself is allowed | Is unlabelled external data allowed for semi-supervised training? | Differs from test pseudo-labelling, so ask separately. |
| Knowledge distillation from an ensemble into one model, using training data only | Medium, and saves runtime | Allowed (train only) | None needed | Distilling on test inputs is transductive, see section 3. |
| Manual or AI-assisted annotation of **training** data (finer labels, intervals, boxes) | Can be large when labels are coarse | Varies; some hosts allow it with validation, some ban AI assistance | May we annotate training data, and may an AI assistant help? | Document the process in the notebook. Validate on a re-checked sample. |
| LLM or VLM generated synthetic training data or labels | Medium | Varies | Are generative models allowed for creating training data? | Keep generation offline and reproducible. Store the generated data as a dataset. |
| Classic synthetic data (simulation, diffusion, augmentation libraries, SMOTE) | Small to medium | Often allowed for training | Usually none | Avoid generating near-copies of validation rows. |
| Label conventions fitted to test prevalence or LB probes | Can be large when the host's labelling is unusual | Banned when values must come from training data | Must label rules and time values be chosen from training data only? | Prefer conventions derived from training annotations and FAQ semantics. |

## 3. Test-time and transductive techniques

| Technique | Typical gain | Status | Ask or check | Notes |
|---|---|---|---|---|
| Test-time augmentation per row (flips, crops, scales, multi-clip, multiple windows) | Small to medium | Often allowed, because it stays inside one row | Usually none; for video, confirm all frames are used | Average only within the same test row. |
| Test-time training or adaptation on test inputs (TENT, self-supervised fine-tuning) | Medium under domain shift | Often banned when test is inference only | Is any training or adaptation on test inputs allowed? | Transductive by definition. |
| Fitting scalers, PCA, vocabularies or normalisation on test inputs | Small | Banned when test is inference only | As above | Fit on training data only to stay safe. |
| Threshold from test quantiles, or prior-shift correction (EM on test predictions) | Medium under label shift | Banned when test analysis is banned | May decision rules use statistics of test predictions? | The safe version is a threshold chosen on out-of-fold data. |
| Adversarial validation (train versus test classifier) | Diagnostic; guides feature removal and validation design | Banned when test analysis is banned | Is analysing test inputs allowed? | When allowed, it is the best shift detector. |
| Unsupervised pretraining on test inputs (MLM on test text, SSL on test images) | Medium | Often banned in "inference only" competitions | Is self-supervised pretraining on test inputs allowed? | Same logic as test-time training. |
| Dropping, subsampling or interpolating test inputs (frames, rows, tokens) | Saves runtime | Banned when all inputs must be processed | Must every frame or row reach the model? | Multi-clip processing that covers every input is the usual compliant alternative. |

## 4. Cross-row context and leaks

| Technique | Typical gain | Status | Ask or check | Notes |
|---|---|---|---|---|
| Reconstructing shuffled sequences (chaining test chunks back into videos, sessions or users) | Can reach near-perfect scores | Banned when each row must be predicted independently; otherwise a host decision | Must each test row be predicted independently? | If allowed, the host should state it publicly. |
| Group features across test rows (same user, session or device statistics) | Large in tabular competitions | Often allowed in tabular competitions that ship IDs; banned under row independence | Are aggregates across test rows allowed? | Compute group features within each fold for validation. |
| ID, ordering, timestamp or file-metadata leaks | Can be large | Host decision; Kaggle treats leaks case by case and may fix the data | Is using feature X (row order, IDs, metadata) acceptable? | Never rely on a leak without the host's public confirmation. |
| Nearest-neighbour matching to training rows (duplicates across splits) | Large when duplicates exist | Often allowed when the data contain duplicates; it signals a split flaw | Report duplicates to the host | It can vanish in the private split. |

## 5. Model families and external services

| Technique | Status | Ask or check |
|---|---|---|
| Zero-shot prediction with a pretrained model (no training) | Often banned in "build a model" competitions; allowed in LLM competitions | Is zero-shot prediction allowed? |
| VLM or CLIP-style image-text encoders as frozen feature extractors | Varies; banned in some video and vision competitions | Are vision-language models allowed as feature extractors? |
| LLM fine-tuning (LoRA or QLoRA) on training data | Often allowed when weights are public and fit the runtime | Are open-weight LLMs allowed? Any size limit? |
| Closed API models (GPT, Claude, Gemini) during inference | Usually impossible (internet off) or banned | Are API calls allowed at inference or for data generation? |
| Models with non-commercial licences | Depends on prize rules; winners often must licence their solution | Do winning solutions need a commercial-friendly licence? |

## 6. Leaderboard use

- Use the LB to check that CV tracks it. Do not tune hyperparameters, thresholds or label conventions to it.
- When the FAQ says decisions must come from training data, an LB-guided choice is a rule problem even if it scores higher.
- Probing submissions that extract test statistics, such as an all-ones prediction to read prevalence, are against the spirit of most competitions. Some FAQs explicitly ban them. Leave them out unless the host clearly allows them.
- Spend the daily submission slots on sanity checks of new pipelines, and keep a margin for the final day.

## 7. Template questions for organizers

Short and specific questions get clear answers. Examples:
- "Is pseudo-labelling of the test set allowed, or must test data be used only for inference?"
- "May we annotate the training data in more detail (for example temporal intervals or boxes), with help from an AI assistant, if we document the process in the notebook?"
- "Is model X (a vision-language model) allowed as a frozen feature extractor if it is not used for zero-shot prediction?"
- "May time values in our labelling rule be chosen from training-data analysis?"
- "Must all N frames of each test sequence be processed directly, or may we sample?"
- "Are statistics of test predictions (for example quantiles) allowed when setting the decision threshold?"

Record every answer in `RULES.md` with its date and source.
