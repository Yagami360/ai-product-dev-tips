# 【Python】LangChain Memory を使用して LLM へのプロンプトや応答文の履歴を保持し、過去の応答履歴を反映した出力を得る

<img width="788" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/6a1c7a5b-4a2e-4841-9819-6323af8b6fca"><br>

LLM へのプロンプトや応答文の履歴を保持したり、Chains や Agents 内部における状態保持をする機能。
LLM へのプロンプトや応答文の履歴を保持することで、それまでの記憶を反映した会話ができるようになる

- Chat Message History<br>
    Chat の履歴データ（History）を管理する機能。<br>
    具体的には、HumanMessages や AIMessages を保存し、それらをすべて取得するための便利なメソッドを提供。
    チェーンの外でメモリを管理する場合は、このクラスを直接使用する。

<!--
- Simple Memory<br>
    xxx
-->

- Buffer Memory<br>
    Chains や Agents 間で履歴データを共有するためのメモリ機能。<br>
    Chains で実行した LLM へのプロンプトや応答文の履歴を保持することで、それまでの記憶を反映した会話ができるようになる

## 使用法

1. 各種 Python ライブラリをインストールする
    ```sh
    pip3 install openai
    pip3 install langchain
    ```

1. OpenAI の APIキーを発行する<br>
    [OpenAI Platform のページ](https://platform.openai.com/account/api-keys) から API キーを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/71ca027f-f4d2-4cde-9961-8a05da5ecf86">

1. LangChain Memory を使用した Python コードを作成する<br>

    - Chat Message History を使用したコード例 : `run_langchain_1.py`
        ```python
        import argparse
        from langchain.memory import ChatMessageHistory
        from langchain.schema import messages_to_dict
        from langchain.schema import messages_from_dict

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--human_prompt', type=str, default="Hello World!")
            parser.add_argument('--ai_prompt', type=str, default="Hello! How can I assist you today?")
            args = parser.parse_args()

            # ChatMessageHistory オブジェクト（Chat の履歴データ（History）を管理する機能）に HumanMessages や AIMessages 追加
            history = ChatMessageHistory()

            history.add_user_message(args.human_prompt)
            history.add_ai_message(args.ai_prompt)
            print(f'history.messages={history.messages}')

            # 履歴の削除
            history.clear()
            print(f'history.messages={history.messages}')

            exit(0)
        ```

        ポイントは、以下の通り

        - Chain を使用していない

        - xxx

    - ConversationBufferMemory を使用したコード例 : `run_langchain_2.py`
        ```python
        import argparse
        from langchain.memory import ConversationBufferMemory
        from langchain.chains import ConversationChain
        from langchain.llms import OpenAI

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--model_name', type=str, default="text-davinci-003")
            parser.add_argument('--human_prompt', type=str, default="Hello World!")
            parser.add_argument('--ai_prompt', type=str, default="Hello! How can I assist you today?")
            args = parser.parse_args()

            # メモリ初期化
            memory = ConversationBufferMemory()

            # モデル定義
            llm = OpenAI(
                openai_api_key=args.openai_api_key,
                model_name=args.model_name,
                temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print("llm: ", llm)

            # チェーンの初期化（使用する LLM と メモリオブジェクトを渡す）
            conversation = ConversationChain(
                llm=llm, 
                memory=memory
            )

            # LLM推論実行
            try:
                # 会話を開始
                user_input=input("You: ")

                while True: 
                    response = conversation.predict(input=user_input)
                    print(f"AI: {response}")
                    user_input = input("You: ")
                    if user_input == "exit":
                        break
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

        ポイントは、以下の通り

        - Chain を使用している

        - xxx

<!--
    - Simple Memory を使用したコード例 : `run_langchain_3.py`
-->

1. Python コードを実行する<br>
    - `run_langchain_1.py`
        ```sh
        python3 run_langchain_1.py
        ```

        ```sh
        history.messages=[HumanMessage(content='Hello World!', additional_kwargs={}, example=False), AIMessage(content='Hello! How can I assist you today?', additional_kwargs={}, example=False)]
        history.messages=[]
        ```

    - `run_langchain_2.py`
        ```sh
        python3 run_langchain_1.py
        ```

        ```sh
        You: Hellow world
        AI:  Hey there! It's so nice to meet you. How can I help you today?
        You: may name is yagami
        AI:  Nice to meet you, Yagami! Is there anything I can do for you today?
        You: Do you know may name?
        AI:  Yes, I do know your name - it's Yagami. Is there something else I can help you with?
        ```

        Chains で実行した LLM へのプロンプトや応答文の履歴を保持することで、それまでの記憶を反映した会話ができるようになっている


## 参考サイト

- https://python.langchain.com/docs/modules/memory/
- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_memory
- https://book.st-hakky.com/docs/memory-of-langchain/