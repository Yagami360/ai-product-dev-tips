# Dify の基本的な使い方（ワークフローを使用した LLM アプリケーションを作成する）

## 使用方法

1. [Dify のコンソール UI](https://cloud.dify.ai/apps) から「スタジオ」に移動する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/d9b6ded0-2bc4-48a8-aeaf-7c4e8e94bbbb"><br>

1. 「アプリを作成する」->「最初から作成する」ボタンをクリックし、アプリを作成する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/67cc635a-a3e6-432c-9106-d5f4db90dabd">

    - 今回は独自のワークフローを作成するので、アプリのタイプとして「ワークフロー」のタイプを選択する

    アプリ作成後、以下のような空のチャットワークフローの UI が表示される<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/aecfe530-e7a0-4c58-8b60-2286691f8199">

1. `開始ノード` の設定を行う<br>
    `開始ノード` をクリックすると、`開始ノード` の設定画面が表示される。<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/099af950-cfce-4c65-9217-92a9e376d709">


    `開始ノード` では、ワークフロー全体の入力変数を設定できる。デフォルトで設定されている入力変数 `sys.xxx` には以下のようなものがある

    - `sys.user_id`: ユーザーを識別するための一意の ID
    - `sys.files`: アップロードされた入力ファイル（活用例：画像ファイルがアップロードされるとその画像の内容をテキストで回答する）

    独自の入力変数を設定したい場合は、「入力フィールド」->「`+`」ボタンをクリックして、追加した入力変数を設定する<br>
    今回の例では、ユーザーからの入力文を表す `input_text` という入力変数を追加する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/071ab12a-0727-4d7b-a25e-37e74f977c68">

<!--
    - `sys.query`: ユーザーからの質問入力文
    - `sys.conversation_id`: ユーザーとチャットボット間のチャットを識別するための一意の ID
-->

1. `LLM ノード` をの設定を行う<br>
    `開始ノード` の右横の「`+`」ボタンをクリックし、開始ノードの次に行うノードを追加する。<br>
    今回の例では、簡単のため `LLMブロック` を追加し、OpenAI の `gpt-3.5-turbo` の LLM モデルのノードを追加する<br>

    <img width="800" alt="image" src="https://github.com/user-attachments/assets/803b7bce-8cb3-494c-a70a-e42fffc0a8a5"><br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/09c8f60a-9da3-4ae4-bbb1-f9dcffbb8b94"><br>

    今回の例では、ユーザーからの入力文 `input_text` に対して、LLM ノードがアニメ口調で回答を行うようにしたいので、例えば以下のようなプロンプト文の設定を行う<br>

    <img width="800" alt="image" src="https://github.com/user-attachments/assets/2329ad28-bd20-4220-9008-642aadd10d4d">

1. `終了ノード` の設定を行う<br>
    ワークフローは、最後に `終了ノード` を追加することで終了させる必要がある。
    今回の例では簡単のため `LLMノード` の右横の「`+`」ボタンをクリックし、LLM ノードの次に終了ノードを設定する。<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/75fe2dea-5e90-4754-8dae-bb91466d7549">

    今回の例では、LLM ノードからの回答を出力したいので、出力変数として LLM ノードからの出力変数である `text` を設定する
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/66cdb4ff-5e98-49a6-b022-b48ab4e827be">

1. ワークフローを実行する<br>
    ノードの作成が完了したら、画面右上の「`▶ 実行`」ボタンをクリックし、作成したワークフローを実行する。<br>
    実行時に入力変数の入力が求められるので、入力変数の値（今回の例では、ユーザーからの質問文である `input_text`）を入力して実行する<br>

    <img width="800" alt="image" src="https://github.com/user-attachments/assets/6444a8b9-92b7-4b8a-b8f7-ec1cc9afc0d3">

    ワークフローが実行され、ユーザーからの質問文 `input_text` に対して、以下のように回答が出力される。

    <img width="800" alt="image" src="https://github.com/user-attachments/assets/eae3e14e-9a77-4afe-8913-9c8bdb86268c">

1. 【オプション】実行トーレスを確認する<br>
    実行したワークフローに対して、｛各ノードの実行時間・トークン数・コスト｝などの実行トーレスも確認できる

    <img width="800" alt="image" src="https://github.com/user-attachments/assets/7a59494c-08ff-4de3-9956-d873f6c83eac">

## 参考サイト
