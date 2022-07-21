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

Amazon Aurora は、以下のようなコンポーネントから構成される

<img width="816" alt="image" src="https://user-images.githubusercontent.com/25688193/180126186-7474d966-1e62-48e4-aebd-4dc387370f46.png">

- クラスター<br>
    xxx

- マスターインスタンス（プライマリインスタンス）<br>
    書き込み＆読み込みを行う DB インスタンス

- リードレプリカ（レプリカインスタンス）<br>
    読み込み専用の DB インスタンス

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

1. MySQL の CLI コマンドをインストールする
    - MacOS の場合
        ```sh
        brew info mysql
        ```

    - Ubuntu の場合
        ```sh
        ```

1. VPC を作成する<br>
    Aurora の各種インスタンスを配置するための VPC を作成する
    ```sh
    # VPC を作成
    aws ec2 create-vpc --cidr-block ${VPC_CIDR_BLOCK} > log/${VPC_NAME}.json

    # 作成した VPC の VPC ID 取得
    VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
    echo "created vpc id=${VPC_ID}"

    # VPC に名前をつける
    aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}

    # DNS ホスト名を有効化
    aws ec2 modify-vpc-attribute --vpc-id ${VPC_ID} --enable-dns-hostnames
    ```

    > Amazon Aurora を外部利用（VPC外部から利用）する際には、DNS ホスト名を有効にする必要があるので、`aws ec2 modify-vpc-attribute` コマンドで DNS ホスト名を有効化している

1. サブネットを作成する<br>
    Aurora の各種インスタンスを配置するためのサブネットを作成する
    ```sh
    #-----------------------------
    # サブネット１を作成する
    #-----------------------------
    # サブネットマスクを作成
    aws ec2 create-subnet \
        --vpc-id ${VPC_ID} \
        --cidr-block ${SUBNET_CIDR_BLOCK_1} \
        --availability-zone ${ZONE_1} > log/${SUBNET_NAME_1}.json

    # サブネット ID を取得
    SUBNET_ID_1=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK_1}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
    echo "created ec2 subnet id=${SUBNET_ID_1}"

    # サブネットに名前をつける
    aws ec2 create-tags --resources ${SUBNET_ID_1} --tags Key=Name,Value=${SUBNET_NAME_1}

    #-----------------------------
    # サブネット２を作成する
    #-----------------------------
    # サブネットマスクを作成
    aws ec2 create-subnet \
        --vpc-id ${VPC_ID} \
        --cidr-block ${SUBNET_CIDR_BLOCK_2} \
        --availability-zone ${ZONE_2} > log/${SUBNET_NAME_2}.json

    # サブネット ID を取得
    SUBNET_ID_2=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK_2}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
    echo "created ec2 subnet id=${SUBNET_ID_2}"

    # サブネットに名前をつける
    aws ec2 create-tags --resources ${SUBNET_ID_2} --tags Key=Name,Value=${SUBNET_NAME_2}
    ```

    > 後述の DB サブネットグループでは、少なくとも２つのサブネットが必要なので、２つのサブネットを作成する

1. インターネットゲートウェイを作成する<br>
    外部から VPC 内の Amzon Aurora にアクセスするためのインターネットゲートウェイを作成する
    ```sh
    # インターネットゲートウェイの作成＆インターネットゲートウェイID取得
    INTERNET_GATEWAY_ID=$( aws ec2 create-internet-gateway | jq -r '.InternetGateway.InternetGatewayId' )
    echo "created internet-gateway id=${INTERNET_GATEWAY_ID}"

    # インターネットゲートウェイの名前を設定
    aws ec2 create-tags --resources ${INTERNET_GATEWAY_ID} --tags Key=Name,Value=${INTERNET_GATEWAY_NAME}

    # 作成したインターネットゲートウェイに VPC を紐付けする
    aws ec2 attach-internet-gateway \
        --internet-gateway-id ${INTERNET_GATEWAY_ID} \
        --vpc-id ${VPC_ID}
    ```

