# 【AWS】Amazon ElastiCache for Redis を使用してメモリのキャッシングを行う（AWS CLI 使用）

Amazon ElastiCache は、データのキャッシング（一時保管）をクラウド上で行うフルマネージド型のインメモリキャッシングサービスであり、以下のような特徴がある

> インメモリ : ソフトウェアを実行する際、使用するプログラムやデータのすべてをメインメモリ（RAM）上に読み込み、ストレージ（外部記憶装置）を使わない方法

- データをノードのメモリに保存するので、HDD や SSD への書き込み読み込みより、非常に高速なデータの出し入れが出来る
- スケールイン、スケールアウト、スケールアップを行うことができる

Amazon ElastiCache では、サードパーティーのキャッシング・キューサービスである Memcached か Redis をエンジンとして使用できるが、両者の違いは以下のようになる。

- Redis をエンジンとして使用する場合<br>
    - シングルスレッドで動作する
    - データを永続化可能

- Memcached をエンジンとして使用する場合<br>
    - マルチスレッドで動作する
    - データを永続化できない

今回は Redis をエンジンとして使用する

Amazon ElastiCache には、以下のようなコンポーネントが存在する

- キャッシュクラスター<br>
    1 つ以上のキャッシュノード（Redis が動作するEC2インスタンス）の集合。

- サブネットグループ<br>
    VPC 環境で実行しているクラスターに対して指定できるサブネットの集合

- パラメータグループ<br>
    ElastiCache 上にデプロイされた Redis の設定(=パラメータ) をAWS上で管理するリソース

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

1. Amazon ElastiCache 用の IAM role を作成する<br>
    IAM policy `AmazonElastiCacheFullAccess`（ARN名 : `arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess`）をもつ IAM role を作成する

    ```sh
    if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
        # IAM ロールを作成する
        aws iam create-role \
            --role-name ${IAM_ROLE_NAME} \
            --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}"

        # 作成した IAM ロールに IAM ポリシーを付与する
        aws iam attach-role-policy \
            --role-name ${IAM_ROLE_NAME} \
            --policy-arn arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess
    fi
    ```

    - 一般的な ElastiCache システム管理者タスクの実行を許可する policy 定義
        ```json
        {
            "Version": "2012-10-17",
            "Statement":[
                {
                    "Sid": "ECAllowSpecific",
                    "Effect":"Allow",
                    "Action":[
                        "elasticache:*"
                    ],
                    "Resource":"*"
                }
            ]
        }
        ```

1. キャッシュクラスターを配置するための VPC を作成する<br>
    ```sh
    # VPC を作成
    aws ec2 create-vpc --cidr-block ${VPC_CIDR_BLOCK}

    # 作成した VPC の VPC ID 取得
    VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
    echo "created vpc id=${VPC_ID}"

    # VPC に名前をつける
    aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}
    ```

1. VPC 内にサブネットを作成する<br>
    ```sh
    # サブネットマスクを作成
    aws ec2 create-subnet \
        --vpc-id ${VPC_ID} \
        --cidr-block ${SUBNET_CIDR_BLOCK} \
        --availability-zone ${ZONE}

    # サブネット ID を取得
    SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
    echo "created subnet id=${SUBNET_ID}"

    # サブネットに名前をつける
    aws ec2 create-tags --resources ${SUBNET_ID} --tags Key=Name,Value=${SUBNET_NAME}
    ```

1. サブネットグループを作成する<br>
    上記作成した VPC 環境で実行させるキャッシュクラスターに対して指定できるサブネットの集合であるサブネットグループを作成する

    ```sh
    aws elasticache create-cache-subnet-group \
        --cache-subnet-group-name ${SUBNET_GROUP_NAME} \
        --cache-subnet-group-description "subnet group" \
        --subnet-ids ${SUBNET_ID}
    ```

1. 【オプション】パラメータグループを作成する<br>
    ElastiCache 上にデプロイされた Redis の設定(=パラメータ) を AWS 上で管理するリソースであるパラメータグループを作成する
    ```sh
    aws elasticache create-cache-parameter-group \
        --cache-parameter-group-name ${PARAMETER_GROUP_NAME}  \
        --cache-parameter-group-family  redis4.0 \
        --description "parameter group for redis4.0"
    ```

1. キャッシュクラスターを作成する
    ```sh
    aws elasticache create-cache-cluster \
        --cache-cluster-id ${CLUSTER_NAME} \
        --cache-parameter-group ${SUBNET_GROUP_NAME} \
    	--cache-parameter-group-name ${PARAMETER_GROUP_NAME} \
        --engine redis \
        --engine-version 3.2.4 \
        --cache-node-type cache.t2.micro \
        --num-cache-nodes 1
    ```

    > `--cache-parameter-group-name` を省略した場合は、デフォルトパラメータグループが使用される

## ■ 参考サイト

- https://docs.aws.amazon.com/ja_jp/AmazonElastiCache/latest/red-ug/GettingStarted.html
- https://siguniang.wordpress.com/2014/09/27/create-elasticache-redis-multi-az-read-replica/
