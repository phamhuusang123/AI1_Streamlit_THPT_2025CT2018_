# src/conversion.py
import numpy as np

def convert_score_via_percentile(src_table: dict, dst_table: dict, score_src: float) -> float:
    """
    Convert score_src from source-percentile-table to equivalent score in dst_table.
    Uses linear interpolation.
    """
    p_src = np.array(sorted(src_table.keys()))
    s_src = np.array([src_table[int(p)] for p in p_src])

    p_dst = np.array(sorted(dst_table.keys()))
    s_dst = np.array([dst_table[int(p)] for p in p_dst])

    if score_src <= s_src.min():
        pct = 0.0
    elif score_src >= s_src.max():
        pct = 100.0
    else:
        pct = float(np.interp(score_src, s_src, p_src))

    score_dst = float(np.interp(pct, p_dst, s_dst))
    return score_dst
