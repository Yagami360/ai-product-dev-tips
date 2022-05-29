# 【GCP】Google Cloud SQL の基礎事項

Google Cloud SQL は、GCP が提供している RDB（MySQL, PostgreSQL, SQL Server）に対してのデータベースサービスで、以下のような機能やメリットをもつ

- ストレージ容量の管理
- バックアップの自動化
- 高可用性と障害復旧やフェイルオーバー機能
- 高いセキュリティレベル
- スケーリング機能
- 多の GCP サービスとの連携が良い

> - RDB（リレーショナルデータベース）<br>
> 表形式の構造化データを保管するためのデータベース

> - Cloud Storate, BigQuery などとの違い<br>
> <img width="475" alt="image" src="https://user-images.githubusercontent.com/25688193/167242282-37c400e6-a6f8-4baa-aa5b-bdd83d8dbcc8.png">


Cloud SQL は、以下のようなコンポーネントから構成される

- Cloud SQL インスタンス<br>
    Google Cloud SQL では、Cloud SQL インスタンス（MySQL用, PostgreSQL用, SQL Server用のCloud SQL インスタンスがそれぞれ存在）と呼ばれる VM インスタンスを構築することで、データベースの管理を行う

    <img width="400" alt="image" src="https://user-images.githubusercontent.com/25688193/167243077-1b2a7671-ea1d-4dcc-bf89-18c9522c095f.png">

    - Cloud SQL インスタンスへの接続方式<br>
        Cloud SQL インスタンスへの接続を行う際には、以下のような公開範囲や接続方法を選択できる

        - 公開範囲
            - プライベート IP アドレス : VPC 内部のみで接続可能（外部公開しない）
            - パブリック IP アドレス : 外部（インターネット）から接続可能

        - 接続方法
            - `gcloud sql connect` コマンドで接続
            - Cloud SQL Auth Proxy を使用して接続：プロキシサーバー経由で接続する・IAM 権限が必要

    <!--
            - セルフマネージド SSL / TLS 証明書 : 特定の公開鍵に基づく接続のみを許可する
            - 承認済みネットワーク : 接続可能な IP アドレスのリスト。
    -->

- xxx

## ◎ 参考サイト

- https://cloud.google.com/sql/docs/introduction?hl=ja