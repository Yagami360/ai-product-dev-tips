# Tip README フォーマット リファレンス

このリポジトリの実際の Tip はかなり多様です。
大きく分けて3つの形があります。
書こうとしている Tip に最も近いものを選び、実在する兄弟 Tip を真似てください。
README は常に日本語で書きます。

## 形A — 概念・概要系の Tip

ネストされたインデントと `<br>` の改行を使った解説的な箇条書き、図、コード/JSON のフェンスブロックで構成し、末尾を `## 参考サイト` で締める。

```markdown
# NVIDIA AI Enterprise & NVIDIA NeMo の概要

- NVIDIA AI Enterprise<br>
    NVIDIA が提供している... プラットフォーム。以下のサービス群から構成される

    - NVIDIA NeMo フレームワーク<br>
        ```mermaid
        flowchart LR
            A[データ準備] --> B[学習] --> C[推論] --> D[デプロイ]
        ```
        NLP や音声系の生成 AI の開発を支援するフレームワーク。

    - NVIDIA NIM<br>
        生成 AI モデルを推論 API として容易に利用できるサービス。

## 参考サイト

- 公式ユーザーガイド: https://docs.nvidia.com/...
- https://developer.nvidia.com/...
```

（実例: `nlp_processing/33`, `nlp_processing/31`）

## 形B — 手順・「使い方」系の Tip

タイトル + 任意の導入 + `## 使用方法`。
読者が実行する「外部から見た」手順を番号付きリストで書く。
各手順を `1.` で始める（GitHub が自動採番）。
コマンドは ```sh / ```bash ブロックに入れる。
末尾を `## 参考サイト` で締める。

```markdown
# NVIDIA NeMo を使用して LLM の推論処理を行う

## 使用方法

1. GPU ありのインスタンス環境を用意する

1. NVIDIA NeMo をインストールする

    - （推奨）Docker を使用する場合
        ```bash
        docker pull nvcr.io/nvidia/nemo:24.12
        ```

1. NeMo を使用したスクリプトを作成する

    - 例: [`run.py`](run.py)

1. NeMo を使用したスクリプトを実行する
    ```bash
    docker run --gpus all -it --rm -v $(pwd):/workspace \
        nvcr.io/nvidia/nemo:24.12 /bin/bash -c "python3 run.py --device cuda"
    ```

## 参考サイト

- 公式ユーザーガイド: https://docs.nvidia.com/...
```

（実例: `nlp_processing/32`, `nlp_processing/34`）

## 形C — コード解説系の Tip

タイトル + 手法を説明する導入 + `## 方法` / `## 使用方法` / `## 実現方法` セクション。
Tip がコードを同梱する場合はファイルをリンクし、必要なら「コードの主なポイント」（重要な設計判断）を短い箇条書きで添える。
1行ずつの逐次解説はしない。
画像処理系の Tip は、`## 機械学習の文脈での用途` / `## 実現方法` / `## 入出力データ` という構成を取り、入出力データに画像を載せることが多い（実例: `image_processing/14`, `image_processing/11`）。

```markdown
# 【Python】OpenCV を使用して画像のヒストグラム平坦化でコントラストを改善する。

OpenCV を用いて、画像のヒストグラム平坦化でコントラストを改善する方法を紹介する。

## 機械学習の文脈での用途

- 撮影条件がばらついた学習データの前処理として、コントラストを揃える目的で利用できる。

## 実現方法

- カラー画像は YCrCb に変換し、輝度成分のみを平坦化することで色味を保つ。
    ```python
    y_eq = cv2.equalizeHist(y)
    ```

- 追加した Python コードの主なポイント
    - 処理スクリプト: [`equalize_hist.py`](equalize_hist.py)
        - `--method {global, clahe}` で平坦化の方法を切り替えられる

## 使用方法

1. 入力画像を `in_image/` に配置する

1. スクリプトを実行する
    ```sh
    sh image_processing_18.sh
    ```

## 入出力データ

- 入力データ<br>
    <!-- TODO: 入力画像を貼り付け -->

- 出力データ<br>
    <!-- TODO: 出力画像を貼り付け -->

## 参考サイト

- OpenCV 公式チュートリアル: https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
```

（実例: `nlp_processing/29`, `image_processing/14`）

## 慣習チェックリスト

- H1 タイトルは近隣のスタイルに合わせる。
  `【Python】` / `【シェルスクリプト】` のプレフィックスは、その言語の兄弟 Tip が付けているときだけ付ける。
- 図は ```mermaid を優先（アップロード不要）。
  実スクリーンショットが必要なときだけ `<img width="500" alt="Image" src="https://github.com/user-attachments/assets/..." />` を使い、アップロードできないので `<!-- TODO: 画像を貼り付け -->` のプレースホルダを残す。
  図には構造・グルーピング・フローの情報を持たせる（単純な放射状の列挙で終わらせない）。
- 手順は、内部実装ではなく、どう実行・使用するか（外部視点）を書く。
  具体的な実行コマンド・操作で書き、曖昧な説明で済ませない。
- コード付き Tip では、追加コードの「主なポイント」箇条書きを推奨。
- 同梱ファイルは相対リンクで参照する（``[`train.py`](train.py)``）。
- 参考 URL は末尾の `## 参考サイト` に箇条書きで置く。
  現行の公式 URL かユーザー提供のものを使い、古い／存在しない可能性のある URL を推測で書かない。
- 正確性をもっともらしさより優先する。
  事実・コマンド名・URL・バージョンは確認して書き、不確実なものは断定せず `<!-- TODO: 要確認 -->` を残すか、ユーザーに確認する。
