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

<img width="605" alt="image" src="https://user-images.githubusercontent.com/25688193/178270926-51a45a2c-a1e0-45cb-8dd8-87218956efc6.png">

- キャッシュクラスター<br>
    １つ以上のキャッシュノード（Redis が動作するサーバー）の集合。

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

1. キャッシュクラスターの作成<br>
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

    1. キャッシュクラスター用のサブネットを作成する<br>
        ```sh
        # サブネットマスクを作成
        aws ec2 create-subnet \
            --vpc-id ${VPC_ID} \
            --cidr-block ${CACHE_SUBNET_CIDR_BLOCK} \
            --availability-zone ${ZONE}

        # サブネット ID を取得
        CACHE_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CACHE_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
        echo "created cache subnet id=${CACHE_SUBNET_ID}"

        # サブネットに名前をつける
        aws ec2 create-tags --resources ${CACHE_SUBNET_ID} --tags Key=Name,Value=${CACHE_SUBNET_NAME}
        ```

    1. キャッシュクラスター用のセキュリティーグループを設定する<br>
        VPC 作成時に自動的に作成されるセキュリティーグループに、インバウンドルールを追加して、キャッシュクラスターに EC2 インスタンス経由で接続できるようにする
        ```sh
        # セキュリティグループIDを取得
        SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[0].GroupId --output text | grep sg- )
        echo "created security-group id=${SECURITY_GROUP_ID}"

        # セキュリティグループのインバウンドルールを設定
        aws ec2 authorize-security-group-ingress \
            --group-id ${SECURITY_GROUP_ID} \
            --protocol tcp \
            --port 6379 \
            --cidr 0.0.0.0/0

        #　セキュリティーグループに名前をつける
        aws ec2 create-tags --resources ${SECURITY_GROUP_ID} --tags Key=Name,Value=${CACHE_SECURITY_GROUP_NAME}
        ```

        > キャッシュクラスターのデフォルトのポートは `6379` なので、`6379` を開放するインバウンドルールを作成する

    1. サブネットグループを作成する<br>
        上記作成した VPC 環境で実行させるキャッシュクラスターに対して指定できるサブネットの集合であるサブネットグループを作成する

        ```sh
        aws elasticache create-cache-subnet-group \
            --cache-subnet-group-name ${CACHE_SUBNET_GROUP_NAME} \
            --cache-subnet-group-description "subnet group" \
            --subnet-ids ${CACHE_SUBNET_ID}
        ```

        > 作成したサブネットグループは、「[[Amazon ElastiCache] -> [サブネットグループ] のコンソール画面](https://us-west-2.console.aws.amazon.com/elasticache/home?region=us-west-2#/subnet-groups)」から確認できる

    1. 【オプション】パラメータグループを作成する<br>
        ElastiCache 上にデプロイされた Redis の設定(=パラメータ) を AWS 上で管理するリソースであるパラメータグループを作成する
        ```sh
        aws elasticache create-cache-parameter-group \
            --cache-parameter-group-name ${CACHE_PARAMETER_GROUP_NAME}  \
            --cache-parameter-group-family  redis4.0 \
            --description "parameter group for redis4.0"
        ```

        > 作成したパラメータグループは、「[[Amazon ElastiCache] -> [パラメータグループ] のコンソール画面](https://us-west-2.console.aws.amazon.com/elasticache/home?region=us-west-2#/parameter-groups)」から確認できる

    1. キャッシュクラスターを作成する
        ```sh
        aws elasticache create-cache-cluster \
            --cache-cluster-id ${CACHE_CLUSTER_NAME} \
            --cache-parameter-group ${CACHE_SUBNET_GROUP_NAME} \
            --cache-parameter-group-name ${CACHE_PARAMETER_GROUP_NAME} \
            --engine redis \
            --engine-version 4.0.10 \
            --cache-node-type cache.t2.micro \
            --num-cache-nodes 1
        ```

        > `--cache-parameter-group-name` を省略した場合は、デフォルトパラメータグループが使用される

        > 作成したパラメータグループは、「[[Amazon ElastiCache] -> [Redis クラスター] のコンソール画面](https://us-west-2.console.aws.amazon.com/elasticache/home?region=us-west-2#/redis)」から確認できる

1. EC2 インスタンスの作成<br>
    キャッシュクラスターと同じ VPC 内に、キャッシュクラスターに接続するための EC2 インスタンスを作成する

    1. EC2 インスタンス用の VPC を作成する<br>
        VPC に関しては、前述のキャッシュクラスター用の VPC と同じものを使用する

    1. EC2 インスタンス用のサブネットを作成する<br>
        ```sh
        # サブネットマスクを作成
        aws ec2 create-subnet \
            --vpc-id ${VPC_ID} \
            --cidr-block ${EC2_SUBNET_CIDR_BLOCK} \
            --availability-zone ${ZONE} > log/${EC2_SUBNET_NAME}.json

        # サブネット ID を取得
        EC2_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
        echo "created ec2 subnet id=${EC2_SUBNET_ID}"

        # サブネットに名前をつける
        aws ec2 create-tags --resources ${EC2_SUBNET_ID} --tags Key=Name,Value=${EC2_SUBNET_NAME}
        ```

    1. EC2 インスタンス用のインターネットゲートウェイを作成する<br>
        ```sh
        # インターネットゲートウェイの作成＆インターネットゲートウェイID取得
        EC2_INTERNET_GATEWAY_ID=$( aws ec2 create-internet-gateway | jq -r '.InternetGateway.InternetGatewayId' )
        echo "created internet-gateway id=${EC2_INTERNET_GATEWAY_ID}"

        # インターネットゲートウェイの名前を設定
        aws ec2 create-tags --resources ${EC2_INTERNET_GATEWAY_ID} --tags Key=Name,Value=${EC2_INTERNET_GATEWAY_NAME}

        # 作成したインターネットゲートウェイに VPC を紐付けする
        aws ec2 attach-internet-gateway \
            --internet-gateway-id ${EC2_INTERNET_GATEWAY_ID} \
            --vpc-id ${VPC_ID}
        ```

    1. EC2 インスタンス用のルートテーブルを作成する<br>
        ```sh
        # ルートテーブルの作成＆ルートテーブルID取得
        EC2_ROUTE_TABLE_ID=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
        echo "created route-table id=${EC2_ROUTE_TABLE_ID}"

        # ルートテーブルの名前を設定
        aws ec2 create-tags --resources ${EC2_ROUTE_TABLE_ID} --tags Key=Name,Value=${EC2_ROUTE_TABLE_NAME}

        # ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
        aws ec2 create-route \
            --route-table-id ${EC2_ROUTE_TABLE_ID} \
            --destination-cidr-block 0.0.0.0/0 \
            --gateway-id ${EC2_INTERNET_GATEWAY_ID}

        # ルートをサブネットに紐付け
        aws ec2 associate-route-table \
            --route-table-id ${EC2_ROUTE_TABLE_ID} \
            --subnet-id ${EC2_SUBNET_ID}
        ```

    1. EC2 インスタンス用のセキュリティーグループを作成する<br>
        キャッシュクラスター用のセキュリティーグループと同じものを使用する

    1. キャッシュクラスターに接続するための EC2 インスタンスの作成
        ```sh
        # サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
        aws ec2 modify-subnet-attribute \
            --subnet-id ${EC2_SUBNET_ID} \
            --map-public-ip-on-launch

        # EC2 インスタンスの作成
        aws ec2 run-instances \
            --image-id ${EC2_IMAGE_ID} \
            --instance-type ${EC2_INSTANCE_TYPE} \
            --count 1 \
            --key-name ${SSH_KEY_NAME} \
            --security-group-ids ${SECURITY_GROUP_ID} \
            --subnet-id ${EC2_SUBNET_ID}

        # インスタンスIDを取得
        EC2_INSTANCE_ID=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
        echo "created ec2-instance id=${EC2_INSTANCE_ID}"

        # インスタンスの名前を設定
        aws ec2 create-tags --resources ${EC2_INSTANCE_ID} --tags Key=Name,Value=${EC2_INSTANCE_NAME}
        ```

1. EC2 インスタンスから キャッシュクラスターの Redis に接続する<br>
    1. キャッシュクラスターに接続可能な EC2 インスタンスに接続する<br>
        ```sh
        IP_ADDRESS=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].PublicIpAddress --output text )
        echo "ec2-instance ip=${IP_ADDRESS}"
        ssh -i "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem" ubuntu@${IP_ADDRESS}
        ```

    1. EC2 インスタンスに redis-cli をインストールする<br>
        ```sh
        ```

    1. EC2 インスタンスから キャッシュクラスターの Redis に接続する<br>
        ```sh
        redis-cli -h ${CLUSTER_ENDPOINT_URL} cluster-endpoint -c -p ${PORT} number
        ```

## ■ 参考サイト

- https://docs.aws.amazon.com/ja_jp/AmazonElastiCache/latest/red-ug/GettingStarted.html
- https://siguniang.wordpress.com/2014/09/27/create-elasticache-redis-multi-az-read-replica/
