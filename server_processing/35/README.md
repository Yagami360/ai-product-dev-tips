# FastAPI での GET / POST 処理

## ■ FastAPI を使用した GET 処理の実装
    
- FastAPI を使用した GET 処理の実装例（`Path`, `Query` クラス不使用）<br>
    ```python
    from fastapi import FastAPI

    app = FastAPI()
    users_db = {
        "name" : {
            0 : "user1",
            1 : "user2",
            2 : "user3",
        },
        "age" : {
            0 : "24",
            1 : "30",
            2 : "18",
        }
    }

    @app.get("/users_name/{users_id}")
    def get_user_name_by_path_parameter(
        users_id: int,  # パスパラメーター
    ):
        return users_db["name"][users_id]

    @app.get("/users_name/")
    def get_user_name_by_query_parameter(
        users_id: int,  # クエリパラメーター
    ):
        return users_db["name"][users_id]

    @app.get("/users/{attribute}")
    def get_user_by_path_and_query_parameter(
        attribute: str, # パスパラメーター
        users_id: int,  # クエリパラメーター
    ):
        return users_db[attribute][users_id]
    ```

    ```sh
    # パスパラメーターで指定
    $ curl http://${HOST}:${PORT}/users_name/0
    $ curl http://${HOST}:${PORT}/users_name/1
    $ curl http://${HOST}:${PORT}/users_name/2
    ```
    ```sh
    # クエリパラメーターで指定
    $ curl http://${HOST}:${PORT}/users_name/?users_id=0
    $ curl http://${HOST}:${PORT}/users_name/?users_id=1
    $ curl http://${HOST}:${PORT}/users_name/?users_id=2
    ```
    ```sh
    # パスパラメーター & クエリパラメーターで指定
    $ curl http://${HOST}:${PORT}/users/name?users_id=0
    $ curl http://${HOST}:${PORT}/users/age?users_id=0
    $ curl http://${HOST}:${PORT}/users/name?users_id=1
    $ curl http://${HOST}:${PORT}/users/age?users_id=1
    $ curl http://${HOST}:${PORT}/users/name?users_id=2
    $ curl http://${HOST}:${PORT}/users/age?users_id=2
    ```

    ポイントは、以下の通り<br>
    > - GET method は、`@app.get` デコレーションをつけた関数で定義できる。
    > - パスパラメータは `@app.get` で指定した GET method のエンドポイントに `{パスパラメーター名}` をつけることで指定できる。
    > - クエリパラメーターは、`@app.get` で指定した GET method の エンドポイントに `{}` をつけずに指定することで指定できる
    > - パスパラメータ・クエリパラメーターは、全て関数の引数として定義する。また、引数には型のヒントをつけるようにする


- FastAPI を使用した GET 処理の実装例（`Path`, `Query` クラス使用）<br>
    xxx

## ■ FastAPI を使用した POST 処理の実装

- FastAPI を使用した POST 処理の実装例<br>
    ```python
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()
    users_db = {
        "name" : {
            0 : "user1",
            1 : "user2",
            2 : "user3",
        },
        "age" : {
            0 : "24",
            1 : "30",
            2 : "18",
        }
    }

    from pydantic import BaseModel
    # `pydantic.BaseModel` 継承クラスでリクエストボディを定義
    class UserData(BaseModel):
        id: int
        name: str
        age: str

    @app.post("/add_users/")
    def add_user(
        user_data: UserData,     # リクエストボディ
    ):
        users_db["name"][user_data.id] = user_data.name
        users_db["age"][user_data.id] = user_data.age
        return users_db
    ```

    ```sh
    $ curl -X POST -H "Content-Type: application/json" \
        -d '{"id":4, "name":"user4", "age":"100"}' \
        http://${HOST}:${PORT}/add_users
    ```

    ポイントは、以下の通り<br>
    > - POST method は、`@app.post` デコレーションをつけた関数で定義できる。
    > - パスパラメータは `@app.post` で指定した GET method のエンドポイントに `{パスパラメーター名}` をつけることで指定できる。
    > - クエリパラメーターは、`@app.post` で指定した GET method の エンドポイントに `{}` をつけずに指定することで指定できる
    > - パスパラメータ・クエリパラメーター・リクエストボディは、全て関数の引数として定義する。また、引数には型のヒントをつけるようにする
    > - リクエストボディは、`pydantic.BaseModel` 継承クラスで定義する


## ■ 参考サイト
- https://qiita.com/kida_kun_/items/a144ce42bb04a344ac6b
- https://qiita.com/uezo/items/847e1911ac486f5a89c4