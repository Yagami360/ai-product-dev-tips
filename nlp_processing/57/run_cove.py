import re
import argparse

import ollama


def chat(model, system_prompt, user_prompt, temperature=0.0, num_predict=512):
    """Ollama のローカル LLM を呼び出して応答文を返す

    Qwen3.5 系は思考モード（thinking）がデフォルト ON で、CPU では膨大な思考生成で
    レイテンシが激増する。CoVe の各ステップは簡潔な事実回答が欲しいので think=False で無効化する。
    """
    resp = ollama.chat(
        model=model,
        think=False,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": temperature, "num_predict": num_predict},
    )
    return resp["message"]["content"].strip()


# ---------------------------------------------------------------
# CoVe の 4 ステップ
# ---------------------------------------------------------------
def step1_baseline_response(model, question):
    """Step 1. Generate Baseline Response（初期回答の生成）"""
    system = "あなたは事実に基づいて簡潔に回答するアシスタントです。"
    return chat(model, system, question)


def step2_plan_verifications(model, question, baseline, max_questions=8):
    """Step 2. Plan Verifications（初期回答の事実確認用の検証質問を計画する）"""
    system = (
        "あなたは事実検証のエキスパートです。"
        "与えられた質問と回答に含まれる個々の事実を検証するための、"
        "短く独立した検証質問を作成してください。"
        "1 行に 1 つの質問のみを出力し、番号・記号・前置きは付けないこと。"
        "同じ質問を繰り返さないこと。"
    )
    user = (
        f"# 元の質問\n{question}\n\n"
        f"# 検証対象の回答\n{baseline}\n\n"
        "# 指示\n上記の回答に含まれる事実を検証するための質問を列挙してください。"
    )
    text = chat(model, system, user)
    # 行頭の箇条書き記号・番号（"1. " "1) " "- " "・" など）のみを除去する
    # （"1964年..." の年号を消さないよう、strip ではなく行頭パターンのみを対象にする）
    questions = [re.sub(r"^\s*(?:[-*・]|\d+[.)、])\s*", "", line).strip() for line in text.splitlines()]
    # 重複除去（順序保持）と件数上限。小さいモデルは同じ質問を大量に繰り返すことがあり、
    # それをそのまま factored で回答すると無駄な LLM 呼び出し（＝レイテンシ）が増えるため。
    unique = list(dict.fromkeys(q for q in questions if q))
    return unique[:max_questions]


def step3_execute_verifications_factored(model, verification_questions):
    """Step 3. Execute Verifications（factored 方式: 各検証質問を独立したプロンプトで回答する）

    factored 方式では、各検証質問を「初期回答を含まない」独立したプロンプトで回答させる。
    これにより、初期回答に含まれる誤り（ハルシネーション）をそのままコピーすることを防ぐ。
    """
    system = "あなたは事実に基づいて簡潔に回答するアシスタントです。わからない場合は「不明」と答えてください。"
    qa_pairs = []
    for q in verification_questions:
        # 各質問は独立したプロンプト（初期回答を文脈に含めない）で回答させる
        answer = chat(model, system, q)
        qa_pairs.append((q, answer))
    return qa_pairs


def step4_final_verified_response(model, question, baseline, qa_pairs):
    """Step 4. Generate Final Verified Response（検証結果を反映した最終回答の生成）"""
    system = (
        "あなたは事実検証の結果を踏まえて回答を修正するアシスタントです。"
        "検証結果と矛盾する箇所は訂正し、検証で確認できなかった内容は削除してください。"
    )
    verifications = "\n".join([f"- Q: {q}\n  A: {a}" for q, a in qa_pairs])
    user = (
        f"# 元の質問\n{question}\n\n"
        f"# 初期回答\n{baseline}\n\n"
        f"# 検証結果\n{verifications}\n\n"
        "# 指示\n検証結果を踏まえて、事実として正しい内容のみを含む最終回答を作成してください。"
    )
    return chat(model, system, user)


def answer_with_cove(model, question, verbose=False):
    """CoVe（factored 方式）でハルシネーションを低減した回答を生成する"""
    baseline = step1_baseline_response(model, question)
    verification_questions = step2_plan_verifications(model, question, baseline)
    qa_pairs = step3_execute_verifications_factored(model, verification_questions)
    final = step4_final_verified_response(model, question, baseline, qa_pairs)

    if verbose:
        print("=" * 60)
        print("[Step 1] Baseline Response:\n", baseline)
        print("-" * 60)
        print("[Step 2] Verification Questions:")
        for q in verification_questions:
            print("  -", q)
        print("-" * 60)
        print("[Step 3] Verification Answers (factored):")
        for q, a in qa_pairs:
            print(f"  Q: {q}\n  A: {a}")
        print("-" * 60)
        print("[Step 4] Final Verified Response:\n", final)
        print("=" * 60)

    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="qwen3.5:2b", help="Ollama のモデル名。GPU 不要の軽量モデルなら qwen3.5:2b 等")
    parser.add_argument("--prompt", type=str, default=None, help="指定した場合は単発実行。未指定の場合は対話モード")
    parser.add_argument("--mode", type=str, default="cove", choices=["baseline", "cove"], help="baseline: CoVe なし / cove: CoVe あり")
    parser.add_argument("--verbose", action="store_true", help="CoVe の中間ステップを表示する")
    args = parser.parse_args()

    def respond(question):
        if args.mode == "baseline":
            return step1_baseline_response(args.model, question)
        return answer_with_cove(args.model, question, verbose=args.verbose)

    if args.prompt is not None:
        # 単発実行
        print(respond(args.prompt))
    else:
        # 対話モード（簡易チャットアプリ）
        print(f"CoVe チャット（mode={args.mode}, model={args.model}）。終了するには 'exit' を入力。")
        while True:
            try:
                question = input("\nYou> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if question.lower() in ("exit", "quit"):
                break
            if not question:
                continue
            print("\nAI>", respond(question))
