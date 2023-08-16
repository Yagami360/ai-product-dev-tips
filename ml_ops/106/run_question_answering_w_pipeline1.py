import argparse

from transformers import pipeline


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--context', type=str, help="コンテキスト（入力する文章）", default="Extractive Question Answering is the task of extracting an answer from a text given a question. An example of a question answering dataset is the SQuAD dataset, which is entirely based on that task. If you would like to fine-tune a model on a SQuAD task, you may leverage the `run_squad.py`.")
    parser.add_argument('--question', type=str, help="質問文", default="What is extractive question answering?")
    args = parser.parse_args()

    # 質疑応答タスクの Pipeline 定義
    qa_pipeline = pipeline("question-answering")

    # 質問応答 NLP モデルの推論
    try:
        predict = qa_pipeline(question=args.question, context=args.context)
        print(f"predict: {predict}")
    except Exception as e:
        print(f"Exception was occured | {e}")
        exit(1)

    exit(0)
