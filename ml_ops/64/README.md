# Opsgenie を使用して EC2 インスタンスに導入している Datadog で検知したアラートを管理・通知する

Opsgenie は、監視対象サーバーに導入している Datadog, Cloud Logging (StackDriver) などから検知したアラートを集約し、発生したアラートに対して誰が、いつ、どういった対応をしたのかを管理し、Slack などのツールに通知することが可能なツールである。

Opsgenie を利用することで、サーバーで発生したアラートを見逃すことなくサーバーやプロダクトを運用できるようになるメリットがある

<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/171974763-f81971b7-2d3a-478f-a191-0c7705bf007c.png">

ここでは、Opsgenie を使用して EC2 インスタンスに導入している Datadog で検知したアラートを管理・通知する方法を記載する

## ■ 方法

1. Opsgenie 設定<br>
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

1. EC2インスタンスの作成<br>
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

        > VPC [Virtual Private Cloud] : AWS専用の仮想ネットワーク。インターネットを利用する際、ルーターやゲートウェイなどのネットワーク機器が必要となるが、VPCはそれらの機器を仮想的に用意し、ネットワーク環境を構築できるようにしている。

        > CIDR 表記 : `198.51.100.xxx/24` のような形で、IPアドレスの後ろに `/` と２進数のサブネットマスクにおける１の個数を書く表記方法。<br>
        > 例えば、/16 => 11111111.11111111.00000000.00000000 => 255.255.0.0 のサブネットマスクとなり、<br>
        > /24 => 11111111.11111111.11111111.00000000 => 255.255.255.0 のサブネットマスクとなる。<br>

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

        > サブネット : １つの大きなネットワークを管理しやすくするために、より小さなネットワークに分割したときのサブネットワークのこと。<br>
        
        > `aws ec2 create-vpc` の `--cidr_block` で指定する VPC の IP アドレスと `aws ec2 create-subnet` の `--cidr_block` で指定するサブネットの IP アドレスは、サブネット部のみ変更された値となり、サブネットマスクは /24 = 255.255.255.0 のサブネット部のマスク値になる

        > <img src="https://user-images.githubusercontent.com/25688193/114671501-21c52200-9d3f-11eb-8d31-e22711f96c4b.png" width="300"><br>


    1. インターネットゲートウェイを作成する<br>
        ```sh
        # インターネットゲートウェイの作成
        aws ec2 create-internet-gateway

        # インターネットゲートウェイID取得
        INTERNET_GATEWAY_ID=`aws ec2 describe-internet-gateways --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query InternetGateways[*].InternetGatewayId | grep igw- | sed 's/ //g' | sed 's/"//g'`
        
        # 作成したインターネットゲートウェイに VPC をアタッチする
        aws ec2 attach-internet-gateway 
            --internet-gateway-id ${INTERNET_GATEWAY_ID} \
            --vpc-id ${VPC_ID}
        ```

        > インターネットゲートウェイ : コンピュータネットワークにおいて、通信プロトコルが異なるネットワーク同士がデータをやり取りする際、中継する役割を担うルータのような機能を備えた機器やそれに関するソフトウェア

    1. xxx

1. Datadog の設定<br>


## ■ 参考サイト
- https://codezine.jp/article/detail/11650?p=2