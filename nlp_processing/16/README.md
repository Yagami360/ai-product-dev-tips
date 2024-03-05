# Prompt flow の概要

Prompt flow（旧 Azure Machine Learning Prompt flow）は、Microsoft が Azure 上で提供している LLM アプリケーションのための LLMOps ツールで、LLM アプリケーションの処理をコンソール UI 上で定義＆実行＆可視化できるようになっている。

<img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/738031ff-58a1-4ed3-87d8-12413886f1aa"><br>

より詳細には、以下のような主要機能をもった LLMOps ツールになる

- LLM アプリケーションの処理をパイプラインとして、コンソールUI上で編集＆実行＆可視化できる<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/738031ff-58a1-4ed3-87d8-12413886f1aa"><br>

- バリアント機能で複数のプロンプトを同時に試行錯誤しながらプロンプトチューニングできる<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/08e19e92-43d4-444b-be29-8bc597937066"><br>

- 作成したフローをデプロイし、Arure リソース上の API として公開することで、任意のアプリケーションに組み込める
    - デプロイした API のオートスケーリングも行える

- CI/CD 機能
    - CIツールと連携して、自動テストを行うことができる
    - CDツールとの統合により、テストが成功した場合に自動で本番環境にデプロイできる

- モニタリング機能
    - デプロイ後の LLM アプリケーションのモニタリングができる

> Prompt flow はもともとは Azure Machine Learning 内の１機能（Azure Machine Learning Prompt flow）であったが、現在は Azure AI Studio で利用できる独立したツールになっている