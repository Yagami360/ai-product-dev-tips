# Amazon SQS を使用して標準キューの簡単なキューイングを行う（AWS CLI 使用）

Amazon SQS は、フルマネージド型のサーバーレスでのキューイングサービスで、GCP でいうところの Cloud Pub/Sub に該当するサービスである。

Amazon SQS で使用できるキューの種類には、標準キューと FIFO キューの２種類があり、それぞれ以下のような特徴がある


- 標準キュー<br>
    順番が保証されない。例えば、1 -> 2 -> 3　の順にキューに送信しても、受信側で 1 -> 3 -> 2 の順で受信される可能性がある。<br>
    またメッセージが重複する可能性もある。例えば、1 -> 2 -> 3　の順にキューに送信しても、受信側 A で 1 -> 2 の順で受信され、受信側 B では 2 -> 3 で受信される可能性がある。<br>
    1秒あたりほぼ無限のAPIコールをサポートで高負荷に適した用途

- FIFO キュー<br>
    順番が保証される。例えば、1 -> 2 -> 3　の順にキューに送信しても、受信側で 1 -> 2 -> 3 の順で必ず受信される。<br>
    またメッセージが重複する可能性がない。例えば、1 -> 2 -> 3 -> 4　の順にキューに送信したら、受信側 A で 1 -> 2 の順で受信され、受信側 B では 3 -> 4 で受信され重複しない。<br>
    但し、標準キューと比較してFIFOキューは$0.1(2-3割)割高。また、1秒あたり300APIコールまでしかサポートしていない

ここでは、標準キューを使用する方法を記載する

## ■ 方法

1. AWS CLI をインストールする<br>
    - MacOS の場合<br>
        ```sh
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
        ```

    - Linux の場合<br>
        ```sh
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        ```

1. キューを作成する
    ```sh
    aws sqs create-queue --queue-name ${QUEUE_NAME}
    ```

    > 作成したキューは、「[Amazon SQS コンソール画面](https://us-west-2.console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues)」から確認できる

1. プロデューサー（送信側）でメッセージをキューに送信する
    ```sh
    aws sqs send-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --message-body "hello world"
    ```

    キュー数は、以下のコマンドで確認できる
    ```sh
    aws sqs get-queue-attributes --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --attribute-names ApproximateNumberOfMessages
    ```

1. コンシューマー（受信側）でキューからメッセージを受信する
    ```sh
    # コンシューマー（受信側）でキューからメッセージを受信する
    aws sqs receive-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" > log/sqs_message.json

    # ReceiptHandle の値を取得
    RECEIPT_HANDLE=$(jq -r '.Messages[].ReceiptHandle' log/sqs_message_1.json)
    ```

    > 上記コマンドで受信後にキューのデータがそのまま残ることに注意

    > `aws sqs receive-message` コマンド実行時に得られる `ReceiptHandle` の値は、後述の `aws sqs delete-message` コマンド実行時に必要になる

1. 【オプション】キューのデータを削除する
    受信後にキューのデータを削除する場合は、上記 `aws sqs receive-message` 実行後に、以下のコマンドを実行すればよい
    ```sh
    aws sqs delete-message --queue-url "https://sqs.${REGION}.amazonaws.com/${AWS_ACCOUNT_ID}/${QUEUE_NAME}" --receipt-handle ${RECEIPT_HANDLE}
    ```
    - `--receipt-handle` : `aws sqs receive-message` コマンド実行時に得られる `ReceiptHandle` の値

## ■ 参考サイト

- https://weblabo.oscasierra.net/aws-sqs-tutorial/