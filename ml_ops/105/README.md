# 【GCP】Vertex AI の基礎事項

## Vertex AI プラットフォーム機能

<img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/90476003-c38f-4aaf-a4bc-ffb6a1857fda">

### MLOps パイプライン機能

- Vertex AI Pipelines<br>
    GCP 上で MLOps パイプラインをオーケストレーション（＝構築、運用管理を自動化）で構築できる機能で、以下のような機能がある
    
    - サーバーレスで MLOps パイプラインを構築可能
    - Python SDK（Kubeflow Pipelines SDK（v2以降））を用いて、独自のパイプラインを構築可能
    - xxx

### 学習用データセット作成機能

- Vertex AI Datasets<br>
    機械学習モデルのためのデータセット（学習用データセットなど）を管理するための機能

- Vertex AI Data Labeling<br>
    学習済みデータセット作成にあたってのラベリングなどのアノテーション作業をサポートする機能

### 学習機能

- Vertex AI Training<br>
    スケール可能で高可用（＝システムが継続して稼働できる能力が高い）な機械学習モデルの学習機能で以下のような特徴がある

    - サーバレスで動作
    - 迅速なクラスタ起動
    - ジョブをキューイングさせオートスケール
    - 使用した時間だけの課金
    - AutoML での自動モデル作成可能
    - カスタムトレーニングで独自の機械学習モデルや学習設定で学習可能

- Vertex AI Experiments<br>
    複雑の機械学習モデルの実験（学習など）を管理

### 推論機能

- Vertex AI Prediction<br>
    機械学習モデルの推論＆デプロイメント機能で、以下のような機能を持つ

    - 機械学習 API のエンドポイント提供
    - 通信トラフィックに応じた自動スケーリング
    - GPU での高速な推論処理

- Explainable AI<br>
    機械学習モデルの説明可能性や推論結果の根拠を（画像モデルの場合は attention 領域のヒートマップなどで）明らかにするための機能


### モデルの運用＆監視機能

- Model Monitoring<br>
    機械学習モデルのパフォーマンス監視機能

### ML モデル管理系機能

- Vertex AI Feature Store<br>
    ML特徴量を管理（共有・再利用など）するための Feature ストア（＝機械学習システムで扱う特徴量を管理・提供するための基盤）

- Vertex AI ML Metedata<br>
    MLパイプラインの各コンポーネントの入出力メタデータ（データセットやアーティファクトなど）を、メタデータストアに自動的に記録・追跡する記録
    
- Vertex AI Model Registry<br>
    学習済み機械学習モデルを管理ための機能で、以下のような機能を持つ<br>

    - 機械学習モデルのバージョン管理
    - GCP 以外で学習したモデルをインポート可能
    - 機械学習モデルを TensorFlow パッケージとしてエクスポートし、GCP 以外の場所にもデプロイ可能

## Vertex AI 学習済みモデル機能

<img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/043b5ce9-5359-4ca5-af7a-83e1deb3cfe2">

- Vertex AI Model Garden<br>
    事前構築済みの機械学習モデルが集約されており、エンタープライズ対応の基盤モデル・タスク固有のモデル・およびAPIを提供するプラットフォーム。

- Vertex AI Matching Engine<br>
    YouTube や Google 画像検索、Google Play などのサービスでレコメンデーションや情報検索を提供している類似ベクトル検索機能を、自前で開発することなくシステムに組み込むことができるサービス

- Vertex AI Vision<br>
    コンピュータビジョン系のアプリケーションを簡単に作成、デプロイ、管理できる機能

- Vertex AI Translation<br>
    学習済みの機械学習モデルを用いて、翻訳（日本語 -> 英語など）を行うための API を提供

- Vertex AI Speech-to-Text<br>
    学習済みの機械学習モデルを用いて、音声からテキスト起こしを行うための API を提供

- Generative AI Studio<br>
    生成 AI モデルを作成してテストできるクラウドベースのプラットフォーム

## 料金体系
