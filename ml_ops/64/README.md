# Opsgenie を使用して EC2 インスタンスに導入している Datadog で検知したアラートを管理・通知する

Opsgenie は、監視対象サーバーに導入している Datadog, Cloud Logging (StackDriver) などから検知したアラートを集約し、発生したアラートに対して誰が、いつ、どういった対応をしたのかを管理し、Slack などのツールに通知することが可能なツールである。

Opsgenie を利用することで、サーバーで発生したアラートを見逃すことなくサーバーやプロダクトを運用できるようになるメリットがある

<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/171974763-f81971b7-2d3a-478f-a191-0c7705bf007c.png">

ここでは、Opsgenie を使用して EC2 インスタンスに導入している Datadog で検知したアラートを管理・通知する方法を記載する

## ■ 方法

### ◎ Opsgenie の設定

1. [Opsgenie サイト](https://www.atlassian.com/ja/software/opsgenie) から、ユーザー登録を行う

    > 14日間の無料トライアルが可能

1. ユーザー登録後、「Quick start guide」に従って初回設定を行う<br>
    1. 電話番号の SMS 認証を行う<br>
        > 先頭に +81 がつくので、電話番号が 090-xxxx-xxxx の場合は、90-xxx-xxxx を入力すればよい

    1. チームを作成する<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/171977710-a21d20ed-76e6-4c89-a399-9f391f6dab6d.png"><br>
    1. ロギング＆モニタリングツールのインテグレーションを追加する<br>
        作成したチームに対して、Datadog のインテグレーションを行う<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/171978602-cb824800-d74e-4397-866e-d07085d769b3.png">

        > Datadog 以外にも様々なツールのインテグレーションが可能になっている

    1. 通知ツールのインテグレーションを行う<br>
        作成したチームに対して、Slack のインテグレーションを行う<br>

### ◎ EC2インスタンスの作成

<img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172035178-ae152147-2056-489f-850a-72da46833dab.png">

> - VPC [Virtual Private Cloud]<br>
> AWS専用の仮想ネットワーク。インターネットを利用する際、ルーターやゲートウェイなどのネットワーク機器が必要となるが、VPCはそれらの機器を仮想的に用意し、ネットワーク環境を構築できるようにしている。

<br>

> - サブネット<br>
> １つの大きなネットワークを管理しやすくするために、より小さなネットワークに分割したときのサブネットワークのこと。<br>

<br>

> - インターネットゲートウェイ<br>
> コンピュータネットワークにおいて、通信プロトコルが異なるネットワーク同士がデータをやり取りする際、中継する役割を担うルータのような機能を備えた機器やそれに関するソフトウェア

<br>

> - ルーティングテーブル<br>
> ルーターに記録される経路情報で、ルーティング処理を行う際に参照されるテーブルデータ。インターネットゲートウェイ経由で VPC へアクセスできるようにするために必要になる

<br>

> - CIDR 表記<br>
> `198.51.100.xxx/24` のような形で、IPアドレスの後ろに `/` と２進数のサブネットマスクにおける１の個数を書く表記方法。<br>
> 例えば、`/16 => 11111111.11111111.00000000.00000000 => 255.255.0.0` のサブネットマスクとなり、
> `/24 => 11111111.11111111.11111111.00000000 => 255.255.255.0` のサブネットマスクとなる。<br>
> <img src="https://user-images.githubusercontent.com/25688193/114671501-21c52200-9d3f-11eb-8d31-e22711f96c4b.png" width="300"><br>

<br>

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
    ```sh
    # VPC 作成
    aws ec2 create-vpc --cidr-block ${CIDR_BLOCK}/16

    # 作成した VPC の VPC ID 取得
    VPC_ID=`aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- | sed 's/ //g' | sed 's/"//g'`

    # VPC に名前をつける
    aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}
    ```

    > `--vpc-id` は、`aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId` などで取得可能

1. サブネットを作成する<br>
    ```sh
    # サブネットマスクを作成
    aws ec2 create-subnet \
        --vpc-id ${VPC_ID} \
        --cidr-block ${CIDR_BLOCK}/24 \
        --availability-zone ${ZONE}

    # サブネット ID を取得
    SUBNET_ID=`aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query Subnets[*].SubnetId | grep subnet- | sed 's/ //g' | sed 's/"//g'`

    # サブネットに名前をつける
    aws ec2 create-tags --resources ${SUBNET_ID} --tags Key=Name,Value=${SUBNET_NAME}
    ```
    
    > `aws ec2 create-vpc` の `--cidr_block` で指定する VPC の IP アドレスと `aws ec2 create-subnet` の `--cidr_block` で指定するサブネットの IP アドレスは、サブネット部のみ変更された値となり、サブネットマスクは /24 = 255.255.255.0 のサブネット部のマスク値になる

    > <img src="https://user-images.githubusercontent.com/25688193/114671501-21c52200-9d3f-11eb-8d31-e22711f96c4b.png" width="300"><br>


1. インターネットゲートウェイを作成する<br>
    ```sh
    # インターネットゲートウェイの作成＆インターネットゲートウェイID取得
    INTERNET_GATEWAY_ID=$( aws ec2 create-internet-gateway | jq -r '.InternetGateway.InternetGatewayId' )

    # インターネットゲートウェイの名前を設定
    aws ec2 create-tags --resources ${INTERNET_GATEWAY_ID} --tags Key=Name,Value=${INTERNET_GATEWAY_ID}     

    # 作成したインターネットゲートウェイに VPC をアタッチする
    aws ec2 attach-internet-gateway \
        --internet-gateway-id ${INTERNET_GATEWAY_ID} \
        --vpc-id ${VPC_ID}
    ```
    > インターネットゲートウェイの作成は、`aws ec2 create-internet-gateway` で行えるが、インターネットゲートウェイIDも同時に取得させるために、`aws ec2 create-internet-gateway` コマンドの json 出力結果に対して、`jq` コマンドで json 出力の要素を抽出し、インターネットゲートウェイID取得を出力している

1. ルーティングテーブルの作成<br>
    インターネットゲートウェイ経由で VPC へアクセスできるようにするためのルートテーブルを作成し、インターネットゲートウェイとサブネットに紐付ける。

    ```sh
    # ルートテーブルの作成＆ルートテーブルID取得
    ROUTE_TABLE_ID=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
    echo "created route-table id=${ROUTE_TABLE_ID}"

    # ルートテーブルの名前を設定
    aws ec2 create-tags --resources ${ROUTE_TABLE_ID} --tags Key=Name,Value=${ROUTE_TABLE_NAME}

    # ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
    aws ec2 create-route \
        --route-table-id ${ROUTE_TABLE_ID} \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id ${INTERNET_GATEWAY_ID}

    # ルートをサブネットに紐付け
    aws ec2 associate-route-table \
        --route-table-id ${ROUTE_TABLE_ID} \
        --subnet-id ${SUBNET_ID}
    ```

1. セキュリティーグループの作成<br>
    ```sh
    # セキュリティーグループの作成＆セキュリティグループIDを取得
    SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${SECURITY_GROUP_NAME} --description "security group for ec2 instance" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
    echo "created security-group id=${SECURITY_GROUP_ID}"

    # セキュリティグループのインバウンドルールを設定
    aws ec2 authorize-security-group-ingress \
        --group-id ${SECURITY_GROUP_ID} \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    ```

1. SSH Key の登録<br>
    EC2 インスタンスに ssh 接続するための `.ssh/*.pem` 形式での SSH 鍵が存在しない場合は、SSH 鍵を生成する
    ```sh
    aws ec2 create-key-pair --key-name ${SSH_KEY_NAME} --query 'KeyMaterial' --output text > ${HOME}/.ssh/${SSH_KEY_NAME}
    chmod 400 ${HOME}/.ssh/${SSH_KEY_NAME}
    ```

1. EC2 インスタンスの作成<br>
    ```sh
    # サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
    aws ec2 modify-subnet-attribute \
        --subnet-id ${SUBNET_ID} \
        --map-public-ip-on-launch

    # EC2 インスタンスの作成
    aws ec2 run-instances \
        --image-id ${IMAGE_ID} \
        --instance-type ${INSTANCE_TYPE} \
        --count 1 \
        --key-name ${SSH_KEY_NAME} \
        --security-group-ids ${SECURITY_GROUP_ID} \
        --subnet-id ${SUBNET_ID}

    # インスタンスIDを取得
    INSTANCE_ID=`aws ec2 describe-instances --filter "Name=subnet-id,Values=${SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId | grep i- | sed 's/ //g' | sed 's/"//g'`
    echo "created ec2-instance id=${INSTANCE_ID}"

    # インスタンスの名前を設定
    aws ec2 create-tags --resources ${INSTANCE_ID} --tags Key=Name,Value=${INSTANCE_NAME}
    ```
    - `--key-name` : pem ファイルパスではなく、`aws ec2 create-key-pair` コマンドの `--key-name` で設定した名前

1. EC2 インスタンスに接続する<br>
    ```sh
    ssh -i "${HOME}/.ssh/${SSH_KEY_NAME}.pem" ubuntu@${IP_ADDRESS}
    ```


### ◎ Datadog の設定

1. 事前準備<br>
    Datadog のユーザー登録を行っていない場合は、[Datadog サイト](https://www.datadoghq.com/ja/) から「無料トライアルを開始」ボタンをクリックして、ユーザー登録を行う<br>

    > 無料トライアルの場合でも、会社名の記載が必要であることに注意

    > Google アカウントでサインインすれば、会社名の記入不要でおすすめ

1. Opsgenie のインテグレーション
    1. 「Integrations」タブから Opsgenie を選択する<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172161536-9f106ae9-e01d-488a-8f0f-6545c498788b.png"><br>

    1. 設定タブから Service「+New」ボタンをクリックし、「Service Name」と「Opsgenie API Key」を入力し、「Save」ボタンをクリックする。このとき API キーには、Opsgenie コンソール画面からコピーした API キーを設定する<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172162090-901f4915-ec86-46f9-b1b3-eb20b2a42853.png">

    1. 【オプション】Datadog と Opsgenie の連携が正常に動作していることを確認するため、Datadog の「Event」タグから「Add」ボタンをクリックし、`@opsgenie` で

        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172163959-66dbec86-7bcd-445c-aa02-19508bfbe122.png"><br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172163986-ab519830-3860-414d-86e8-39eb6ca82e8d.png"><br>


1. EC2 のインテグレーション
    1. 「Integrations」タブから AWS を選択する<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172161685-7cf61860-8cba-4bba-8699-a1c80d19e926.png"><br>

    1. 「設定」タブから EC2 を選択した上で、「Install Integration」ボタンをクリックする<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172161303-17ddfd6d-a68f-466e-940b-f77d42813bf0.png"><br> 

    1. 作成した EC2 インスタンスに対して、Datadog Agent が通信を行うためのポート `10516` を開放させておく。

    1. Datadog Agent を EC2 インスタンスにインストールする

    1. Datadog　から各種 AWS サービスにアクセスするための IAM を作成する。



## ■ 参考サイト
- https://codezine.jp/article/detail/11650?p=2
- https://support.atlassian.com/ja/opsgenie/docs/integrate-opsgenie-with-datadog/