# 【AWS】Amazon Aurora を使用して MySQL データベースの CRUD 処理を行う（Amazon CLI 使用）

Amazon Aurora は、RDS [Amazon Relational Database Service] の１つのオプション機能であり、MySQL とPostgreSQL 対応のフルマネージド型の RDB（リレーショナルデータベース）サービスになっている。

Amazon Aurora は、以下のような特徴がある

- 動作が高速（MySQLの最大5倍高速、PostgreSQLの最大3倍高速）
- スケールアップ・スケールダウンを容易に行うことができる
- ストレージシステムの拡張性が高い<br>
    データベースインスタンスごとに最大128TBまで自動的にスケールされ耐障害性と自己修復機能も兼ね揃えている

> - RDS [Amazon Relational Database Service]<br>
>    フルマネージド型の RDB（リレーショナルデータベース）サービス。
>    Aurora は RDS の中の１つのオプション機能になっている。
>    RDS と Aurora の相違点としては、xxx


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

1. VPC を作成する<br>
    Aurora の各種インスタンスを配置するための VPC を作成する

1. サブネットを作成する<br>
    Aurora の各種インスタンスを配置するためのサブネットを作成する

1. セキュリティーグループを作成する<br>
    Aurora の各種インスタンスへアクセス可能にするためのセキュリティーグループを作成する

1. クラスタを作成する<br>
    ```sh
    aws rds restore-db-cluster-from-snapshot \
        --db-cluster-identifier ${CLUSTER_NAME} \
    #    --snapshot-identifier sample-snapshot \
        --engine aurora-mysql \
        --engine-version 5.7.mysql_aurora.2.10.1 \
        --availability-zones "ap-northeast-1a" "ap-northeast-1c" \
        --db-subnet-group-name sample-db-subnet-group \
        --db-cluster-parameter-group-name sample-cluster-parameter \
        --vpc-security-group-ids sg-xxxx \
        --kms-key-id xxx \
        --enable-cloudwatch-logs-exports "error" "slowquery"
    ```

1. プライマリインスタンスを作成する<br>
    ```sh
    aws rds create-db-instance \
        --db-cluster-identifier ${CLUSTER_NAME} \
        --db-instance-identifier ${PRIMARY_INSTANCE_NAME} \
        --db-instance-class db.r5.xlarge \
        --db-parameter-group-name sample-instance-parameter \
        --availability-zone ap-northeast-1a \
        --engine aurora-mysql \
        --monitoring-interval 60 \
        --monitoring-role-arn arn:aws:iam::${AWS_ID}:role/rds-monitoring-role \
        --no-publicly-accessible \
        --auto-minor-version-upgrade \
        --storage-encrypted \
        --preferred-maintenance-window mon:13:14-mon:13:44 \
        --enable-performance-insights \
        --performance-insights-kms-key-id xxxx \
        --performance-insights-retention-period 7
    ```

1. レプリカインスタンスを作成する<br>
    ```sh
    aws rds create-db-instance \
        --db-cluster-identifier sample-cluster \
        --db-instance-identifier sample-primary \
        --db-instance-class db.r5.xlarge \
        --db-parameter-group-name sample-instance-parameter \
        --availability-zone ap-northeast-1c \
        --engine aurora-mysql \
        --monitoring-interval 60 \
        --monitoring-role-arn arn:aws:iam::アカウントID:role/rds-monitoring-role \
        --no-publicly-accessible \
        --auto-minor-version-upgrade \
        --storage-encrypted \
        --preferred-maintenance-window mon:13:14-mon:13:44 \
        --enable-performance-insights \
        --performance-insights-kms-key-id xxxx \
        --performance-insights-retention-period 7
    ```

## ■ 参考サイト

- https://dev.classmethod.jp/articles/developers-io-2019-in-osaka-aurora-or-rds/
- xxx
