import json
import os
import argparse
import openai


def get_weather(location):
    if location in ["東京", "Tokyo"]:
        weather = "曇り"
    elif location in ["広島", "Hiroshima"]:
        weather = "晴れ"
    else:
        weather = "不明"

    resp = [
        {"天気": weather}
    ]

    # Function calling での外部関数は、json データで戻り値を返す必要あり
    return json.dumps(resp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo")
    parser.add_argument('--prompt', type=str, default="広島の天気を教えて")
    args = parser.parse_args()

    # Function calling で呼び出す関数リストの定義
    functions = [
        {
            "name": "get_weather",
            "description": "都市の天気を取得する",
            "parameters": {
                "type": "object",
                "properties": {
                    # 関数の引数（今回の例では location 引数）についての情報を記述
                    "location": {
                        "type": "string",
                        "description": "天気を知りたい都市名を入力してください",
                    },
                },
                "required": ["location"],
            },
        }
    ]

    # OpenAPI の Chat 用 API 呼び出し
    try:
        resp = openai.ChatCompletion.create(
            model=args.model,
            messages=[
                {"role": "user", "content": args.prompt},
            ],
            functions=functions,    # Function calling で呼び出す関数リストを指定
            function_call="auto",   # 
        )
        print("resp: ", json.dumps(resp, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Excception was occurred | {e}")
        exit(1)

    # Function calling で呼び出すと判断された場合
    if resp["choices"][0]["message"].get("function_call"):
        print("[Function calling を呼び出すと判断されました]")

        # Function calling で呼び出すと判断された関数名とその関数の引数値
        func_name = resp["choices"][0]["message"]["function_call"]["name"]
        func_args = json.loads(resp["choices"][0]["message"]["function_call"]["arguments"])
        print("func_name: ", func_name)
        print("func_args: ", func_args)

        # 外部関数を実行
        if func_name == "get_weather":
            func_resp = get_weather(
                location=func_args.get("location"),
            )

        # 外部関数の戻り値や各種外部関数情報を元に再度 OpenAI の Chat 用 API を呼び出し、出力文を生成する
        try:
            second_resp = openai.ChatCompletion.create(
                model=args.model,
                messages=[
                    {"role": "user", "content": args.prompt},
                    resp["choices"][0]["message"],
                    # function_call で呼び出された関数の情報をおくる
                    {
                        "role": "function",
                        "name": func_name,
                        "content": func_resp,
                    },
                ],
            )
            print("second_resp: ", json.dumps(second_resp, indent=4, ensure_ascii=False))
            print("回答:\n", second_resp["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"Excception was occurred | {e}")
            exit(1)

    # Function calling で呼び出すと判断されなかった場合は、LLM での回答を表示
    else:
        print("[Function calling を呼び出すと判断されませんでした]")
        print("回答:\n", resp["choices"][0]["message"]["content"])

    exit(0)
