import argparse
import torch

from transformers import AutoTokenizer, AutoModelForQuestionAnswering


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokenizer_model', type=str, default="bert-large-uncased-whole-word-masking-finetuned-squad")
    parser.add_argument('--qa_model', type=str, default="bert-large-uncased-whole-word-masking-finetuned-squad")
    parser.add_argument('--context', type=str, help="コンテキスト（入力する文章）", default="Extractive Question Answering is the task of extracting an answer from a text given a question. An example of a question answering dataset is the SQuAD dataset, which is entirely based on that task. If you would like to fine-tune a model on a SQuAD task, you may leverage the `run_squad.py`.")
    parser.add_argument('--question', type=str, help="質問文", default="What is extractive question answering?")
    args = parser.parse_args()

    # Tokenizer 定義
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_model)
    
    # NLP モデル定義
    qa_model = AutoModelForQuestionAnswering.from_pretrained(args.qa_model)

    # Tokenizer でトークン化（単語に分割）し、各単語に ID を付与
    inputs = tokenizer.encode_plus(args.question, args.context, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]
    print(f"inputs={inputs}")
    print(f"input_ids={input_ids}")

    # 【デバック】ID化したトークンから単語のトークン
    text_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    print(f"text_tokens={text_tokens}")

    # 質問応答 NLP モデルの推論。Tokenizer でトークン化したデータ `inputs` を NLP モデルに入力する
    predict = qa_model(**inputs)
    print(f"predict={predict}")

    # 最大確率の回答取得
    answer_start = torch.argmax(predict.start_logits)  
    answer_end = torch.argmax(predict.end_logits) + 1 
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    print(f"question: {args.question}")
    print(f"answer: {answer}\n")
