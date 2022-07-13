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

Amazon ElastiCache には、以下のようなコンポーネントが存在する。Amazon ElastiCache と同じ VPC 内の EC2 インスタンスからしかクラスター内の redis に接続できないことに注意

<img width="843" alt="image" src="https://user-images.githubusercontent.com/25688193/178675544-4e59606b-c5a3-4407-8102-1b355add7e7a.png">

<img width="690" alt="image" src="https://user-images.githubusercontent.com/25688193/178502456-bb742698-fb54-421a-9d30-9a1413c3492b.png">

- キャッシュクラスター<br>
    １つ以上のキャッシュノード（Redis が動作するサーバー）の集合。

- サブネットグループ<br>
    VPC 環境で実行しているクラスターに対して指定できるサブネットの集合

- パラメータグループ<br>
    ElastiCache 上にデプロイされた Redis の設定(=パラメータ) をAWS上で管理するリソース

- プライマリノード<br>
    xxx

- レプリカノード<br>
    xxx

- ノードグループ（シャード）<br>
    xxx

- レプリケーショングループ<br>
    xxx

- クラスターモード<br>
    クラスターモードが無効な場合は単一のシャード（ノードグループ）構成となり、プライマリノードは全体で一つのみになる。<br>
    クラスターモードが有効な場合は最大 500 個までシャード（ノードグループ）を増やすことができ、それぞれのシャード（ノードグループ）にプライマリノードが存在する。

    本項で記載する方法では、クラスターモードが無効の場合の構成になる

- エンドポイント<br>
    - Configuration Endpoint（設定エンドポイント）<br>
        クラスターモードが有効の場合のみ割り当てられるエンドポイントで、シャーディング（ノードグループ）構成全体に対してのエンドポイント。シャーディング（ノードグループ）構成全体に対する読み込み、書き込み操作を行うために使う

    - PrimaryEndpoint（プライマリエンドポイント）<br>
        クラスターモードが無効の場合のみ割り当てられるエンドポイントで、シャード（ノードグループ）のプライマリーノードに対してのエンドポイント。シャード（ノードグループ）に対する書き込み操作を行うために使う

    - ReaderEndpoint（リーダーエンドポイント）<br>
        クラスターモードが無効の場合のみ割り当てられるエンドポイントで、シャード（ノードグループ）のレプリカノード群に対してのエンドポイント。シャード（ノードグループ）に対する読み込み操作を行うために使う


## ■ ToDo

