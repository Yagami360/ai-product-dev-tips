# OpenAI API の使用方法

OpenAI API は、API 経由で OpenAI が開発いている LLM モデルの推論が簡単に使用できる API サービス<br>
利用可能な言語モデルは、[OpenAI Platform](https://platform.openai.com/docs/models/overview) に記載されている。<br>
現時点（2023/08/06）では、例えば、以下の言語モデルが使用可能（他にもあるので、詳細はリンク先参照）<br>

- GPT-4<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/016e7363-1ee5-451e-89ac-43da1c7b7cf3"><br>

- GPT-3.5<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/7ef13d72-203e-40c3-8ddf-3e81f39e1532">

- GPT-3<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/5db34c90-6dc3-4f97-bbdc-2c8093074176">

- DALL·E（text-to-image モデル）<br>

## 使用方法

### 共通作業

1. OpenAI の APIキー発行
    [OpenAI Platform のページ](https://platform.openai.com/account/api-keys) から API キーを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/71ca027f-f4d2-4cde-9961-8a05da5ecf86">

OpenAI API には様々な API があるが、ここでは、[Chat機能](https://platform.openai.com/docs/api-reference/chat) のみの使用方法記載<br>
その他 API の詳細は、[API reference](https://platform.openai.com/docs/api-reference) 参照

### curl で使用する場合（Chat 機能）

1. API リクエストする<br>
    Chat 機能を使用する場合は、以下のような curl コマンドを実行する
    ```sh
    export OPENAI_API_KEY="dummy"
    curl https://api.openai.com/v1/chat/completions -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${OPENAI_API_KEY}" \
        -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "自己紹介をして下さい"}]}'
    ```

    Bearer 認証でアクセス。`model` フィールドに言語モデルを指定

1. レスポンスデータを確認する<br>
    ```json
    {
        "id": "chatcmpl-7kMZj5TU31ClLUOWrmrXZvFKuImXU",
        "object": "chat.completion",
        "created": 1691284223,
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "そうですね、今日は本当に暑いですね。 질문이 있으십니까?"
            },
            "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 16,
            "completion_tokens": 31,
            "total_tokens": 47
        }
    }
    ```

### Python から使用する場合（Chat 機能）

1. OpenAI API のライブラリをインストールする
    ```sh
    pip3 install openai
    ```

1. Python コードを作成する<br>
    Chat 機能を使用する場合は、例えば、以下のような Python コードを作成する
    ```python
    import argparse
    import openai

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--openai_api_key', type=str, default="dummuy")
        parser.add_argument('--model', type=str, default="gpt-3.5-turbo")
        parser.add_argument('--content', type=str, default="今日は天気が良いですね")
        args = parser.parse_args()

        # APIキーの設定
        openai.api_key = args.openai_api_key

        # 使用可能なモデルリスト
        print("available models: ", openai.Model.list())

        # OpenAI API 呼び出し
        try:
            response = openai.ChatCompletion.create(
                model=args.model,
                messages=[
                    {"role": "user", "content": args.content},
                ],
                # temperature=0.7,        # number or null Optional Defaults to 1 / 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
                # top_p=1,                # number or null Optional Defaults to 1 / An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both.
                # n=1,                    # integer Optional Defaults to 1 / 回答の数。3を指定すれば3つの回答を得られる。
                # stream=False,           # boolean or null Optional Defaults to falseIf set, partial message deltas will be sent, like in ChatGPT. Tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Example Python code.
                # stop=None,              # string / array / null Optional Defaults to null / トークンの生成を停止する文字列
                # max_tokens=100,         # integer Optional Defaults to inf / 生成されるレスポンスのトークンの最大数
                # presence_penalty=0,     #
                # frequency_penalty=0,    # 2.0 から 2.0 の間の数値を指定。値が低い場合、生成された文章に既に含まれている単語やフレーズが強調されすぎて、文章の多様性が低下する可能性がある。値が髙い場合、生成された文章が同じ単語やフレーズを繰り返すことが少なくなり、より多様な文章を生成することができる。
                # logit_bias={96096:20},  # {トークンID: value} で指定 / トークンの生成確率を調整するために、各トークンに対してlogit_biasを設定することができる。正の値を持つトークンは出現確率が上がり、負の値を持つトークンは出現確率が下がる。
            )
            print(f"response: {response}")
            print(f"content: {response['choices'][0]['message']['content'].strip()}")
        except Exception as e:
            print(f"Excception was occurred | {e}")
            exit(1)

        exit(0)
    ```

1. Python スクリプトを実行する
    ```sh
    python3 run_open_ai_api.py --openai_api_key=${OPENAI_API_KEY}
    ```

## OpenAI Playground

<img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/3ede4a5f-cff6-4509-880e-cbfd4f3241b2"><br>
OpenAI API には様々な LLM モデルが用意されているが、OpenAI Playground では、それぞれの LLM モデルの機能を UI ツール上で簡単に検証できる。

## 料金体系

https://openai.com/pricing

- GPT-4
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/b162ea12-f48a-4c02-9990-2039edab8079">

- GPT-3.5 Turbo
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/9be0eef6-8747-4d72-b46f-a4438e091f55">

## 参考サイト

- OpenAI 公式ドキュメント（OpenAI Platform）<br>
    https://platform.openai.com/docs/introduction/overview
