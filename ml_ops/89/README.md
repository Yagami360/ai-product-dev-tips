# 【AWS】 ALB [Application Load Balancer] を使用して複数の EC2 インスタンスに対しての HTTP 接続の L7 ロードバランシングを行う（AWS CLI 使用）

ALB は、AWS における L7 ロードバランサーで、以下のような特徴がある。

- L7 ロードバランサーなので、アプリケーションレイヤーで動作する

- WebSocket と HTTP/2 という2つの通信プロトコルをサポートしている

- xxx

> - CLB [Classic Load Balancer] / ELB [Elastic Load Balancer] との違い<br>
>    CLB/ELB は、L4ロードバランサーとL7ロードバランサー両方で機能するロードバランサーであるが、ALB は L7 ロードバランサーのみで機能するロードバランサーになっておいる。ALB アプリケーション層で特化することにより、アプリケーション側からより便利で使いやすい機能の実装や追加が行われている


## ■ ToDo

- [ ] ２つの EC2 インスタンス上それぞれに Web-API を構築して、その ２つの Web-API に対してロードバランシングを行うようにする

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

1. EC2 インスタンスの作成<br>
    1. VPC を作成する<br>
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

    1. サブネットを作成する<br>
        VPC 内に複数のサブネットを作成する
        ```sh
        #-----------------------------
        # サブネット１を作成する
        #-----------------------------
        # サブネットマスクを作成
        aws ec2 create-subnet \
            --vpc-id ${VPC_ID} \
            --cidr-block ${EC2_SUBNET_CIDR_BLOCK_1} \
            --availability-zone ${ZONE_1} > log/${EC2_SUBNET_NAME_1}.json

        # サブネット ID を取得
        EC2_SUBNET_ID_1=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK_1}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
        echo "created ec2 subnet id=${EC2_SUBNET_ID_1}"

        # サブネットに名前をつける
        aws ec2 create-tags --resources ${EC2_SUBNET_ID_1} --tags Key=Name,Value=${EC2_SUBNET_NAME_1}

        #-----------------------------
        # サブネット２を作成する
        #-----------------------------
        # サブネットマスクを作成
        aws ec2 create-subnet \
            --vpc-id ${VPC_ID} \
            --cidr-block ${EC2_SUBNET_CIDR_BLOCK_2} \
            --availability-zone ${ZONE_2} > log/${EC2_SUBNET_NAME_2}.json

        # サブネット ID を取得
        EC2_SUBNET_ID_2=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK_2}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
        echo "created ec2 subnet id=${EC2_SUBNET_ID_2}"

        # サブネットに名前をつける
        aws ec2 create-tags --resources ${EC2_SUBNET_ID_2} --tags Key=Name,Value=${EC2_SUBNET_NAME_2}
        ```

    1. EC2 インスタンス用のセキュリティーグループを作成する<br>
        ```sh
        # セキュリティグループ作成
        EC2_SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${EC2_SECURITY_GROUP_NAME} --description "security group for efs" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
        echo "created security-group id=${EC2_SECURITY_GROUP_ID}"

        # セキュリティグループのインバウンドルールを設定（SSH接続）
        aws ec2 authorize-security-group-ingress \
            --group-id ${EC2_SECURITY_GROUP_ID} \
            --protocol tcp \
            --port 22 \
            --cidr 0.0.0.0/0

        # セキュリティグループのインバウンドルールを設定（HTTP接続）
        aws ec2 authorize-security-group-ingress \
            --group-id ${EC2_SECURITY_GROUP_ID} \
            --protocol tcp \
            --port 80 \
            --cidr 0.0.0.0/0

        #　セキュリティーグループに名前をつける
        aws ec2 create-tags --resources ${EC2_SECURITY_GROUP_ID} --tags Key=Name,Value=${EC2_SECURITY_GROUP_NAME}
        ```

        > ALB で HTTP で EC2 インスタンスに接続するので、HTTP 接続用（ポート番号 `80`）ののインバウンドルールを作成している

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

    1. 複数の EC2 インスタンスを作成する<br>
        ```sh
        #-----------------------------
        # EC2 インスタンス１の作成
        #-----------------------------
        # サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
        aws ec2 modify-subnet-attribute \
            --subnet-id ${EC2_SUBNET_ID_1} \
            --map-public-ip-on-launch

        # EC2 インスタンスの作成
        aws ec2 run-instances \
            --image-id ${EC2_IMAGE_ID_1} \
            --instance-type ${EC2_INSTANCE_TYPE_1} \
            --count 1 \
            --key-name ${EC2_SSH_KEY_NAME} \
            --security-group-ids ${EC2_SECURITY_GROUP_ID} \
            --subnet-id ${EC2_SUBNET_ID_1} > logs/${EC2_INSTANCE_NAME_1}.json

        # インスタンスIDを取得
        EC2_INSTANCE_ID_1=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID_1}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
        echo "created ec2-instance id=${EC2_INSTANCE_ID_1}"

        # インスタンスの名前を設定
        aws ec2 create-tags --resources ${EC2_INSTANCE_ID_1} --tags Key=Name,Value=${EC2_INSTANCE_NAME_1}

        #-----------------------------
        # EC2 インスタンス２の作成
        #-----------------------------
        # サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
        #aws ec2 modify-subnet-attribute \
        #	--subnet-id ${EC2_SUBNET_ID_2} \
        #	--map-public-ip-on-launch

        # EC2 インスタンスの作成
        aws ec2 run-instances \
            --image-id ${EC2_IMAGE_ID_2} \
            --instance-type ${EC2_INSTANCE_TYPE_2} \
            --count 1 \
            --key-name ${EC2_SSH_KEY_NAME} \
            --security-group-ids ${EC2_SECURITY_GROUP_ID} \
            --subnet-id ${EC2_SUBNET_ID_2} > logs/${EC2_INSTANCE_NAME_2}.json

        # インスタンスIDを取得
        EC2_INSTANCE_ID_2=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID_2}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
        echo "created ec2-instance id=${EC2_INSTANCE_ID_2}"

        # インスタンスの名前を設定
        aws ec2 create-tags --resources ${EC2_INSTANCE_ID_2} --tags Key=Name,Value=${EC2_INSTANCE_NAME_2}
        ```

