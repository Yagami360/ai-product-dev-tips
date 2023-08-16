# 【Python】Hugging Face Spaces を利用して簡単な機械学習デモアプリを構築する

Hugging Face Spaces は、機械学習モデルのデモアプリを Hugging Face レポジトリ上で実行できる機能。    

機械学習モデルのデモアプリのコードとしては、以下のものが利用可能。ここでは、Gradio を利用する

- Gradio<br>
    機械学習モデルのデモアプリを簡単に作成するための Python製 UI ライブラリ

- Streamlit<br>

- Docker<br>
    一応可能レベル？

## 使用方法

1. Hugging Face のコンソール UI から Space のレポジトリを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/12ffb62a-5894-4c06-86fe-329b58cc3fd9"><br>
    <img width="416" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/b131ac67-f9b1-49e7-82e2-c27ba7c894d8"><br>

1. Space のレポジトリを git clone する<br>
    ```sh
    git clone https://huggingface.co/spaces/${ユーザー名}/${レポジトリ名}
    ```

1. Gradio を用いたデモアプリの Python コードを実装する<br>
    - `app.py`
        ```python
        import gradio as gr
        from transformers import pipeline

        # ホットドッグ画像分類モデルのパイプライン
        pipeline = pipeline(task="image-classification", model="julien-c/hotdog-not-hotdog")

        # ホットドッグ画像分類モデルの推論処理を行うメソッド
        def predict(image):
            predictions = pipeline(image)
            return {p["label"]: p["score"] for p in predictions}

        # gradio を使用した機械学習モデルのデモアプリ定義
        demo = gr.Interface(
            predict,                                                                    # inputs -> outputs を得るための関数（通常推論関数）を指定
            inputs=gr.inputs.Image(label="Upload hot dog candidate", type="filepath"),  # 入力データ
            outputs=gr.outputs.Label(num_top_classes=2),                                # 出力データ
            title="Hot Dog? Or Not?",
        )

        # デモアプリ起動
        demo.launch()
        ```

        ポイントは、以下の通り

        - Hugging Face Transformers の Pipeline を用いて、ホットドッグ画像分類モデル `julien-c/hotdog-not-hotdog` とその推論処理を定義

        - gradio を使用して、ホットドッグ画像分類モデルのデモアプリ定義


1. `requirements.txt` を追加する<br>
    今回の `app.py` では、Hugging Face Transformers を使用しており、また pipeline 内部の機械学習モデルで PyTorch を使用しているので、例えば以下のような `requirements.txt` を定義する
    ```txt
    transformers
    torch
    ```

1. Hugging Face レポジトリ（Space）に git push する<br>
    ```sh
    cd ${レポジトリ名}
    git add .
    git commit -m "Add application file"
    git push
    ```

1. Hugging Face レポジトリ（Space）上からデモアプリを実行する<br>
    <img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/714118b9-b182-4519-8d13-094f7dc9816b"><br>
    <img width="1000" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/34050a93-f80a-4730-9067-eb0f9e21528a"><br>

## 参考サイト

- https://huggingface.co/docs/hub/spaces-overview
- https://huggingface.co/docs/hub/spaces-sdks-gradio