# 【GCP】Google Cloud Pub/Sub の基礎事項
Google Cloud Pub/Sub は、GCP で提供されている Pub/Sub [Publish/Subscribe] モデル（送信者と受信者が 1 対 多）でのメッセージングサービス・キューサービスであり、各種 GCP サービスとの連携が容易になるというメリットがある。

以下の図は、Pub/Sub での送受信例を示した図である。<br>
１つまたは複数の Publisher が Message（Event）を Topic に対して Publish すると、その Message に興味のある１つまたは複数の Subscriber がその Message を受け取ることができる動作になる。

<img src="https://user-images.githubusercontent.com/25688193/120064509-79c5a700-c0a7-11eb-8152-a3ec2fa8422b.png" width="500"><br>
- Publisher（発行者） : メッセージの送信側
- Subscriber（購読者） : メッセージの受信側
- Message（メッセージ） : Publisher がトピックに送信し、最終的にはサブスクライバーに配信されるデータ
- topic（トピック） : Publisher がメッセージを送信する名前付きのリソース？（キューのこと？）

## ■ 使用法

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

1. トピックにメッセージを publish (push) する
    ```sh
    $ gcloud pubsub topics publish ${TOPIC_ID} --message "Hello World!"
    ```

1. トピックのメッセージを subscribe (pop) する
    ```sh
    $ gcloud pubsub subscriptions pull --auto-ack ${SUBSCRIPTION_ID}
    ```

    