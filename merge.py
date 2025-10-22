from typing import List, Tuple, Optional
import json

from typing import List, Tuple, Optional

def nw_ref_match_flags(
    ref: List[str], whisper: List[str]
) -> List[Tuple[str, int, Optional[int]]]:
    """
    Needleman–Wunsch (global alignment) with:
      match = +1, mismatch = -1, gap = -1

    Returns:
      A list of tuples for each original token in `ref`:
        (ref_word, flag, whisper_index_or_None)
      - flag = 1 iff ref_word is aligned to an IDENTICAL word in whisper
      - whisper_index_or_None = the index in `whisper` when flag == 1, else None

    No normalization is performed.
    """
    MATCH, MISMATCH, GAP = 1, -1, -1
    n, m = len(ref), len(whisper)

    # DP score matrix and backtrace pointers: 'D' (diag), 'U' (up), 'L' (left)
    dp = [[0]*(m+1) for _ in range(n+1)]
    bt = [[None]*(m+1) for _ in range(n+1)]

    # init first row/col with gaps
    for i in range(1, n+1):
        dp[i][0] = dp[i-1][0] + GAP
        bt[i][0] = 'U'
    for j in range(1, m+1):
        dp[0][j] = dp[0][j-1] + GAP
        bt[0][j] = 'L'

    # fill
    for i in range(1, n+1):
        for j in range(1, m+1):
            score_diag = dp[i-1][j-1] + (MATCH if ref[i-1] == whisper[j-1] else MISMATCH)
            score_up   = dp[i-1][j] + GAP   # gap in whisper (ref aligned to gap)
            score_left = dp[i][j-1] + GAP   # gap in ref (whisper aligned to gap)

            best = max(score_diag, score_up, score_left)

            # tie-breaker: prefer diagonal (encourages matches), then up, then left
            if best == score_diag:
                dp[i][j] = score_diag
                bt[i][j] = 'D'
            elif best == score_up:
                dp[i][j] = score_up
                bt[i][j] = 'U'
            else:
                dp[i][j] = score_left
                bt[i][j] = 'L'

    # backtrace to build aligned sequences and track whisper indices
    aligned_ref:  List[Optional[str]] = []
    aligned_wh:   List[Optional[str]] = []
    aligned_widx: List[Optional[int]] = []

    i, j = n, m
    while i > 0 or j > 0:
        move = bt[i][j] if (i >= 0 and j >= 0) else None
        if i > 0 and j > 0 and move == 'D':
            aligned_ref.append(ref[i-1])
            aligned_wh.append(whisper[j-1])
            aligned_widx.append(j-1)
            i -= 1; j -= 1
        elif i > 0 and (j == 0 or move == 'U'):
            aligned_ref.append(ref[i-1])
            aligned_wh.append(None)
            aligned_widx.append(None)
            i -= 1
        else:  # move == 'L'
            aligned_ref.append(None)
            aligned_wh.append(whisper[j-1])
            aligned_widx.append(j-1)
            j -= 1

    aligned_ref.reverse()
    aligned_wh.reverse()
    aligned_widx.reverse()

    # produce per-original-ref output
    result: List[Tuple[str, int, Optional[int]]] = []
    for r_tok, w_tok, w_idx in zip(aligned_ref, aligned_wh, aligned_widx):
        if r_tok is None:
            continue
        if w_tok is not None and r_tok == w_tok:
            result.append((r_tok, 1, w_idx))
        else:
            result.append((r_tok, 0, None))
    return result

with open('compareOne.json', 'r', encoding='utf-8') as f1:
    dataOne = json.load(f1)
    ref = dataOne['ref']
    ref_id = dataOne['ref_id']
with open('compareTwo.json', 'r', encoding='utf-8') as f2:
    dataTwo = json.load(f2)
    whisper_list_word = dataTwo['whisper_list_word']
    whisper_time_stamp = dataTwo["whisper_time_stamp"]


merge_result = []
for i, word in enumerate(nw_ref_match_flags(ref, whisper_list_word)):
    if word[1] == 1:
        merge_result.append({"word": word[0], "idx_w": ref_id[i][1][0], "idx_s": ref_id[i][1][1], "has_timestamp": True, "start": whisper_time_stamp[word[2]]["start"], "end": whisper_time_stamp[word[2]]["end"]})

    else:
        merge_result.append({"word": word[0], "idx_w": ref_id[i][1][0], "idx_s": ref_id[i][1][1],"has_timestamp": False, "start": None, "end": None})

with open('compare_result.json', 'w', encoding='utf-8') as f:
    json.dump(merge_result, f, indent=2)
