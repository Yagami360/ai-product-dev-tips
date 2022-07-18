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
    ```sh
    # VPC を作成
    aws ec2 create-vpc --cidr-block ${VPC_CIDR_BLOCK} > log/${VPC_NAME}.json

    # 作成した VPC の VPC ID 取得
    VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
    echo "created vpc id=${VPC_ID}"

    # VPC に名前をつける
    aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}
    ```

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

    > 作成したクラスターは、「[[Amazon RDS] -> [データベース] コンソール画面](https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#databases:)」から確認できる

1. プライマリインスタンスを作成する<br>
    ```sh
    aws rds create-db-instance \
        --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
        --db-instance-identifier ${PRIMARY_INSTANCE_NAME} \
        --db-instance-class db.r5.xlarge \
        --db-parameter-group-name sample-instance-parameter \
        --availability-zone ${ZONE_1} \
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
        --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
        --db-instance-identifier sample-primary \
        --db-instance-class db.r5.xlarge \
        --db-parameter-group-name sample-instance-parameter \
        --availability-zone ap-northeast-1c \
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

## ■ 参考サイト

- https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.CreateInstance.html
- https://dev.classmethod.jp/articles/developers-io-2019-in-osaka-aurora-or-rds/
