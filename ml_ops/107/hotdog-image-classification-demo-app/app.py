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
