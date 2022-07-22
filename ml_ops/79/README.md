# CircleCI と Terraform を使用して EC2 インスタンスの CI/CD を行う

- 対象レポジトリ
    - https://github.com/Yagami360/terraform-circleci-aws-cicd-exercises
    
## ■ 方法

1. 【初回のみ】CircleCI のユーザー登録を行う<br>
    「[CircleCI の Web ページ](https://circleci.com/ja/signup/)」から、ユーザー登録を行う

1. 【初回のみ】AWS Systems Manager のパラメーターストアに ssh 公開鍵を登録する<br>
    ```sh
    aws ssm get-parameter --name "ssh_public_key" &> /dev/null
    if [ $? -ne 0 ] ; then
    aws ssm put-parameter \
        --name "ssh_public_key" \
        --value "`cat ${HOME}/.ssh/id_rsa.pub`" \
        --type String
    fi
    ```

1. EC2 インスタンス用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
  
	Terraform のテンプレートファイルは、１つのテンプレートファイルに全ての定義を記述してもよいし、異なるリソースを別々のテンプレートファイルに記載してもよい。<br>

	ssh 接続可能な EC2 インスタンスを構築するためには、上記 EC2リソースの設定以外に、 ｛VPC・ゲートウェイ・ルーティングテーブル・セキュリティグループ・固定IP（使用する場合）・SSH鍵登録｝の設定が必要になる。

	<img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/172035178-ae152147-2056-489f-850a-72da46833dab.png">

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
		方法としては以下の方法がありえるが、今回は AWS Systems Manager のパラメーターストアを使用する方法を採用する

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

1. `.circleci/config.yml` を作成する<br>
    ```yml
		# CircleCIのバージョン。現状、1 か 2 か 2.1 を指定可能
		version: 2.1
		#===============================================
		# ジョブ定義
		#===============================================
		jobs:
			#-------------------------------------
			# terraform init & plan
			#-------------------------------------
			terraform-init-plan-job:
					# インデント幅が、Tab２回 or 半角スペース4文字になることに注意
					# job レベルでの環境変数
					environment:
							TERRAFORM_DIR: terraform/aws/ec2
					# CircleCI の実行ディレクトリ（デフォルトは ~/project）
					working_directory: ~/project
					# executor タイプ（docker, machine, macos, windows）
					# docker => docker 環境で job を実行
					docker:
						- image: docker.mirror.hashicorp.services/hashicorp/terraform:light
					steps:
						# working_directory に GitHub レポジトリをコピー
						- checkout
						# terraform init
						- run:
								# インデント幅が、Tab２回 or 半角スペース4文字になることに注意
								name: terraform init
								command: terraform -chdir="${TERRAFORM_DIR}" init
						# terraform plan
						- run:
								name: terraform plan
								command: terraform -chdir="${TERRAFORM_DIR}" plan -out workspace.plan
						# 一時的にファイルを job 間で共有できるようにする(最大30日間)
						- persist_to_workspace:
								root: .
								paths:
									- .
			#-------------------------------------
			# terraform-apply
			#-------------------------------------
			terraform-apply-job:
					environment:
							TERRAFORM_DIR: terraform/aws/ec2
					docker:
						- image: docker.mirror.hashicorp.services/hashicorp/terraform:light
					steps:
						# persist_to_workspace で共有されたファイルを取得
						- attach_workspace:
								at: .
						# terraform apply
						- run:
								name: terraform apply
								command: terraform -chdir="${TERRAFORM_DIR}" apply workspace.plan
		#===============================================
		# ワークフロー定義（jobの実行タイミングを定義）
		# CircleCI 2.0 で Workflow を設定しなかった場合、job 名が build の job のみが実行される。
		# ビルドパイプラインの種類 : パラレル（デフォルト設定）| job がパラレルに実行される。
		#===============================================
		workflows:
			version: 2
			terraform-ec2-workflow:
				jobs:
					- terraform-init-plan-job
					- terraform-init-plan-hold-job:
							# CircleCI のコンソール画面から手動承認
							type: approval
							# requires を指定する事でシーケンシャル（1つ前のjobの完了を待って次の1つのjobを実行する）になる
							requires: 
								- terraform-init-plan-job
					- terraform-apply-job:
							requires: 
								- terraform-init-plan-hold-job
    ```

    ポイントは、以下の通り

    - CircleCI では、CI/CDの設定は全て `.circleci/config.yml` に記載する

    - `workflows` は、ver2.0 以降に導入されたビルドパイプライン機能である。
        CircleCI 2.0 で Workflow を設定しなかった場合、job 名が build の job のみが実行される。

    - `:` の後で `-` がつかない場合は、インデント幅が、Tab２回 or 半角スペース4文字になることに注意

    - terraform がインストールされている docker image として、`docker.mirror.hashicorp.services/hashicorp/terraform:light` を使用する

    - `terraform plan` で `workspace.plan` という外部ファイルを出力しているが、この外部ファイルは `terraform apply` 実行時に参照する必要がある。異なる job で毎回 `checkout` していると job の実行中に出力されたファイルが異なる job 間で共有されずこのようなファイル `workspace.plan` を共有できなくなってしまう。そのため、前段の job（`terraform-init-plan-job`）にて `- persist_to_workspace:` を使用して一時的にファイルを job 間で共有できるようにし、後段の job（`terraform-apply-job`）にて `- attach_workspace:`　を使用して共有されたファイル（`workspace.plan`）を取得できるようにしている

    - ワークフロー定義（`workflows:`）にて、`terraform plan` を行う job（`terraform-init-plan-job`）に対して、`type: approval` を追加することで CircleCI コンソール画面から手動認証するようにしている

1. 【初回のみ】GitHub レポジトリを CircleCI に登録する<br>
    「[CircleCI の Web ページ](https://app.circleci.com)」からログインした後、Projects ページから　GitHub　レポジトリを CircleCI に登録する

1. 【初回のみ】CircleCI コンソール画面から AWS 認証用の環境変数を登録する<br>
    [CircleCI コンソール画面の [Project Settings] -> [Environment Variables]](https://app.circleci.com/settings/project/github/Yagami360/terraform-circleci-aws-cicd-exercises/environment-variables?return-to=https%3A%2F%2Fapp.circleci.com%2Fpipelines%2Fgithub%2FYagami360%2Fterraform-circleci-aws-cicd-exercises) から、CircleCI のワークフローから各種 AWS サービスを認証するための各種環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` を登録する<br>

    <img width="693" alt="image" src="https://user-images.githubusercontent.com/25688193/180351580-3affda05-4850-43ae-aea9-cf0562ea7c01.png">

1. 【オプション】CircleCI CLI コマンドを使用して、`.circleci/config.yml` の文法チェック・ジョブの実行確認を行う
    1. CircleCI CLI コマンドをインストールする
        ```sh
        curl -fLSs https://circle.ci/cli | bash
        ```

    1. CircleCI CLI コマンドを使用して、文法チェック・ジョブの実行確認を行う
        ```sh
        circleci config validate
        ```

1. 修正したコードを git push する
    ```sh
    git add .
    git commit -m "a"
    git push origin main
    ```

1. CircleCI コンソール画面から CI/CD の動作確認する<br>
    `terraform plan` 実行後、手動承認待ちで一時停止するので、`terraform plan` の変更内容が問題なければ、「Approve」ボタンをクリックする<br>
    <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/180383193-60326f72-77e9-4b4d-9f7e-5640ff645a43.png">


## ■ 参考サイト

- https://blog.not75743.com/post/circleci_terraform_vpc/
- https://qiita.com/gold-kou/items/4c7e62434af455e977c2
