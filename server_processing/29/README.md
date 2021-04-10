# REST API / RESTful API の基本事項

- REST : <br>
    分散型システムにおける複数のソフトウェアを連携させるのに適した設計原則<br>
    具体的には、主に以下の4つの原則から成る。<br>
    > API 開発者と API 利用者としては、特に HTTPメソッド(GET、POST、PUT、DELETE)の利用を定めた部分の恩恵が大きい

    - アドレス可能性(Addressability)<br>
        提供する情報がURIを通して表現できること。全ての情報はURIで表現される一意なアドレスを持っていること

    - ステートレス性(Stateless)<br>
        HTTPをベースにしたステートレスなクライアント/サーバプロトコルであること。セッション等の状態管理はせず、やり取りされる情報はそれ自体で完結して解釈できること。

    - 接続性(Connectability)<br>
        情報の内部に、別の情報や(その情報の別の)状態へのリンクを含めることができること。

    - **統一インターフェース(Uniform Interface)**<br>
        情報の操作(取得、作成、更新、削除)は、全てHTTPメソッド(GET、POST、PUT、DELETE)を利用すること。

    また以下のような原則もある？（或いは上記４つの原則に含まれる？）<br>
    - （処理ではなく）リソースに対して URL が対応づけられる。

- RESTful API : <br>
    REST の設計原則に沿って構築された Web システムの HTTP での呼び出しインターフェース（API）<br>
    インターフェイス仕様を統一的に定めることで、API 開発者と API 利用者ともに開発＆利用が容易になるなどのメリットが存在する。

- REST API : <br>
    RESTful API とほぼ同意味


## 非 REST API と REST API の具体例

- 非 RESTful API<br>
    例えば、ユーザーの登録・取得・更新・削除といった処理を別々の URL で行うようにした API は、非 RESTful API になる。（RESTful API はリソースに対応づいて URL が決まるのであって、ユーザーの登録・取得・更新・削除といった処理には URL は対応づかないため）<br>

    このような 非 RESTful API の Flask でのコード例は、以下のようになる。
    ```python
    # flask の @app.route() で別々の URL を設定することで、
    # ユーザーの登録・取得・更新・削除といった処理を別々の URL で行うようにしている
    @app.route('/add_user')
    def add_user():
        # ユーザーの登録処理
        ...

    @app.route('/get_user')
    def get_user():
        # ユーザーの取得処理
        ...

    @app.route('/update_user')
    def update_user():
        # ユーザーの更新処理
        ...

    @app.route('/delete_user')
    def delete_user():
        # ユーザーの削除処理
        ...
    ```

- RESTful API<br>
    例えば、ユーザーの登録・取得・削除といった処理を同じ URL で行うようにした API は、RESTful API になる。<br>
    このような RESTful API の Flask でのコード例は、以下のようになる。
    ```python
    # flask の @app.route() での methods に HTTEP を設定することで、
    # ユーザーの登録・取得・更新・削除といった処理を同じ URL で行うようにしている
    @app.route('/user_info', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def responce():
        # ユーザーの登録処理
        if(flask.request.method == "GET"):
            ...

        # ユーザーの取得処理
        if(flask.request.method == "POST"):
            ...

        # ユーザーの更新処理
        ...

        # ユーザーの削除処理
        ...
    ```

## 参考サイト
- https://qiita.com/NagaokaKenichi/items/0647c30ef596cedf4bf2
- https://qiita.com/masato44gm/items/dffb8281536ad321fb08