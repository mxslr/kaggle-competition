# Research playbook

Research is the cheapest score you will ever get. One hour of reading winning write-ups usually beats one day of blind tuning.

## Contents
1. What to find
2. Where to look
3. Query patterns
4. How to read a winning solution
5. Recency, licence and fit checks
6. Writing RESEARCH.md
7. Research during the competition

## 1. What to find

- The 3 to 5 **closest past competitions**: same modality, similar label structure, similar metric, similar train/test shift.
- Their **top solutions**: validation, backbones, input representation, augmentation, loss, external data or pseudo-labels (and whether those were allowed), ensembling, post-processing, runtime.
- The **newest strong models** for the modality (see `model-zoo.md`), checked for licence and fit.
- **Papers on the exact sub-problem** (for example temporal localisation inside short clips, long-tail classes, domain shift across subjects).
- **Current public notebooks and discussion** of this competition: baseline scores, data quirks, host clarifications, known leaks (to avoid when banned).

## 2. Where to look

| Source | Use it for |
|---|---|
| Kaggle competition "Discussion" (sort by votes) and "Code" (sort by score) | Data quirks, host answers, strong public baselines, LB-to-CV relations other teams report |
| Past competitions' "Solution" write-ups (discussion threads titled "1st place solution", "Xth place") | What actually wins on similar data |
| Curated solution lists (search "kaggle past solutions" collections) | Fast index of write-ups by competition type |
| Hugging Face Hub (models sorted by trending, downloads, recent; filter by task) | Newest checkpoints, licences, model cards, sizes |
| Hugging Face Papers and arXiv (cs.CV, cs.CL, cs.LG, eess.AS) | New methods; check whether code and weights exist |
| `timm` results tables and model cards | Image backbone accuracy versus speed |
| Library release notes (transformers, timm, ultralytics, lightgbm, xgboost, catboost) | New features that change what fits the runtime |

## 3. Query patterns

- `kaggle <competition name> 1st place solution`, `kaggle <task> winning solution writeup`
- `kaggle <metric> <modality> competition solution` (for example `kaggle macro f1 video classification solution`)
- `<task> state of the art <current year>`, `<task> benchmark`, `<modality> foundation model <current year>`
- `<model family> fine-tune kaggle`, `<model family> vs <other family> <task>`
- `<sub-problem> paper` (for example `label noise temporal boundaries action detection`)
- `huggingface <task> model` and the Hub's own search with task filters

Run several in parallel, then read the best 3 to 8 results in full.

## 4. How to read a winning solution

Extract into a table:

| Item | Why it matters |
|---|---|
| Validation scheme and CV-LB correlation | Tells you whether to trust your CV design |
| Input representation (resolution, crop, frames, context length, features) | Often the largest gain |
| Backbone(s) and pretraining source | What to try first |
| Augmentations and their strength | Match to the test shift |
| Loss, targets, label handling | Especially for noisy or coarse labels |
| Extra data, pseudo-labels, distillation | Only transferable if this competition's rules allow them |
| Ensemble size and weighting | Gives a realistic runtime budget |
| Post-processing | Cheap gains for the same metric |
| What did not work | Saves you the same dead ends |

Separate what is **transferable under the current rules** from what is not.

## 5. Recency, licence and fit checks

For every candidate model, record:
- release date and version;
- licence (some research weights are non-commercial, and prize rules may need open licences);
- parameter count and memory at your input size;
- training and inference time per sample on the competition GPU (T4 runs fp16 well but has no fast bf16; P100 has no tensor cores);
- whether the weights can be loaded offline (upload as a Kaggle dataset if internet is off);
- rule status: banned families (VLM, LLM, CLIP-style), zero-shot bans, external-data rules.

A slightly older model that fits the runtime and the rules beats a newer one that does not.

## 6. Writing RESEARCH.md

Use `assets/RESEARCH.md`. Rank candidates by expected gain over the baseline, cost (GPU hours) and rule status. State the realistic ceiling and the reasons for it. Keep links next to every claim.

## 7. Research during the competition

- Re-read the discussion forum every few days: host clarifications change what is allowed.
- When a bottleneck appears (for example one class with low recall), research that bottleneck specifically, not the whole task again.
- Check whether public notebooks expose a leak. If the rules ban it, avoid any feature that depends on it, and expect the public LB to be inflated by teams using it.
