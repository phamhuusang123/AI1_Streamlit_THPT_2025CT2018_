# src/analysis.py
import numpy as np

def compute_totals(df, subjects, backend="pandas"):
    """
    Return numpy array of total scores per candidate for given subjects.
    """
    if len(subjects) == 0:
        return np.array([])

    if backend == "polars":
        # convert only selected cols to pandas to sum reliably
        try:
            pdf = df.select(subjects).to_pandas()
            totals = pdf.fillna(0).sum(axis=1).to_numpy()
            return totals
        except Exception:
            # fallback: try direct to_numpy
            try:
                arr = df.select(subjects).to_numpy()
                return np.nansum(arr, axis=1)
            except Exception:
                return np.array([])
    else:
        # pandas
        totals = df[subjects].fillna(0).sum(axis=1).to_numpy()
        return totals

def build_percentile_table(totals: np.ndarray):
    """
    Return dict {percentile: score}.
    """
    if totals.size == 0:
        return {p: 0.0 for p in range(0, 101)}
    pct_scores = np.percentile(totals, np.arange(0, 101, 1))
    return {int(p): float(s) for p, s in zip(range(0, 101), pct_scores)}

def percentile_of_score(totals: np.ndarray, score: float) -> float:
    """
    empirical percentile (0..100): percent below + 0.5*equal
    """
    n = totals.size
    if n == 0:
        return 0.0
    less = int((totals < score).sum())
    equal = int((totals == score).sum())
    pct = (less + 0.5 * equal) / n * 100.0
    return float(pct)

def rank_of_score(totals: np.ndarray, score: float) -> int:
    """
    Rank where 1 is best (highest). rank = #with score > yours + 1
    """
    return int((totals > score).sum() + 1)

def counts_at_thresholds(totals: np.ndarray, max_score=30, min_score=0):
    """
    Return list of dicts for m in [max..min]: {'moc': 'm+','count':int,'pct':float}
    """
    n = totals.size
    rows = []
    for m in range(int(max_score), int(min_score) - 1, -1):
        cnt = int((totals >= m).sum())
        pct = round(cnt / n * 100.0, 2) if n > 0 else 0.0
        rows.append({"moc": f"{m}+", "count": cnt, "pct": pct})
    return rows
