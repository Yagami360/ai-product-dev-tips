# 【Python】Huggingface Transformers を使用して NLP モデルの推論処理を行う
Huggingface Transformers は、Huggingface で提供されているライブラリの１つで、自然言語処理モデルを簡単に使用できるようにするライブラリになっている。<br>
具体的には、学習済みモデルの利用・独自データセットでの事前学習・モデルのファインチューニングを行うためのツール等を提供しており、テキスト分類・情報抽出・質問応答・テキスト生成などの各種 NLP タスクを容易に実行できるようになっている。また、多数のプログラミング言語（Python、Node.js、Rustなど）に対応している。

- Huggingface Transformers が提供する NLP モデル<br>
    [公式ドキュメント](https://huggingface.co/docs/transformers/index#supported-models) を参照

Huggingface Transformers を用いて NLP モデルの推論を行うためには、以下の２つの方法がある

1. Pipeline を使用する方法<br>
    NLP モデルの推論処理を簡単に実装できる。
    但し、実装可能なNLP タスクが（Text classification, Text generation, question-answering, conversation, ... などに）限定される

1. Pipeline を使用しない方法<br>
    Pipeline を使用する方法に比べて、NLP モデルの推論処理の実装が複雑になるが、実装可能なNLP タスクや NLP モデルの柔軟性が高い

## 使用方法

1. Huggingface Transformers と Datasets のライブラリをインストールする<br>
    ```sh
    pip3 install transformers, datasets
    ```
    > Huggingface Datasets: 大規模なデータセットの処理と操作を効率的に行うためのライブラリ

1. Tensorflow と PyTorch をインストールする<br>
    Huggingface Transformers 内部の NLP モデルでは、Tensorflow か PyTorch を使用しているので、それぞれインストールする
    ```sh
    pip3 install tensorflow
    pip3 install torch
    ```

1. Huggingface Transformers を使用した Python コードを実装する<br>
    - Pipeline を使用する場合
        - 例１：質問応答タスクの場合（`run_question_answering_w_pipeline1.py`）
            ```python
            import argparse

            from transformers import pipeline

            if __name__ == '__main__':
                parser = argparse.ArgumentParser()
                parser.add_argument('--context', type=str, help="コンテキスト（入力する文章）", default="Extractive Question Answering is the task of extracting an answer from a text given a question. An example of a question answering dataset is the SQuAD dataset, which is entirely based on that task. If you would like to fine-tune a model on a SQuAD task, you may leverage the `run_squad.py`.")
                parser.add_argument('--question', type=str, help="質問文", default="What is extractive question answering?")
                parser.add_argument('--out_dir', type=str, default="out_dir/")
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
            ```

            ポイントは、以下の通り

            - 質問回答とは、与えられたテキスト（入力文）に対しての質問の回答を抽出するタスク。`content` 引数に与えられたテキスト（入力文）を渡し、質問を `question` 引数に渡す。

            - NLP モデルを明示的に定義していないが、どのモデルを使用している？

        - 例２：質問応答タスクの場合（`run_question_answering_w_pipeline2.py`）
            ```python
            import argparse

            from transformers import AutoTokenizer, AutoModelForQuestionAnswering
            from transformers import QuestionAnsweringPipeline

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

                # 質疑応答タスクの Pipeline 定義
                qa_pipeline = QuestionAnsweringPipeline(tokenizer=tokenizer, model=qa_model)

                # 質問応答 NLP モデルの推論
                try:
                    predict = qa_pipeline(question=args.question, context=args.context)
                    print(f"predict: {predict}")
                except Exception as e:
                    print(f"Exception was occured | {e}")
                    exit(1)

                exit(0)
            ```

            ポイントは、以下の通り

            - Tokenizer と QA の NLP モデルを定義<br>
                - この例では Tokenizer と QA の NLP モデルは、BERT のモデル（それぞれ `bert-large-uncased-whole-word-masking-finetuned-squad`）を使用している

            - 文章のトークン化処理は明示的に行われていないようなコードになっているが、QuestionAnsweringPipeline に Tokenizer のオブジェクトを渡しているので、Pipeline 内部でよしなに行っていると思われる

            - 質問回答とは、与えられたテキスト（入力文）に対しての質問の回答を抽出するタスク。`content` 引数に与えられたテキスト（入力文）を渡し、質問を `question` 引数に渡す。

    - Pipeline を使用しない場合<br>
        - 例：質問応答タスクの場合（`run_question_answering_wo_pipeline.py`）
            ```python
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
            ```

            ポイントは、以下の通り

            - Tokenizer と QA の NLP モデルを定義<br>
                - この例では Tokenizer と QA の NLP モデルは、BERT のモデル（それぞれ `bert-large-uncased-whole-word-masking-finetuned-squad`）を使用している

            - Tokenizer で入力分と質問文トークン化（単語に分割）<br>
                今回の例では、以下のようになる
                ```sh
                text_tokens=['[CLS]', 'what', 'is', 'extract', '##ive', 'question', 'answering', '?', '[SEP]', 'extract', '##ive', 'question', 'answering', 'is', 'the', 'task', 'of', 'extract', '##ing', 'an', 'answer', 'from', 'a', 'text', 'given', 'a', 'question', '.', 'an', 'example', 'of', 'a', 'question', 'answering', 'data', '##set', 'is', 'the', 'squad', 'data', '##set', ',', 'which', 'is', 'entirely', 'based', 'on', 'that', 'task', '.', 'if', 'you', 'would', 'like', 'to', 'fine', '-', 'tune', 'a', 'model', 'on', 'a', 'squad', 'task', ',', 'you', 'may', 'leverage', 'the', '`', 'run', '_', 'squad', '.', 'p', '##y', '`', '.', '[SEP]']
                ```

            - Tokenizer でトークン化した各単語をID化する<br>
                今回の例では、以下のようになる<br>
                ```sh
                input_ids=[101, 2054, 2003, 14817, 3512, 3160, 10739, 1029, 102, 14817, 3512, 3160, 10739, 2003, 1996, 4708, 1997, 14817, 2075, 2019, 3437, 2013, 1037, 3793, 2445, 1037, 3160, 1012, 2019, 2742, 1997, 1037, 3160, 10739, 2951, 13462, 2003, 1996, 4686, 2951, 13462, 1010, 2029, 2003, 4498, 2241, 2006, 2008, 4708, 1012, 2065, 2017, 2052, 2066, 2000, 2986, 1011, 8694, 1037, 2944, 2006, 1037, 4686, 4708, 1010, 2017, 2089, 21155, 1996, 1036, 2448, 1035, 4686, 1012, 1052, 2100, 1036, 1012, 102]
                ```                

            - Tokenizer でトークン化したデータ `inputs` を NLP モデルに入力する<br>
                ```python
                answer_start_scores, answer_end_scores = qa_model(**inputs)
                ```

1. Python コードを実行する<br>
    - `run_question_answering_w_pipeline1.py`
        ```sh
        python3 run_question_answering_w_pipeline1.py
        ```

    - `run_question_answering_w_pipeline2.py`
        ```sh
        python3 run_question_answering_w_pipeline2.py
        ```

    - `run_question_answering_wo_pipeline.py`
        ```sh
        python3 run_question_answering_wo_pipeline.py
        ```
        ```sh
        question: What is extractive question answering?
        answer: the task of extracting an answer from a text given a question
        ```

## 参考サイト

- https://huggingface.co/docs/transformers/index
- https://zenn.dev/novel_techblog/articles/362fceec01c8b1
- https://note.com/npaka/n/n5bb043191cc9
