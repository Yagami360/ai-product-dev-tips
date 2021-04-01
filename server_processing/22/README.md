# 【nginx】nginx の基本事項
Nginx（エンジンエックス）とは、オープンソースのWebサーバ/リバースプロキシ。<br>

> - リバースプロキシ（Reverse Proxy）<br>
> クライアントとサーバの通信の間に入って、サーバの応答を「代理（proxy）」しつつ通信を中継する機能、あるいはその役割を担うサーバ。Webシステムのセキュリティ対策や性能向上、負荷分散、あるいはシステム構成の自由度向上などのためによく利用される。

同様のものとして Apache（Apache HTTP Server）があるが、Nginx は Apache より高速かつ高負荷に強いというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/113256811-a9a13a00-9304-11eb-8132-ec0f0e2ad8b3.png" width="500"><br>


## ■ 使用法

1. nginx をインストールする<br>
    - MacOS の場合
        ```sh
        $ brew install nginx
        ```
    - Ubuntu の場合
        ```sh
        ```
1. nginx のバージョン確認<br>
    正しくインストールされたことを確認するために、以下のコマンドでバージョン確認
    ```sh
    # nginx のバージョン確認
    $ nginx -v
    ```
1. `nginx` コマンドで Nginx の Web サーバーを起動する
    ```sh
    # デフォルトでは、ドメイン名（localhost） 8080 版ポートの Web サーバーが構築される
    $ nginx
    ```

    独自の `nginx.conf` を指定したい場合は、`-c` オプション付きでコマンド実行すればよい
    ```
    $ nginx -c ${NGINX_CONF_FILE_PATH}
    ```

    ※ 以下のエラーメッセージが出る場合は、`ps aux | grep nginx` で確認された nginx プロセスをすべて kii した後に、`nginx` コマンドを `sudo` コマンド付きで実行する解決法がある
    ```sh
    nginx: [error] open() "/usr/local/var/run/nginx.pid" failed (2: No such file or directory)
    ```

1. Web サーバーにブラウザアクセスする<br>
    ```sh
    # 8080 版ポートの場合
    $ open http://localhost:8080
    ```
    「Welcome to nginx!」が表示されれば成功
1. Ngix サーバーを停止する場合は、以下のコマンドを実行
    ```sh
    $ nginx -s quit
    ```

## ■ Nginx 設定ファイル
Nginx の細かい起動条件は、CLI コマンドではなく、Nginx 設定ファイルで行う。

### ◎ `nginx.conf`
HTTPなどアクセス関連の設定ファイル

#### ☆ `nginx.conf` のファイルパス
- MacOS の場合
    ```sh
    /usr/local/etc/nginx/nginx.conf
    ```
- Ubuntu の場合
    ```sh
    ```

#### ☆ `nginx.conf` の中身

```conf
#----------------
# Core モジュール。
# プロセスの管理・設定ファイル制御・セキュリティ・ロギングなどの設定を行う。
#----------------
worker_processes  auto;         # 実行プロセス数
include servers/*;              # nginx.conf 以外の読み込みファイルの読み込みパス

#----------------
# Events モジュール。
# イベント処理(パフォーマンス・チューニングなどの設定を行う
#----------------
events {
    worker_connections  1024;   # コネクション数（同時接続数？）の制限
}

#----------------
# HTTP モジュール。
# Web サーバーに関しての設定を行う
#----------------
http{
    listen       8080;                      # IP アドレスとポート番号（ポート番号のみの指定も可能）
    server_name  localhost;                 # ドメイン名（www.example.com など）
    root /usr/local/var/www/;               # ドキュメントルート（トップページのHTML ファイルパス）/ MacOS の場合 : /usr/local/var/www/
    charset UTF-8;                          # レスポンスヘッダの Content-type

    # 仮想サーバの構築
    server {
        listen 0.0.0.0:80;
        server_name localhost;
    }
}
```

## ■ 参考サイト
- https://qiita.com/riita10069/items/5d36dfeb756e3b6c4978
- https://www.yaz.co.jp/tec-blog/web%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9/263
- https://qiita.com/morrr/items/7c97f0d2e46f7a8ec967