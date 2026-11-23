# %% [markdown]
# # <Competition name>: <short task title>
#
# <Task in one sentence>. Evaluation metric: <metric>.
#
# Pipeline: <data preparation>, <validation scheme>, <model families>, out-of-fold ensemble with a threshold selected on validation data. <Compliance statement, for example: every test row is predicted independently and test data is used only for inference.>

# %% [markdown]
# ## 1. Setup

# %%
import os, gc, json, time, random, hashlib, itertools, warnings
from pathlib import Path
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

NB_T0 = time.time()
warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)
try:
    display
except NameError:
    display = print

# %%
@dataclass
class CFG:
    comp_slug: str = "competition-slug"
    seed: int = 42
    n_folds: int = 5
    debug: bool = os.environ.get("COMP_DEBUG", "0") == "1"
    target: str = "target"
    group_col: str = "group"
    metric: str = "macro_f1"
    thr_smooth: float = 0.03
    gbm_lr: float = 0.05
    gbm_iter: int = 400
    lr_c: float = 1.0
    time_limit_h: float = 11.0
    time_reserve_min: float = 20.0


cfg = CFG()
KEY_NEUTRAL = {}


def fingerprint(obj):
    return hashlib.md5(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:8]


def cfg_subset(prefixes=(), names=()):
    return {k: v for k, v in asdict(cfg).items()
            if (k.startswith(tuple(prefixes)) or k in names) and not (k in KEY_NEUTRAL and v == KEY_NEUTRAL[k])}


def time_left_min():
    return cfg.time_limit_h * 60 - (time.time() - NB_T0) / 60


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


seed_everything(cfg.seed)
IS_KAGGLE = Path("/kaggle/input").exists()
INPUT = Path("/kaggle/input") if IS_KAGGLE else Path(os.environ.get("COMP_INPUT", "input"))
WORK = Path("/kaggle/working") if IS_KAGGLE else Path(os.environ.get("COMP_WORK", "work"))
ART = WORK / ("artifacts_debug" if cfg.debug else "artifacts")
ART.mkdir(parents=True, exist_ok=True)
DATA = next((p.parent for p in sorted(INPUT.rglob("sample_submission.csv")) if cfg.comp_slug in str(p)), None) if INPUT.exists() else None
ART_ROOTS = [ART] + (sorted(p for p in INPUT.rglob("artifacts") if p.is_dir()) if INPUT.exists() else [])


def find_artifact(rel):
    for root in ART_ROOTS:
        if (root / rel).exists():
            return root / rel
    return None


print(f"data       : {DATA}")
print(f"artifacts  : {[str(r) for r in ART_ROOTS]}")
print(f"debug      : {cfg.debug}")

# %% [markdown]
# ## 2. Data
# Training data overview. Test data is only checked for completeness, since it is used for inference only.

# %%
if DATA is not None:
    train = pd.read_csv(DATA / "train.csv")
    test = pd.read_csv(DATA / "test.csv")
    sub = pd.read_csv(DATA / "sample_submission.csv")
else:
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=1200, n_features=12, n_informative=6, weights=[0.7], random_state=cfg.seed)
    frame = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    frame[cfg.target] = y
    frame[cfg.group_col] = np.random.RandomState(cfg.seed).randint(0, 40, len(frame))
    frame.insert(0, "id", np.arange(len(frame)))
    train, test = frame.iloc[:1000].reset_index(drop=True), frame.iloc[1000:].drop(columns=[cfg.target]).reset_index(drop=True)
    sub = test[["id"]].assign(**{cfg.target: 0})
FEATURES = [c for c in train.columns if c not in ("id", cfg.target, cfg.group_col)]
print(f"train {train.shape}, test rows {len(test)}, sample submission rows {len(sub)}, features {len(FEATURES)}")
display(train[cfg.target].value_counts(normalize=True).rename("share").to_frame().round(3))

# %% [markdown]
# ## 3. Validation
# Folds are grouped by `group_col`, the entity that differs between training and test data, and stratified by the target. The fold assignment is fixed by the seed and shared by every model, so out-of-fold predictions can be blended.

# %%
train["fold"] = -1
for k, (_, va) in enumerate(StratifiedGroupKFold(cfg.n_folds, shuffle=True, random_state=cfg.seed)
                            .split(train, train[cfg.target], train[cfg.group_col])):
    train.loc[va, "fold"] = k
display(train.groupby("fold").agg(rows=("id", "size"), groups=(cfg.group_col, "nunique"),
                                  positive_rate=(cfg.target, "mean")).round(3))
LABEL_KEY = fingerprint([cfg.n_folds, cfg.seed, cfg.target, cfg.group_col, len(train)])
(ART / f"preds_{LABEL_KEY}").mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## 4. Models
# Each model family is trained once per fold. Out-of-fold and test predictions are cached under a key of the settings that affect them, so a re-run reuses finished folds and only trains what changed.

# %%
def metric(y, p, thr=0.5):
    if cfg.metric == "auc":
        return roc_auc_score(y, p)
    return f1_score(y, (p >= thr).astype(int), average="macro" if cfg.metric == "macro_f1" else "binary", zero_division=0)


