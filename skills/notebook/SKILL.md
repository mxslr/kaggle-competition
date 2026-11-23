---
name: notebook
description: "Writes and maintains professional, reproducible Kaggle competition notebooks: a percent-format Python source built into .ipynb, numbered sections with short research-style explanations, no code comments, config dataclass with fingerprinted stage caches, Kaggle/Colab/local path detection, a runtime guard for the session limit, a debug mode for a quick Kaggle check run, delivery of the built .ipynb for import into Kaggle (all compute runs on Kaggle, never on the user's machine), and a transparency section that states data, labels and selection basis honestly. Use it whenever a competition notebook has to be created, restructured, cleaned for hand-in, or made to fit the runtime limit, including requests like 'buat notebook kaggle', 'rapikan notebook', 'notebook final'."
---

# Competition notebook

The notebook is the deliverable the organizers read and re-run. It has to run from scratch inside the limit, produce exactly the submitted file, and explain itself briefly and honestly.

It is also the only place where the pipeline runs. Every step executes on Kaggle, and the user receives the built `.ipynb` to import. Nothing is trained, and no competition data or pretrained weights are processed, on the user's machine.

## 1. Source of truth and build

- Write the notebook as a percent-format Python file, for example `nb_src.py`:
  - code cells start with `# %%`;
  - markdown cells start with `# %% [markdown]`, with each markdown line prefixed by `# `.
- Build with `python scripts/build_nb.py nb_src.py notebook.ipynb`. The builder validates the syntax of each code cell. By default it rejects `#` comments inside code cells, because the user prefers comment-free code and explanations live in markdown. Use `--allow-comments` when a project wants comments. It also warns about em dashes and emoji in markdown.
- Start new notebooks from `assets/nb_template.py`. It already contains environment detection, the config dataclass, fingerprints, the artifact search over earlier notebook outputs, the time guard, seeding, out-of-fold storage and the submission cell.
- Never hand-edit the built `.ipynb`. Change the source, rebuild, run the static checks, and send the new `.ipynb` to the user.

## 2. Structure

Use numbered sections. Sub-steps use `### 4.1`, `### 4.2` and so on.

1. **Title and summary**: task, metric, pipeline in one paragraph, and a one-line compliance statement (for example "every test sequence is predicted independently from all of its frames; test data is used only for inference").
2. **Setup**: installs (guarded by version checks), imports, config, paths, device.
3. **Data**: training data overview. When the rules forbid test analysis, the test part is limited to checking that every id has its file.
4. **Labels and preprocessing**: label sources and rules, cropping or feature extraction, caches.
5. **Validation**: fold scheme and why it mirrors the test split, plus evaluation labels if they differ from the training targets.
6. **Models**: one subsection per model family, each with its OOF metrics.
7. **Evaluation and ensemble**: per-model table, blend weights, threshold, per-fold scores, error tables built from OOF only.
8. **Inference and submission**: test predictions, blending, file writing, total runtime.
9. **Notes on data, labels and compliance**: sources, licences, labelling process, selection basis. Required when the FAQ asks for transparency.

## 3. Writing style

- Short, plain, professional sentences in a research tone. One short paragraph per markdown cell is usually enough.
- Explain **what** a step does and **why**, citing the rule or FAQ number when a design choice comes from it.
- No em dashes, no emoji, no marketing words, no claims the code does not support.
- State numbers that come from the run as outputs of the code, not as hard-coded text that can go stale.
- Name the train-only basis of every chosen constant (thresholds, time values, margins, label rules).
- Keep test-related output to what the rules allow. When test analysis is banned, print only the submission path and row count, never label counts or score histograms.

## 4. Engineering conventions

- **One config dataclass.** Every tunable value lives in it. Stage keys are fingerprints of the config fields each stage depends on. New fields stay out of the key while at their neutral default, so old caches remain valid.
- **Artifact search.** Look for cached files in `/kaggle/working` first, then in every attached input, so earlier notebook versions act as caches. Never write into inputs.
- **Time guard.** `T0` is set in the first code cell. Long loops check `time_left_min()` and skip work that would overrun, printing what was skipped. The submission cell always runs.
- **Determinism.** Seed everything, fix the fold assignment, and keep per-fold outputs so an interrupted run resumes.
- **Debug mode.** A config flag (`debug=True`, or the `COMP_DEBUG=1` environment variable) shrinks data, folds and epochs so the whole notebook finishes in minutes. Before a long run, give the user the debug version to commit on Kaggle first.
- **Local checks stay light.** Build the notebook (every code cell is syntax-checked) and, at most, run pure helper functions on tiny synthetic inputs for a few seconds. No training, no competition data and no downloaded weights on the user's machine.
- **Outputs for blending.** Each model writes `oof_<stem>.csv` and `test_<stem>.csv` with the same ids, and an `ensemble.json` records models, file stems, weights, threshold and the full config.

## 5. Before handing in

- Rebuild from the source, run the static checks, and have the user run the debug version on Kaggle when the change is large.
- Run the `kaggle-competition:rules-gate` audit on the built notebook.
- Check that the markdown matches the final config: model list, label rules, thresholds and the selection basis.
- Confirm that the final run's log shows every stage completed within the limit, and that the submission file has the expected row count.

## 6. Giving run instructions to the user

Every time the user must run the notebook on Kaggle, send the built `.ipynb` file (with the file-sharing tool when available, otherwise its path) and tell them:
- the notebook name and the source version to import;
- the inputs to attach;
- the accelerator and internet setting;
- **whether to restart the session** (a commit run always starts fresh);
- the expected runtime;
- the log lines to check and when to cancel;
- what to send back.
