"""Out-of-fold tools for Kaggle competitions.

Subcommands
  noise      bootstrap the spread of a metric at the public-LB size
  compare    paired bootstrap of the metric difference between two OOF files
  threshold  fold-averaged, smoothed decision threshold for F1-type metrics
  blend      simplex-grid blend weights on OOF plus a robust threshold, optional blended test file

OOF files are CSVs with an id column, a label column, a prediction column and optionally a fold column.
Column names are set with --id-col, --y-col, --p-col and --fold-col.
"""
import argparse
import itertools
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, log_loss, roc_auc_score

THRESHOLD_METRICS = {"macro_f1", "f1", "accuracy"}


def score(metric, y, p, thr=0.5):
    if metric == "auc":
        return roc_auc_score(y, p)
    if metric == "logloss":
        return log_loss(y, np.clip(p, 1e-7, 1 - 1e-7), labels=[0, 1])
    pred = (p >= thr).astype(int)
    if metric == "macro_f1":
        return f1_score(y, pred, average="macro", zero_division=0)
    if metric == "f1":
        return f1_score(y, pred, zero_division=0)
    if metric == "accuracy":
        return accuracy_score(y, pred)
    raise ValueError(metric)


def load(path, a):
    df = pd.read_csv(path)
    missing = [c for c in (a.y_col, a.p_col) if c not in df.columns]
    if missing:
        sys.exit(f"{path}: missing columns {missing}; columns are {list(df.columns)}")
    return df


