"""
======================================================
Word-Level and Sentence-Level Timestamp Alignment Tool
======================================================

Purpose:
    - Align reference text tokens and Whisper ASR tokens using
      the Needleman–Wunsch global alignment algorithm.
    - Fill missing timestamps for unaligned words by interpolation.
    - Aggregate word timestamps into sentence-level timestamps.

Inputs (from Get_lists.py):
    - list_ref:  cleaned reference words (flat list)
    - list_id:   [(word, (word_index, sentence_index)), ...]
    - whisper:   cleaned Whisper words (flat list)
    - whisper_wordtimestamp: [{"word": ..., "start": ..., "end": ...}, ...]

Outputs:
    - checkaudio.json:
        JSON file containing timestamps per sentence with
        fields: {"start": ..., "end": ..., "text": ...}

Author: (your name)
Date: (today’s date)
"""

from typing import List, Tuple, Optional
from Get_lists import list_ref, list_id, whisper_wordtimestamp, whisper
import json


# ============================================================
# 1. Needleman–Wunsch alignment between ref and whisper tokens
# ============================================================

def nw_ref_match_flags(
    ref: List[str], whisper: List[str]
) -> List[Tuple[str, int, Optional[int]]]:
    """
    Perform Needleman–Wunsch (global) alignment between `ref` and `whisper`.

    Scoring:
        match = +1, mismatch = -1, gap = -1

    Returns:
        A list of tuples (ref_word, flag, whisper_index_or_None):
            - flag = 1  → word matches exactly
            - flag = 0  → word not aligned / mismatched
            - whisper_index_or_None: index of aligned whisper word, if any

    Notes:
        - No normalization is applied here; assume pre-cleaned input.
        - Diagonal preference ensures stable alignment for speech data.
    """
    MATCH, MISMATCH, GAP = 1, -1, -1
    n, m = len(ref), len(whisper)

    # Initialize DP matrices
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    bt = [[None] * (m + 1) for _ in range(n + 1)]  # 'D', 'U', 'L'

    # Initialize first row and column (gap penalties)
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + GAP
        bt[i][0] = 'U'
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + GAP
        bt[0][j] = 'L'

    # Fill dynamic programming table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            score_diag = dp[i - 1][j - 1] + (MATCH if ref[i - 1] == whisper[j - 1] else MISMATCH)
            score_up = dp[i - 1][j] + GAP
            score_left = dp[i][j - 1] + GAP

            best = max(score_diag, score_up, score_left)

            # Tie-breaking priority: diagonal > up > left
            if best == score_diag:
                dp[i][j], bt[i][j] = score_diag, 'D'
            elif best == score_up:
                dp[i][j], bt[i][j] = score_up, 'U'
            else:
                dp[i][j], bt[i][j] = score_left, 'L'

    # Backtrace to reconstruct alignment
    aligned_ref, aligned_wh, aligned_widx = [], [], []
    i, j = n, m
    while i > 0 or j > 0:
        move = bt[i][j] if (i >= 0 and j >= 0) else None
        if i > 0 and j > 0 and move == 'D':
            aligned_ref.append(ref[i - 1])
            aligned_wh.append(whisper[j - 1])
            aligned_widx.append(j - 1)
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or move == 'U'):
            aligned_ref.append(ref[i - 1])
            aligned_wh.append(None)
            aligned_widx.append(None)
            i -= 1
        else:  # move == 'L'
            aligned_ref.append(None)
            aligned_wh.append(whisper[j - 1])
            aligned_widx.append(j - 1)
            j -= 1

    aligned_ref.reverse()
    aligned_wh.reverse()
    aligned_widx.reverse()

    # Build result flags per reference token
    result = []
    for r_tok, w_tok, w_idx in zip(aligned_ref, aligned_wh, aligned_widx):
        if r_tok is None:
            continue
        if w_tok is not None and r_tok == w_tok:
            result.append((r_tok, 1, w_idx))
        else:
            result.append((r_tok, 0, None))
    return result


# Run alignment between reference and Whisper words
needleman_result = nw_ref_match_flags(list_ref, whisper)


# ============================================================
# 2. Create word-level timestamps (aligned + interpolated)
# ============================================================

timestamp_word_level = []

for i, item in enumerate(list_id):
    word, (w_idx, s_idx) = item
    matched_flag, matched_whisper_idx = needleman_result[i][1], needleman_result[i][2]

    if matched_flag == 1:
        # Word directly aligned with Whisper token
        ts = whisper_wordtimestamp[matched_whisper_idx]
        timestamp_word_level.append({
            "word": word,
            "w_idx": w_idx,
            "s_idx": s_idx,
            "has_timestamp": True,
            "start": ts["start"],
            "end": ts["end"],
        })
    else:
        # Word not aligned → mark as missing timestamp
        timestamp_word_level.append({
            "word": word,
            "w_idx": w_idx,
            "s_idx": s_idx,
            "has_timestamp": False,
            "start": None,
            "end": None,
        })


# ============================================================
# 3. Interpolate timestamps for consecutive missing words
# ============================================================

consecutive_nulls_idx = []
i = 0
while i < len(timestamp_word_level):
    start = i
    end = i
    if not timestamp_word_level[i]["has_timestamp"]:
        while i + 1 < len(timestamp_word_level) and not timestamp_word_level[i + 1]["has_timestamp"]:
            i += 1
            end = i
        consecutive_nulls_idx.append((start, end))
    i += 1

# Fill missing timestamps using interpolation
for first_null, final_null in consecutive_nulls_idx:
    if first_null > 0 and final_null < len(timestamp_word_level) - 1:
        start_time = timestamp_word_level[first_null - 1]["end"]
        end_time = timestamp_word_level[final_null + 1]["start"]

        number_nulls = final_null - first_null + 1
        gap = (end_time - start_time) / number_nulls

        for j in range(number_nulls):
            word_obj = timestamp_word_level[first_null + j]
            word_obj["has_timestamp"] = True
            word_obj["start"] = start_time + j * gap
            word_obj["end"] = start_time + (j + 1) * gap


# ============================================================
# 4. Group words by sentence index
# ============================================================

words_in_the_same_sentence = []
current_sentence = []
current_s_idx = 0

for word in timestamp_word_level:
    if word["s_idx"] == current_s_idx:
        current_sentence.append(word)
    else:
        words_in_the_same_sentence.append(current_sentence)
        current_s_idx += 1
        current_sentence = [word]

if current_sentence:
    words_in_the_same_sentence.append(current_sentence)


# ============================================================
# 5. Derive sentence-level timestamps
# ============================================================

timestamp_sentence_level = []
for words in words_in_the_same_sentence:
    sentence_text = " ".join([w["word"] for w in words])
    first_non_null = next((w for w in words if w["has_timestamp"]), None)
    final_non_null = next((w for w in reversed(words) if w["has_timestamp"]), None)

    if not first_non_null or not final_non_null:
        start = end = None
    else:
        start = round(first_non_null["start"], 2)
        end = round(final_non_null["end"], 2)

    timestamp_sentence_level.append({"start": start, "end": end, "text": sentence_text})
    print(f"start: {str(start):<6} - end: {str(end):<6} | {sentence_text}")


# ============================================================
# 6. Save results
# ============================================================

with open("checkaudio.json", "w", encoding="utf-8") as file:
    json.dump(timestamp_sentence_level, file, indent=2)
