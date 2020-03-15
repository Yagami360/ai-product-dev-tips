# 【Docker】 requests モジュールを用いてコンテナ間通信するときの、IP アドレス指定方式（コンテナ名で指定）

一般的に、docker コンテナとホスト環境間で通信を行う際には、`http://${IPアドレス}:${ポート番号}` のようにコンテナの IP アドレスを指定する必要がある.

一方、requests モジュールを用いて docker コンテナ内部から別のコンテナへの通信（＝コンテナ間通信）を行う際は、IP アドレスではなく、`http://${コンテナ名}:${ポート番号}`, `http://${コンテナID}:${ポート番号}` のようにコンテナ名（又はコンテナID）を指定することで通信が可能になる。

※ IP アドレスではなく、コンテナ名を指定したときのみ通信が可能となるのは、Flask & requests モジュールを使用したときの特有の処理なのかは不明

- 動作する例（コンテナ名で指定）
    ```python
    # API サーバーへの POST リクエスト時の処理
    # API サーバーのコンテナ内から Graphonomy サーバーのコンテナへ通信を行う
    @app.route('/api_server', methods=['POST'])
    def responce():
        ...

        # Graphonomy サーバーの POST リクエスト（コンテナ名で指定）
        graphonomy_msg = json.dumps( {'pose_img_base64': pose_img_base64 } )
        graphonomy_responce = requests.post( http://graphonomy_server_gpu_container:5001/graphonomy, json=graphonomy_msg )
    ```

- 動作しない例（IP アドレスで指定）
    ```python
    # API サーバーへの POST リクエスト時の処理
    # API サーバーのコンテナ内から Graphonomy サーバーのコンテナへ通信を行う
    @app.route('/api_server', methods=['POST'])
    def responce():
        ...
        # Graphonomy サーバーの POST リクエスト（IPアドレスで指定）
        graphonomy_msg = json.dumps( {'pose_img_base64': pose_img_base64 } )
        graphonomy_responce = requests.post( http://0.0.0.0:5001/graphonomy, json=graphonomy_msg )
    ```
