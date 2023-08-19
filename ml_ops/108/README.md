# 【Python】ChatGPT plugins を利用＆作成する

## ChatGPT plugins の利用方法

1. 【事前準備】ChatGPT Plus ユーザーとして登録する

1. 「Settings & Beta」->「Beta features」->「Plugins」を有効化する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/0300bc66-7758-4b7c-9348-f71914653052"><br>

1. 「GPT-4」をマウスオーバーし、「Plugins（Beta）」を選択する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/76e3a514-f945-4111-9c8b-37126b03e9c9"><br>

1. 「No plugins enabled」->「Plugin store」を選択し、使用したい Plugin を選択する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/3453dc30-4c80-454b-9455-1b03b66a828d"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/7c803a60-a88f-43f3-9999-96cc6d68a170"><br>


## ChatGPT plugins の作成方法

1. 【事前準備】ChatGPT Plus ユーザーとして登録する

1. 【事前準備】ChatGPT Plugins waitlist に登録する<br>
    [こちらのページ](https://openai.com/waitlist/plugins) から ChatGPT plugins を作成するための利用登録を行う

1. ChatGPT plugins が呼び出す API の作成<br>
    1. API コードを作成する<br>
        今回の例では、以下のような Flask API をコード `app.py` を作成する
        ```python
        import argparse
        import io
        import json

        import flask
        from flask_cors import CORS
        from PIL import Image

        app = flask.Flask(__name__)

        # OPTIONS を受け取らないようにする（Access-Control-Allow-Origin エラー対策）
        CORS(
            app,
            resources={r"*": {"origins": "https://chat.openai.com"}},
            methods=["POST", "GET", "DELETE"],
        )
        # 日本語文字化け対策
        app.config["JSON_AS_ASCII"] = False
        # ソートをそのまま
        app.config["JSON_SORT_KEYS"] = False

        # TODO List（API 起動時は空）
        _TODOS = {}

        # ---------------------------------------
        # ChatGPT Plugin API で共通に必要な API
        # ---------------------------------------


        @app.route("/.well-known/ai-plugin.json", methods=["GET"])
        def plugin_manifest():
            with open("./.well-known/ai-plugin.json") as f:
                json_text = f.read()

            resp = flask.Response(response=json_text, status=200, mimetype="application/json")
            return resp


        @app.route("/openapi.yaml", methods=["GET"])
        def openapi_spec():
            with open("openapi.yaml") as f:
                yaml_text = f.read()

            resp = flask.Response(response=yaml_text, status=200, mimetype="text/yaml")
            return resp


        @app.route("/logo.png", methods=["GET"])
        def plugin_logo():
            img_pillow = Image.open("logo.png")
            img_io = io.BytesIO()
            img_pillow.save(img_io, "PNG")
            img_io.seek(0)

            resp = flask.Response(response=img_io, status=200, mimetype="image/png")
            return resp


        # ---------------------------------------
        # TODO API
        # ---------------------------------------

        # TODO 追加 API
        @app.route("/todos/<username>", methods=["POST"])
        def add_todo(username):
            print(f"[add_todo] username={username}")
            if flask.request.headers["Content-Type"] != "application/json":
                resp = flask.Response(response="NG", status=400, mimetype="application/json")
                return resp

            # リクエスト body の todo 内容を取得
            json_body = flask.request.get_json()
            print(f"[add_todo] json_body={json_body}")
            todo = json_body["todo"]

            # _TODOS の配列に {"username": ["todo1", "todo2", ...]} の形式で追加
            if username not in _TODOS:
                _TODOS[username] = []
            _TODOS[username].append(todo)

            resp = flask.Response(response="OK", status=200)
            return resp


        # TODO 取得 API
        @app.route("/todos/<username>", methods=["GET"])
        def get_todos(username):
            resp = flask.Response(response=json.dumps(_TODOS.get(username, [])), status=200)
            return resp


        # TODO 削除 API
        @app.route("/todos/<username>", methods=["DELETE"])
        def delete_todo(username):
            if flask.request.headers["Content-Type"] != "application/json":
                resp = flask.Response(response="NG", status=400, mimetype="application/json")
                return resp

            # リクエスト body の todo 内容を取得
            json_body = flask.request.get_json()
            todo_idx = json_body["todo_idx"]

            # delete todo
            if 0 <= todo_idx < len(_TODOS[username]):
                _TODOS[username].pop(todo_idx)

            resp = flask.Response(response="OK", status=200)
            return resp


        if __name__ == "__main__":
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "--host", type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）"
            )
            parser.add_argument("--port", type=str, default="5000", help="ポート番号")
            args = parser.parse_args()

            # API サーバー起動
            app.run(host=args.host, port=args.port, debug=True)
        ```

        ポイントは、以下の通り

        - ChatGPT Plugin の API では、以下のエンドポイントを共通で定義する必要がある
            - `ai-plugin.json` を取得するための API
                - エンドポイント : `${API_URL}/.well-known/ai-plugin.json`
                - メソッド: `GET`
                - レスポンスデータ: `ai-plugin.json` の text データ

            - `openapi.yaml` を取得するための API
                - エンドポイント : `${API_URL}/openapi.yaml`
                - メソッド: `GET`
                - レスポンスデータ: `openapi.yaml` の text データ

            - `logo.png` を取得するための API
                - エンドポイント : `${API_URL}/logo.png`
                - メソッド: `GET`
                - レスポンスデータ: `logo.png` の画像データ

        - 今回の例では、TODOリストの追加・取得・削除を行う GET, POST, DELETE の API を追加している


    1. Dockerfile を作成する<br>
        ```Dockerfile
        FROM python:3.9-buster

        # install basic libs
        ENV DEBIAN_FRONTEND noninteractive

        RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
            curl \
            wget \
            sudo \
            python3-pip \
            && apt-get clean \
            && rm -rf /var/lib/apt/lists/*

        RUN pip3 install --upgrade pip

        # define ARG and ENV
        ARG WORKDIR="/app"
        ENV WORKDIR=${WORKDIR}

        ENV LC_ALL=C.UTF-8
        ENV export LANG=C.UTF-8
        ENV PYTHONIOENCODING utf-8

        # install dependences
        WORKDIR ${WORKDIR}
        COPY requirements.txt .
        RUN pip3 install -r requirements.txt

        # write src
        COPY . ${WORKDIR}

        # set workdir
        WORKDIR ${WORKDIR}
        ```

    1. docker-compose.yaml を作成する
        ```yml
        version: '3.4'

        services:
          chatgpt-plugin-api-server:
            container_name: chatgpt-plugin-api-server
            image: chatgpt-plugin-api-server
            build:
              context: "."
              dockerfile: Dockerfile
            volumes:
              - ${PWD}:/app
            ports:
              - "5000:5000"
            tty: true
            environment:
            LOG_LEVEL: DEBUG
            command: python3 app.py
        ```

1. ChatGPT plugins の json マニフェストファイルを作成する<br>
    `.well-known` ディレクトリ以下に、ChatGPT plugins のメタデータを定義した json マニフェストファイル `.well-known/ai-plugin.json` を作成する

    ```json
    {
        "schema_version": "v1",
        "name_for_human": "TODO List (no auth)",
        "name_for_model": "todo",
        "description_for_human": "Manage your TODO list. You can add, remove and view your TODOs.",
        "description_for_model": "Plugin for managing a TODO list, you can add, remove and view your TODOs.",
        "auth": {
        "type": "none"
        },
        "api": {
        "type": "openapi",
        "url": "http://localhost:5000/openapi.yaml"
        },
        "logo_url": "http://localhost:5000/logo.png",
        "contact_email": "legal@example.com",
        "legal_info_url": "http://example.com/legal"
    }
    ```

    ポイントは、以下の通り

    - `description_for_model` で定義したワードをもとに ChatGPT がどの API を起動すべきなのかを判断しているので、このフィールドにどのような文字列を設定するかが重要になる。<br>
        例えば、今回のケースでは `description_for_model="Plugin for managing a TODO list, you can add, remove and view your TODOs."`（TODOリストを管理するためのプラグインで、TODOを追加、削除、表示できます。）なので、本プラグイン適用後の ChatGPT に「買い物にいくを todo に追加してください」を送ると、本プラグインの API で実装されている TODOリスト 追加 API が ChatGPT から呼び出され、応答メッセージ（例：買い物にいくを TODO に追加しました。他に何かお手伝いできることはありますか？）が返信されるようになる<br>

        詳細は、[こちらのページ](https://platform.openai.com/docs/plugins/getting-started/writing-descriptions) を参照

1. ChatGPT plugins が呼び出す API の API 仕様を定義した yaml マニフェストファイル `openapi.yaml` を作成する<br>
    ```yml
    openapi: 3.0.1
    info:
    title: TODO Plugin
    description: A plugin that allows the user to create and manage a TODO list using ChatGPT. If you do not know the user's username, ask them first before making queries to the plugin. Otherwise, use the username "global".
    version: 'v1'
    servers:
    - url: http://localhost:5000  # API の URL
    paths:
    # API のエンドポイント毎の定義
    /todos/{username}:
        # GET method
        get:
        operationId: getTodos
        summary: Get the list of todos
        # パスパラメータ
        parameters:
        - in: path
            name: username
            schema:
                type: string
            required: true
            description: The name of the user.
        # レスポンス定義
        responses:
            # ステータスコード: 200 => {"OK", ["todo1", "todo2", ...]}
            "200":
            description: OK
            content:
                # json レスポンス
                application/json:
                # components.schemas フィールドで定義しているものの参照
                schema:
                    $ref: '#/components/schemas/getTodosResponse'
        # POST method
        post:
        operationId: addTodo
        summary: Add a todo to the list
        # パスパラメータ
        parameters:
        - in: path
            name: username
            schema:
                type: string
            required: true
            description: The name of the user.
        # リクエスト body 定義
        requestBody:
            required: true
            content:
            application/json:
                schema:
                $ref: '#/components/schemas/addTodoRequest'
        # レスポンス定義
        responses:
            # ステータスコード: 200 => {"OK"}
            "200":
            description: OK
        # DELETE method
        delete:
        operationId: deleteTodo
        summary: Delete a todo from the list
        # パスパラメータ
        parameters:
        - in: path
            name: username
            schema:
                type: string
            required: true
            description: The name of the user.
        # リクエスト body 定義
        requestBody:
            required: true
            content:
            application/json:
                schema:
                $ref: '#/components/schemas/deleteTodoRequest'
        # レスポンス定義
        responses:
            # ステータスコード :200 => {"OK"}
            "200":
            description: OK

    components:
    # スキーマ（レスポンスやリクエストbody）定義
    schemas:
        getTodosResponse:
        type: object
        # json レスポンスの形式
        properties:
            todos:
            type: array
            items:
                type: string
            description: The list of todos.
        addTodoRequest:
        type: object
        # リクエスト body に "todo" 必要
        required:
        - todo
        properties:
            todo:
            type: string
            description: The todo to add to the list.
            required: true
        deleteTodoRequest:
        type: object
        # リクエスト body に "todo_idx" 必要
        required:
        - todo_idx
        properties:
            todo_idx:
            type: integer
            description: The index of the todo to delete.
            required: true
    ```

    ポイントは、以下の通り

    - xxx

1. Plugin のロゴ画像を配置する<br>
    デフォルトでは、ルートディレクトリに `logo.png` という名前のロゴ画像を配置する<br> 
    `.well-known/ai-plugin.json` の `logo_url` フィールドの値を変更すればよい

1. ChatGPT plugins を動かす<br>
    - ローカル環境の API で動かす場合<br>
        1. ローカル環境上で API サーバーを起動する
            ```sh
            docker-compose up
            ```

        1. [ChatGPT のコンソール UI](https://chat.openai.com/)から「GPT-4」をマウスオーバーし、「Plugins（Beta）」を選択し、「No plugins enabled」->「Plugin store」->「Develop your own plugin」を選択する<br>
            <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/e63d31d7-443d-4307-9a79-c54d46d4fc88">

        1. ローカル環境上で動作している API の URL `localhost:5003` を入力する
            <img width="700" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/653abb97-cdc0-42cd-a71c-edf8ed5facd9">

    - サーバー環境の API で動かす場合<br>
        1. サーバー上の API を起動する

        1. `ai-plugin.json` の `api.url`, `logo_url` フィールドの値を、サーバー環境上で動作している API の URL（例：`https//hogehoge:5003`）に修正する

        1. `openapi.yaml` の `servers.url` フィールドの値を、サーバー環境上で動作している API の URL（例：`https//hogehoge:5003`）に修正する

        1. [ChatGPT のコンソール UI](https://chat.openai.com/)から「GPT-4」をマウスオーバーし、「Plugins（Beta）」を選択し、「No plugins enabled」->「Plugin store」->「Develop your own plugin」を選択する

        1. サーバー環境上で動作している API の URL（例：`https//hogehoge:5003`）を入力する

## 参考サイト

- https://openai.com/blog/chatgpt-plugins
- https://github.com/openai/plugins-quickstart
- https://chatgpt-lab.com/n/n9df36720c5d0
- https://www.m3tech.blog/entry/chatgpt-retrieval-plugin-vector-search
