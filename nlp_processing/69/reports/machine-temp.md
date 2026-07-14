# 系統(a) 数値直接入力 検知レポート

- データ: NAB: realKnownCause/machine_temperature_system_failure.csv（946 点）
- 検知モデル: gemini-3.5-flash
- 評価（NAB 既知異常区間ラベル基準）: {'windows_total': 4, 'windows_detected': 2, 'window_recall': 0.5, 'false_alarms': 0, 'pa_f1': 0.662, 'n_pred': 3}

## 検出した異常点

- index=166 (2013-12-16 17:15, 値=6.44): 周囲の温度水準（約45〜93度）から極端に逸脱した一時的なスパイク低下（6.44度）
- index=808 (2014-02-08 04:15, 値=39.27): 通常水準（約80〜100度）から30度台へと持続的に低下し始めるレベルシフトの開始点
- index=823 (2014-02-09 10:15, 値=29.54): 異常な低温状態（約30度）から通常水準への急激な復帰点
