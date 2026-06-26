import re
import argparse
import unicodedata

import dspy


# =============================================================================
# 評価タスク（評価ハーネス）
#   各タスクは「質問」と「正準形の正解」を持ち、正規化した完全一致で自動採点する。
#   正解ラベルがあるので LLM-as-judge（LLM 自身に採点させる手法）不要で客観的にスコア化でき、
#   MIPROv2 が「instruction + few-shot を変えてスコアが上がるか」をベイズ最適化で探索できる。
#   汎用プロンプトのままだと冗長な文（「日本の首都は東京です。」）を返して完全一致に落ちるため、
#   instruction と few-shot を最適化する余地がある。
# =============================================================================
DATA = [
    ("水の化学式は何ですか？", "H2O"),
    ("二酸化炭素の化学式は何ですか？", "CO2"),
    ("食塩（塩化ナトリウム）の化学式は何ですか？", "NaCl"),
    ("水の沸点は摂氏何度ですか？", "100"),
    ("水の凝固点は摂氏何度ですか？", "0"),
    ("太陽系の惑星の数はいくつですか？", "8"),
    ("地球の大陸の数はいくつですか？", "7"),
    ("一週間は何日ですか？", "7"),
    ("オーストラリアの首都はどこですか？", "キャンベラ"),
    ("カナダの首都はどこですか？", "オタワ"),
    ("太陽系で最も大きい惑星は何ですか？", "木星"),
    ("地球から最も近い恒星は何ですか？", "太陽"),
    ("金の元素記号は何ですか？", "Au"),
    ("鉄の元素記号は何ですか？", "Fe"),
    ("光の三原色のうち赤・緑ともう一つは何ですか？", "青"),
    ("日本の最高峰の山は何ですか？", "富士山"),
]


def normalize(text):
    """採点用の正規化。NFKC で全角・上下付き数字を ASCII 化（例: Ｈ₂Ｏ→h2o）し、小文字化し、
    空白と記号・句読点を除去する。日本語・英数字（化学式の数字含む）は残すので、表記揺れや
    「〜です。」などの装飾は無視しつつ、冗長な説明文は別物として弾ける。"""
    text = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"[\s　。、．，・…！!？?「」『』（）()\[\]【】〔〕:：;；'\"`*]", "", text)


class QA(dspy.Signature):
    """質問に答えてください。"""  # ← この instruction プロンプト（簡単のためプロンプトのみがハーネス対象）を MIPROv2 が最適化する
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()


def metric(gold, pred, trace=None, *args, **kwargs):
    """MIPROv2 用の評価関数。正規化した完全一致なら 1（True）、外したら 0（False）を返す。
    MIPROv2 はこのスコアを目的関数に、instruction と few-shot の組み合わせをベイズ最適化で探索する。
    GEPA と違い自然言語フィードバックは不要で、スカラの良し悪しだけで動く。"""
    return normalize(getattr(pred, "answer", "")) == normalize(gold.answer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-model", type=str, default="qwen3.5:2b",
                        help="タスクを解く側（被最適化）の Ollama モデル")
    parser.add_argument("--prompt-model", type=str, default="qwen3.5:9b",
                        help="instruction（指示文）の候補を提案する LLM。強いモデルが推奨")
    parser.add_argument("--auto", type=str, default="light", choices=["light", "medium", "heavy"],
                        help="MIPROv2 の探索強度（light < medium < heavy）")
    parser.add_argument("--mode", type=str, default="mipro", choices=["baseline", "mipro"],
                        help="baseline: 初期プロンプトのみ評価 / mipro: MIPROv2 で最適化して評価")
    args = parser.parse_args()

    # Ollama 上のローカル LLM を DSPy（LiteLLM 経由）で使う。think=False で Qwen3.5 の
    # 思考モードを無効化（CPU では思考生成だけで激遅になるため）
    task_lm = dspy.LM(f"ollama_chat/{args.task_model}", api_base="http://localhost:11434",
                      api_key="", temperature=0.0, max_tokens=512, think=False)
    dspy.configure(lm=task_lm)

    devset = [dspy.Example(question=q, answer=a).with_inputs("question") for q, a in DATA]

    # 採点だけのシンプルな評価器（スコアの平均％を返す）
    evaluate = dspy.Evaluate(devset=devset, metric=metric, num_threads=1, display_progress=False)

    program = dspy.Predict(QA)  # 初期ハーネス（instruction = "質問に答えてください。"、few-shot なし）

    baseline = evaluate(program)
    print(f"[baseline] score = {baseline.score:.1f}%  (instruction = {QA.instructions!r}, demos = 0)")

    if args.mode == "baseline":
        raise SystemExit

    # MIPROv2: instruction（指示文）と few-shot（デモ）を同時にベイズ最適化する DSPy のオプティマイザ。
    #   prompt_model が instruction 候補を提案し、task_model が実際にタスクを解く。
    #   ① trainset から成功トラジェクトリを bootstrap して few-shot 候補を作り、
    #   ② instruction 候補を生成し、③ 両者の組み合わせをベイズ最適化で探索する。
    prompt_lm = dspy.LM(f"ollama_chat/{args.prompt_model}", api_base="http://localhost:11434",
                        api_key="", temperature=1.0, max_tokens=1024, think=False)
    mipro = dspy.MIPROv2(
        metric=metric,
        prompt_model=prompt_lm,   # instruction を提案する LLM（強いモデル推奨）
        task_model=task_lm,       # タスクを解く LLM（被最適化）
        auto=args.auto,           # 探索強度のプリセット
        num_threads=1,
    )
    optimized = mipro.compile(
        program, trainset=devset, valset=devset,
        max_bootstrapped_demos=2, max_labeled_demos=2,
    )

    after = evaluate(optimized)
    print(f"[mipro] score = {after.score:.1f}%  ({baseline.score:.1f}% -> {after.score:.1f}%)")
    print("=" * 60)
    print("MIPROv2 が最適化した instruction プロンプト:\n")
    print(optimized.signature.instructions)
    print("\n" + "=" * 60)
    print(f"MIPROv2 が選んだ few-shot デモ（{len(optimized.demos)} 件）:\n")
    for i, demo in enumerate(optimized.demos):
        print(f"[demo {i}] Q: {demo.get('question', '')}  ->  A: {demo.get('answer', '')}")
