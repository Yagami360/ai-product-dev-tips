# LangChain の概要

LangChain は、OpenAI API などの LLM API のラッパーライブラリであり、LLM アプリケーションを構築する上で必要となる各種機能郡を組み込んだライブラリ。
具体的には、以下のようなモジュール郡を持つ

1. Model I/O<br>
    <img width="700" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/e105f560-624f-4b16-89de-a338df5ca75d"><br>
    LLM とのインターフェースモジュール<br>

    - Prompts<br>
        プロンプト（LLMモデルへの入力文章。特にLLMモデルの応答を導くためにユーザーによって提供される一連の指示や入力）のラッパーモジュール<br>
        具体的には、プロンプトのテンプレート化や Zero-shot, Few-shot learning などの機能を提供している

    - Language models
        OpenAI API の LLM モデル（GPT-3.5 など）や他の LLM モデルのラッパーモジュール<br>
        その企業の LLM モデルによって、API のライブラリや呼び出し方が異なるが、LangChain を使用するととで同じ手続きで LLM を使用できるようになるメリットがある

    - Output parsers

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

1. Agents<br>

1. Memory<br>

1. Callbacks<br>

1. LangSmith<br>
    LangSmith は、2023/7/21 月頃に新規追加された LangChain の機能（2023/08/26 時点では、クローズドベータ版機能）の１つで、LLM アプリケーションの本番運用のための便利機能（LLM アプリケーション実行トレースや実行ログのモニタリング機能など）を織り込んだ UI コンソール付きのモジュールになっている。

## 参加サイト
- https://python.langchain.com/docs/get_started/introduction.html
- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_overview
