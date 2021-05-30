# 【GCP】Google Cloud Pub/Sub を Python スクリプト上で利用する（PULL 方式）

## ■ 使用法

1. Pub/Sub の Python API をインストールする
    ```sh
    $ pip install google-cloud-pubsub
    ```
1. Cloud Pub/Sub の API を有効化する
    ```sh
    ```

1. トピックを作成する
    ```sh
    $ gcloud pubsub topics create ${TOPIC_NAME}
    ```
    作成したトピックは、以下のコマンドで確認可能
    ```sh
    $ gcloud pubsub topics list
    ```

1. サブスクリプション（受信側）を作成する。
    上記で作成したトピックに紐付いたサブスクリプション（受信側）を作成する。
    ```sh
    $ gcloud pubsub subscriptions create ${SUBSCRIPTION_NAME} 
        --topic ${TOPIC_NAME} \
        --ack-deadline 10
    ```
    - `--push-endpoint` : このサブスクリプションの URL
    - `--ack-deadline` : 

    作成したサブスクリプションは、以下のコマンドで確認可能
    ```sh
    $ gcloud pubsub subscriptions list
    ```

1. 【オプション】CLI での送受信の動作確認
    1. トピックにメッセージを publish (push) する
        ```sh
        $ gcloud pubsub topics publish ${TOPIC_ID} --message "Hello World!"
        ```

    1. トピックのメッセージを subscribe (pop) する
        ```sh
        $ gcloud pubsub subscriptions pull --auto-ack ${SUBSCRIPTION_ID}
        ```

1. サービスアカウントを作成する<br>
    「[IAM のサービスアカウントコンソール](https://console.cloud.google.com/iam-admin/serviceaccounts?hl=ja&project=my-project2-303004) 」から、Pub/Sub を各種 GCP サービスや Pub/Sub の Python API から使用できるようにするためのサービスアカウントを作成する<br>
    サービスアカウントのロールは、「Pub/Sub 管理者」にする。

    <!--
    <img src="https://user-images.githubusercontent.com/25688193/120065918-c52f8380-c0ae-11eb-8c41-2b05cc6e266d.png" width="300"><br>
    -->

    その後、作成したサービスアカウントの json 鍵を作成して保存しておく。
    <img src="https://user-images.githubusercontent.com/25688193/120065983-340cdc80-c0af-11eb-8bee-d43ba505a1e8.png" width="300"><br>


    後述の パブリッシャー or サブスクライバーの Python スクリプトで明示的に json 鍵を指定しない場合は、作成したサービスアカウントの json 鍵のファイルパスを環境変数に追加しておく。
    > .gitignore に追加するなどして、json キーを公開しないように注意すること

    ```sh
    $ export GOOGLE_APPLICATION_CREDENTIALS="${JSON_KEY_FILE_PATH}"
    ```

1. Python スクリプトでのパブリッシャー（発行者）を作成する
    Pub/Sub の Python API を用いて、例えば、以下のような Python スクリプトでのパブリッシャー（発行者）を作成する
    ```python
    # pub.py
    import os
    import argparse
    import time, datetime
    from google.cloud import pubsub_v1

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("--project_id", default="my-project2-303004", help="GCP のプロジェクトID")
        parser.add_argument("--topic_name", type=str, default="topic-sample", help="Pub/Sub のトピック名")
        parser.add_argument("--credentials_file_path", type=str, default="", help="Pub/Sub のjson鍵のファイルパス")
        parser.add_argument("--pub_times", type=str, default=10, help="送信回数")
        parser.add_argument('--debug', action='store_true')
        args = parser.parse_args()
        if( args.debug ):
            for key, value in vars(args).items():
                print('%s: %s' % (str(key), str(value)))

        # publisher のインスタンス作成
        publisher = pubsub_v1.publisher.Client.from_service_account_file(args.credentials_file_path)
        topic_path = publisher.topic_path(args.project_id, args.topic_name)

        # publish 処理
        for i in range(args.pub_times):
            # メッセージの設定
            data = u"Message from test publisher {}".format(i) + " | " + datetime.datetime.now().isoformat(" ")
            data = data.encode("utf-8")
            print("Publish: " + data.decode("utf-8", "ignore") )

            # トピックにメッセージを publish (push) する
            future = publisher.publish(topic_path, data=data)
            print("return ", future.result())
            time.sleep(0.25)
    ```

1. Python スクリプトでのサブスクライバー（購読者）を作成する
    Pub/Sub の Python API を用いて、例えば、以下のような Python スクリプトでのサブスクライバー（購読者）を作成する
    ```python
    import os
    import argparse
    import time, datetime
    from google.cloud import pubsub_v1

    def callback(message):
        """
        トピックにメッセージが届いたときに呼び出されるコールバック関数
        """
        now = datetime.datetime.now()
        print( "msg = \"" + message.data.decode("utf-8") + "\"" +  "  [" + now.isoformat(" ") + "]")

        # ACK メッセージを送信（受信メッセージの処理が完全に完了したことを通知）
        message.ack()
        return

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument("--project_id", default="my-project2-303004", help="GCP のプロジェクトID")
        parser.add_argument("--sub_name", type=str, default="sub-sample", help="サブスクリプション名")
        parser.add_argument("--credentials_file_path", type=str, default="", help="Pub/Sub のjson鍵のファイルパス")
        parser.add_argument('--debug', action='store_true')
        args = parser.parse_args()
        if( args.debug ):
            for key, value in vars(args).items():
                print('%s: %s' % (str(key), str(value)))

        # subscriber のインスタンス作成
        subscriber = pubsub_v1.subscriber.Client.from_service_account_file(args.credentials_file_path)
        subpath = subscriber.subscription_path(args.project_id, args.sub_name)
        flow_control = pubsub_v1.types.FlowControl(max_messages=2)

        # トピックのメッセージを subscribe (pop) する
        subscriber.subscribe(subpath, callback=callback, flow_control = flow_control)
        input()
    ```

1. パブリッシャーとサブスクライバーの Python スクリプトを各々適切なタイミングで実行する
    ```sh
    # パブリッシャーの Python スクリプトを実行する | 別プロセスで実行することで、サブスクライバーの Python スクリプトと並列実行
    python pub.py --project_id ${PROJECT_ID} --topic_name ${TOPIC_NAME} --credentials_file_path ${CREDENTIALS_FILE_PATH} &
    ```
    ```sh
    # サブスクライバーの Python スクリプトを実行する
    python sub.py --project_id ${PROJECT_ID} --sub_name ${SUBSCRIPTION_NAME} --credentials_file_path ${CREDENTIALS_FILE_PATH
    ```
    > ここでの処理は、PULL 方式（受信側が一定間隔でトピックをサンプリング）でのやりとりになっていることに注意


## ■ 参考サイト
- https://ohshige.hatenablog.com/entry/2019/03/25/190000
- https://qiita.com/XPT60/items/61e16fd980e5ea87519b