"""Paired significance tests between two strategies' per-page metric scores.

Every page in the corpus is converted by all four strategies, so per-page
scores form paired samples. For each metric, the difference between the two
strategies is tested with a two-sided paired sign-flip permutation test:
under the null hypothesis (no difference), each page's difference is equally
likely to have either sign, so the observed mean difference is compared
against the distribution of mean differences over random sign assignments.
The test makes no distributional assumptions and handles the many zero
differences (pages where both strategies score identically) naturally, since
flipping a zero changes nothing.

Usage:
    python3 -m evaluation.significance -i output/results.json -a adaptive -b text
"""

import json
import random
from collections import defaultdict

METRICS = [
    "text_similarity",
    "heading_structure",
    "list_structure",
    "table_structure",
    "code_block_score",
    "paragraph_structure",
    "word_overlap",
]

N_RESAMPLES = 100_000
SEED = 42


def paired_permutation_test(diffs: list[float], n_resamples: int = N_RESAMPLES,
                            seed: int = SEED) -> float:
    """Two-sided p-value for the mean of paired differences via sign-flipping."""
    n = len(diffs)
    if n == 0 or all(d == 0 for d in diffs):
        return 1.0
    observed = abs(sum(diffs) / n)
    rng = random.Random(seed)
    hits = 0
    for _ in range(n_resamples):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs)
        if abs(s / n) >= observed - 1e-15:
            hits += 1
    # Add-one smoothing so the estimate is never exactly zero.
    return (hits + 1) / (n_resamples + 1)


def load_paired_scores(path: str, strategy_a: str, strategy_b: str) -> dict[str, list[float]]:
    """Return per-metric lists of per-page differences (a minus b)."""
    with open(path) as f:
        data = json.load(f)
    scores: dict[tuple, dict[str, dict[str, float]]] = defaultdict(dict)
    for r in data:
        scores[(r["pdf_path"], r["page_number"])][r["strategy"]] = r["metrics"]
    diffs: dict[str, list[float]] = {m: [] for m in METRICS}
    for page, per_strategy in sorted(scores.items()):
        if strategy_a not in per_strategy or strategy_b not in per_strategy:
            continue
        for m in METRICS:
            diffs[m].append(per_strategy[strategy_a][m] - per_strategy[strategy_b][m])
    return diffs


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Paired permutation tests between two strategies")
    parser.add_argument("-i", "--input", default="output/results.json")
    parser.add_argument("-a", "--strategy-a", default="adaptive")
    parser.add_argument("-b", "--strategy-b", default="text")
    args = parser.parse_args()

    diffs = load_paired_scores(args.input, args.strategy_a, args.strategy_b)
    print(f"Paired sign-flip permutation test: {args.strategy_a} vs {args.strategy_b}")
    print(f"{'metric':22s} {'n':>3s} {'nonzero':>7s} {'mean diff':>10s} {'p':>8s}")
    for m in METRICS:
        d = diffs[m]
        nonzero = sum(1 for x in d if x != 0)
        mean = sum(d) / len(d) if d else 0.0
        p = paired_permutation_test(d)
        print(f"{m:22s} {len(d):3d} {nonzero:7d} {mean:+10.4f} {p:8.4f}")


if __name__ == "__main__":
    main()