- [ ] EC2 インスタンスから、クラスターのエンドポイントに redis-cli コマンドでアクセスしても、redis に接続できない問題の解決

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

        # セキュリティグループのインバウンドルールを設定（SSH接続）
        aws ec2 authorize-security-group-ingress \
            --group-id ${SECURITY_GROUP_ID} \
            --protocol tcp \
            --port 22 \
            --cidr 0.0.0.0/0

        # セキュリティグループのインバウンドルールを設定（キャッシュクラスターへの接続）
        aws ec2 authorize-security-group-ingress \
            --group-id ${SECURITY_GROUP_ID} \
            --protocol tcp \
            --port 6379 \
            --cidr 0.0.0.0/0

        #　セキュリティーグループに名前をつける
        aws ec2 create-tags --resources ${SECURITY_GROUP_ID} --tags Key=Name,Value=${CACHE_SECURITY_GROUP_NAME}
        ```

        > キャッシュクラスターのデフォルトのポートは `6379` なので、`6379` ポートを開放するインバウンドルールを作成する

        > EC2インスタンスでも使用するセキュリティーグループなので、ssh 接続で使用する `22` ポートを開放するインバウンドルールも作成する

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

        > 作成したキャッシュクラスターは、「[[Amazon ElastiCache] -> [Redis クラスター] のコンソール画面](https://us-west-2.console.aws.amazon.com/elasticache/home?region=us-west-2#/redis)」から確認できる

        > `aws elasticache create-cache-cluster` コマンドで作成したキャッシュクラスターは、クラスターモードが無効になることに注意

    1. キャッシュクラスターにセキュリティーグループを適用する<br>
        「[[Amazon ElastiCache] -> [Redis クラスター] のコンソール画面](https://us-west-2.console.aws.amazon.com/elasticache/home?region=us-west-2#/redis)」から、作成したキャッシュクラスターを選択し、「変更」->「セキュリティー」から変更できる。

    1. レプリケーショングループを作成する<br>
        クラスター内にレプリカノードを配置するためのレプリケーショングループを作成する
        ```sh
        aws elasticache create-replication-group \
            --replication-group-id ${CACHE_REPLICA_GROUP_NAME} \
            --primary-cluster-id ${CACHE_CLUSTER_NAME} \
            --replication-group-description 'test replication group'
        ```

        > レプリケーショングループを作成することで、キャッシュクラスターの PrimaryEndpoint（URL:`${CACHE_REPLICA_GROUP_NAME}.a5lv69.ng.0001.usw2.cache.amazonaws.com:6379` のような形式） と ReaderEndpoint（URL : `${CACHE_REPLICA_GROUP_NAME}-ro.a5lv69.ng.0001.usw2.cache.amazonaws.com:6379` のような形式）が割り当て、キャッシュクラスター内の Redis にアクセス可能になる

    1. レプリカノードを作成する<br>
        上記作成したレプリケーショングループ内にレプリカノードを追加する
        ```sh
        aws elasticache create-cache-cluster \
            --cache-cluster-id ${CACHE_REPLICA_CLUSTER_NAME} \
            --replication-group-id ${CACHE_REPLICA_GROUP_NAME} \
            --preferred-availability-zone ${ZONE}
        ```

        >  キャッシュクラスター作成時にも使用したコマンド `aws elasticache create-cache-cluster` を使用していることに注意。（但し、今回は `--replication-group-id` オプションを指定している）

    <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/178510260-b01c0ce4-9750-4c35-a6c7-dc4fcf4e6200.png">


1. EC2 インスタンスの作成<br>
    Amazon ElastiCache と同じ VPC 内の EC2 インスタンスからしかクラスター内の redis に接続できないので、キャッシュクラスターと同じ VPC 内に、キャッシュクラスターに接続するための EC2 インスタンスを作成する

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
        - Ubuntu の場合
            ```sh
            sudo apt update
            sudo apt install redis-server
            ```

    1. EC2 インスタンスから キャッシュクラスターの Redis に接続する<br>
        ```sh
        redis-cli -h ${ENDPOINT_URL} -p "6379"
        ```
        - `${ENDPOINT_URL}` : キャッシュクラスター（厳密にはノードグループ）のエンドポイントの URL
            - PrimaryEndpoint の場合 : `${CACHE_REPLICA_GROUP_NAME}.a5lv69.ng.0001.usw2.cache.amazonaws.com` のような形式
            - ReaderEndpoint の場合 : `${CACHE_REPLICA_GROUP_NAME}-ro.a5lv69.ng.0001.usw2.cache.amazonaws.com` のような形式

<!--
1. ローカルPCからキャッシュクラスターの Redis に接続する場合<br>

    1. ローカルPCに redis-cli をインストールする<br>
        - Mac の場合<br>
            ```sh
            brew install redis
            ```

        - Ubuntu の場合<br>
            ```sh
            sudo apt update
            sudo apt install redis-server
            ```

    1. EC2 インスタンスから キャッシュクラスターの Redis に接続する<br>
        ```sh
        redis-cli -h ${ENDPOINT_URL} -p "6379"
        ```

        - `${ENDPOINT_URL}` : キャッシュクラスター（厳密にはノードグループ）のエンドポイントの URL
            - PrimaryEndpoint の場合 : `${CACHE_REPLICA_GROUP_NAME}.a5lv69.ng.0001.usw2.cache.amazonaws.com:6379` のような形式
            - ReaderEndpoint の場合 : `${CACHE_REPLICA_GROUP_NAME}-ro.a5lv69.ng.0001.usw2.cache.amazonaws.com:6379` のような形式

-->

## ■ 参考サイト

- https://docs.aws.amazon.com/ja_jp/AmazonElastiCache/latest/red-ug/GettingStarted.html
- https://siguniang.wordpress.com/2014/09/27/create-elasticache-redis-multi-az-read-replica/
- https://qiita.com/charon/items/53790d8826e32561535d