def robust_threshold(metric, y, p, folds, smooth=0.03, lo=0.02, hi=0.98, step=0.01):
    ts = np.round(np.arange(lo, hi + 1e-9, step), 4)
    groups = [folds == f for f in np.unique(folds) if len(np.unique(y[folds == f])) > 1] if folds is not None else []
    groups = groups or [np.ones(len(y), bool)]
    curve = np.mean([[score(metric, y[g], p[g], t) for t in ts] for g in groups], 0)
    k = max(0, int(round(smooth / step)))
    smoothed = np.convolve(np.pad(curve, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    t = float(ts[int(np.argmax(smoothed))])
    return t, score(metric, y, p, t)


def cmd_noise(a):
    df = load(a.oof, a)
    y, p = df[a.y_col].values.astype(int), df[a.p_col].values.astype(float)
    rng = np.random.default_rng(a.seed)
    vals = np.array([score(a.metric, y[i], p[i], a.threshold)
                     for i in (rng.integers(0, len(y), a.n) for _ in range(a.iters))])
    full = score(a.metric, y, p, a.threshold)
    print(f"metric {a.metric} at threshold {a.threshold}: full OOF {full:.4f}")
    print(f"bootstrap at n={a.n}: mean {vals.mean():.4f}, sd {vals.std():.4f}, "
          f"95% interval [{np.percentile(vals, 2.5):.4f}, {np.percentile(vals, 97.5):.4f}]")
    print(f"a public LB of this size can sit about +-{2 * vals.std():.4f} away from the score on all data; "
          f"for the gap between two submissions on the same rows use: compare --n {a.n}")


def cmd_compare(a):
    da, db = load(a.a, a), load(a.b, a)
    key = a.id_col if a.id_col in da.columns and a.id_col in db.columns else None
    if key:
        m = da[[key, a.y_col, a.p_col] + ([a.group_col] if a.group_col else [])].merge(
            db[[key, a.p_col]], on=key, suffixes=("_a", "_b"))
    else:
        m = da.assign(**{f"{a.p_col}_a": da[a.p_col], f"{a.p_col}_b": db[a.p_col].values})
    y, pa, pb = m[a.y_col].values.astype(int), m[f"{a.p_col}_a"].values, m[f"{a.p_col}_b"].values
    units = m[a.group_col].values if a.group_col else np.arange(len(m))
    uniq = np.unique(units)
    index = {u: np.where(units == u)[0] for u in uniq}
    rng = np.random.default_rng(a.seed)
    diffs = []
    for _ in range(a.iters):
        if a.n:
            idx = rng.integers(0, len(m), a.n)
        else:
            idx = np.concatenate([index[u] for u in rng.choice(uniq, len(uniq))])
        diffs.append(score(a.metric, y[idx], pb[idx], a.threshold) - score(a.metric, y[idx], pa[idx], a.threshold))
    diffs = np.array(diffs)
    base = score(a.metric, y, pb, a.threshold) - score(a.metric, y, pa, a.threshold)
    print(f"{a.metric}: B - A = {base:+.4f}; bootstrap sd {diffs.std():.4f}; "
          f"95% interval [{np.percentile(diffs, 2.5):+.4f}, {np.percentile(diffs, 97.5):+.4f}]; "
          f"B better in {np.mean(diffs > 0):.1%} of resamples")


def cmd_threshold(a):
    df = load(a.oof, a)
    folds = df[a.fold_col].values if a.fold_col in df.columns else None
    t, s = robust_threshold(a.metric, df[a.y_col].values.astype(int), df[a.p_col].values.astype(float), folds, a.smooth)
    print(f"threshold {t:.2f} (fold-averaged, smoothed +-{a.smooth}), {a.metric} at it {s:.4f}")


def simplex(k, step):
    n = int(round(1 / step))
    return [np.array(c, float) / n for c in itertools.product(range(n + 1), repeat=k) if sum(c) == n]


def cmd_blend(a):
    frames = []
    for i, path in enumerate(a.oof):
        df = load(path, a)
        cols = [a.id_col, a.y_col, a.p_col] + ([a.fold_col] if a.fold_col in df.columns else [])
        df = df[cols].rename(columns={a.p_col: f"m{i}"})
        frames.append(df if i == 0 else df[[a.id_col, f"m{i}"]])
    m = frames[0]
    for df in frames[1:]:
        m = m.merge(df, on=a.id_col)
    names = [f"m{i}" for i in range(len(a.oof))]
    y, P = m[a.y_col].values.astype(int), m[names].values
    folds = m[a.fold_col].values if a.fold_col in m.columns else None
    weight_metric = "auc" if a.metric in THRESHOLD_METRICS else a.metric
    sign = -1 if weight_metric == "logloss" else 1
    cands = simplex(len(names), a.step)
    best = max(cands, key=lambda w: sign * score(weight_metric, y, P @ w))
    for path, name in zip(a.oof, names):
        print(f"{name} = {path}: {weight_metric} {score(weight_metric, y, m[name].values):.4f}")
    print("weights:", {n: round(float(w), 3) for n, w in zip(names, best)})
    print(f"blend {weight_metric}: {score(weight_metric, y, P @ best):.4f}")
    thr = 0.5
    if a.metric in THRESHOLD_METRICS:
        thr, s = robust_threshold(a.metric, y, P @ best, folds, a.smooth)
        print(f"threshold {thr:.2f} (fold-averaged, smoothed), {a.metric} {s:.4f}")
    if a.test:
        if len(a.test) != len(a.oof):
            sys.exit("--test needs one file per --oof file, in the same order")
        t = None
        for i, path in enumerate(a.test):
            d = pd.read_csv(path)[[a.id_col, a.p_col]].rename(columns={a.p_col: f"m{i}"})
            t = d if t is None else t.merge(d, on=a.id_col, how="outer")
        t["pred"] = t[names].fillna(t[names].mean()).values @ best
        if a.metric in THRESHOLD_METRICS:
            t["label"] = (t.pred >= thr).astype(int)
        t.drop(columns=names).to_csv(a.out, index=False)
        print(f"blended test predictions written to {a.out} ({len(t)} rows)")


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--id-col", default="id")
    common.add_argument("--y-col", default="y")
    common.add_argument("--p-col", default="pred")
    common.add_argument("--fold-col", default="fold")
    common.add_argument("--metric", default="macro_f1", choices=["macro_f1", "f1", "accuracy", "auc", "logloss"])
    common.add_argument("--threshold", type=float, default=0.5)
    common.add_argument("--iters", type=int, default=2000)
    common.add_argument("--seed", type=int, default=0)
    common.add_argument("--smooth", type=float, default=0.03)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("noise", parents=[common], help="bootstrap the metric at the public-LB size")
    s.add_argument("--oof", required=True)
    s.add_argument("--n", type=int, required=True, help="number of public-LB rows")
    s = sub.add_parser("compare", parents=[common], help="paired bootstrap of B minus A")
    s.add_argument("--a", required=True)
    s.add_argument("--b", required=True)
    s.add_argument("--group-col", default=None, help="resample whole groups (subjects, videos) instead of rows")
    s.add_argument("--n", type=int, default=None, help="resample this many rows, for example the public-LB size")
    s = sub.add_parser("threshold", parents=[common], help="fold-averaged smoothed threshold")
    s.add_argument("--oof", required=True)
    s = sub.add_parser("blend", parents=[common], help="simplex blend weights plus robust threshold")
    s.add_argument("--oof", nargs="+", required=True)
    s.add_argument("--test", nargs="*", default=None)
    s.add_argument("--out", default="blend_test.csv")
    s.add_argument("--step", type=float, default=0.1)
    a = ap.parse_args()
    {"noise": cmd_noise, "compare": cmd_compare, "threshold": cmd_threshold, "blend": cmd_blend}[a.cmd](a)


if __name__ == "__main__":
    main()
