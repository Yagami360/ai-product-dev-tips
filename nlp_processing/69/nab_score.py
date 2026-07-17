"""NAB 公式スコアで検知結果を採点する。

NAB 公式スコアの考え方（[NAB 公式](https://github.com/numenta/NAB) の採点方式）:

- 正解の**異常区間の早い時点**で検知するほど高得点（scaled sigmoid で重み付け。運用では
  「異常をいち早く捕まえる」ことに価値があるため、検出の遅さがペナルティになる）
- 異常区間を 1 つも検知できなければ FN ペナルティ、異常区間の外での検知は FP ペナルティ
  （区間の終端からの距離で減衰）
- 生スコアを **0〜100 に正規化**する:
      score = 100 * (raw - null) / (perfect - null)
  null = 無検出の検出器（0 点相当）、perfect = 全ての異常区間を最速で当てた検出器（100 点相当）

アプリケーションプロファイル（誤検知と見逃しのどちらを重く見るか）:

| プロファイル | tp | fp | fn | 用途 |
|---|---|---|---|---|
| standard | 1.0 | 0.11 | 1.0 | 汎用 |
| reward_low_FP_rate | 1.0 | 0.22 | 1.0 | 誤検知のコストが高い現場 |
| reward_low_FN_rate | 1.0 | 0.11 | 2.0 | 見逃しのコストが高い現場 |

採点そのものは NAB 公式実装（nab_sweeper.py）に委譲する。
"""

from nab_sweeper import Sweeper

# NAB 公式の config/profiles.json と同じ重み
PROFILES = {
    "standard": {"tpWeight": 1.0, "fpWeight": 0.11, "fnWeight": 1.0, "tnWeight": 1.0},
    "reward_low_FP_rate": {"tpWeight": 1.0, "fpWeight": 0.22, "fnWeight": 1.0, "tnWeight": 1.0},
    "reward_low_FN_rate": {"tpWeight": 1.0, "fpWeight": 0.11, "fnWeight": 2.0, "tnWeight": 1.0},
}


def _snap_windows(timestamps, gt_windows):
    """異常区間の端点を、実在するタイムスタンプに寄せる。

    NAB 公式 Sweeper は区間の端点が timestamps に含まれる前提（timestamps.index で引く）。
    本 Tip は --downsample で間引くため端点が消えることがあるので、
    区間に含まれる最初/最後の点へ寄せる（1 点も含まなければその区間は捨てる）。
    """
    snapped = []
    for s, e in gt_windows:
        inside = [t for t in timestamps if s <= t <= e]
        if inside:
            snapped.append((inside[0], inside[-1]))
    return snapped


def _raw_score(timestamps, anomaly_scores, windows, cost_matrix):
    """NAB 公式 Sweeper で生スコアを得る（threshold=0.5 の二値検知として採点）。"""
    sweeper = Sweeper(probationPercent=0.15, costMatrix=cost_matrix)
    _, matching_row = sweeper.scoreDataSet(timestamps, anomaly_scores, list(windows), "dataset", 0.5)
    return matching_row.score


def nab_score(pred_flags, timestamps, gt_windows):
    """NAB 公式スコア（0〜100, 3 プロファイル）を返す。

    pred_flags は二値の検知フラグ。NAB は連続スコア＋しきい値を前提とするため、
    検知点を 1.0 / 非検知を 0.0 とし、しきい値 0.5 で採点する（＝二値検知そのもの）。

    正規化は NAB 公式 runner.normalize() と同じ:
        score = 100 * (raw - null) / (perfect - null),  perfect = 異常区間数 * tpWeight
    """
    windows = _snap_windows(timestamps, gt_windows)
    if not windows:
        return {name: float("nan") for name in PROFILES}

    scores = [1.0 if f else 0.0 for f in pred_flags]
    null_scores = [0.0] * len(timestamps)  # 無検出の検出器（正規化の下限）

    out = {}
    for name, cm in PROFILES.items():
        raw = _raw_score(timestamps, scores, windows, cm)
        null = _raw_score(timestamps, null_scores, windows, cm)
        perfect = len(windows) * cm["tpWeight"]  # 公式定義: 検知可能な異常区間数 × tp 重み
        denom = perfect - null
        out[name] = round(100.0 * (raw - null) / denom, 1) if denom else float("nan")
    return out