1. ルートテーブルを作成する<br>
    ```sh
    #-----------------------------
    # ルートテーブル１を作成する
    #-----------------------------
    # ルートテーブルの作成＆ルートテーブルID取得
    ROUTE_TABLE_ID_1=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
    echo "created route-table id=${ROUTE_TABLE_ID_1}"

    # ルートテーブルの名前を設定
    aws ec2 create-tags --resources ${ROUTE_TABLE_ID_1} --tags Key=Name,Value=${ROUTE_TABLE_NAME_1}

    # ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
    aws ec2 create-route \
        --route-table-id ${ROUTE_TABLE_ID_1} \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id ${INTERNET_GATEWAY_ID}

    # ルートをサブネットに紐付け
    aws ec2 associate-route-table \
        --route-table-id ${ROUTE_TABLE_ID_1} \
        --subnet-id ${SUBNET_ID_1}

    #-----------------------------
    # ルートテーブル２を作成する
    #-----------------------------
    # ルートテーブルの作成＆ルートテーブルID取得
    ROUTE_TABLE_ID_2=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
    echo "created route-table id=${ROUTE_TABLE_ID_2}"

    # ルートテーブルの名前を設定
    aws ec2 create-tags --resources ${ROUTE_TABLE_ID_2} --tags Key=Name,Value=${ROUTE_TABLE_NAME_2}

    # ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
    aws ec2 create-route \
        --route-table-id ${ROUTE_TABLE_ID_2} \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id ${INTERNET_GATEWAY_ID}

    # ルートをサブネットに紐付け
    aws ec2 associate-route-table \
        --route-table-id ${ROUTE_TABLE_ID_2} \
        --subnet-id ${SUBNET_ID_2}
    ```

1. セキュリティーグループを作成する<br>
    Aurora の各種インスタンスへアクセス可能にするためのセキュリティーグループを作成する
    ```sh
    # セキュリティグループ作成
    SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${SECURITY_GROUP_NAME} --description "security group for efs" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
    echo "created security-group id=${SECURITY_GROUP_ID}"

    # セキュリティグループのインバウンドルールを設定（SSH接続）
    aws ec2 authorize-security-group-ingress \
        --group-id ${SECURITY_GROUP_ID} \
        --protocol tcp \
        --port 3306 \
        --cidr 0.0.0.0/0 > log/${SECURITY_GROUP_NAME}.json
        
    aws ec2 create-tags --resources ${SECURITY_GROUP_ID} --tags Key=Name,Value=${SECURITY_GROUP_NAME}
    ```

    > クラスタ内の MySQL では `3306` を使用するのでこのポート番号を解放する

