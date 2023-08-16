# Hugging Face の概要

- Hugging Face Hub<br>
    Hugging Face レポジトリの管理など

    - Hugging Face レポジトリの種類
        - Model: 機械学習モデルのレポジトリ
        - Dataset: データセットのレポジトリ
        - Space: アプリケーションのレポジトリ

- Datasets<br>
    大規模なデータセットの処理と操作を効率的に行うためのライブラリ

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

- xxx

## 参考サイト
- https://zenn.dev/novel_techblog/articles/362fceec01c8b1
