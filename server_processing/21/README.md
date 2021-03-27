# 【シェルスクリプト】ポートフォワーディングを使用した tensorboard 接続
サーバー上で tensorboard コマンドを使用した場合に、`http://${SERVER_ADDRESS}:${PORT}` にアクセスしても tensorboard にアクセスできないケースがあるが、この場合は、ポートフォワーディングを使用してサーバー上の tensorborad ポートをローカルPC上にポートフォワーディングすることで、ローカルPC上から tesnorboard アクセスできるようにする方法がある。

<img src="https://user-images.githubusercontent.com/25688193/112706578-83d0fb00-8ee8-11eb-8e15-24f50d2a81af.png" width="500">

## ■ 使用法

- サーバー上の　tensorboard ポートをローカルのポートに転送して、ローカルPCの localhost から tensorboard アクセスする場合<br>
    サーバー上で tensorboard コマンドを実行した状態で、ローカルPC上から以下のコマンドを実行
    ```sh
    $ ssh -N -L localhost:${LOCAL_PORT}:localhost:${SERVER_PORT} ${USER_NAME}@${IP_ADDRESS}
    ```
    - `-N` : ssh 接続先にログインするのではなく待機状態にする
    - `-L` : ポートフォワーディング先を Local PC にする
    - `-f` : バックグラウンド実行する
    - `${USER_NAME}@${IP_ADDRESS}` : 接続先サーバー

    ```sh
    # 使用例
    $ ssh -N -L localhost:6006:localhost:6006 ubuntu@100.20.254.22
    ```

