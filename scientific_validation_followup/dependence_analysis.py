"""Reconstruct repeated splits and quantify overlap without importing project code."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


def summarize_pairwise(named_sets: dict[int, set[int]], split: str) -> list[dict]:
    rows = []
    for a, b in combinations(sorted(named_sets), 2):
        sa, sb = named_sets[a], named_sets[b]
        inter = len(sa & sb)
        union = len(sa | sb)
        rows.append({"set_type": split, "seed_a": a, "seed_b": b, "n_a": len(sa), "n_b": len(sb), "intersection": inter, "fraction_of_a": inter / len(sa), "fraction_of_b": inter / len(sb), "jaccard": inter / union})
    return rows


def main() -> None:
    df = pd.read_csv(ROOT / "online_shoppers_intention.csv")
    y = df["Revenue"].map({True: 1, False: 0, "TRUE": 1, "FALSE": 0}).astype(int)
    sets = {name: {} for name in ("train", "calibration", "test")}
    shifted = {p: {} for p in (.1, .155, .25)}
    membership = []
    for seed in range(42, 72):
        dev_ids, test_ids, y_dev, y_test = train_test_split(df.index.to_numpy(), y, test_size=.2, stratify=y, random_state=seed)
        train_ids, cal_ids, _, _ = train_test_split(dev_ids, y_dev, test_size=.25, stratify=y_dev, random_state=seed + 1)
        for name, ids in (("train", train_ids), ("calibration", cal_ids), ("test", test_ids)):
            sets[name][seed] = set(map(int, ids))
            membership.extend({"sample_id": int(i), "seed": seed, "set_type": name} for i in ids)
        ya = np.asarray(y_test)
        for offset, prior in enumerate((.1, .155, .25)):
            rng = np.random.default_rng(seed + offset)
            pos, neg = np.flatnonzero(ya == 1), np.flatnonzero(ya == 0)
            total = max(2, int(np.floor(min(len(pos)/prior, len(neg)/(1-prior)))))
            npos = min(len(pos), max(1, int(round(total*prior))))
            nneg = min(len(neg), max(1, total-npos))
            chosen = np.concatenate([rng.choice(pos, npos, replace=False), rng.choice(neg, nneg, replace=False)])
            rng.shuffle(chosen)
            shifted[prior][seed] = set(map(int, test_ids[chosen]))
    rows = []
    for name, values in sets.items():
        rows.extend(summarize_pairwise(values, name))
    for prior, values in shifted.items():
        rows.extend(summarize_pairwise(values, f"shifted_{prior}"))
    overlap = pd.DataFrame(rows)
    overlap.to_csv(OUT / "PAIRWISE_SPLIT_OVERLAP.csv", index=False)
    use = pd.DataFrame(membership).groupby(["sample_id", "set_type"]).size().unstack(fill_value=0).reset_index()
    for prior, values in shifted.items():
        counts = pd.Series({i: sum(i in s for s in values.values()) for i in df.index}, name=f"shifted_{prior}")
        use = use.merge(counts.rename_axis("sample_id").reset_index(), on="sample_id")
    use.to_csv(OUT / "OBSERVATION_REUSE_COUNTS.csv", index=False)
    summary = overlap.groupby("set_type").agg(pairs=("intersection", "size"), mean_intersection=("intersection", "mean"), min_intersection=("intersection", "min"), max_intersection=("intersection", "max"), mean_fraction=("fraction_of_a", "mean"), mean_jaccard=("jaccard", "mean")).reset_index()
    summary.to_csv(OUT / "OVERLAP_SUMMARY.csv", index=False)
    print(summary.to_string(index=False))
    print("\nReuse counts across 30 seeds:")
    print(use.drop(columns="sample_id").agg(["min", "mean", "max"]).to_string())


if __name__ == "__main__":
    main()
