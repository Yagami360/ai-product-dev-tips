# Fluentd (td-​agent) を使用してログデータを転送する

Fluentd (td-​agent) は、ログデータの転送や集約を行うためのツールである。<br>
Fluentd を使用することで、例えば、複数の Web-API からのログデータを１箇所に集約し、各種クラウドのログサービス（Cloud logging など）に転送するような処理が可能になる

Fluentd と td-​agent の違いは、以下の通り

- fluentd: コミュニティによって開発が進められている ruby gem のパッケージ
- td-agent: fluentd の安定版 + 各OS用インストーラ

## ■ 方法

### ◎ fluentd の場合

1. Fluentd をインストールする<br>
    ```sh
    $ sudo gem install fluentd -n /usr/local/bin
    ```
    > Ruby1.9.2以上が必要

1. Fluentd の設定ファイル `fluent.conf` を作成する<br>
    デフォルトの設定ファイルを作成する場合は、以下のコマンドで作成できる
    ```sh
    $ mkdir -p fluent
    $ fluentd --setup ./fluent
    ```
    > この例では ${PWD}/fluent 以下に設定ファイル `fluent.conf` を作成しているが、別のディレクトリでもよい

    デフォルト値以外での設定ファイルを作成したい場合は、手作業で `fluent.conf` に適切な値を設定すればよい

1. Fluentd サーバーを起動する
    ```sh
    $ fluentd -c fluent/fluent.conf 
    ```

1. Fluentd を用いて標準入力からログデータを転送する<br>
    Fluentd サーバーが起動されている状態で、`fluent-cat` コマンドを使用することで、標準入力から tcp 経由でログデータを送信できる
    ```sh
    $ echo ${VALUE_DATA} | fluent-cat ${TAG_NAME}
    ```
    - 送信例<br>
        ```sh
        # 送信例
        $ echo '{"log_message":"sample"}' | fluent-cat debug.test
        ```

        このコマンドでログ転送が可能であるためには、`fluent.conf` 内の以下のような設定が行われている必要があることに注意
        > ```conf
        >## built-in TCP input
        >## $ echo <json> | fluent-cat <tag>
        ><source>
        >  @type forward
        >  @id forward_input
        ></source>
        >
        > ## match tag=debug.** and dump to console
        > <match debug.**>
        >   @type stdout
        >   @id stdout_output
        > </match>
        > ```

    このコマンドを実行すると、Fluentd サーバー側で以下のような出力が表示される
    ```
    2021-06-14 19:14:24.947341000 +0900 debug.test: {"log_message":"sample"}
    ```

### ◎ td-agent の場合
xxx

## ■ Fluentd 設定ファイル `fluent.conf`

`<source></<source>` でログの入力方法を指定し、`<match></<match>` でログの出力方法を指定する

1. 標準入力から標準出力へログデータを転送する場合<br>
    ```yaml
    ```

1. 標準入力から外部ファイルにログデータを転送する場合<br>
    ```yaml
    ```

1. 外部ファイルから外部ファイルにログデータを転送する場合<br>
    ```yaml
    ```

## ■ 参考サイト
- https://qiita.com/zaburo/items/dbd943d370afe8e4a304
- https://hivecolor.com/id/37