def run_model(name, make_model, keys):
    stem = f"{name}_{fingerprint(cfg_subset(keys))}"
    rel = f"preds_{LABEL_KEY}/oof_{stem}.csv"
    if find_artifact(rel) is not None:
        print(f"[{name}] cached")
        return stem
    oof = np.zeros(len(train))
    tst = np.zeros(len(test))
    for k in range(cfg.n_folds):
        if time_left_min() < cfg.time_reserve_min:
            print(f"[{name}] stopped by the time budget before fold {k}")
            return None
        tr, va = train.fold != k, train.fold == k
        model = make_model().fit(train.loc[tr, FEATURES], train.loc[tr, cfg.target])
        oof[va.values] = model.predict_proba(train.loc[va, FEATURES])[:, 1]
        tst += model.predict_proba(test[FEATURES])[:, 1] / cfg.n_folds
        print(f"[{name}] fold {k}: auc {roc_auc_score(train.loc[va, cfg.target], oof[va.values]):.4f}")
    pd.DataFrame({"id": train.id, "fold": train.fold, "y": train[cfg.target], "pred": oof}).to_csv(ART / rel, index=False)
    pd.DataFrame({"id": test.id, "pred": tst}).to_csv(ART / f"preds_{LABEL_KEY}/test_{stem}.csv", index=False)
    print(f"[{name}] OOF auc {roc_auc_score(train[cfg.target], oof):.4f}")
    return stem


# %% [markdown]
# ### 4.1 Gradient boosting

# %%
from sklearn.ensemble import HistGradientBoostingClassifier

STEMS = {}
STEMS["gbm"] = run_model("gbm", lambda: HistGradientBoostingClassifier(
    learning_rate=cfg.gbm_lr, max_iter=60 if cfg.debug else cfg.gbm_iter, random_state=cfg.seed), ["gbm_"])

# %% [markdown]
# ### 4.2 Logistic regression
# A linear model adds diversity to the ensemble at almost no cost.

# %%
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

STEMS["logreg"] = run_model("logreg", lambda: make_pipeline(StandardScaler(), LogisticRegression(C=cfg.lr_c, max_iter=1000)),
                            ["lr_"])

# %% [markdown]
# ## 5. Evaluation and Ensemble
# Blend weights maximise out-of-fold AUC over a simplex grid. The decision threshold maximises the metric curve averaged over the folds and smoothed over +-`thr_smooth`, which is more stable on unseen groups than the pooled optimum. Both choices use out-of-fold predictions only.

# %%
USED = [n for n, s in STEMS.items() if s is not None]
OOF = train[["id", "fold", cfg.target]].copy()
TEST_P = test[["id"]].copy()
for n in USED:
    OOF[n] = pd.read_csv(find_artifact(f"preds_{LABEL_KEY}/oof_{STEMS[n]}.csv")).pred.values
    TEST_P[n] = pd.read_csv(find_artifact(f"preds_{LABEL_KEY}/test_{STEMS[n]}.csv")).pred.values
Y, FOLDS = OOF[cfg.target].values, OOF.fold.values


def robust_threshold(y, p):
    ts = np.round(np.arange(0.05, 0.951, 0.01), 2)
    curve = np.mean([[metric(y[FOLDS == k], p[FOLDS == k], t) for t in ts] for k in np.unique(FOLDS)], 0)
    w = max(0, int(round(cfg.thr_smooth / 0.01)))
    smooth = np.convolve(np.pad(curve, w, mode="edge"), np.ones(2 * w + 1) / (2 * w + 1), mode="valid")
    return float(ts[int(np.argmax(smooth))])


grid = [np.array(c) / 10 for c in itertools.product(range(11), repeat=len(USED)) if sum(c) == 10]
W = max(grid, key=lambda w: roc_auc_score(Y, OOF[USED].values @ w))
OOF["ens"] = OOF[USED].values @ W
THR = robust_threshold(Y, OOF.ens.values) if cfg.metric != "auc" else 0.5
display(pd.DataFrame({n: {"auc": roc_auc_score(Y, OOF[n]), cfg.metric: metric(Y, OOF[n].values, THR)} for n in USED + ["ens"]}).T.round(4))
print("weights   :", {n: round(float(w), 2) for n, w in zip(USED, W)})
print(f"threshold : {THR:.2f} (fold-averaged, smoothed)")
display(OOF.groupby("fold").apply(lambda d: metric(d[cfg.target].values, d.ens.values, THR)).rename(cfg.metric).to_frame().T.round(4))

# %% [markdown]
# ## 6. Inference and Submission
# Test predictions of every fold model are averaged per model, blended with the out-of-fold weights and thresholded.

# %%
TEST_P["ens"] = TEST_P[USED].values @ W
submission = sub[["id"]].merge(TEST_P[["id", "ens"]], on="id", how="left")
submission[cfg.target] = (submission.ens.fillna(0) >= THR).astype(int) if cfg.metric != "auc" else submission.ens.fillna(0)
submission = submission.drop(columns="ens")
out_path = WORK / ("submission_debug.csv" if cfg.debug else "submission.csv")
submission.to_csv(out_path, index=False)
with open(ART / "ensemble.json", "w") as f:
    json.dump({"models": USED, "files": {n: STEMS[n] for n in USED}, "weights": [float(w) for w in W], "threshold": THR,
               "config": asdict(cfg)}, f, indent=2)
print(f"{out_path}: {len(submission)} rows")
print(f"total runtime: {(time.time() - NB_T0) / 3600:.2f} h")

# %% [markdown]
# ## 7. Notes on Data, Labels and Compliance
# - Data: <competition data only, or list each external source with its licence and the rule that allows it>.
# - Pretrained weights: <list with source and licence, or none>.
# - Labels: <how training labels were produced and validated; evaluation-label convention and its training-data basis>.
# - Selection: blend weights and the threshold are chosen on out-of-fold predictions; test data is used only for inference.
