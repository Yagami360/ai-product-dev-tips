# 【GCP】Google Cloud Pub/Sub の基礎事項
Google Cloud Pub/Sub は、GCP で提供されている Pub/Sub [Publish/Subscribe] モデル（送信者と受信者が 1 対 多）でのメッセージングサービス・キューサービスであり、各種 GCP サービスとの連携が容易になるというメリットがある。

## ■ Pub/Sub の構成
以下の図は、Pub/Sub での送受信例を示した図である。<br>
１つまたは複数の Publisher が Message（Event）を Topic に対して Publish すると、その Message に興味のある１つまたは複数の Subscriber がその Message を受け取ることができる動作になる。

<img src="https://user-images.githubusercontent.com/25688193/120064509-79c5a700-c0a7-11eb-8152-a3ec2fa8422b.png" width="500"><br>
- Publisher（発行者） : メッセージの送信側
- Subscriber（購読者） : メッセージの受信側
- Message（メッセージ） : Publisher がトピックに送信し、最終的にはサブスクライバーに配信されるデータ
- topic（トピック） : Publisher がメッセージを送信する名前付きのリソース？（キューのこと？）

## ■ PULL, PUSH

- PULL<br>
    Subscriber（受信側）が、新しいメッセージを取りに来るタイプ。 <br>
    例えば1秒に1回とか、1分に1回などの頻度でメッセージをサンプリングするので、その分のタイムラグが発生する
    <img src="https://user-images.githubusercontent.com/25688193/120090316-6b759a80-c13c-11eb-8f14-843536cf20d1.png" width="500"><br>

- PUSH<br>
    新しいメッセージがあると (比較的) すぐに受信側に送りつけるタイプ<br>
    PULL のようなサンプリング間隔によるタイミングラグが発生しないメリットがある。
    <img src="https://user-images.githubusercontent.com/25688193/120090346-a7a8fb00-c13c-11eb-911f-75235e0e72d3.png" width="500"><br>

## ■ 使用法

### ◎ PULL 方式
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
    - `--push-endpoint` : このサブスクリプションの URL。PUSH 方式でやりとりする場合に設定する？
    - `--ack-deadline` : ACK メッセージのタイムアウト待ち時間

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

### ◎ PUSH 方式