# Dify の基本的な使い方（チャットボット用ワークフロー）

## 使用方法

1. [Dify のコンソール UI](https://cloud.dify.ai/apps) から「スタジオ」に移動する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/d9b6ded0-2bc4-48a8-aeaf-7c4e8e94bbbb"><br>

1. 「アプリを作成する」->「最初から作成する」ボタンをクリックし、アプリを作成する<br>
    <img width="300" alt="image" src="https://github.com/user-attachments/assets/ef02b2fe-642e-4764-8c48-960b2a9faa39"><br>

    - 今回は、サンプルとしてチャットボットのアプリを作成するので、アプリのタイプとして「チャットボット」のタイプを選択する

    - またチャットボット用ワークフローを使用するので、オーケストレーション方法として「Chatflow」を選択する

1. 作成されたアプリのワークフローを確認する<br>
    アプリ作成後、以下のようなチャットワークフローの UI が表示される<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/98f250b7-2886-4214-bf58-903fd4cd7fe8">

1. 入力ノード（開始ノード）の設定を行う<br>
    開始ノードをクリックすると、開始ノードの設定画面が表示される。<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/823d053c-fd00-4f83-90e2-26c4de5ebbd7">

    開始ノードでは、ワークフロー全体の入力変数を設定できる。設定可能な入力変数には以下のようなものがある

    - `sys.query`: ユーザーからの質問入力文
    - `sys.files`: アップロードされた入力ファイル（活用例：画像ファイルがアップロードされるとその画像の内容をテキストで回答する）
    - `sys.user_id`: ユーザーを識別するための一意の ID
    - `sys.conversation_id`: ユーザーとチャットボット間のチャットを識別するための一意の ID

    独自の入力変数を設定したい場合は、「入力フィールド」->「`+`」ボタンをクリックして、追加した入力変数を設定する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/47cdc981-0ffc-4797-9c11-fcb5b0b63e82">

1. LLM ノードをの設定を行う<br>
    今回の初期設定の例では、OpenAI の `gpt-3.5-turbo` の LLM モデルを使用して回答を行う設定になっている

1. 出力ノード（回答ノード）の設定を行う<br>


1. ワークフローを実行する<br>



## 参考サイト

- https://www.ai-souken.com/article/what-is-dify