1. DB サブネットグループを作成する<br>
    ```sh
    aws rds create-db-subnet-group \
        --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
        --db-subnet-group-description "aurora mysql subnet group" \
        --subnet-ids "${SUBNET_ID_1}" "${SUBNET_ID_2}" > log/${DB_SUBNET_GROUP_NAME}.json
    ```

    > `--subnet-ids` には、最低２つの AZ（アベイラビリティーゾーン）のサブネットを指定する必要がある

    > 作成した DB サブネットグループは、「[[Amazon RDS] -> [サブネットグループ] コンソール画面](https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#db-subnet-groups-list:)」から確認できる

1. クラスタを作成する<br>
    MySQL をエンジンとする Aurora のクラスターを作成する
    ```sh
    aws rds create-db-cluster \
        --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
        --engine aurora-mysql \
        --engine-version 8.0 \
        --master-username admin \
        --master-user-password 12345678 \
        --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
        --vpc-security-group-ids ${SECURITY_GROUP_ID} \
        --availability-zones ${ZONE_1}
    ```

    > `aws rds create-db-cluster` コマンド実行後の出力コンソールの `Endpoint` に、クラスター内の DB インスタンスにアクセスするためのエンドポイントの URL が出力される

1. マスターインスタンス（プライマリインスタンス）を作成する<br>
    クラスターの中に MySQL をエンジンとするマスターインスタンスを作成する。マスターインスタンスは、MySQL データベースへの書き込みと読み込みを行う

    ```sh
    aws rds create-db-instance \
        --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
        --db-instance-identifier ${MASTER_INSTANCE_NAME} \
        --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
        --db-instance-class ${DB_INSTANCE_TYPE} \
        --availability-zone ${ZONE_1} \
        --engine aurora-mysql \
        --engine-version 8.0 \
        --publicly-accessible
    ```
    - `--db-instance-class` : `db.r5.large` など
    - xxx

1. リードレプリカ（レプリカインスタンス）を作成する<br>
    クラスターの中に MySQL をエンジンとするリードレプリカを作成する。リードレプリカは、MySQL データベースへの読み込みのみを行う

    ```sh
    aws rds create-db-instance \
        --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
        --db-instance-identifier ${REPLICA_INSTANCE_NAME} \
        --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
        --db-instance-class ${DB_INSTANCE_TYPE} \
        --availability-zone ${ZONE_2} \
        --engine aurora-mysql \
        --engine-version 8.0 \
        --publicly-accessible
    ```

    > 作成したクラスターと DB インスタンスは、「[[Amazon RDS] -> [データベース] コンソール画面](https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#databases:)」から確認できる<br>
    > <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/180122641-0a25aa12-bf7f-4637-94e9-2ea5889f3a0c.png">

1. MySQL データベースにアクセスするためのエンドポイントを取得する<br>
    ```sh
    # クラスターエンドポイント（書き込み＆読み込み用エンドポイント）を取得
    ENDPOINT_URL=$( aws rds describe-db-clusters --query DBClusters[*].Endpoint --output text )
    echo "ENDPOINT_URL : ${ENDPOINT_URL}"

    # 読み込みエンドポイントを取得
    READER_ENDPOINT_URL=$( aws rds describe-db-clusters --query DBClusters[*].ReaderEndpoint --output text )
    echo "READER_ENDPOINT_URL : ${READER_ENDPOINT_URL}"
    ```

1. mysql コマンドで エンドポイントにアクセスする<br>
    ```sh
    mysql -u admin -p -h ${ENDPOINT_URL}
    ```
    
    上記コマンド実行後にパスワード入力を求められるので、`aws rds create-db-cluster` コマンド実行時の `--master-user-password` で指定した値（今回の場合は `12345678`）を入力する
    
1. クラスター上の MySQL データベースの CRUD 処理を行う<br>
    クラスター上の MySQL 接続後に SQL 構文を使用して、MySQL データベースの CRUD 処理を行う

    1. MySQL データベースを作成する
        ```sql
        CREATE DATABASE sample_database;
        ```
    1. データベースにデータを追加する
        ```sql
        USE sample_database;
        CREATE TABLE entries (name VARCHAR(255), gender VARCHAR(255), entryID INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(entryID));
            INSERT INTO entries (name, gender) values ("Yagami", "male");
            INSERT INTO entries (name, gender) values ("Yagoo", "male");
        ```
    1. 作成したデータベースを取得する
        ```sql
        SELECT * FROM entries;
        ```
        ```sql
        mysql> SELECT * FROM entries;
        +--------+--------+---------+
        | name   | gender | entryID |
        +--------+--------+---------+
        | Yagami | male   |       1 |
        | Yagoo  | male   |       2 |
        +--------+--------+---------+
        2 rows in set (1.71 sec)
        ```
        
## ■ 参考サイト

- https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.CreateInstance.html
- https://dev.classmethod.jp/articles/developers-io-2019-in-osaka-aurora-or-rds/
- https://zenn.dev/nekoniki/articles/5da3016346b4b0