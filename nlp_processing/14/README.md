# Azure Machine Learning Prompt flow の基本的な使い方

## 使用方法

1. [Azure コンソール UI](https://portal.azure.com/?quickstart=true#home) から `Azure Machine Learing` を選択する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/60cdfa98-c95e-4e3e-a0eb-014733d26de3"><br>

1. `Azure Machine Learing` のワークスペースを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/f44e8328-b72c-44ec-a775-b609c47eba4d"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/25136f7d-95c1-43f2-8e0f-1c00d904ee81"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/82f90f65-2da0-42d3-bc05-d613fc7a3c2e"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/b2eadd87-8df6-4cf8-a140-2307276b0c50"><br>

1. ワークスペースから `Azure Machine Learning Studio` を起動する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/88d1d875-885a-4b1d-99e0-45f6af9303db"><br>

1. Prompt flow を作成する<br>
    `Azure Machine Learning Studio` のワークスペースから、Prompt flow を作成する。<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/77f1159d-1633-40f7-85ed-c02570a62e63"><br>

    今回は簡単のため、既存の「標準フロー（Standard flow）」を選択する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/49ffd07b-8123-4d80-8314-d3cc423bd40d"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/9289215a-f85b-4783-88fb-8169d72f69ff"><br>

1. 作成された Prompt flow を確認する<br>
    今回の「標準フロー（Standard flow）」の例では、LLM API がジョークを出力するという単純なフローになっている。
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/738031ff-58a1-4ed3-87d8-12413886f1aa"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/746ab5ef-bb52-44ca-8ec3-9863b043191f"><br>

1. Prompt flow で使用する LLM API の設定を行う<br>
    LLM API を呼び出している箇所は、使用する LLM API（Azure OpenAI API, OpenAI API など）を設定する。<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/633cba47-289d-47af-b98b-06050cb46b92"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/19b7c0cb-25b8-4ff7-b91f-7c130b5b03c7"><br>

    API 接続後、LLM API の各種パラメーターも設定することができる。
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/546a20fa-fa4a-4daa-a152-27effca1244e">


1. Prompt flow を実行するための Runtime を作成する<br>
    Prompt flow を実行するための Runtime（Docker や各種ライブラリなどの実行環境がインストールされた VM インスタンス）を作成する。今回は簡単のため「自動ランタイム」で作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/6583ee31-5565-4f4c-a77f-933ba9b058aa"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/f0614f1c-ae2e-4dcb-af5d-2c97e378f10b"><br>

    > Runtime 起動中は、コストが発生することに注意。デフォルト設定では、Runtime 起動後に1時間アイドリング状態なら Runtime は自動的に停止するようになっている

1. Prompt flow を実行する<br>
    入力項目に入力文を入力後、「実行」ボタンをクリックし、この Prompt flow を実行する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/255944c8-1e3d-42a8-ad49-a7266f61ca42">

1. Prompt flow の実行結果を確認する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/3986d3e4-dd75-4c26-b9f9-40555ada39ec"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/5874ff4f-6ce7-4124-b0d7-be9055134513"><br>

## 参考サイト

- https://qiita.com/sergicalsix/items/05110edb2b66c7a53d37
- 公式ドキュメント
    - https://learn.microsoft.com/ja-jp/azure/machine-learning/prompt-flow/get-started-prompt-flow?view=azureml-api-2