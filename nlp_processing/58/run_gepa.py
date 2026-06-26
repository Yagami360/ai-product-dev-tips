import re
import argparse
import unicodedata

import dspy


# =============================================================================
# 評価タスク（評価ハーネス）
#   各タスクは「質問」と「正準形の正解」を持ち、正規化した完全一致で自動採点する。
#   正解ラベルがあるので LLM-as-judge（LLM 自身に採点させる手法）不要で客観的にスコア化でき、
#   GEPA が「改善のみ採用」を厳密に判定できる。汎用プロンプトのままだと冗長な文（"The capital
#   is Canberra."）を返して完全一致に落ちるため、GEPA でプロンプトを自己進化させる余地がある。
# =============================================================================
DATA = [
    ("What is the chemical formula of water?", "H2O"),
    ("What is the chemical formula of carbon dioxide?", "CO2"),
    ("What is the boiling point of water in Celsius?", "100"),
    ("How many planets are in the Solar System?", "8"),
    ("What is the capital of Australia?", "Canberra"),
    ("What is the largest planet in the Solar System?", "Jupiter"),
    ("What is the chemical symbol for gold?", "Au"),
    ("How many continents are there on Earth?", "7"),
]


def normalize(text):
    """採点用の正規化。NFKC で上下付き・全角数字を ASCII 化（例: H₂O→H2O）してから
    小文字化し英数字以外を除去する。句読点・記号・余分な空白の差は無視する。"""
    text = unicodedata.normalize("NFKC", text or "")
    return re.sub(r"[^a-z0-9]", "", text.lower())


class QA(dspy.Signature):
    """Answer the question."""  # ← この instruction（ハーネス）を GEPA が自己進化させる
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()


def metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    """GEPA 用の評価関数。スコア（1/0）に加え、外したときは自然言語フィードバックを返す。
    GEPA はこのフィードバックを反省材料にして instruction（プロンプト）を書き換える。"""
    got = getattr(pred, "answer", "")
    ok = normalize(got) == normalize(gold.answer)
    feedback = (
        "Correct."
        if ok
        else (
            f"Wrong. Expected exactly {gold.answer!r} (exact match after lowercasing and "
            f"removing non-alphanumerics); got {got!r}. "
            f"Return ONLY the canonical answer, with no extra words, units, or sentences."
        )
    )
    return dspy.Prediction(score=1.0 if ok else 0.0, feedback=feedback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-model", type=str, default="qwen3.5:2b",
                        help="タスクを解く側（被最適化）の Ollama モデル")
    parser.add_argument("--reflection-model", type=str, default="qwen3.5:9b",
                        help="改修案（新プロンプト）を生成する反省 LM。GEPA では強いモデルが推奨")
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

    program = dspy.Predict(QA)  # 初期ハーネス（instruction = "Answer the question."）

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
    print("GEPA が進化させた最終 instruction（ハーネス）:\n")
    print(optimized.signature.instructions)
