# 【AWS】 Amazon EFS を使用して EC2 インスタンスに共有ストレージ（NAS）を追加する（AWS CLI 使用）

Amazon EFS [Elastic File System] は、フルマネージド型の NAS [Network Attached Storage] / NFS [Network File System] のサービスになっており、以下のような特徴を持つ

- xxx


> - NFS [Network File System]<br>
>    ネットワーク上の Unix マシンがストレージを共有するためのプロトコル。ネットワークを介してサーバ上のストレージ領域をローカルストレージと同様にマウントして使える
> 
> - NAS [Network Attached Storage]<br>
>    ネットワーク上の Unix マシンがストレージを共有するためのファイルシステムの名称。
>    NAS で使われるファイル共有のためのプロトコルが、NFS になる
>
> <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/179341043-398d3bb3-15b2-44a4-8414-4f62b6b57afc.png">

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

        > Amazon EFS で利用する際には、DNS ホスト名を有効にする必要があるので、`aws ec2 modify-vpc-attribute` コマンドで DNS ホスト名を有効化している

    1. サブネットを作成する<br>
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

        #　セキュリティーグループに名前をつける
        aws ec2 create-tags --resources ${EC2_SECURITY_GROUP_ID} --tags Key=Name,Value=${EC2_SECURITY_GROUP_NAME}
        ```

    1. EC2 インスタンスの作成
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
            --security-group-ids ${EC2_SECURITY_GROUP_ID} \
            --subnet-id ${EC2_SUBNET_ID}

        # インスタンスIDを取得
        EC2_INSTANCE_ID=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
        echo "created ec2-instance id=${EC2_INSTANCE_ID}"

        # インスタンスの名前を設定
        aws ec2 create-tags --resources ${EC2_INSTANCE_ID} --tags Key=Name,Value=${EC2_INSTANCE_NAME}
        ```

1. Amazon EFS リソース作成<br>
    1. Amazon EFS 用のセキュリティーグループを作成する<br>
        ```sh
        # セキュリティグループ作成
        EFS_SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${EFS_SECURITY_GROUP_NAME} --description "security group for efs" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
        echo "created security-group id=${EFS_SECURITY_GROUP_ID}"

        # セキュリティグループのインバウンドルールを設定（SSH接続）
        aws ec2 authorize-security-group-ingress \
            --group-id ${EFS_SECURITY_GROUP_ID} \
            --protocol tcp \
            --port 2049 \
            --cidr 0.0.0.0/0

        #　セキュリティーグループに名前をつける
        aws ec2 create-tags --resources ${EFS_SECURITY_GROUP_ID} --tags Key=Name,Value=${EFS_SECURITY_GROUP_NAME}
        ```

    1. EFS ファイルシステムを作成する
        ```sh
        EFS_FILE_SYSTEM_ID=$( aws efs create-file-system --creation-token TestFileSystem --tags Key=Name,Value="Test File System" | jq -r '.FileSystemId' )
        echo "created efs file system id=${EFS_FILE_SYSTEM_ID}"
        ```

        > 作成したファイルシステムは、「[[Amazon EFS] -> [ファイルシステム] のコンソール画面](https://us-east-1.console.aws.amazon.com/efs/home?region=us-east-1#/file-systems)」から確認できる

    1. 【オプション】ライフサイクル管理の有効化<br>
        ```sh
        aws efs put-lifecycle-configuration --file-system-id ${EFS_FILE_SYSTEM_ID} --lifecycle-policies TransitionToIA=AFTER_30_DAYS
        ```

        > ライフサイクル管理 : 有効にすると、ライフサイクル管理により、ファイルシステムに応じて、設定された期間アクセスされなかったファイルは、EFS スタンダード-低頻度アクセス（標準-IA）または 1 ゾーン-低頻度アクセス（1 ゾーン-IA）ストレージクラスに移行されます。

    1. マウントターゲットを作成する<br>
        ```sh
        aws efs create-mount-target --file-system-id ${EFS_FILE_SYSTEM_ID} --subnet-id ${EC2_SUBNET_ID} --security-group ${EFS_SECURITY_GROUP_ID}
        ```

1. EC2 インスタンスに共有ディスク（NAS）をマウントする<br>
    1. EC2 インスタンスに接続する<br>
        ```sh
        IP_ADDRESS=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].PublicIpAddress --output text )
        echo "ec2-instance ip=${IP_ADDRESS}"
        ssh -i "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem" ubuntu@${IP_ADDRESS}
        ```

    1. EFS クライアントをインストールする<br>
        - Amzon Linux の場合
            ```sh
            sudo yum install -y amazon-efs-utils
            ```

        - Ubuntu の場合
            ```sh
            sudo apt update
            sudo apt upgrade

            # 必要なパッケージをインストール
            sudo apt install -y stunnel4
            sudo apt install -y binutils

            # ソースコードを GitHub から取得
            git clone https://github.com/aws/efs-utils
            cd efs-utils

            # DEV パッケージをビルド&インストール
            ./build-deb.sh
            sudo apt-get install -y ./build/amazon-efs-utils*deb
            ```

    1. EC2 インスタンスへファイルシステムをマウントする<br>
        ```sh
        mkdir -p ~/efs-mnt
        sudo mount -t efs -o tls ${EFS_FILE_SYSTEM_ID}:/ ~/efs-mnt
        ```

    1. マウントしたディレクトリを確認する<br>
        ```sh
        df -h
        ```
        ```sh
        ubuntu@ip-10-0-1-230:~/efs-mnt$ df -h
        Filesystem      Size  Used Avail Use% Mounted on
        udev            488M     0  488M   0% /dev
        tmpfs           100M  3.4M   96M   4% /run
        /dev/xvda1      7.7G  1.5G  6.3G  20% /
        tmpfs           496M     0  496M   0% /dev/shm
        tmpfs           5.0M     0  5.0M   0% /run/lock
        tmpfs           496M     0  496M   0% /sys/fs/cgroup
        /dev/loop0       98M   98M     0 100% /snap/core/10126
        /dev/loop1       29M   29M     0 100% /snap/amazon-ssm-agent/2012
        tmpfs           100M     0  100M   0% /run/user/1000
        127.0.0.1:/     8.0E     0  8.0E   0% /home/ubuntu/efs-mnt
        ```

        > `/home/ubuntu/efs-mnt` に共有ディスク（NAS）がマウントされている

## ■ 参考サイト

- https://dev.classmethod.jp/articles/lim-efs-hands-on/
- https://qiita.com/leomaro7/items/32c8cc73cf11f41df078
