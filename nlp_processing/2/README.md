# 【Python】 LangChain Model I/O を使用して OpenAI API の LLM モデルから応答文を得る

## 使用方法

1. LangChain の Python ライブラリをインストールする
    ```sh
    pip3 install langchain
    ```

1. OpenAI の APIキーを発行する<br>
    [OpenAI Platform のページ](https://platform.openai.com/account/api-keys) から API キーを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/71ca027f-f4d2-4cde-9961-8a05da5ecf86">

1. LangChain を使用した Python コードを作成する<br>
    - `run_langchain.py`
        ```python
        import argparse
        from langchain.llms import OpenAI

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--prompt', type=str, default="今日は天気が良いですね")
            args = parser.parse_args()

            # モデル定義
            llm = OpenAI(
                openai_api_key=args.openai_api_key,
                temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print("llm: ", llm)

            # LLM推論実行
            try:
                response = llm(prompt=args.prompt)
                print(f"response: {response}")
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

1. Python スクリプトを実行する
    ```sh
    python3 run_langchain.py --openai_api_key=${OPENAI_API_KEY}
    ```

## 参加サイト
- https://python.langchain.com/docs/modules/model_io/
- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_models
- https://qiita.com/kzkymn/items/a72796c89ffc696034c8
