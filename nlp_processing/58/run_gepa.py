import re
import argparse
import unicodedata

import dspy


# =============================================================================
# 評価タスク（評価ハーネス）
#   各タスクは「質問」と「正準形の正解」を持ち、正規化した完全一致で自動採点する。
#   正解ラベルがあるので LLM-as-judge（LLM 自身に採点させる手法）不要で客観的にスコア化でき、
#   GEPA が「改善のみ採用」を厳密に判定できる。汎用プロンプトのままだと冗長な文（「日本の
#   首都は東京です。」）を返して完全一致に落ちるため、GEPA でプロンプトを自己進化させる余地がある。
# =============================================================================
DATA = [
    ("水の化学式は何ですか？", "H2O"),
    ("二酸化炭素の化学式は何ですか？", "CO2"),
    ("水の沸点は摂氏何度ですか？", "100"),
    ("太陽系の惑星の数はいくつですか？", "8"),
    ("オーストラリアの首都はどこですか？", "キャンベラ"),
    ("太陽系で最も大きい惑星は何ですか？", "木星"),
    ("金の元素記号は何ですか？", "Au"),
    ("地球の大陸の数はいくつですか？", "7"),
]


def normalize(text):
    """採点用の正規化。NFKC で全角・上下付き数字を ASCII 化（例: Ｈ₂Ｏ→h2o）し、小文字化し、
    空白と記号・句読点を除去する。日本語・英数字（化学式の数字含む）は残すので、表記揺れや
    「〜です。」などの装飾は無視しつつ、冗長な説明文は別物として弾ける。"""
    text = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"[\s　。、．，・…！!？?「」『』（）()\[\]【】〔〕:：;；'\"`*]", "", text)


class QA(dspy.Signature):
    """質問に答えてください。"""  # ← この instruction プロンプト（簡単のためプロンプトのみがハーネス対象）を GEPA が自己進化させる
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()


def metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    """GEPA 用の評価関数。スコア（1/0）に加え、外したときは日本語の自然言語フィードバックを返す。
    GEPA はこのフィードバックを反省材料にして instruction（プロンプト）を書き換える。"""
    got = getattr(pred, "answer", "")
    ok = normalize(got) == normalize(gold.answer)
    feedback = (
        "正解。"
        if ok
        else (
            f"不正解。期待する正解は厳密に「{gold.answer}」（小文字化・記号除去後の完全一致で採点）"
            f"ですが、「{got}」が返りました。余計な語・単位・文を付けず、正準形の答えだけを返してください。"
        )
    )
    return dspy.Prediction(score=1.0 if ok else 0.0, feedback=feedback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-model", type=str, default="qwen3.5:2b",
                        help="タスクを解く側（被最適化）の Ollama モデル")
    parser.add_argument("--reflection-model", type=str, default="qwen3.5:9b",
                        help="改修案（新プロンプト）を生成する反省 LLM。GEPA では強いモデルが推奨")
    parser.add_argument("--max-metric-calls", type=int, default=24,
                        help="GEPA の探索予算（評価関数の呼び出し回数）")
    parser.add_argument("--mode", type=str, default="gepa", choices=["baseline", "gepa"],
                        help="baseline: 初期プロンプトのみ評価 / gepa: GEPA で自己進化させて評価")
    args = parser.parse_args()

    # Ollama 上のローカル LLM を DSPy（LiteLLM 経由）で使う。think=False で Qwen3.5 の
    # 思考モードを無効化（CPU では思考生成だけで激遅になるため）
    student = dspy.LM(f"ollama_chat/{args.student_model}", api_base="http://localhost:11434",
                      api_key="", temperature=0.0, max_tokens=512, think=False)
    dspy.configure(lm=student)

    # 採点だけのシンプルな指標で評価器を作る（スコアの平均％を返す）
    evaluate = dspy.Evaluate(
        devset=[dspy.Example(question=q, answer=a).with_inputs("question") for q, a in DATA],
        metric=lambda gold, pred, trace=None: metric(gold, pred).score,
        num_threads=1, display_progress=False,
    )

    program = dspy.Predict(QA)  # 初期ハーネス（instruction = "質問に答えてください。"）

    baseline = evaluate(program)
    print(f"[baseline] score = {baseline.score:.1f}%  (instruction = {QA.instructions!r})")

    if args.mode == "baseline":
        raise SystemExit

    # GEPA: トラジェクトリ＋フィードバックを反省して instruction を進化させ、
    #       Pareto front で候補を選抜（= 改善のみ採用 / regression-free）する公式オプティマイザ
    reflection = dspy.LM(f"ollama_chat/{args.reflection_model}", api_base="http://localhost:11434",
                         api_key="", temperature=1.0, max_tokens=1024, think=False)
    gepa = dspy.GEPA(
        metric=metric,
        max_metric_calls=args.max_metric_calls,
        reflection_lm=reflection,
        candidate_selection_strategy="pareto",
        reflection_minibatch_size=3,
    )
    optimized = gepa.compile(program, trainset=evaluate.devset, valset=evaluate.devset)

    after = evaluate(optimized)
    print(f"[gepa] score = {after.score:.1f}%  ({baseline.score:.1f}% -> {after.score:.1f}%)")
    print("=" * 60)
    print("GEPA が進化させた最終 instruction プロンプト（簡単のためプロンプトのみがハーネス対象）:\n")
    print(optimized.signature.instructions)
