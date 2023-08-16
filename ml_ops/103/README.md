# Hugging Face の概要

Hugging Face は、機械学習やディープラーニングのモデルやデータ（学習用データセット）を共有・利用するためのオープンソースプラットフォームで、以下のような主要機能がある

<img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/72ed3bbf-c285-4e37-b763-d555bb89790f">

- [Models](https://huggingface.co/models)<br>
    <img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/cbe65524-e138-450e-9287-d2d2a2c8a0d4"><br>
    様々な機械学習モデルを公開している場所（＝実体は Hugging Face レポジトリ集）

- [Datasets](https://huggingface.co/datasets)<br>
    <img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/74242e77-dfb3-4d6c-9725-7f88298730d7"><br>
    様々な学習用データセットを公開している場所（＝実体は Hugging Face レポジトリ集）

- [Spaces](https://huggingface.co/spaces)<br>
    <img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/07524339-7e1c-46e8-8687-313b6bc8fd62"><br>
    様々な機械学習やディープラーニングモデルのデモアプリを公開している場所（＝実体は Hugging Face レポジトリ集）<br>    
    Space（の Hugging Face レポジトリ）では、Gradio（機械学習モデルのデモアプリを簡単に作成するための Python製 UI ライブラリ）, Streamlit を利用して機械学習モデルのデモアプリを構築する（Docker も利用可能？）

上記 Models, Datasets, Spaces は、Hugging Face レポジトリとして作成されており、Hugging Face レポジトリは、Hugging Face Hub で作成・管理される

- Hugging Face Hub<br>
    Hugging Face レポジトリの管理などを行う機能で、コンソールUI・SDK・CLI の形式で提供されている

    - Hugging Face レポジトリの種類
        - Model: 機械学習モデルのレポジトリ
        - Dataset: データセットのレポジトリ
        - Space: 機械学習モデルのデモアプリ（Space）のレポジトリ

更に、Hugging Face には、以下のようなライブラリがある

- Transformers<br>
    自然言語処理モデルを簡単に使用できるようにするライブラリ。<br>
    具体的には、学習済みモデルの利用・独自データセットでの事前学習・モデルのファインチューニングを行うためのツール等を提供しており、テキスト分類、情報抽出、質問応答、テキスト生成などの NLP タスクを容易に実行できるようになっている。<br>
    また、多数のプログラミング言語（Python、Node.js、Rustなど）に対応している。

    - Tokenizers<br>
        Transformers ライブラリに含まれるライブラリで、自然言語処理における文章のトークン化（文章 -> 単語に分割 -> 各単語をID化）に用いられるライブラリ。
        通常 NLP モデル（BERT など）へ文章を入力する際は、事前に文章をトークン化する必要がある<br>

    - Pipeline<br>
        Transformers ライブラリに含まれるライブラリで、NLP モデルの推論処理を簡単に実装できるライブラリ。
        但し、実装可能なNLP タスクが（Text classification, Text generation, question-answering, conversation, ... などに）限定される

- Datasets<br>
    機械学習モデルの学習用データセットなどの大規模なデータセットに対しての標準的なインターフェースを用意し、多種多様な学習用データセットを共通の手続きで操作できるようにしたライブラリ
    具体的には、データセットの読み込み・変換・フィルタリングなどの一般的な前処理タスクを簡単に行えるように設計されている

- Accelerate<br>
    xxx
    
## 参考サイト
- https://zenn.dev/novel_techblog/articles/362fceec01c8b1
