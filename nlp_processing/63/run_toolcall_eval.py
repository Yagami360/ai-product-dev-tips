import argparse

import ollama
from deepeval.models import OllamaModel
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall, ToolCallParams


# =============================================================================
# エージェントが使えるツール（関数）定義
#   OpenAI 互換の function-calling スキーマ。Ollama の chat(tools=...) に渡すと、
#   モデルが「どのツールを・どんな引数で呼ぶか」を tool_calls として返す。
# =============================================================================
TOOLS = [
    {"type": "function", "function": {
        "name": "get_weather", "description": "指定した都市の現在の天気を取得する",
        "parameters": {"type": "object", "properties": {
            "city": {"type": "string", "description": "都市名（例: 東京）"}}, "required": ["city"]}}},
    {"type": "function", "function": {
        "name": "set_timer", "description": "指定した秒数のタイマーをセットする",
        "parameters": {"type": "object", "properties": {
            "seconds": {"type": "integer", "description": "タイマーの秒数"}}, "required": ["seconds"]}}},
    {"type": "function", "function": {
        "name": "send_email", "description": "メールを送信する",
        "parameters": {"type": "object", "properties": {
            "to": {"type": "string", "description": "宛先メールアドレス"},
            "subject": {"type": "string", "description": "件名"}}, "required": ["to", "subject"]}}},
    {"type": "function", "function": {
        "name": "search_flights", "description": "出発地・目的地・日付から航空便を検索する",
        "parameters": {"type": "object", "properties": {
            "origin": {"type": "string", "description": "出発地"},
            "destination": {"type": "string", "description": "目的地"},
            "date": {"type": "string", "description": "日付（YYYY-MM-DD）"}}, "required": ["origin", "destination", "date"]}}},
]


# =============================================================================
# 評価データ（ゴールデンタスク集）
#   各ケースは「ユーザー発話」と「正解のツール呼び出し（name + 引数）」を持つ。
#   name=None のケースは「どのツールも呼ぶべきでない（無関係）」を表す（BFCL の irrelevance）。
# =============================================================================
CASES = [
    {"query": "東京の天気を教えて", "name": "get_weather", "args": {"city": "東京"}},
    {"query": "大阪の天気はどう？", "name": "get_weather", "args": {"city": "大阪"}},
    {"query": "300 秒のタイマーをセットして", "name": "set_timer", "args": {"seconds": 300}},
    {"query": "tanaka@example.com に件名「会議の件」でメールを送って",
     "name": "send_email", "args": {"to": "tanaka@example.com", "subject": "会議の件"}},
    {"query": "羽田から札幌へ、2026-07-01 の便を探して",
     "name": "search_flights", "args": {"origin": "羽田", "destination": "札幌", "date": "2026-07-01"}},
    {"query": "ニューヨークの天気を教えて", "name": "get_weather", "args": {"city": "ニューヨーク"}},
    {"query": "ありがとう、助かったよ", "name": None, "args": {}},  # 無関係: ツールを呼ぶべきでない
]


def predict_tool_calls(model, query):
    """Ollama のツール呼び出しでモデルにツールを選ばせ、DeepEval の ToolCall のリストに変換する。
    ツールを呼ばなかった場合は空リスト。think=False で CPU 高速化、temperature=0 で決定的に。"""
    resp = ollama.chat(
        model=model, messages=[{"role": "user", "content": query}],
        tools=TOOLS, think=False, options={"temperature": 0.0},
    )
    calls = resp["message"].get("tool_calls") or []
    return [ToolCall(name=c["function"]["name"], input_parameters=dict(c["function"].get("arguments") or {}))
            for c in calls]


def expected_tool_calls(case):
    """正解のツール呼び出しを DeepEval の ToolCall のリストにする。無関係ケースは空リスト。"""
    if case["name"] is None:
        return []
    return [ToolCall(name=case["name"], input_parameters=case["args"])]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="qwen3.5:4b",
                        help="評価対象のエージェント（ツール呼び出しを行う）Ollama モデル")
    args = parser.parse_args()

    # DeepEval の ToolCorrectnessMetric（ツール呼び出し評価専用・決定論的）。
    #   expected_tools と tools_called を BFCL の AST 照合に相当する方式で突き合わせる。
    #   include_reason=False かつ model にローカルモデルを渡すことで、採点に LLM を使わない
    #   （スコア計算自体は決定論的で、reason 生成のときだけ LLM が必要になるため）。
    judge = OllamaModel(model=args.model, base_url="http://localhost:11434", temperature=0)
    name_metric = ToolCorrectnessMetric(model=judge, include_reason=False)  # ツール名のみ照合
    args_metric = ToolCorrectnessMetric(  # 引数まで完全一致で照合
        model=judge, include_reason=False,
        evaluation_params=[ToolCallParams.INPUT_PARAMETERS], should_exact_match=True)

    print(f"=== ツール呼び出し精度評価（DeepEval ToolCorrectnessMetric / BFCL 方式 AST 照合）  model = {args.model} ===")
    n_relevant = sel_ok = full_ok = 0          # 関連ケース: ツール選択正答数 / 完全一致数
    n_irrelevant = irr_ok = 0                   # 無関係ケース: 正しく「呼ばない」を選べた数
    for case in CASES:
        called = predict_tool_calls(args.model, case["query"])
        expected = expected_tool_calls(case)
        tc = LLMTestCase(input=case["query"], actual_output="(tool call)",
                         tools_called=called, expected_tools=expected)
        name_metric.measure(tc)
        args_metric.measure(tc)
        called_str = [f"{c.name}{c.input_parameters}" for c in called] or "（呼ばない）"

        if case["name"] is None:
            n_irrelevant += 1
            ok = name_metric.score == 1.0       # 期待は空。呼ばなければ 1.0
            irr_ok += ok
            print(f"\nQ: {case['query']}")
            print(f"  [無関係] {'OK（呼ばない）' if ok else f'NG（誤って呼んだ: {called_str}）'}")
        else:
            n_relevant += 1
            selected = name_metric.score == 1.0
            matched = args_metric.score == 1.0
            sel_ok += selected
            full_ok += matched
            print(f"\nQ: {case['query']}")
            print(f"  正解: {case['name']}{case['args']}")
            print(f"  予測: {called_str}")
            print(f"  ツール選択: {'○' if selected else '×'}  / 引数まで完全一致: {'○' if matched else '×'}")

    print("\n" + "=" * 60)
    print(f"ツール選択正答率: {sel_ok}/{n_relevant}  ({100*sel_ok/n_relevant:.0f}%)")
    print(f"完全一致正答率（name+引数）: {full_ok}/{n_relevant}  ({100*full_ok/n_relevant:.0f}%)")
    print(f"無関係検出（呼ばない）正答率: {irr_ok}/{n_irrelevant}")
    print("→ ツール選択・引数抽出・無関係検出のどこで失敗するかが、action 評価の診断になる")
