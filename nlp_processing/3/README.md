# 【Python】LangChain Retrievers を使用して LLM が学習に使用していない独自ドメインでの外部データに対しての LLM の応答文を得る

LLM を学習に使用していない独自のドメイン（分野）での応答できるようにするためには、通常そのドメインに関しての学習用データセットを用意して LLM をその学習用データセットでファインチューニングが必要があり、再学習などの開発コストが高くなるが、LangChain の Retrievers 機能を使用することで、LLM の再学習やファインチューニングせずとも LLM の学習用データセットには含まれない独自ドメインに対しての応答分を出力できるようになる。

> - Retrievers
> 分割した各文章から類似度の高い文章を検索＆取得をするための機能

## 使用法

1. 各種 Python ライブラリをインストールする
    ```sh
    pip3 install openai
    pip3 install langchain
    pip3 install chromadb
    ```
    > `chromadb` は LangChain VectorDB のパッケージ

1. OpenAI の APIキーを発行する<br>
    [OpenAI Platform のページ](https://platform.openai.com/account/api-keys) から API キーを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/71ca027f-f4d2-4cde-9961-8a05da5ecf86">

1. 外部テキストデータを用意する<br>
    LLM が学習に使用していないデータであるが、そのドメイン（分野）に関しての応答分を出力できるようにしたい外部データを用意する。<br>
    今回は、例えば以下のようなとあるゲームのテキストデータを用意する（wiki にあるテキストデータ）
    ```txt
    あらすじ
    大部分が氷と水に覆われて人の住まう土地で無い火星では、多くの人々は都市船と呼ばれる巨大な潜水艦で暮らす。
    火星の水はエネルギー源であり、かつてはその水を巡って地球を巻き込んだ銀河大戦が展開された。
    終戦に伴う空前の大不況の真っ只中、フリーターのグラムは、海賊「夜明けの船」の都市船アデナ襲撃に巻き込まれ海に投げ出されたところを、彼の所有するペンダントの輝きに惹かれるように現れたラウンドバックラー（RB）「希望号」に乗り込む形となった。
    「希望号」を「夜明けの船」関係だと勘違いした地球軍のRBと交戦し、なんとか退けたグラムは「夜明けの船」のRBダイバーのヤガミにスカウトされ、やがて、彼は「夜明けの船」に迎え入れられる。

    ヤガミ・アリアン
    夜明けの船に所属するRBダイバーであり、RB「士翼号」に搭乗する。超絶的な操縦技術とセンスを持ち、出撃の際には地球軍のRBを残らず破壊し尽くすことから「死神ヤガミ」の異名で恐れられている。
    戦況判断能力にも長けており、エリザベスら幹部陣の作戦会議によく出席している。
    グラムやアキ達の突飛な行動にも1歩引いた立場からメスを入れる事が多い。
    基本的には保守的な考え方をしているが、絶体絶命の場面では一か八かの大胆不敵な一手を打つこともある。
    およそ海賊らしからぬクールな物腰からは想像もつかない、熱い魂の持ち主。
    しかし、方向音痴で大学都市船内で迷子になる、アキ発案の仮装パーティでノリノリのコスプレを披露する、エステルの誕生日会の為に率先して小芝居を打つなど、意外にくだけた一面も。
    元々はナイアル・ポー側の人間で、夜明けの船と共にエリザベスたちの前に現れて以降行動を共にしている。
    その兼ね合いで、とある作戦中に夜明けの船から離れた。
    作中で銃を手にしているシーンはあるが、ポーズだけだったり銃で殴るなど本来の使用目的とは異なる使用方法を取っているので格闘戦は不得手と見える。
    ```

1. LangChain を使用した Python コードを作成する<br>
    - `run_langchain.py`
        ```python
        import os
        import argparse

        # LangChain Data connection
        from langchain.document_loaders import TextLoader           # LangChain Data connection の Document Loaders
        from langchain.text_splitter import CharacterTextSplitter   # LangChain Data connection の Text Splitters
        from langchain.embeddings.openai import OpenAIEmbeddings    # LangChain Data connection の Text embedding models
        from langchain.vectorstores import Chroma                   # LangChain Data connection の VectorStores
        from langchain.chains import RetrievalQA                    # LangChain Data connection の Retrievers
        # LangChain Model I/O
        from langchain.llms import OpenAI                           # LangChain Model I/O の Language models


        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--text_path', type=str, default="in_data/kenran.txt")
            parser.add_argument('--emb_model_name', type=str, default="text-embedding-ada-002")
            parser.add_argument('--model_name', type=str, default="text-davinci-003")
            parser.add_argument('--prompt', type=str, default="ヤガミについて教えてください")
            args = parser.parse_args()

            # OpenAI の API キー設定
            os.environ["OPENAI_API_KEY"] = args.openai_api_key

            # LangChain Data connection の Document Loaders を使用して、テキストデータ読み込み
            document_loader = TextLoader(args.text_path)
            documents = document_loader.load()

            # LangChain Data connection の Text Splitters を使用して、テキストを分割
            text_splitter = CharacterTextSplitter(
                # separator = "\n",   # セパレータ
                chunk_size=700,     # チャンクの文字数
                chunk_overlap=0
            )
            split_documents = text_splitter.split_documents(documents)
            print(f'split_documents={split_documents}')

            # LangChain Data connection の Text embedding models を使用して、埋め込みモデル定義
            # デフォルトでは、OpenAI 推奨の "text-embedding-ada-002" モデルが使用される
            emb_model = OpenAIEmbeddings(
                model=args.emb_model_name,
            )
            print(f'emb_model={emb_model}')

            emb_result_0 = emb_model.embed_query(split_documents[0].page_content)
            print(f'emb_result_0[0:10]={emb_result_0[0:10]}')

            # 埋め込みモデルで分割テキストを埋め込み、埋め込みベクトルを作成し、特徴量データベース（VectorDB）に保存
            # LangChain Data connection の VectorStores を使用
            feature_db = Chroma.from_documents(split_documents, emb_model)
            print(f'feature_db={feature_db}')

            # 特徴量データベース（VectorDB）から retriever（ユーザーからの入力文に対して、分割した各文章から類似度の高い文章を検索＆取得をするための機能）作成
            retriever = feature_db.as_retriever(
                search_kwargs={"k": 1},     # 
            )
            print(f'retriever={retriever}')

            # 【デバック】retriever で類似度の高い情報を検索＆取得
            print(f"retriever.get_relevant_documents(query=args.prompt)={retriever.get_relevant_documents(query=args.prompt)}")

            # LLM モデル定義
            llm = OpenAI(
                model_name=args.model_name,
                temperature=0.9,                # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print(f'llm={llm}')

            # LangChain Data connection の Retrievers を使用して、RetrievalQA Chain（質問応答 QA の取得に使用する Chain）を生成
            # Chain : 複数のプロンプト入力を実行するための機能
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff", 
                retriever=retriever
            )
            print(f'qa_chain={qa_chain}')

            # LLM 推論実行（QA:質問応答）
            try:
                answer = qa_chain.run(args.prompt)
                print(f'answer={answer}')
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

        ポイントは、以下の通り

        1. LLM が学習に使用していない外部テキストデータを分割する
        1. OpenAI の埋め込みモデル `text-embedding-ada-002` で、分割した各テキストの埋め込みベクトルを得る
        1. 各種埋め込みベクトルを特徴量データベース（VectorDB）に保存
        1. ユーザーが入力した文章（の埋め込みベクトル）と分割した各テキストの埋め込みベクトルの類似度を検索＆取得（リトライブ）する
        1. OpenAI の LLM モデルにリトライブ結果（類似度の高い外部テキストデータ）を渡し、ユーザーが入力した文章に対しての応答文を得る
            - リトライブ結果（入力文に対して類似度の高い外部テキストデータ）が渡されているので、LLM としては、類似度の高い外部テキストデータからユーザーの入力文に対して応答するという簡単化されたタスクになるので、LLM が学習に使用していない独自ドメインの外部データに対しても独自ドメインの応答文を出力できるようになる。

1. Python スクリプトを実行する
    ```sh
    python3 run_langchain.py --openai_api_key=${OPENAI_API_KEY}
    ```

    1. Retriever で取得した類似度が高いテキスト
        - ユーザーからの入力文
            ```txt
            ヤガミについて教えてください
            ```
        - Retriever で取得した類似度が高いテキスト
            ```txt
            'ヤガミ・アリアン\n夜明けの船に所属するRBダイバーであり、RB「士翼号」に搭乗する。超絶的な操縦技術とセンスを持ち、出撃の際には地球軍のRBを残らず破壊し尽くすことから「死神ヤガミ」の異名で恐れられている。\n戦況判断能力にも長けており、エリザベスら幹部陣の作戦会議によく出席している。\nグラムやアキ達の突飛な行動にも1歩引いた立場からメスを入れる事が多い。\n基本的には保守的な考え方をしているが、絶体絶命の場面では一か八かの大胆不敵な一手を打つこともある。\nおよそ海賊らしからぬクールな物腰からは想像もつかない、熱い魂の持ち主。\nしかし、方向音痴で大学都市船内で迷子になる、アキ発案の仮装パーティでノリノリのコスプレを披露する、エステルの誕生日会の為に率先して小芝居を打つなど、意外にくだけた一面も。\n元々はナイアル・ポー側の人間で、夜明けの船と共にエリザベスたちの前に現れて以降行動を共にしている。\nその兼ね合いで、とある作戦中に夜明けの船から離れた。\n作中で銃を手にしているシーンはあるが、ポーズだけだったり銃で殴るなど本来の使用目的とは異なる使用方法を取っているので格闘戦は不得手と見える。', metadata={'source': 'in_data/kenran.txt'})]
            ```

        ユーザーからの入力文に対して、類似度が高い外部分割テキストをうまく取得できている。

    1. LLM からの QA 結果
        - 質問
            ```txt
            ヤガミについて教えてください
            ```
        - 応答
            ```txt
            ヤガミ・アリアンは夜明けの船に所属するRBダイバーであり、超絶的な操縦技術とセンスを持っています。そして”死神ヤガミ”の異名で恐れられています。戦況判断能力にも長けており、エリザベスら幹部陣の作戦会議によく出席しています。作中で銃を手にしている場面がありますが、実際の使用方法は異なっており格闘戦能力は不得手となっています。
            ```

        LLM が学習に使用していない独自ドメインに対してもうまく応答できている。<br>
        リトライブ結果が正しいので、LLM としては、類似度の高い外部テキストデータ（今回の例では「ヤガミ・アリアン\n夜明けの船に所属するRBダイバーであり、RB「士翼号」に搭乗する。超絶的な操縦技術とセンスを持ち、...」）からユーザーの入力文（今回の例では、「ヤガミについて教えてください」）に対して応答するという簡単化されたタスクになるので、LLM が学習に使用していない独自ドメインの外部データに対しても独自ドメインの応答文を出力できるようになる。

        この手法においては、Retriever でうまくユーザーからの入力文に対して、類似度が高い外部テキストを取得できるかがポイントとなる。
        今回の例では埋め込みモデルとして、`text-embedding-ada-002` を使用し、外部テキストも単純なものだったが、複雑な外部テキストや質問文の場合は、埋め込みモデルの品質や外部テキストのパース処理などが重要になる

## 参加サイト
- https://note.com/npaka/n/nf2849b26a524
- https://qiita.com/kzkymn/items/8739762fab8cf9d6edad
