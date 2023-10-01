# 【Python】LangChain Prompt の Prompt templates 使用してプロンプトを生成する

LangChain Prompt には、以下の２種類の機能が存在する

- Prompt templates
    LLM 用のプロンプトを生成するためのあらかじめ定義されたテンプレートを提供する機能

- Example selectors
    大量の教師データからプロンプトに入力するデータを選択するための機能

ここでは、Prompt templates の使用方法を説明する

## 

## 使用法

1. 各種 Python ライブラリをインストールする
    ```sh
    pip3 install openai
    pip3 install langchain
    ```

1. OpenAI の APIキーを発行する<br>
    [OpenAI Platform のページ](https://platform.openai.com/account/api-keys) から API キーを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/71ca027f-f4d2-4cde-9961-8a05da5ecf86">

1. LangChain Prompt を使用した Python コードを作成する<br>

    - `PromptTemplate` を使用したコード例 : `run_langchain_1.py`
        ```python
        import argparse
        from langchain import PromptTemplate
        from langchain.llms import OpenAI

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--model_name', type=str, default="text-davinci-003")
            parser.add_argument('--template', type=str, default="{keyword1}と{keyword2}について教えてください")
            parser.add_argument('--keyword1', type=str, default="LLM")
            parser.add_argument('--keyword2', type=str, default="ChatGPT")
            parser.add_argument('--save_propmt_filepath', type=str, default="out_data/prompt-template-1.json")
            args = parser.parse_args()

            # PromptTemplate オブジェクト作成（バリデーションなし）
            # prompt = PromptTemplate.from_template(
            #     template=args.template      # 例 : "{keyword1}と{keyword2}について教えてください"
            # )

            # PromptTemplate オブジェクト作成（バリデーションあり）
            prompt = PromptTemplate(
                template=args.template,      # 例 : "{keyword1}と{keyword2}について教えてください"
                input_variables=["keyword1", "keyword2"],
            )

            # プロンプトテンプレートの json データをローカル環境に保存
            prompt.save(args.save_propmt_filepath)

            # プロンプト文生成
            # 例 : "{keyword1}と{keyword2}について教えてください" -> "{LLM}と{ChatGPT}について教えてください"
            prompt_text = prompt.format(keyword1=args.keyword1, keyword2=args.keyword2)
            print("prompt_text: ", prompt_text)

            # モデル定義
            llm = OpenAI(
                openai_api_key=args.openai_api_key,
                model_name=args.model_name,
                temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print("llm: ", llm)

            # LLM推論実行
            try:
                response = llm(prompt=prompt_text)
                print(f"response: {response}")
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

        ポイントは、以下の通り

        - `PromptTemplate` では、`... {keyword} ...` の `{keyword}` の部分を他のワードに置き換えるのみ

        - `PromptTemplate` オブジェクトの `save(json_file_path)` メソッドで、プロンプトテンプレートの json データをローカルに保存できる

            > プロンプト管理機能（過去のプロンプトを保存）に使えそう

    - `FewShotPromptTemplate` を使用したコード例 : `run_langchain_2.py`
        ```python
        import argparse
        from langchain import PromptTemplate
        from langchain import FewShotPromptTemplate
        from langchain.llms import OpenAI

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--model_name', type=str, default="text-davinci-003")
            parser.add_argument('--save_propmt_filepath', type=str, default="out_data/prompt-template-2.json")
            args = parser.parse_args()

            # ---------------------------------
            # PromptTemplate オブジェクト作成
            # ---------------------------------
            template = """
            英語: {keyword1}
            日本語: {keyword2}\n
            """

            prompt = PromptTemplate(
                template=template,
                input_variables=["keyword1", "keyword2"],
            )

            # ---------------------------------
            # FewShotPromptTemplate オブジェクト作成
            # ---------------------------------
            # Few-shot learning（いくつかの正解例を与えた後に、質問文を投げる形式）の正解例
            # PromptTemplate の {...} 部分の値を定義することで正解例を与える
            fewshot_examples = [
                {
                    "keyword1": "cat",
                    "keyword2": "猫",
                },
                {
                    "keyword1": "dog",
                    "keyword2": "犬",
                },
            ]

            fewshot_prompt = FewShotPromptTemplate(
                examples=fewshot_examples,              # Few-shot learning での正解例
                example_prompt=prompt,                  # PromptTemplate オブジェクト
                prefix="英語を日本語に翻訳してください",     # プロンプト（質問文）
                suffix="英語 : {input}\n",               # Few-shot learning での正解例における接頭語（この例では "英語 : "） 
                input_variables=["input"],              # suffix の {...} の変数名
                example_separator="\n\n",
            )

            # プロンプトテンプレートの json データをローカル環境に保存
            fewshot_prompt.save(args.save_propmt_filepath)

            # ---------------------------------
            # FewShotPromptTemplate オブジェクトからプロンプト文生成
            # ---------------------------------
            prompt_text = fewshot_prompt.format(input="cheese")
            print("prompt_text: ", prompt_text)

            # ---------------------------------
            # モデル定義
            # ---------------------------------
            llm = OpenAI(
                openai_api_key=args.openai_api_key,
                model_name=args.model_name,
                temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print("llm: ", llm)

            # ---------------------------------
            # LLM推論実行
            # ---------------------------------
            try:
                response = llm(prompt=prompt_text)
                print(f"response: {response}")
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

        ポイントは、以下の通り

        - `FewShotPromptTemplate` では、Few-shot learning（いくつかの正解例を与えた後に、質問文を投げる形式）用の Prompt template になっている

        - この例では、Few-shot learning でのいくつかの正解例として、「英語: cat -> 日本語: 猫, 英語: dog -> 日本語: 犬」を与えた後に、「英語 : cheese」に対して、うまく回答できるか試している

        - `FewShotPromptTemplate` オブジェクトの `save(json_file_path)` メソッドで、Few-shot learning 用プロンプトテンプレートの json データをローカルに保存できる

            > プロンプト管理機能（過去のプロンプトを保存）に使えそう

    - `ChatPromptTemplate` を使用したコード例 : `run_langchain_3.py`
        ```python
        import argparse
        from langchain.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )
        from langchain.chat_models import ChatOpenAI

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--model_name', type=str, default="gpt-3.5-turbo")
            args = parser.parse_args()

            # ---------------------------------
            # SystemMessagePromptTemplate オブジェクト作成
            # ---------------------------------
            system_template="あなたは、質問者からの質問を{language}で回答するAIです。"
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

            # ---------------------------------
            # HumanMessagePromptTemplate オブジェクト作成
            # ---------------------------------
            human_template="質問者：{question}"
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

            # ---------------------------------
            # ChatPromptTemplate オブジェクト作成
            # ---------------------------------
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_message_prompt, human_message_prompt]
            )

            # ---------------------------------
            # ChatPromptTemplate オブジェクトからプロンプト文生成
            # ---------------------------------
            prompt_message_list = chat_prompt.format_prompt(language="アニメ口調", question="VTuber について教えて").to_messages()
            print(prompt_message_list)

            # ---------------------------------
            # Chat 用モデル定義
            # ---------------------------------
            chat_llm = ChatOpenAI(
                openai_api_key=args.openai_api_key,
                model_name=args.model_name,
                temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print("chat_llm: ", chat_llm)

            # ---------------------------------
            # Chat 用LLM推論実行
            # ---------------------------------
            try:
                response = chat_llm(prompt_message_list)
                print(f"response: {response}")
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

        ポイントは、以下の通り

        - `ChatPromptTemplate` は Chat 用 LLM 専用のプロンプトテンプレートで、Chat モデル特有のプロンプト種類であるシステム用プロンプト（実際の質問文を投げる前に Chat LLM モデルに基本的な役割など指示するプロンプト。例："あなたは、質問者からの質問をアニメ口調で回答するAIです。" など）と実際に人間が入力する質問文用プロンプト（例："VTuber について教えて" など）を簡単に設定できるプロンプトテンプレートになっている

        - `SystemMessagePromptTemplate` オブジェクトに、システム用プロンプト（実際の質問文を投げる前に Chat LLM モデルに基本的な役割など指示するプロンプト。例："あなたは、質問者からの質問をアニメ口調で回答するAIです。" など）を設定する

        - `HumanMessagePromptTemplate` オブジェクトに、実際に人間が入力する質問文用プロンプト（例："VTuber について教えて" など）を設定する

        - その後 `SystemMessagePromptTemplate` オブジェクトと `HumanMessagePromptTemplate` から `ChatPromptTemplate` オブジェクトを作成する


1. Python コードを実行する<br>
    - `run_langchain_1.py`
        ```sh
        python3 run_langchain_1.py
        ```

        出力結果は、以下の通り
        ```sh
        prompt_text:  LLMとChatGPTについて教えてください
        llm:  OpenAI
        Params: {'model_name': 'text-davinci-003', 'temperature': 0.9, 'max_tokens': 256, 'top_p': 1, 'frequency_penalty': 0, 'presence_penalty': 0, 'n': 1, 'request_timeout': None, 'logit_bias': {}}
        response: 

        LLM (Latent Language Model) は自然言語処理タスクにおいて、ニューラルネットワークを利用して予測を行うモデルです。LLMモデルを使用すると、予測を行う際に訓練データの偏りを回避し、より正確な予測が行えます。

        ChatGPTは、Transformerベースの専門的な自然言語処理フレームワークです。ChatGPTは、対話の中に出現する専門的な概念を処理するために開発されました。ChatGPTを使用する
        ```

    - `run_langchain_2.py`
        ```sh
        python3 run_langchain_2.py
        ```

        出力結果は、以下の通り
        ```sh
        prompt_text:  英語を日本語に翻訳してください

            英語: cat
            日本語: 猫

            英語: dog
            日本語: 犬

            英語 : cheese

        llm:  OpenAI
        Params: {'model_name': 'text-davinci-003', 'temperature': 0.9, 'max_tokens': 256, 'top_p': 1, 'frequency_penalty': 0, 'presence_penalty': 0, 'n': 1, 'request_timeout': None, 'logit_bias': {}}
        response: 日本語: チーズ
        ```

        - Few-shot learning でのいくつかの正解例（「英語: cat -> 日本語: 猫」,「英語: dog -> 日本語: 犬」）を与えた後に、「英語 : cheese」に対して、正しい応答文「日本語: チーズ」を出力できている


    - `run_langchain_3.py`
        ```sh
        python3 run_langchain_3.py
        ```

        出力結果は、以下の通り
        ```sh
        [SystemMessage(content='あなたは、質問者からの質問をアニメ口調で回答するAIです。', additional_kwargs={}), HumanMessage(content='質問者：VTuber について教えて', additional_kwargs={}, example=False)]

        chat_llm:  cache=None verbose=False callbacks=None callback_manager=None tags=None metadata=None client=<class 'openai.api_resources.chat_completion.ChatCompletion'> model_name='gpt-3.5-turbo' temperature=0.9 model_kwargs={} openai_api_key='dummy' openai_api_base='' openai_organization='' openai_proxy='' request_timeout=None max_retries=6 streaming=False n=1 max_tokens=None tiktoken_model_name=None

        response: content='AI：ふふふ、VTuberについて教えてあげるわ！VTuberは、バーチャルユーチューバーの略で、仮想のキャラクターが配信を通じてコミュニケーションを取ることを楽しむんだよ。それぞれのキャラクターは、個性豊かで魅力的な外見とパーソナリティを持っていて、動画や生配信を通じて視聴者と交流するんだ！\n\nVTuberは、ゲーム実況やバラエティ番組、歌唱活動など様々なジャンルのコンテンツを提供しているよ。彼らは配信中に視聴者とのチャットやコメント交流を楽しむことができるし、ファンとの絆を深めることも大切にしているんだ。\n\nVTuberは、近年特に日本で人気を集めていて、数多くの配信者が活躍しているよ。彼らの魅力は、可愛らしいキャラクターデザインや、楽しいパーソナリティ、そして独自の個性にあるんだよ。\n\nVTuberは、リアルタイムでのコミュニケーションを楽しむことができるし、視聴者も彼らの活動をサポートすることができるんだ。ハラハラドキドキの瞬間や笑いの渦、感動の瞬間など、様々なエモーショナルな体験ができるよ！\n\nVTuberの世界はまだまだ広がり続けていて、新しい才能や楽しさが生み出されているんだ。だから、もし興味があるなら、ぜひ一度覗いてみるといいよ！あなたもVTuberの魅力にハマるかもしれないからね！' additional_kwargs={} example=False
        ```

## 参考サイト
- https://python.langchain.com/docs/modules/model_io/prompts/
- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_prompt
