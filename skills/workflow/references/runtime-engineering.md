# Runtime engineering for Kaggle notebooks

## Contents
1. Limits to confirm on day one
2. Notebook source and build
3. Stage caches keyed by config fingerprints
4. Time-budget guard
5. Local smoke test without a GPU
6. GPU efficiency on Kaggle hardware
7. Offline competitions
8. Running on Kaggle
9. Instructions to give the user for every run

## 1. Limits to confirm on day one

Confirm each value on the competition page and the user's Kaggle account, because they change:
- session runtime limit for the submission or re-run;
- weekly GPU quota;
- GPU type (T4 x2 or P100);
- RAM and disk, including the output size limit of `/kaggle/working`;
- internet on or off;
- the submission format.

Write them into `COMPETITION.md`.

## 2. Notebook source and build

- Keep the notebook as a percent-format Python source (`# %%` code cells, `# %% [markdown]` cells) and build the `.ipynb` with the notebook skill's `scripts/build_nb.py`.
- One source of truth makes diffs, patches and smoke tests easy. Never hand-edit the built `.ipynb`.

## 3. Stage caches keyed by config fingerprints

- Split the pipeline into stages: preprocess, features, labels, models (one per family), ensemble.
- Each stage writes to a directory named by a hash of the config fields that affect it, for example `feat_<hash>`. Changing an unrelated field never invalidates it. Changing a relevant field never reuses a stale artifact.
- When adding a new config field, exclude it from the hash while it sits at a neutral default, so existing caches stay valid.
- Search for cached artifacts in both `/kaggle/working` and every attached input (earlier notebook versions' outputs). This turns earlier runs into free caches.
- Save per-fold outputs (`oof_<stem>_fold<k>.csv`, model weights), so an interrupted run resumes at the next fold.

## 4. Time-budget guard

- Record `T0` at the first cell.
- Before each expensive unit (a fold, a model family), estimate its time from the previous unit and skip it, with a printed message, if it would overrun `limit - reserve`.
- The final cells (ensemble, submission) must always have time left. Print the total runtime at the end.
- Measure each stage once on Kaggle and write the times into `COMPETITION.md`. The from-scratch runtime decides whether the organizers' re-run fits.

## 5. Local smoke test without a GPU

- Build a tiny synthetic dataset with the same folder structure as the competition data: a few files per class, short videos or small images, a matching sample submission.
- Replace heavy models with tiny random-initialised versions (monkeypatch `from_pretrained` to return a 2-layer config of the same class) and fake external models (detectors, gaze or pose models).
- Run the whole notebook end to end with a debug flag (fewer folds, epochs and windows). This catches shape bugs, missing files and cache-key mistakes in minutes instead of hours of GPU time.
- Re-run the smoke test after every change to the source.

## 6. GPU efficiency on Kaggle hardware

- **T4:**
  - Use fp16 autocast with a GradScaler. bf16 is not fast on T4.
  - Use channels-last for CNNs.
  - Use gradient checkpointing for large models.
  - Both T4s can be used through DDP, through two processes on different folds, or through DataParallel as a simple fallback.
- **P100:** fp32 is about as fast as fp16.
- **Data loading:**
  - Decode once and cache crops or frames as JPEG or uint8 arrays.
  - Use thread pools when multiprocessing workers misbehave (seen with Python 3.13 on Kaggle).
  - Prefetch.
- Extract frozen-backbone features once and train many light heads on them. This is the cheapest way to try many ideas.

## 7. Offline competitions

- Upload wheels (`pip download` on a machine with the same Python version) and model weights as Kaggle datasets in advance. Install with `pip install --no-index --find-links /kaggle/input/<wheels>`.
- Test the offline path in a notebook with internet turned off before the final week.

## 8. Running on Kaggle

- "Save Version, Save & Run All (Commit)" runs in a fresh session, so no restart is needed.
- Interactive sessions keep `/kaggle/working` between runs. Stale artifacts are the classic source of "it worked yesterday". Fingerprinted cache dirs prevent it.
- Attach earlier notebook versions as inputs to reuse their caches. List exactly which ones in the run instructions.

## 9. Instructions to give the user for every run

1. Notebook name and which source version to import.
2. Inputs to attach: competition data, datasets, earlier notebook outputs.
3. Accelerator and internet setting.
4. Whether a session restart is needed.
5. Expected runtime and GPU hours.
6. Log lines that confirm caches are reused or that training started as intended, and when to cancel.
7. What to send back: metric tables, blend weights, threshold, error tables, runtime lines, LB score.
