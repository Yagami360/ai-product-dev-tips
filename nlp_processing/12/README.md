# Function calling を使用して、入力文に応じて適切な外部関数の呼び出し、外部関数の戻り値に基づく出力文を生成する

Function calling とは、OpenAI の LLM API において、ユーザーからの入力文に応じて適切な外部関数の呼び出し、外部関数の戻り値に基づく出力文の生成ができる機能。

OpenAI の LLM API が回答できないようなある特定ドメインでの質問文の場合は外部関数からの戻り値から生成した回答文を返し、OpenAI の LLM API が回答できる一般的な質問文の場合は OpenAI の LLM API での回答文を直接返すといったことができるようになる。

なお LangChain を使用する場合は、LangChain Agents の OpenAI Functions Agent を使用すれば同様の機能を実現できる

> - LangChain Agents の OpenAI Functions Agent<br>
> 「[LangChain Agents の OpenAI Functions Agent を使用して Function calling を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/12)」を使用することができる


## 使用方法

1. OpenAPI キーを設定する
    ```sh
    export OPENAI_API_KEY=dummy
    ```

1. Function calling を使用した Python コードを作成する
    ```python
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
    ```

    ポイントは、以下の通り

    - xxx

1. Python コードを実行する

    - 外部関数を使用する場合
        ```sh
        python3 run_llm.py --prompt 広島の天気について教えて
        ```

        入力文「広島の天気について教えて」は、外部関数（今回の例では、都市の天気を返す関数）を使用する必要がある（使用しない場合は、「申し訳ありませんが、私の訓練データは2022年1月までのものであり、現在の天気情報を提供することはできません。広島の現在の天気予報を知りたい場合は、天気予報サイトや気象情報アプリを確認するか、地元の気象庁のウェブサイトを参照してください。」のような回答になる）ので、外部関数の呼び出しが行われる。この時の API からのレスポンスデータは、以下のようになる

        ```sh
        resp:  {
            "id": "chatcmpl-8l9xSnfkAPGNwpFKYYozOhQ7YnCEM",
            "object": "chat.completion",
            "created": 1706250386,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": null,
                        "function_call": {
                            "name": "get_weather",
                            "arguments": "{\n\"location\": \"広島\"\n}"
                        }
                    },
                    "logprobs": null,
                    "finish_reason": "function_call"
                }
            ],
            "usage": {
                "prompt_tokens": 84,
                "completion_tokens": 18,
                "total_tokens": 102
            },
            "system_fingerprint": null
        }
        ```

        `choices.[*].message.function_call` に呼び出された Function calling が設定される。`choices.[*].message.function_call.name` に外部関数名が設定され、`choices.[*].message.function_call.arguments` に外部関数の引数の値が設定されるので、これら情報から外部関数を呼び出す。
        
        その後、外部関数の戻り値や各種外部関数情報を入力として、再度 OpenAI の Chat 用 API の呼び出しを行う。２回目のレスポンスデータは、以下のようになる

        ```sh
        second_resp:  {
            "id": "chatcmpl-8l9xTPAfYYFKs8nyJutR1h1L5ml10",
            "object": "chat.completion",
            "created": 1706250387,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "広島の天気は「晴れ」です。"
                    },
                    "logprobs": null,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 69,
                "completion_tokens": 16,
                "total_tokens": 85
            },
            "system_fingerprint": null
        }
        ```

        `choices.[*].message.content` に外部関数の戻り値から生成した出力文が返る。

    - 外部関数を使用せず通常の回答を行う場合
        ```sh
        python3 run_llm.py --prompt AIについて教えて
        ```

        入力文「AIについて教えて」は、外部関数（今回の例では、都市の天気を返す関数）を使用しなくてもいい一般的な質問文なので、外部関数の呼び出しは行われない。この時の API からのレスポンスデータは、以下のようになる。

        ```json
        resp:  {
            "id": "chatcmpl-8l9M5NyhayD48Tyuab00MYP69hvuN",
            "object": "chat.completion",
            "created": 1706248069,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "AI（人工知能）とは、人間の思考能力や認識能力、学習能力などをコンピューターシステムによって再現する技術や研究のことです。AIは、機械学習やパターン認識、自然言語処理などの技術を用いて、データから知識を獲得し、問題解決や意思決定を行うことができます。\n\nAIの応用例は多岐にわたります。例えば、自動運転車の開発、音声アシスタント（SiriやGoogleアシスタント）の実現、医療診断支援、金融取引の予測、画像認識、翻訳などがあります。また、AIは大量のデータを処理し、パターンを見つけることが得意なため、ビジネス分野やマーケティング分析、品質管理などでも活用されています。\n\nAIの技術は急速に進化しており、ディープラーニング（深層学習）やリカレントニューラルネットワークなどのニューラルネットワークモデルが注目されています。これらのモデルは、大量のデータから特徴を抽出し、学習し、予測や分類を行うことができます。\n\nただし、AIにはまだ課題も存在します。例えば、人間の感情や複雑な推論、倫理的判断などはまだ完全に再現することが難しいです。また、AIのアルゴリズムにバイアスが含まれることや、プライバシーの問題、個人情報の悪用なども懸念事項となっています。\n\nAIの研究や技術開発は現在も進んでおり、今後ますますAIが私たちの生活や社会に深く関わることが予想されます。"
                    },
                    "logprobs": null,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 77,
                "completion_tokens": 621,
                "total_tokens": 698
            },
            "system_fingerprint": null
        }
        ```

        `choices.[*].message.function_call` は存在せず、`choices.[*].message.content` に出力文が返る。

## 参考サイト

- https://qiita.com/yu-Matsu/items/12b686fe4cab343f50b3
- https://dev.classmethod.jp/articles/understand-openai-function-calling/