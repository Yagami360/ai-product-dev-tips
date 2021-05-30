# docker + Flask での Web-API を Cloud Pub/Sub を利用して非同期実行する（PULL方式）

<img src="https://user-images.githubusercontent.com/25688193/120090908-1be59d80-c141-11eb-84f5-c36cbe774951.png" width="500"><br>

> わざわざ Flask 使わなくても、Cloud Pub/Sub 経由でクライアントと Web-API 間の通信ができるのでは？

## ■ 方法

1. Web-API のコード（サブスクライバー）を作成する<br>
    Web-API のコード `app.py` を Flask を利用して作成する。<br>
    この Web-API のコードは、Cloud Pub/Sub の文脈ではサブスクライバー（購読者）になり、Cloud Pub/Sub の Python API を使用して、サブスクライバーとしてのコードも追加する

    ```python
    # app.py
    ```

    更に、コンテナ内で Web-API を実行できるように、Web-API の dockerfile と docker-compose.yml を作成する<br>

    - dockerfile の例
        ```
        ```

        > `google-cloud-pubsub` のインストールを追加している点がポイント

    - docker-compose の例
        ```
        ```

1. クライアント側のリクエスト処理のコード（パブリッシャー）を作成する<br>
    `request` モジュールを用いて、Flask での Web-API にリクエスト処理を行うコードを作成する

    ```python
    # request.py
    ```
  
1. Cloud Pub/Sub の設定<br>
    1. トピックを作成する<br>
        ```sh
        $ gcloud pubsub topics create ${TOPIC_NAME}
        ```
        作成したトピックは、以下のコマンドで確認可能
        ```sh
        $ gcloud pubsub topics list
        ```

    1. サブスクリプション（受信側）を作成する。<br>
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

    1. サービスアカウントを作成する<br>
        「[IAM のサービスアカウントコンソール](https://console.cloud.google.com/iam-admin/serviceaccounts?hl=ja&project=my-project2-303004) 」から、Pub/Sub を各種 GCP サービスや Pub/Sub の Python API から使用できるようにするためのサービスアカウントを作成する<br>
        サービスアカウントのロールは、「Pub/Sub 管理者」にする。

        <!--
        <img src="https://user-images.githubusercontent.com/25688193/120065918-c52f8380-c0ae-11eb-8c41-2b05cc6e266d.png" width="300"><br>
        -->

        その後、作成したサービスアカウントの json 鍵を作成して保存しておく。
        <img src="https://user-images.githubusercontent.com/25688193/120065983-340cdc80-c0af-11eb-8bee-d43ba505a1e8.png" width="300"><br>

1. Web-API の docker コンテナを起動する
    ```sh
    $ docker-compose -f ${DOCKER_COMPOSE_YAML_FILE} stop
    $ docker-compose -f ${DOCKER_COMPOSE_YAML_FILE} up -d
    ```

1. リクエスト処理を行う<br>
    ```sh
    $ python request.py --project_id ${PROJECT_ID} --sub_name ${SUBSCRIPTION_NAME} --credentials_file_path ${CREDENTIALS_FILE_PATH}
    ```

    > リクエスト処理後は、リクエスト処理待ちでプログラムが停止することなく、別の処理を行うことができるようになっている（＝非同期実行になっている）ことに注目。
    > ここでは、リクエスト処理後にリクエスト処理が完了したかを一定間隔でポーリングしているが、この処理の間に別の処理を入れても良い


## ■ 参考サイト
- https://cloud.google.com/python/docs/getting-started/background-processing?hl=ja