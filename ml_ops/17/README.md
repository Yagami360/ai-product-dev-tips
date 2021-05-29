# メッセージングサービス・キューサービスの基本事項
AWS, GCP などの各種クラウドサービスが提供しているメッセージングサービス・キューサービス（Google Cloud Pub/Sub など）は、「あるプログラムがキューにメッセージを送信し、それを別のプログラムで受信することができにした」サービスである。

このメッセージング・キューサービスを利用することで、例えば、以下のようなケースの処理が比較的容易に実現できるようになる。

- 処理 A をサーバー１で実行し、その後、処理 B を別サーバで実行する
- サーバー上で行われる処理を並列実行する
- Cloud Function を定期的に実行する
- GCE インスタンスを指定時間で起動・停止する
- サーバー上での処理が完了すると、slack に通知する


キューサービス・メッセージングサービスは、下記の２種類に分類できる。

- PTP (Peer To Peer) モデル<br>
    1本のキューのみ存在し、送信側と受信側がその１本のキューで 1対1 の形で送受信するモデル<br>
    以下のサービスが、PTP モデルに相当する。
    - Amazon SQS

- Pub/Sub [Publish/Subscribe] モデル<br>
    送信側と受信側が、1 対 1 or 1 対 多の形で送受信するモデル<br>
    以下のサービスが、Pub/Sub モデルに相当する。
    - Google Cloud Pub/Sub

    以下の図は、Pub/Sub での送受信例を示した図である。<br>
    １つまたは複数の Publisher が Message（Event）を Topic に対して Publish すると、その Message に興味のある１つまたは複数の Subscriber がその Message を受け取ることができる動作になる。

    <img src="https://user-images.githubusercontent.com/25688193/120064509-79c5a700-c0a7-11eb-8152-a3ec2fa8422b.png" width="500"><br>
    - Publisher（発行者） : メッセージの送信側
    - Subscriber（購読者） : メッセージの受信側
    - Message（メッセージ） : Publisher がトピックに送信し、最終的にはサブスクライバーに配信されるデータ
    - topic（トピック） : Publisher がメッセージを送信する名前付きのリソース？（キューのこと？）


## 参照サイト
- https://cloud-textbook.com/60/