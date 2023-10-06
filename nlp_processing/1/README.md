# LangChain の概要

LangChain は、OpenAI API などの LLM API のラッパーライブラリであり、LLM アプリケーションを構築する上で必要となる各種機能郡を組み込んだライブラリ。
具体的には、以下のようなモジュール郡を持つ

1. Model I/O<br>
    <img width="700" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/e105f560-624f-4b16-89de-a338df5ca75d"><br>
    LLM とのインターフェースモジュール<br>

    - Prompts<br>
        プロンプト（LLMモデルへの入力文章。特にLLMモデルの応答を導くためにユーザーによって提供される一連の指示や入力）のラッパーモジュール<br>
        具体的には、プロンプトのテンプレート化（Prompt templates）や Zero-shot, Few-shot learning などの機能を提供している。<br>
        LangChain Prompt には、以下の機能ある

        - Prompt templates<br>
            LLM 用のプロンプトを生成するためのあらかじめ定義されたテンプレートを提供する機能

        - Example selectors<br>
            大量の教師データ（正解例）からプロンプトに入力するデータを選択するための機能。Few-shot learning（いくつかの正解例を与えた後に、質問文を投げる形式）の文脈等での利用を想定した機能

    - Language models<br>
        OpenAI API の LLM モデル（GPT-3.5 など）や他の LLM モデルのラッパーモジュール。その企業の LLM モデルによって、API のライブラリや呼び出し方が異なるが、LangChain を使用するととで同じ手続きで LLM を使用できるようになるメリットがある

    - Output parsers<br>
        出力のデータ形式を指定するための機能

1. Data connection<br>
    <img width="700" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/2195a553-b688-4f91-8212-d0e0ab0a5ba6"><br>
    LLM を活用したアプリケーションでは多くの場合、LLM モデルの学習用データセットには含まれないユーザ固有データ（ユーザーIDなどの顧客情報など）を必要するが、LangChain の Data connection では、これらユーザー固有データ（PDF,CSV）の読み込み・保存・変換・クエリのための機能郡を提供している<br>

    - Document Loaders<br>
        PDFやCSVなどの外部データを読み込むための機能

    - Text Splitters<br>
        文章データを分割するための機能

    - Text embedding models<br>
        テキストを埋め込みベクトル変換し、テキスト間の類似度を計算できるようにする

    - VectorStores<br>
        埋め込みベクトル化されたデータを管理するための機能

    - Retrievers（リトライバー）<br>
        ユーザーからの入力文に対して、外部テキストデータの分割した各文章から類似度の高い文章を検索＆取得をするための機能

    > - Indexes（インデックス化）<br>
    >   LLM における インデックス化とは、あらかじめシステムに情報を用意しておき、ユーザーの入力に応じて抜粋した情報と合わせてプロンプトとして LLM にわたす手法。
    >   具体的には、PDF や CSV などの外部データを用いて LLM の回答を生成する機能で、上記 Data connection の機能がインデックス化に対応している<br>

1. Chains<br>
    複数のプロンプト入力を実行するための機能

1. Memory<br>
    <img width="788" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/6a1c7a5b-4a2e-4841-9819-6323af8b6fca"><br>
    LLM へのプロンプトや応答文の履歴を保持したり、Chains や Agents 内部における状態保持をする機能。
    
    - Chat Message History<br>
        xxx

    - Simple Memory<br>
        xxx

    - Buffer Memory<br>
        xxx

1. Agents<br>
    LLM を使って一連の外部ツール（例：Python スクリプトの実行、外部 API の実行など）を選択して実行できる機能。<br>
    Chains を使用すれば、同様の機能は実現可能であるが、Chain では Python スクリプトで一連の機能をハードコードする必要がある。一方エージェントでは、LLM を推論エンジンとして使用し、どの外部ツールをどの順番で実行するかを決定できる。

    LangChain Agents には、以下の主要モジュールがある

    - Agent
        プロンプトの内容に応じて適切な外部ツールを選択するための Agent

    - Tools
        Agent が外部とやり取りをするために呼び出す関数

    - Toolkits
        特定のユースケースに応じて、外部ツールを初期搭載した Agent 機能

    - Agent Executor
        Agent の行動（最適な外部ツール選択）を実行するための機能（＝最適な外部ツール実行）

1. Callbacks<br>

1. LangSmith<br>
    LangSmith は、2023/7/21 月頃に新規追加された LangChain の機能（2023/08/26 時点では、クローズドベータ版機能）の１つで、LLM アプリケーションの本番運用のための便利機能（LLM アプリケーション実行トレースや実行ログのモニタリング機能など）を織り込んだ UI コンソール付きのモジュールになっている。

## 参加サイト
- https://python.langchain.com/docs/get_started/introduction.html
- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_overview