1. ALB [Application Load Balancer] の作成<br>
    1. ALB を作成する<br>
        ```sh
        aws elbv2 create-load-balancer \
            --name ${ALB_NAME} \
            --subnets ${EC2_SUBNET_ID_1} ${EC2_SUBNET_ID_2} \
            --security-groups ${EC2_SECURITY_GROUP_ID}

        ALB_ARN=$( aws elbv2 describe-load-balancers --query LoadBalancers[0].LoadBalancerArn --output text )
        ```

        > ALB 作成の CLI コマンドは、`aws elbv2` のように ELB のような名前になっていることに注意

        > 作成した ALB は、「[AWS のロードバランサーのコンソール画面](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#LoadBalancers:sort=loadBalancerName)」から確認できる

    1. ターゲットグループを作成する<br>
        ALB から HTTP (tcp/80) でアクセスを受ける（EC2 インスタンスの）ターゲットグループを作成する
        ```sh
        aws elbv2 create-target-group \
            --name ${ALB_TARGET_GROUP_NAME} \
            --protocol HTTP --port 80 \
            --vpc-id ${VPC_ID}

        ALB_TARGET_GROUP_ARN=$( aws elbv2 describe-target-groups --query TargetGroups[0].TargetGroupArn --output text )
        ```
        - `--port` : ALB が使用するEC2インスタンスのポート番号。HTTP 接続の場合は `80`
        
            > セキュリティーグループのインバウンドルールに HTTP `80` のインバウンドルールを追加している必要があることに注意

        > 作成したターゲットグループは、「[AWS のターゲットグループのコンソール画面](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#TargetGroups:)」から確認できる

    1. ターゲットグループに EC2 インスタンスを登録する
        ```sh
        aws elbv2 register-targets \
            --target-group-arn ${ALB_TARGET_GROUP_ARN} \
            --targets Id=${EC2_INSTANCE_ID_1},Port=80 Id=${EC2_INSTANCE_ID_2},Port=80
        ```

    1. HTTP リスナー（ALBとターゲットグループの紐付け）を作成する<br>
        ALB とターゲットグループの紐付けを行う
        ```sh
        aws elbv2 create-listener \
            --load-balancer-arn ${ALB_ARN} \
            --protocol HTTP --port 80 \
            --default-actions Type=forward,TargetGroupArn=${ALB_TARGET_GROUP_ARN}
        ```

    1. 【オプション】ターゲットグループに登録されている EC2 インスタンスの状態が healthy になっていることを確認する<br>
        - コンソール画面を使用する場合<br>
            ここまでの設定が正常に完了している場合は、「[AWS のターゲットグループのコンソール画面](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#TargetGroups:)」から確認できる作成したターゲットグループに登録されている EC2 インスタンスの「Health Status」が healthy になっている

        - CLI の場合<br>
            ```sh
            aws elbv2 describe-target-health --target-group-arn ${ALB_TARGET_GROUP_ARN}
            ```

1. HTTP アクセスでロードバランシングされていることを確認する<br>
    xxx

## ■ 参考サイト

- https://docs.aws.amazon.com/ja_jp/elasticloadbalancing/latest/application/tutorial-application-load-balancer-cli.html
- https://qiita.com/zakky/items/fc9c9da174aafd9f87ff
- https://recipe.kc-cloud.jp/archives/9942