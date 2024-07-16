# Dify を使用した LLM アプリケーションを Web サイトへの埋め込みとして外部公開する

## 使用方法

1. 「[Dify の基本的な使い方（ワークフローを使用した LLM アプリケーションを作成する）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/20)」に従って、Dify を使用した LLM アプリケーションのワークフローを作成する

1. 埋め込み用の `<iframe>` を取得する<br>
    「概要」ページ -> 「Embedded」ボタンをクリックし、埋め込み用の `<iframe>` を取得する
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/590f2646-da91-4cb8-bd5b-927a59c60af3">

    > [TODO]
    > - 公式ドキュメントには「概要」->「Embedded」ボタンが存在し、そこから埋め込み用 `<iframe>` のリンクが取得できると記載されているが、手元の環境では見当たらなかった
    > - また「アプリを公開する」 -> 「サイトに組み込む」ボタンも見当たらなかった

1. 自身の Web サイトの HTML の `<body>` 内に、上記コピーした `<iframe>` のコードを貼り付ける

## 参考サイト

- https://docs.dify.ai/v/japanese/guides/application-publishing/launch-your-webapp-quickly#aisaitonomemi

- https://qiita.com/nyakiri_0726/items/0ef05499ac75ded4bead#3-streamlit%E3%81%AE%E3%82%A2%E3%83%97%E3%83%AA%E3%82%92%E4%BD%9C%E6%88%90
