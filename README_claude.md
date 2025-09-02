# ai-product-dev-tips

AIプロダクト開発のための包括的なTips集

## 📋 概要

このリポジトリは、AIプロダクト開発に必要な幅広い技術領域をカバーする実践的なサンプル集です。機械学習論文調査から前処理・後処理、機械学習モデル開発、MLOps、フロントエンド・アプリ開発まで、AIプロダクト開発の全工程における実用的なコード例とベストプラクティスを提供しています。

## ✨ 特徴

- **包括性**: AIプロダクト開発の全工程をカバー
- **実践性**: すぐに使える実装例とコードスニペット
- **豊富な例**: 200以上の具体的な実装例
- **日本語ドキュメント**: 全て日本語で詳細に説明
- **最新技術**: PyTorch、TensorFlow、Transformers、Docker、Kubernetesなど最新技術スタック
- **クラウド対応**: GCP、AWS、Azureでの本番運用例

## 🛠️ 技術スタック

### 機械学習・AI
- **深層学習フレームワーク**: PyTorch、TensorFlow
- **自然言語処理**: Transformers (Hugging Face)、OpenAI API
- **画像処理**: OpenCV、Pillow、DensePose、OpenPose
- **音声処理**: 音声認識・合成関連技術

### バックエンド・インフラ
- **Web API**: Flask、FastAPI、Express.js
- **コンテナ**: Docker、docker-compose、Kubernetes
- **クラウド**: Google Cloud Platform、AWS、Azure
- **データベース**: Redis、PostgreSQL、MongoDB
- **監視**: Grafana、Prometheus

### フロントエンド・アプリ開発
- **Web**: React、Vue.js、Next.js
- **モバイル**: Flutter (クロスプラットフォーム)
- **デスクトップ**: Electron

### 開発・運用
- **CI/CD**: GitHub Actions、Cloud Build
- **品質管理**: black、flake8、isort、pytest
- **環境管理**: conda、Python仮想環境

## 📦 ディレクトリ構造

```
ai-product-dev-tips/
├── ml_ops/                     # MLOps・機械学習基盤 (119例)
│   ├── 001/                   # Dockerを使用した機械学習環境
│   ├── 108/                   # ChatGPT Pluginsの作成
│   └── ...
├── nlp_processing/            # 自然言語処理 (34例)
│   ├── 001/                   # 基本的なテキスト処理
│   ├── 030/                   # Transformersを使用したNLP
│   └── ...
├── server_processing/         # サーバー・インフラ処理 (39例)
│   ├── 001/                   # GCP/AWSインスタンス管理
│   ├── 021/                   # Tensorboard接続
│   └── ...
├── image_processing/          # 画像処理・コンピュータビジョン (18例)
│   ├── 001/                   # 基本的な画像処理
│   ├── openpose/              # OpenPose関連
│   └── ...
├── front_end/                 # フロントエンド・アプリ開発
│   ├── web_app/              # Webアプリケーション
│   ├── mobile_app/           # モバイルアプリ
│   └── cross_platform_app/   # クロスプラットフォームアプリ
├── pytorch_tips/              # PyTorch関連Tips (7例)
├── docker_processing/         # Docker・コンテナ化
├── conda_processing/          # Conda環境管理
├── io_processing/             # 入出力・ファイル処理
├── acceleration_processing/   # 高速化・最適化
└── video_processing/          # 動画処理
```

## 🚀 使用方法

### 基本的な使い方

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/Yagami360/ai-product-dev-tips.git
   cd ai-product-dev-tips
   ```

2. **具体例の実行**
   ```bash
   # 例：MLOps例の実行
   cd ml_ops/108
   
   # 依存関係のインストール
   pip install -r requirements.txt
   
   # ローカル開発環境での実行
   ./run_api_dev.sh
   
   # APIテスト
   python request.py --host 0.0.0.0 --port 5000
   ```

### Docker使用例

多くの例でDocker環境が整備されています：

```bash
# Docker環境での実行
cd ml_ops/30
docker-compose up -d

# サービスの確認
docker-compose ps

