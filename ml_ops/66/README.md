# GitHub Actions と Terraform を使用して EC2 インスタンスの CI/CD を行う

- 対象レポジトリ
    - https://github.com/Yagami360/terraform-github-actions-aws-cicd-exercises

## ■ 方法

1. EC2 インスタンス用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
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
            方法としては以下の方法がありえるが、今回は４つ目の AWS Systems Manager のパラメーターストアを使用する方法を採用する

            1. 【NG】ローカル環境にある ssh 公開鍵の値をそのまま設定<br>
                ```sh
                # ssh-key 登録
                resource "aws_key_pair" "terraform_key_pair" {
                    key_name   = "id_rsa"
                    public_key = file("/.ssh/id_rsa.pub")  # GitHub Action 実行時の terraform 環境には *.pub ファイルが存在しないのでエラーになる
                }
                ```

                > `public_key = file("/.ssh/id_rsa.pub")` で ssh 公開鍵の値を設定すると、GitHub Action 実行時の terraform 環境には `*.pub` ファイルが存在しないのでエラーになる。
            

            1. 【NG】`terraform.tfvars` に ssh 公開鍵を書き込み<br>
                別途 `terraform.tfvars` ファイル（ファイル名は `terraform.tfvars` である必要があることに注意）に ssh 公開鍵の値を設定した変数を定義し、これを `var.ssh_public_key` の形式で参照するようにする

                ```python
                # terraform.tfvars
                ssh_public_key = "ssh-rsa xxxxx"
                ```

                ```sh
                # 変数定義
                variable ssh_public_key {}

                # ssh-key 登録
                resource "aws_key_pair" "terraform_key_pair" {
                    key_name   = "id_rsa"
                    public_key = var.ssh_public_key     # *.tfvars で定義した値を参照
                }
                ```

                > `terraform.tfvars` を GitHub レポジトリに公開しないと workflow の `terraform` コマンド実行時に `terraform.tfvars` ファイルを参照できなくなるが、公開すると SSH 公開鍵が流出してしまうので NG

            1. secret と `terraform` コマンドの `-var` オプションを使用<br>
                secret に SSH 公開鍵 `SSH_PUBLIC_KEY` を登録した上で、`terraform` コマンドの `-var` オプションを使用して、`terraform plan -var 'ssh_public_key=${{ secrets.SSH_PUBLIC_KEY }}'` などの形式で SSH 公開鍵を指定する。

                ```sh
                # 変数定義
                variable ssh_public_key {}

                # ssh-key 登録
                resource "aws_key_pair" "terraform_key_pair" {
                    key_name   = "id_rsa"
                    public_key = var.ssh_public_key     # secrets の SSH_PUBLIC_KEY で定義した値を参照
                }
                ```                
                > EC2 インスタンスの tf ファイルのみの構成の場合は、これでもいいが、他のリソースの tf ファイルがあるときに、変数 `ssh_public_key` が未定義なので、その tf ファイルに対して `terraform plan -var 'ssh_public_key=${{ secrets.SSH_PUBLIC_KEY }}'` を実行すると、エラーが発生してしまう問題がある

            1. AWS Systems Manager のパラメーターストアを使用する<br>
                [AWS Systems Manager のパラメーターストア](https://us-west-2.console.aws.amazon.com/systems-manager/parameters/?region=us-west-2&tab=Table) に ssh 公開鍵を以下のコマンドで登録し、このパラメーターストアの値を参照するようにする
                ```sh
                aws ssm put-parameter \
                    --name "ssh_public_key" \
                    --value "`cat ${HOME}/.ssh/id_rsa.pub`" \
                    --type String
                ```

                ```sh
                # AWS Systems Manager のパラメーターストア
                data "aws_ssm_parameter" "ssh_public_key" {
                    name            = "ssh_public_key"
                    with_decryption = true
                }

                # ssh-key 登録
                resource "aws_key_pair" "terraform_key_pair" {
                    key_name   = "id_rsa"
                    public_key = data.aws_ssm_parameter.ssh_public_key.value # パラメーターストアの値を参照
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

1. GitHub レポジトリに secrets を登録する。<br>
    github レポジトリの [setting -> secrets -> Actions](https://github.com/Yagami360/terraform-github-actions-aws-cicd-exercises/settings/secrets/actions) から、必要な secrets を登録する。
    ここで設定した secrets の値は、後述の GitHub Actions の Workflow ファイルにて、`secrets.xxx` の形式で参照できるようになる。

    > 一般的に、認証情報や秘密鍵などの秘匿値を Workflow で扱いたいときは、リポジトリの秘匿情報（Settings > Secrets > Actions secrets）で秘匿値を記録し、それを Workflow で参照するようにする

    今回は、`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` の secret を登録しておく

    > `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` の値は、`cat ${HOME}/.aws/credentials` で確認できる

    > 後述の workflow ファイルでは、`secrets.GITHUB_TOKEN` も参照しているが、`GITHUB_TOKEN` 荷関しては、ここで設定する必要はない？

    <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/173190216-1484c5f9-777d-43f4-9be1-555cc468d27c.png">

1. GitHub Actions の Workflow ファイルを作成する<br>
    Workflow ファイル（yaml 形式）をリポジトリ内の `.github/workflows/` ディレクトリ上に作成する

    ```yml
    # ワークフローの名前
    name: terrafform workflow for aws
    #------------------------------------------------------
    # ワークフローをトリガーするイベントを定義
    #------------------------------------------------------
    on:
      # 新しいコードが main ブランチに push された時にトリガー
      push:
        branches:
          - main
        # 変更がトリガーとなるファイル
        paths:
          - '.github/workflows/*'  
          - 'terraform/ec2/*.tf'
          - 'terraform/iam/*.tf'
          - 'terraform/eks/*.tf'
      # main ブランチに PR された時にトリガー
      pull_request:
        branches:
          - main
        paths:
          - '.github/workflows/*'
          - 'terraform/ec2/*.tf'
          - 'terraform/iam/*.tf'
          - 'terraform/eks/*.tf'
    #------------------------------------------------------
    # GitHub レポジトリへの権限設定
    #------------------------------------------------------
    permissions:
      contents: "read"
      id-token: "write"
      issues: "write"
      pull-requests: "write"      # Pull Request へのコメントを可能にする
    #------------------------------------------------------
    # job（ワークフローの中で実行される処理のひとまとまり）を定義
    #------------------------------------------------------
    jobs:
      terraform-aws-job:                    # job ID
        name: terraform job for aws         # job 名
          runs-on: ubuntu-latest              # ジョブを実行するマシン
          #-----------------------------
          # GitHub Actions の build matrix 機能を使用して、同一ジョブを複数ディレクトリに対して並列実行
          # これにより、異なる AWS リソース（ec2, iamなど）の tf ファイルに対しての terraform 処理を並列に実行できるようになる
          #-----------------------------    
          strategy:
          matrix:
            dir:
              - terraform/aws/ec2           # AWS の EC2 インスタンスの tf ファイルを格納
              - terraform/aws/iam           # AWS の IAM の tf ファイルを格納
              - terraform/aws/eks           # AWS の EKS クラスターの tf ファイルを格納
          #-----------------------------
          # 環境変数の設定
          #-----------------------------
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}     # GitHub レポジトリへのアクセストークンを設定し、GitHub レポジトリへのコメントが可能にする / secrets は、github レポジトリの project の setting > secrets から登録する
            AWS_REGION: "us-west-2"
            TERRAFORM_DIR: ${{ matrix.dir }}              # tf ファイルの格納ディレクトリ
          #-----------------------------
          # ジョブの中で実行される一連のタスク
          #-----------------------------
          steps:
            #-----------------------------
            # ブランチを切る
            #-----------------------------
            - uses: actions/checkout@v2       # use タグで Actions（一連の定義済み処理）を指定 / actions/checkout@v2 : actions/v2 という GitHub リポジトリにあるアクションの v2 ブランチのコードを使用し、指定したリポジトリからソースコードを git checkout する
            #-----------------------------
            # tf ファイルの diff があるか確認
            #-----------------------------
            - name: Check diff for .tf files
              id: diff
              uses: technote-space/get-diff-action@v4.0.2
              with:
              PATTERNS: |
                ${{ env.TERRAFORM_DIR }}/*.tf
            #-----------------------------
            # IAM ユーザーの 認証情報を設定
            #-----------------------------
            - name: Configure aws credentials
              if: steps.diff.outputs.diff == 'true'
              uses: aws-actions/configure-aws-credentials@v1            # configure-aws-credentials を使うことで、AWSのアクセスキーをハードコードすることなく権限を入手できる
              with:
                aws-region: ${{ env.AWS_REGION }}        
                aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}           # github レポジトリの [setting -> secrets -> Actions] で設定した AWS_ACCESS_KEY_ID を設定
                aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}   # github レポジトリの [setting -> secrets -> Actions] で設定した AWS_SECRET_ACCESS_KEY を設定
            #-----------------------------
            # terraform のインストール
            #-----------------------------
            - name: install terraform
              if: steps.diff.outputs.diff == 'true'
              uses: hashicorp/setup-terraform@v1
              with:
                terraform_version: 1.0.9
            #-----------------------------
            # terraform init
            #-----------------------------
            - name: terraform init
              if: steps.diff.outputs.diff == 'true'
              run: terraform -chdir="${TERRAFORM_DIR}" init
            #-----------------------------
            # terraform plan
            #-----------------------------
            # terraform plan
            - name: terraform plan
              if: steps.diff.outputs.diff == 'true'
              run: terraform -chdir="${TERRAFORM_DIR}" plan -out workspace.plan
            # PR 時に terraform plan の内容を投稿
            - name: post plan
              if: always() && steps.diff.outputs.diff == 'true' && github.event_name == 'pull_request'
              uses: robburger/terraform-pr-commenter@v1
              with:
                commenter_type: plan
                commenter_input: ${{ format('{0}{1}', steps.plan.outputs.stdout, steps.plan.outputs.stderr) }}
                commenter_exitcode: ${{ steps.plan.outputs.exitcode }}
            #-----------------------------
            # terraform apply
            #-----------------------------
            - name: terraform apply
              if: steps.diff.outputs.diff == 'true' && github.event_name == 'push'
              run: terraform -chdir="${TERRAFORM_DIR}" apply workspace.plan
    ```

    ポイントは、以下の通り

    - ワークフローをトリガーするイベントを定義<br>
        PR -> merge で CI/CD を行えるように、`on.push`, `on.pull_request` タグでのトリガーを定義している

    - GitHub レポジトリへの権限設定<br>
        `permissions` タグで、GitHub レポジトリへの権限設定を行う。今回は PR 経由での CI/CD トリガーを行うので、`pull-requests: "write"` を追加している

    - GitHub Actions の build matrix 機能を使用<br>
        - terraform を使用したリソース管理としては、`tf` ファイルを リソース毎に細かく定義するのがベターな設計であるが、細かく分けすぎると個々の tf ファイルに対して、terraform コマンドを順次直列実行することになり、処理に時間がかかってしまう問題がある。

        - `strategy.matrix` タグを設定することで、GitHub Actions の build matrix 機能を使用して、同一ジョブを複数ディレクトリに対して並列実行する。これにより、異なる AWS リソース（ec2, iamなど）の tf ファイルに対しての terraform 処理を並列に実行できるようになる

    - 環境変数の設定<br>
        - 環境変数 `GITHUB_TOKEN` に、`secrets.GITHUB_TOKEN` を設定する。これにより、GitHub レポジトリへのコメント投稿可能な権限が付与される

    - tf ファイルの diff があるか確認<br>
        - action `technote-space/get-diff-action@v4.0.2` を use して、tf ファイルの差分があったかを確認する。

        - tf ファイルの差分があったかは、`if: steps.diff.outputs.diff` で確認可能なので、公団の処理は、tf ファイルの差分があるときのみ実行するようにする

    - AWS の IAM ユーザーの認証情報を設定<br>
        - 各種 terraform コマンド実行前に、IAM ユーザーの認証情報を設定する必要がある。具体的には、環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` に、IAM ユーザーの適切な認証情報の値を設定することで、terraform に対して AWS の認証情報を設定する必要がある<br>

            > IAM ユーザーの認証情報を設定していないと、後述の `terraform plan` or `terraform apply` コマンド使用時、`Error: error configuring Terraform AWS Provider: no valid credential sources for Terraform AWS Provider found.` のようなエラーメッセージがでて、`.tf` ファイルに記述した AWS リソースを認証できなくなる

        - 環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` の値は、github レポジトリの [setting -> secrets -> Actions](https://github.com/Yagami360/terraform-github-actions-aws-cicd-exercises/settings/secrets/actions) で設定した `secrets.AWS_ACCESS_KEY_ID`, `secrets.AWS_ACCESS_KEY_ID` を設定する

        - action（定義済み処理）`aws-actions/configure-aws-credentials@v1` を使うことで、AWSのアクセスキーをハードコードすることなく、IAM ユーザーの認証情報を設定できる

    - terraform のインストール<br>
        - `if: steps.diff.outputs.diff` を設定することで、step id `diff` の step 実行時結果が true で tf ファイルの差分がある時だけ、インストール処理を実行するようにしている。
        
    - terraform init<br>
        - `if: steps.diff.outputs.diff` を設定することで、step id `diff` の step 実行時結果が true で tf ファイルの差分がある時だけ、インストール処理を実行するようにしている。

    - terraform plan<br>
        - xxx

    - terraform apply<br>
        - xxx

1. EC2 インスタンスの CI/CD を行う<br>

    - git push で行う場合<br>
        Workflow ファイルで定義したトリガーイベントが `main` ブランチへの git push であれば、Workflow ファイルか tf ファイルをレポジトリの `main` ブランチに git push した時点で、ワークフローが自動的に実行され EC2 インスタンスへの CI/CD が行われる。
        ```sh
        git add .
        git commit -m "cicd for ec2"
        git push origin main
        ```

    - PR -> merge で行う場合<br>
        Workflow ファイルで定義したトリガーイベントが、pull_request (PR) であれば、Workflow ファイルか tf ファイルを修正後、[GitHub レポジトリ上で PR](https://github.com/Yagami360/terraform-github-actions-aws-cicd-exercises/pulls) を出して、main ブランチに merge した時点で、ワークフローが自動的に実行され EC2 インスタンスへの CI/CD が行われる。

        > 一般的に CI/CD を行うトリガーは、main ブランチへの `git push` ではなく、こちらの PR を出して main ブランチへの merge が行われるタイミングにすることが推奨されている

1. GitHub リポジトリの Actions タブから、実行されたワークフローのログを確認する

1. ワークフローステータスのバッジ（badge）を表示したい場合は、各ワークフローの「Create status badge」ボタンをクリックして画像リンクを取得して、`README.md` などに貼り付ける。

1. xxx

## ■ 参考サイト

- https://kiririmode.hatenablog.jp/entry/20211219/1639901955
- https://zenn.dev/rinchsan/articles/de981e561eb36ebfab70