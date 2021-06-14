# Fluentd を使用してログ集約する

## 方法

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

1. Fluentd にログ送信<br>
    Fluentd サーバーが起動されている状態で、`fluent-cat` コマンドを使用することで、tcp 経由でログデータを送信できる
    ```sh
    $ echo ${VALUE_DATA} | fluent-cat ${TAG_NAME}
    ```
    - 送信例<br>
        ```sh
        # 送信例
        $ echo '{"log_message":"sample"}' | fluent-cat debug.test
        ```

        > この例での tag 名 `debug.test` は、`fluent.conf` 内の以下の部分に対応したものになっている
        > ```conf
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

## ■ Fluentd 設定ファイル `fluent.conf` の中身

`<source></<source>` でログの入力方法を指定し、`<match></<match>` でログの出力方法を指定する

1. ログデータをファイルに出力する場合<br>
    ```yaml
    <source>
    type forward
    </source>

    <match log.**>
        type file
        path /var/log/fluentd/out
    </match>
    ```

1. ログデータを転送する場合<br>
    ```
    ```


## ■ 参考サイト
- https://qiita.com/zaburo/items/dbd943d370afe8e4a304
- https://hivecolor.com/id/37