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

1. クラスターを配置するための VPC を作成する<br>
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

1. Amazon ElastiCache のクラスターを作成する
    ```sh
    ```

1. xxx

## ■ 参考サイト

- https://siguniang.wordpress.com/2014/09/27/create-elasticache-redis-multi-az-read-replica/