# Terraform を利用して AWS インスタンスを自動的に構築する

## ■ 手順

1. AWS CLI をインストールする<br>
    - MacOS の場合<br>
        ```sh
        $ brew install awscli

        # インストール確認
        $ which aws
        $ aws --version
        ```
    - Linux の場合<br>
        ```sh
        # pip インストール
        # ※ --user で、pipのスクリプトを ~/.local/bin にインストール
        $ curl -O https://bootstrap.pypa.io/get-pip.py
        $ python get-pip.py --user 
        $ echo export PATH='~/.local/bin:$PATH' >> ~/.bash_profile
        $ source ~/.bash_profile
        $ pip --version

        # aws-cliインストール
        # ※ --user で、pipのスクリプトを ~/.local/bin にインストール
        $ pip install awscli --upgrade --user

        $ which aws
        $ aws --version
        ```

1. `aws configure` コマンドで認証情報を設定する。<br>
    ```sh
    $ aws configure
    ```
    ```sh
    # プロファイル名を別に設定する場合
    $ aws configure --profile ${プロファイル名}
    ```
    - AWS Access Key ID : [AWS の IAM](https://console.aws.amazon.com/iam/home?#/security_credentials) ページの「セキュリティ認証情報」→「アクセスキー (アクセスキー ID とシークレットアクセスキー)」から取得した "アクセスキーID"
    - AWS Secret Access Key : [AWS の IAM](https://console.aws.amazon.com/iam/home?#/security_credentials) ページの「セキュリティ認証情報」→「アクセスキー (アクセスキー ID とシークレットアクセスキー)」から取得した "シークレットアクセスキー"
    - Default region name : EC2インスタンスのリージョン（us-west-2 など）
    - Default output format : "text","json","table" のどれかを指定

    > 上記コマンドで作成された認証情報は、`${HOME}/.aws/credentials` ファイル内に保管される。

    > AWS の認証情報を設定していないと、後述の `terraform plan` or `terraform apply` コマンド使用時、`Error: error configuring Terraform AWS Provider: no valid credential sources for Terraform AWS Provider found.` のようなエラーメッセージがでて、`.tf` ファイルに記述した AWS リソースを認証できなくなる

1. IAM ユーザーを追加する<br>
    GUI を 用いて作成する場合は、「[IAM ダッシュボード](https://console.aws.amazon.com/iam/home?#/home)」のページから作成できる。<br>
    CLI を用いて作成する場合は、xxx

1. 設定した認証情報と IAM ユーザーを確認する<br>
    - 現在のプロファイルを確認<br>
        ```sh
        $ aws configure list
        ```
    - IAM ユーザーを確認<br>
        ```sh
        $ aws iam list-users
        ```
    - IAM グループを確認<br>
        ```sh
        $ aws iam list-groups
        ```

1. Terraform をインストールする<br>
    - MacOS の場合<br>
        ```sh
        $ brew install terraform
        ```

1. Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
    Terraform のテンプレートファイルは、１つのテンプレートファイルに全ての定義を記述してもよいし、異なるリソースを別々のテンプレートファイルに記載してもよい。<br>

    1. ssh 接続を考慮しない場合（最も簡単な例）<br>
        ここでは最も単純な例として、以下のような構成のテンプレートファイルを作成する。但しこの設定では、ssh 接続は行えないことに注意

        - プロバイダーの設定<br>
            プロバイダーの設定は、`provider` ブロックで行う。AWS を使う場合は `provider` ブロックで `"aws"` を指定する。<br>
            ```python
            provider "aws" {
                profile = "Yagami360"
                region = "us-west-2"
            }
            ```
            > デフォルトのプロファイルを使用する場合は `profile = "default"` を設定

            `aws configure` で AWS 認証情報を設定していない場合は、以下のような内容で、アクセスキー・シークレットキー・リージョンを指定する。（※但しこの方法作成したテンプレートファイルを GitHub などで公開する際には、情報漏えいに注意すること。）
            ```python
            provider "aws" {
                access_key = "ACCESS_KEY_HERE"
                secret_key = "SECRET_KEY_HERE"
                region = "us-west-2"
            }
            ```

        - EC2 リソースの設定<br>
            リソースの設定は、`resource` ブロックで `resource "<リースの種類>" "<リソース名>" {}` の構文で行う。<br>
            ソースの種類は、プロバイダーが AWS の場合は `"aws_*"` という名前で Terraform 側で予め定義されており、EC2 であれば `"aws_instance"` になる。

            例えば、Ubuntu 16.04 LST をベースイメージにした t2.micro のインスタンスを２台（名前 "terraform-0" と "terraform-1" ）作成する場合は、以下のようになる<br>
            ```python
            resource "aws_instance" "terraform_instance" {
                count         = 2
                ami           = "ami-008b09448b998a562" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
                instance_type = "t2.micro"

                tags = {
                    Name = "${format("terraform_instance-%02d", count.index + 1)}"
                }
            }
            ```

    1. ssh 接続を考慮する場合<br>
        ssh 接続可能な EC2 インスタンスを構築するためには、上記 EC2リソースの設定以外に、 ｛VPC・ゲートウェイ・ルーティングテーブル・セキュリティグループ・固定IP（使用する場合）・SSH鍵登録｝の設定が必要になる。

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

        - VPC リソースの設定<br>
            VPC リソースは、`resource` ブロックのリソース名 `"aws_vpc"` で設定可能。
            EC インスタンスは、この VPC に直接後述のサブネット内に
            ```python
            resource "aws_vpc" "terraform_vpc" {
                cidr_block = "10.0.0.0/16"      # IP アドレスは CIDR 表記で記載
                enable_dns_hostnames = true
                enable_dns_support = true
                tags = {
                    Name = "terraform_vpc"
                }
            }
            ```

        - サブネットの設定<br>
            VPC ネットワークの中にサブネットワークを構成し、そのサブネット内で EC2 インスタンスを起動するように設定する。（サブネットのEC2インスタンスの関連付けは `"aws_instance"` 内で行う）<br>
            AWS のサブネットは `resource` ブロックのリソース名 `"aws_subnet"` で設定可能。

            > `<リソースタイプ>.<リソース名>.<属性名>` で同じテンプレートファイル内の他リソースの属性を参照することができる。

            ```python
            resource "aws_subnet" "terraform_subnet" {
                vpc_id = "${aws_vpc.terraform_vpc.id}"
                cidr_block = "10.0.1.0/24"          # VPC リソースの IP アドレスのサブネット部（x.x.サブネット部.ホスト番号）のみ変更
                availability_zone = "us-west-2a"
            }
            ```
            
            > "aws_vpc" の `cidr_block` で指定する VPC の IP アドレスと "aws_subnet" の `cidr_block` で指定するサブネットの IP アドレスは、サブネット部のみ変更された値となり、サブネットマスクは /24 = 255.255.255.0 のサブネット部のマスク値になる

            > <img src="https://user-images.githubusercontent.com/25688193/114671501-21c52200-9d3f-11eb-8d31-e22711f96c4b.png" width="300"><br>

        - インターネットゲートウェイの設定<br>
            インターネット ↔ VPC 間のゲートウェイを設定する。<br>
            AWS におけるゲートウェイは、`resource` ブロックのリソース名 `"aws_internet_gateway"` で設定可能。
            ```python
            resource "aws_internet_gateway" "terraform_gateway" {
                vpc_id = "${aws_vpc.terraform_vpc.id}"
            }
            ```

        - ルーティングテーブルの設定<br>
            VPC からゲートウェイまでのルーティングテーブルを設定する。<br>
            AWS でのルーティングテーブルは、`resource` ブロックのリソース名 `"aws_route_table"` で設定可能。

            ```python
            resource "aws_route_table" "terraform_route_table" {
                vpc_id = "${aws_vpc.terraform_vpc.id}"
                route {
                    cidr_block = "0.0.0.0/0"    # インターネット(0.0.0.0/0)
                    gateway_id = "${aws_internet_gateway.terraform_gateway.id}"
                }
            }
            ```

            設定したルーティングテーブルは、サブネットと関連づける必要がある。<br>
            ルーティングテーブルのサブネットへの関連付けは、`resource` ブロックのリソース名 `"aws_route_table_association"` で設定可能。
            ```python
            resource "aws_route_table_association" "terraform_route_table_association" {
                subnet_id = "${aws_subnet.terraform_subnet.id}"
                route_table_id = "${aws_route_table.terraform_route_table.id}"
            }
            ```

        - セキュリティーグループの設定<br>
            AWS でのセキュリティーグループは、`"aws_security_group"` ブロックで設定可能。
            ```python
            resource "aws_security_group" "terraform_security_group" {
                name = "terraform_security_group"
                description = "Used in the terraform"
                vpc_id = "${aws_vpc.terraform_vpc.id}"
                ingress {           # インバウンドルール(ssh接続用)
                    from_port = 22
                    to_port = 22
                    protocol = "tcp"
                    cidr_blocks = ["0.0.0.0/0"]
                }
                ingress {           # インバウンドルール(ping用)
                    from_port = -1
                    to_port = -1
                    protocol = "icmp"
                    cidr_blocks = ["0.0.0.0/0"]
                }
                egress {            # アウトバウンドルール(全開放)
                    from_port = 0
                    to_port = 0
                    protocol = "-1"
                    cidr_blocks = ["0.0.0.0/0"]
                }
            }
            ```

        - 固定 IP アドレスの設定<br>
            固定 IP アドレスを使用したい場合は、"aws_eip" ブロックで固定IPアドレスを設定可能。
            ```python
            resource "aws_eip" "terraform_eip" {
                instance = "${aws_instance.terraform_instance.id}"
                vpc = true
            }
            ```

        - SSH 鍵の設定<br>
            接続元マシンの ssh 公開鍵のパスを設定する。<br>
            ```python
            resource "aws_key_pair" "terraform_key_pair" {
                key_name   = "id_rsa"
                public_key = file("/Users/sakai/.ssh/id_rsa.pub")
            }
            ```

        - EC2 インスタンスの設定<br>
            上記設定したサブネットやセキュリティーグループと関連付けを行った EC2 インスタンスを設定する。<br>
            例えば、Ubuntu 16.04 LST をベースイメージにした t2.micro のインスタンスを２台（名前 "terraform-0" と "terraform-1" ）作成する場合は、以下のようになる<br>
            ```python
            resource "aws_instance" "terraform_instance" {
                count         = 2
                ami           = "ami-008b09448b998a562" # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
                instance_type = "t2.micro"
                vpc_security_group_ids = ["${aws_security_group.terraform_security_group.id}"]
                subnet_id = "${aws_subnet.terraform_subnet.id}"
                associate_public_ip_address = "true"
                key_name      = aws_key_pair.terraform_key_pair.id
                tags = {
                    Name = "${format("terraform_instance-%02d", count.index + 1)}"
                }
            }
            ```

1. terraform を初期化する。
    ```sh
    $ terraform init
    ```
    > `terraform` コマンドは、`.terraform` ディレクトリ作成後有効になる

1. 作成したテンプレートファイルの定義内容を確認する
    ```sh
    $ terraform plan
    ```

    このコマンドを実行することで、以下のように、定義内容をもとに実行されるプランの内容が出力される
    ```sh
    Terraform will perform the following actions:

    # aws_instance.terraform[0] will be created
    + resource "aws_instance" "terraform" {
        + ami                          = "ami-008b09448b998a562"
        ...
        + instance_type                = "t2.micro"
        ...
        + tags                         = {
            + "Name" = "terraform-01"
            }
        ...
        }

    # aws_instance.terraform[1] will be created
    + resource "aws_instance" "terraform" {
        + ami                          = "ami-008b09448b998a562"
        ...
        + instance_type                = "t2.micro"
        + tags                         = {
            + "Name" = "terraform-02"
            }
        ...
        }

    Plan: 2 to add, 0 to change, 0 to destroy.
    ```

1. 定義を適用してインスタンスを作成する
    ```sh
    $ terraform apply
    ```

    以下の画面が出力されるので `yes` を入力する
    ```
    Terraform will perform the actions described above.
    Only 'yes' will be accepted to approve.

    Enter a value: yes
    ```

    > `terraform apply` を実行すると、tf ファイルに基づいて、各種インフラが作成されるが、そのインフラ情報が、以下のような `*.tfstate` ファイル（json形式）に自動的に保存され（場所は、tf ファイルと同じディレクトリ内）、次回の `terraform apply` 実行時等で前回のインフラ状態との差分をみる際に利用される。（tfstate ファイルの直接編集は非推奨）

    > ```json
    > {
    >   "version": 4,
    >   "terraform_version": "0.14.4",
    >   "serial": 99,
    >   "lineage": "b3db0982-ad72-b91e-cc7a-d58ff80308c7",
    >   "outputs": {},
    >   "resources": []
    > }
    
    > そのため、tfstate ファイルをローカルに置いたままでは複数人で terraform を実行できなくなってしまう。この問題を解決するためには、tfstate ファイルを GCS or Amazon S3 などのクラウドデータレイク上に保管する方法もあるが、今回のケースではローカルに保存する

1. terraform が作成したオブジェクトの内容を確認
    ```sh
    $ terraform show
    ```

1. [EC2 コンソール](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#Instances:) や [VPC コンソール](https://us-west-2.console.aws.amazon.com/vpc/home?region=us-west-2#vpcs:) をブラウザで開き、正しいインスタンスや VPC などが作成されていることを確認する。
    - MacOS の場合
        ```sh
        open https://${AWS_REGION}.console.aws.amazon.com/ec2/v2/home?region=${AWS_REGION}#Instances:
        open https://${AWS_REGION}.console.aws.amazon.com/vpc/home?region=${AWS_REGION}#vpcs:
        ```

1. 作成したインスタンスに ssh 接続する
    ```sh
    $ ssh ubuntu@${IP_ADRESS}
    ```

    terraform で作成したインスタンスの IP アドレスは、以下のコマンドで確認可能
    ```sh
    $ terraform show | grep public_ip
    ```

1. terraform で定義したリソースを全て削除する<br>
    terraform で作成した全リソース（今の場合は EC2インスタンス）を削除したい場合は、以下のコマンドを実行
    ```sh
    $ terraform destroy
    ```

## ■ 参考サイト
- https://qiita.com/Chanmoro/items/55bf0da3aaf37dc26f73
- https://dev.classmethod.jp/articles/terraform-getting-started-with-aws/
- https://qiita.com/takumiabe/items/07943f23436aa983f397#%E6%93%8D%E4%BD%9C%E7%94%A8aws%E3%82%A2%E3%82%AB%E3%82%A6%E3%83%B3%E3%83%88%E3%81%AE%E8%AA%8D%E8%A8%BC%E6%83%85%E5%A0%B1%E3%81%AE%E6%89%B1%E3%81%84
- http://togattti.hateblo.jp/entry/2019/02/26/223925
- https://qiita.com/kou_pg_0131/items/45cdde3d27bd75f1bfd5