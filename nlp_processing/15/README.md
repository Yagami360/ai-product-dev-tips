# Azure Machine Learning Prompt flow を使用してプロンプトチューニングを行う

Azure Machine Learning Prompt flow を使用すれば、プロンプトチューニングやプロンプト管理も簡単に行える。
より詳細には、Azure Machine Learning Prompt flow では、バリアント（variant）と名付けられた機能でプロンプト管理を行うことができる

## 使用方法

1. 「[Azure Machine Learning Prompt flow の基本的な使い方](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/14)」に従って Prompt flow を作成する

1. 作成された Prompt flow を確認する<br>
    今回の「標準フロー（Standard flow）」の例では、LLM API がジョークを出力するという単純なフローになっている。
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/738031ff-58a1-4ed3-87d8-12413886f1aa"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/746ab5ef-bb52-44ca-8ec3-9863b043191f"><br>

1. Prompt flow のバリアントでプロンプトチューニングを行う<br>
    作成したフローにおける LLM ノード or プロンプトノードの設定で、「複製」ボタンをクリックし、別のプロンプトの変種（バリアント）を作成する<br>

    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/0229dc76-5aab-4ba6-9ff2-b71b8f3ebaaf">

    複製後、LLM ノード or プロンプトノードの同じ設定のバリアント `variant_1` が作成されるので、コピー元のプロンプトとは別のプロンプトを設定する。<br>
    更に、デフォルトのバリアントに変更すれば、新しいプロンプトでフローが実行されるようにする

    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/3dae9eba-37b7-4e66-9810-19aefc6842ea"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/0653201e-6a20-4850-9405-17e3e40e6fad"><br>

    > Azure Machine Learning Prompt flow では、プロンプトID のようなプロンプトを一意に識別する ID は存在しない？

1. Prompt flow を実行する<br>
    入力項目に入力文を入力後、「実行」ボタンをクリックし、この Prompt flow を実行する<br>
    バリアントが複数ある場合は、各々のノードに対してどのバリアントを使うのか？あるいは全てのノードに対してデフォルトのバリアントを使用するのかを選択して実行できる。

    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/e68f44c9-7f2f-484c-87a9-8fe767012deb"><br>

    今回の例では、新しいプロンプトのバリアント `variant_1` で処理を行うので、出力結果が英語から日本語になる

## 参考サイト

- 公式ドキュメント
    - https://learn.microsoft.com/ja-jp/azure/machine-learning/prompt-flow/how-to-tune-prompts-using-variants?view=azureml-api-2