# ログの確認
docker-compose logs -f
```

### 一般的なコマンドパターン

```bash
# コード品質チェック
make lint
flake8 .

# コードフォーマット
make fmt
black .
isort -rc -sl .

# GKEデプロイ（該当例）
./deploy_api_gke.sh

# Firebase デプロイ（該当例）
./deploy_webapp_firebase.sh
```

## 📁 主要カテゴリの詳細

### MLOps・機械学習基盤 (ml_ops/)
- Docker・Kubernetesを使用した機械学習環境構築
- マイクロサービス型MLアプリケーションアーキテクチャ
- Redis、バッチ処理、監視システムとの連携
- ChatGPT Plugins開発
- クラウドでの本番運用例

### 自然言語処理 (nlp_processing/)
- Transformers（Hugging Face）を使用した最新NLP
- ChatGPT・OpenAI API連携
- テキスト分類、感情分析、要約
- 多言語対応・翻訳システム

### サーバー・インフラ処理 (server_processing/)
- GCP、AWS、Azureでのインスタンス管理
- ポートフォワーディング、VPN設定
- GoogleDriveとの大容量データ転送
- 監視・ロギングシステム

### 画像処理 (image_processing/)
- OpenCV、Pillowを使用した基本画像処理
- OpenPose、DensePoseによる姿勢推定
- セマンティックセグメンテーション
- 画像の品質評価・データオーギュメンテーション

### フロントエンド開発 (front_end/)
- React、Vue.jsを使用したWebアプリ
- Flutterによるクロスプラットフォームモバイルアプリ
- Firebase hosting、GitHub Pagesでのデプロイ

## 💡 開発パターン

### ディレクトリ構成パターン
各例は独立したディレクトリで以下の構成を持ちます：

```
example_directory/
├── README.md              # 日本語での詳細説明
├── requirements.txt       # Python依存関係
├── package.json          # Node.js依存関係（該当例）
├── Dockerfile            # コンテナ定義
├── docker-compose.yml    # マルチサービス設定
├── run_*.sh             # ローカル実行スクリプト
├── deploy_*.sh          # デプロイスクリプト
├── request.py           # APIテストスクリプト
└── app.py              # メインアプリケーション
```

### マイクロサービスアーキテクチャ
多くのML例で以下のサービス構成を採用：

- **predict-server**: ML推論サービス
- **redis-server**: モデル結果キャッシュ
- **batch-server**: バッチ訓練処理
- **proxy-server**: Nginxロードバランシング
- **monitoring-server**: 監視・メトリクス収集

## 🧪 品質管理・テスト

### コード品質
```bash
# リンティング
flake8 .
make lint

# フォーマット
black .
isort -rc -m 3 .
make fmt

# 品質チェック
make check-fmt
isort -rc -m 3 --check-only .
```

### テスト実行
```bash
# 単体テスト
pytest

# APIテスト
python request.py
./run_request.sh
```

## ☁️ クラウドデプロイ

### Google Cloud Platform
```bash
# GKE クラスタデプロイ
./deploy_api_gke.sh
./run_gke.sh

# Cloud Functions デプロイ
gcloud functions deploy function-name

# Firebase Hosting
./deploy_webapp_firebase_hosting.sh
```

### AWS
```bash
# EKS デプロイ
kubectl apply -f k8s/

# Lambda デプロイ
aws lambda create-function
```

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### コントリビューションガイドライン
- 各例は独立したディレクトリで完結させる
- 日本語でのREADME.md作成必須
- Docker環境の提供を推奨
- テスト・リクエストスクリプトを含める
- シェルスクリプトは `set -eu` でエラーハンドリング

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 📞 お問い合わせ

- GitHub Issues: [Issues](https://github.com/Yagami360/ai-product-dev-tips/issues)
- 作成者: [Yagami360](https://github.com/Yagami360)

## 🔗 関連リンク

- [機械学習論文サーベイ記事](https://github.com/Yagami360/MachineLearning-Papers_Survey)
- [DensePose推論API](https://github.com/Yagami360/densepose_wrapper)

---

**このリポジトリがAIプロダクト開発の参考になれば幸いです。スターやフォークをお待ちしております！⭐**