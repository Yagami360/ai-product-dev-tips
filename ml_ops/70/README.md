# Terraform を利用して Amazon EKS クラスターを構築する（docker 使用時）

## ■ 方法

1. `aws configure` コマンドで AWS 認証情報を設定する。<br>
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

1. terraform 用の Dockerfile を作成する
	```dockerfile
	FROM alpine:3.10

	#ARG terraform_version="0.12.5"
	ARG terraform_version="1.2.3"

	# Install terraform etc
	RUN apk update --no-cache \
		&& apk add --no-cache \
				wget \
				unzip \
				curl \
		&& wget https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_linux_amd64.zip \
		&& unzip ./terraform_${terraform_version}_linux_amd64.zip -d /usr/local/bin/ \
		&& rm -rf ./terraform_${terraform_version}_linux_amd64.zip

	WORKDIR /.ssh    
	WORKDIR /.kube
	WORKDIR /k8s
	WORKDIR /terraform/aws
	```

	ポイントは、以下の通り

	- terraform のバージョンが古いと、バージョン不整合エラーがでたので、比較的新しいバージョン `1.2.3` をインストールするようにしている

	- 後述の処理で `.ssh/` ディレクトリにある ssh 公開鍵を同期させるために、`WORKDIR /.ssh` でディレクトリを作成している

	- 後述の処理で `/.kube/config` を同期させるために `WORKDIR /.kube` でディレクトリを作成している

	- 後述の処理で `k8s/eks_configmap.yaml` を同期させるために、`WORKDIR /k8s` でディレクトリを作成している

1. terraform 用の docker-compose を作成する
	```yaml
	version: '3'
	services:
		terraform-service:
			container_name: terraform-container
			image: terraform-image
			build:
				context: "."
				dockerfile: Dockerfile
			volumes:
	      - ${PWD}/:/terraform/aws
  	    - ${HOME}/.ssh/:/.ssh
    	  - ${HOME}/.kube/config:/.kube/config
      	- ${PWD}/k8s:/k8s
			tty: true
			environment:
				TZ: "Asia/Tokyo"
				LC_ALL: C.UTF-8
				LANG: C.UTF-8
	#      AWS_ACCESS_KEY_ID: xxx           
	#      AWS_SECRET_ACCESS_KEY: xxx
	#      AWS_DEFAULT_REGION: us-west-2
			env_file:
			- aws_key.env
	```

	ポイントは、以下の通り

	- terraform では、環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` に、IAM ユーザーの適切な認証情報の値を設定することで、terraform に対して AWS の認証情報を設定できる。

		> 環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` を設定していないと、後述の `terraform plan` or `terraform apply` コマンド使用時、`Error: error configuring Terraform AWS Provider: no valid credential sources for Terraform AWS Provider found.` のようなエラーメッセージがでて、`.tf` ファイルに記述した AWS リソースを認証できなくなる

	- 但し、`docker-compose.yml` にこれら環境変数の値を直接設定すると、キー情報が GitHub 上に公開されてしまうので、`aws_key.env` に、これら環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` の値を定義し、`aws_key.env` を gitignore するようにしている

		- `aws_key.env` の中身
			```sh
			AWS_ACCESS_KEY_ID=xxxxxxxxxxxx
			AWS_SECRET_ACCESS_KEY=xxxxxxxxx
			AWS_DEFAULT_REGION=us-west-2
			```

	- 設定すべき `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` の値は、`cat ${HOME}/.aws/credentials` で確認できる

	- 後述の処理で `.ssh/` ディレクトリにある ssh 公開鍵を同期させる必要があるので、`volumes` タグの設定を行っている

	- 後述の処理で `/.kube/config` を同期させる必要があるので、`volumes` タグの設定を行っている

	- 後述の処理で `k8s/eks_configmap.yaml` を同期させる必要があるので、`volumes` タグの設定を行っている

1. tfstate ファイル保存用の Amazon S3 パケットを作成する<br>
	`terraform apply` を実行すると、tf ファイルに基づいて各種インフラが作成されるが、そのインフラ情報が、`*.tfstate` ファイル（json形式）に自動的に保存され（場所は、tf ファイルと同じディレクトリ内）、次回の `terraform apply` 実行時等で前回のインフラ状態との差分をみる際に利用される。（tfstate ファイルの直接編集は非推奨）<br>
	そのため、tfstate ファイルをローカルに置いたままでは複数人で terraform を実行できなくなってしまう。この問題を解決するためには、tfstate ファイルを Amazon S3に保管するようにする

	1. Amazon S3 の terraform `*.tf` ファイルを作成する
		- `terraform/aws/s3/variables.tf`<br>
			```python
			variable "profile" {
				default = "Yagami360"
			}

			variable "region" {
				default = "us-west-2"
			}

			variable "bucket_name" {
				default = "terraform-tf-states-bucket"
			}
			```

		- `terraform/aws/s3/main.tf`<br>
			```python
			#-------------------------------
			# プロバイダー設定
			#-------------------------------
			provider "aws" {
					profile = "${var.profile}"
					region = "${var.region}"
			}

			#-------------------------------
			# 実行する Terraform 環境情報
			#-------------------------------
			terraform {
				# terraform のバージョン
				required_version = "~> 1.2.0"

				# 実行するプロバイダー
				required_providers {
					aws       = {
						source  = "hashicorp/aws"
						version = "~> 3.71.0"
					}
			    kubernetes = {
    			  version = ">= 2.7.1"
		    	}
				}
			}

			#-------------------------------
			# Amazon S3 パケット
			#-------------------------------
			resource "aws_s3_bucket" "terraform_tf_states_bucket" {
					bucket = "${var.bucket_name}"
			#    acl = "private"     # S3 上の ACL 指定 ※現バージョンでは private しか指定できない
			}
			```

		ポイントは、以下の通り

		- `resource "aws_s3_bucket"` で Amazon S3 パケットのリソースを定義する

		- 本 tf ファイルで S3 パケット作成時は、tfstate ファイル保存用の S3 パケット未作成であるので、tfstate ファイルを通常通りローカルディレクトリに保存するようにする

		- `terraform {...}` 内で `backend "s3"` として、terraform のバックエンドを Amazon S3 にすることで、tfstate ファイルが S3 パケット上に保存されるようになるが、S3 パケット未作成の時点では S3 パケット上にtfstate ファイルを保存できないので、S3 パケットに関する tfstate ファイルに関しては S3 ではなくローカルに保存するようにしている

	1. terraform コンテナを起動する<br>
		```sh
		cd terraform/aws
		docker-compose -f docker-compose.yml stop
		docker-compose -f docker-compose.yml up -d
		```

	1. terraform init を実行する<br>
		作成した Amazon S3 の tf ファイル郡に対して terraform init を実行し、terraform を初期化する。
		```sh
		docker exec -it terraform-aws-container /bin/sh -c "cd s3 && terraform init"
		```

	1. terraform plan を実行する<br>
		作成した Amazon S3 の tf ファイル郡に対して terraform plan を実行し、作成したテンプレートファイルの定義内容を確認する。
		```sh
		docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd s3 && terraform plan"
		```

	1. terraform apply を実行する<br>
		作成した Amzaon S3 の tf ファイル郡に対して terraform apply を実行し、定義を適用してインスタンスを作成する
		```sh
		docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd s3 && terraform apply"
		```

		以下の画面が出力されるので `yes` を入力する
		```
		Terraform will perform the actions described above.
		Only 'yes' will be accepted to approve.

		Enter a value: yes
		```

1. EKS クラスターの作成<br>
	<img width="924" alt="image" src="https://user-images.githubusercontent.com/25688193/176890411-f64b491d-684d-49ac-9212-c93eaa045480.png">

	> VPC [Virtual Private Cloud] : AWS専用の仮想ネットワーク。インターネットを利用する際、ルーターやゲートウェイなどのネットワーク機器が必要となるが、VPCはそれらの機器を仮想的に用意し、ネットワーク環境を構築できるようにしている。

	> サブネットワーク: １つの大きなネットワーク（今の場合はVPC）を管理しやすくするために、より小さなネットワークに分割したときのサブネットワークのこと。

	> インターネットゲートウェイ : コンピュータネットワークにおいて、通信プロトコルが異なるネットワーク同士がデータをやり取りする際、中継する役割を担うルータのような機能を備えた機器やそれに関するソフトウェア

	> ルーティングテーブル : ルーターに記録される経路情報で、ルーティング処理を行う際に参照されるテーブルデータ。インターネットゲートウェイ経由で VPC へアクセスできるようにするために必要になる

	1. EKS クラスターの terraform `*.tf` ファイルを作成する<br>

		- `terraform/aws/eks/variables.tf`
			```python
			variable "profile" {
				default = "Yagami360"
			}

			variable "region" {
				default = "us-west-2"
			}

			# data {...} ブロックを使用することで、Terraform 外部で定義されたデータを取得して、tf ファイル内で利用することができる
			# data "aws_availability_zones" {...} を使用すると、プロバイダ provider "aws" で設定されたリージョン内のAWSアカウントでアクセス可能な AWS Availability Zones のリストにアクセスすることを可能に
			data "aws_availability_zones" "available" {
			}

			#variable "zone" {
			#  default = "us-west-2a"
			#}

			variable "num_subnets" {
				default = 2
			}

			variable "vpc_cidr_block" {
				default = "10.0.0.0/16"
			}

			#variable "cluster_name" {
			#  default = "terraform-eks-cluster"
			#}

			#variable "cluster_version" {
			#  default = "1.10"
			#}

			variable "instance_type" {
				default = "t2.small"
			}

			# EC2 インスタンスで使用するキー名（`.ssh/**.pem` の ** の部分）/ resource "aws_launch_configuration" で使用
			variable "key_name" {
				default = "key"
			}

			# ローカル変数
			locals {
				cluster_name    = "terraform-eks-cluster"   # variable で定義すると aleady exsist エラーになるケースがある？ので、local で定義
				#cluster_version = "1.10"                   
				cluster_version = "1.20"                    # "1.10" だと `unsupported Kubernetes version` エラーができるので、1.20 を使用
			}
			```

		- `terraform/aws/eks/main.tf`
			```python
			#-------------------------------
			# プロバイダー設定
			#-------------------------------
			provider "aws" {
					profile = "${var.profile}"
					region = "${var.region}"
			}

			# EKS クラスターのリソース（resource "aws_eks_cluster"）使用時に必要 / EKSクラスター内に aws-auth ConfigMap リソース？を作成する際に使用される
			#provider "kubernetes" {
			#  host                   = aws_eks_cluster.terraform_eks_cluster.endpoint
			#  cluster_ca_certificate = base64decode(aws_eks_cluster.terraform_eks_cluster.certificate_authority[0].data) # EKSクラスタへの認証情報
			#  token                  = aws_eks_cluster_auth.terraform_eks_cluster.token
			#}

			#-------------------------------
			# 実行する Terraform 環境情報
			#-------------------------------
			terraform {
				# terraform のバージョン
				required_version = "~> 1.2.0"

				# バックエンドを S3 にする
				backend "s3" {
					bucket = "terraform-tf-states-bucket"
					key = "aws/eks/terraform.tfstate"
				}

				# 実行するプロバイダー
				required_providers {
					aws       = {
						source  = "hashicorp/aws"
						version = "~> 3.71.0"
					}
					kubernetes = {
						version = ">= 2.7.1"
					}
				}
			}

			#-------------------------------
			# IAM
			#-------------------------------
			# EKS クラスター用の IAM role
			resource "aws_iam_role" "terraform_eks_master_iam_role" {
				name = "terraform-eks-master-iam-role"

				# AWS での iam policy は json 形式になるので <<EOF ~ EOF（ヒアドキュメント）で定義
				# ヒアドキュメント : 特殊な記号などを含む文字列リテラルをソースコード（今回の場合は terraform コード）中に記述するための特別な記法
				assume_role_policy = <<EOF
			{
				"Version": "2012-10-17",
				"Statement": [
					{
						"Effect": "Allow",
						"Principal": {
							"Service": "eks.amazonaws.com"
						},
						"Action": "sts:AssumeRole"
					}
				]
			}
			EOF
			}

			# EKS クラスター用の IAM role に IAM policy（EKSクラスターのARN）を割り当て 
			resource "aws_iam_role_policy_attachment" "terraform_eks_cluster_iam_policy_attachment" {
				policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
				role       = "${aws_iam_role.terraform_eks_master_iam_role.name}"
			}

			# EKS クラスター用の IAM role に IAM policy（EKSサービズのARN）を割り当て 
			resource "aws_iam_role_policy_attachment" "terraform_eks_service_iam_policy_attachment" {
				policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
				role       = "${aws_iam_role.terraform_eks_master_iam_role.name}"
			}

			# EKS クラスター内の ノード（EC2インスタンス）用の IAM role
			resource "aws_iam_role" "terraform_eks_node_iam_role" {
				name = "terraform-eks-node-iam-role"

				assume_role_policy = <<EOF
			{
				"Version": "2012-10-17",
				"Statement": [
					{
						"Effect": "Allow",
						"Principal": {
							"Service": "ec2.amazonaws.com"
						},
						"Action": "sts:AssumeRole"
					}
				]
			}
			EOF
			}

			# EKS クラスター内の ノード（EC2インスタンス）用の IAM role に IAM policy（AmazonEKSWorkerNodePolicyのARN）を割り当て 
			resource "aws_iam_role_policy_attachment" "terraform_eks_worker_node_iam_policy_attachment" {
				policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
				role       = "${aws_iam_role.terraform_eks_node_iam_role.name}"
			}

			# EKS クラスター内の ノード（EC2インスタンス）用の IAM role に IAM policy（AmazonEKS_CNI_PolicyのARN）を割り当て
			resource "aws_iam_role_policy_attachment" "terraform_eks_cni_iam_policy_attachment" {
				policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
				role       = "${aws_iam_role.terraform_eks_node_iam_role.name}"
			}

			# EKS クラスター内の ノード（EC2インスタンス）用の IAM role に IAM policy（AmazonEC2ContainerRegistryReadOnlyのARN）を割り当て
			resource "aws_iam_role_policy_attachment" "terraform_eks_ro_iam_policy_attachment" {
				policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
				role       = "${aws_iam_role.terraform_eks_node_iam_role.name}"
			}

			# EKS クラスター内の ノード（EC2インスタンス）用のインスタンスプロファイル。IAM ロールを EC2 インスタンスに紐つけるために必要
			resource "aws_iam_instance_profile" "terraform_eks_node_iam_instance_profile" {
				name = "terraform-eks-node-iam-instance-profile-2"
				role = "${aws_iam_role.terraform_eks_node_iam_role.name}"
			}

			#-------------------------------
			# VPC
			#-------------------------------
			# VPC の設定
			resource "aws_vpc" "terraform_eks_vpc" {
					cidr_block = var.vpc_cidr_block
					enable_dns_hostnames = true     # ?
					enable_dns_support = true       # ?

					tags = {
						Name = "terraform-eks-vpc"
						"kubernetes.io/cluster/${local.cluster_name}" = "shared"  # VPC を EKS で使用する場合には必須のタグ
					}
			#    tags = "${merge(map("Name", "terraform-eks-subnet-${count.index+1}"), map("kubernetes.io/cluster/${local.cluster_name}", "owned"))}"
			}

			# サブネットワークの設定
			resource "aws_subnet" "terraform_eks_subnet" {
					count = "${var.num_subnets}"                                                    # VPC の中にあるサブネットの数
					vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
					#availability_zone = "${var.zone}"
					availability_zone       = "${element(data.aws_availability_zones.available.names, count.index % var.num_subnets)}"  # 複数のサブネットが存在する場合は、それぞれ異なる zone に割りあて 
					#cidr_block = "10.0.1.0/24"
					cidr_block              = "${cidrsubnet(var.vpc_cidr_block, 8, count.index)}"   # サブネットが２つ以上ある場合は、両方 cidr_block = "10.0.1.0/24" にすると conflicts するので、cidrsubnet() を使って各サブネットのCIDRがそれぞれ異なるようにする
					map_public_ip_on_launch = true                    # ?

					tags = {
						Name = "terraform-eks-subnet-${count.index+1}"
						"kubernetes.io/cluster/${local.cluster_name}" = "shared"  # VPC を EKS で使用する場合には必須のタグ
					}
			#    tags = "${merge(map("Name", "terraform-eks-subnet-${count.index+1}"), map("kubernetes.io/cluster/${local.cluster_name}", "owned"))}"
			}

			# ゲートウェイの設定
			resource "aws_internet_gateway" "terraform_eks_gateway" {
					vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
					tags = {
							Name = "terraform-eks-gateway"
					}
			}

			# ルーティングテーブルの設定
			resource "aws_route_table" "terraform_eks_route_table" {
					vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
					route {
							cidr_block = "0.0.0.0/0"
							gateway_id = "${aws_internet_gateway.terraform_eks_gateway.id}"
					}
					tags = {
							Name = "terraform-eks-route-table"
					}
			}

			resource "aws_route_table_association" "terraform_eks_route_table_association" {
					count          = "${var.num_subnets}"                                             # リソースの数
					subnet_id      = "${element(aws_subnet.terraform_eks_subnet.*.id, count.index)}"  # element(リスト,要素番号) : リストの要素を取得 / aws_subnet.terraform_eks_subnet.* : 全ての aws_subnet リソースを参照 / count.index : リソースのインデックス
					route_table_id = "${aws_route_table.terraform_eks_route_table.id}"
			}

			# マスターノード用のセキュリティーグループの設定
			resource "aws_security_group" "terraform_eks_master_security_group" {
					name = "terraform-eks-master-security-group"
					description = "EKS master security group"
					vpc_id = "${aws_vpc.terraform_eks_vpc.id}"
					# インバウンドルール(SSL通信ではHTTPSプロトコルにあたる443番を利用)
					ingress {
							from_port = 443
							to_port = 443
							protocol = "tcp"
							cidr_blocks = ["0.0.0.0/0"]
					}
					# アウトバウンドルール(全開放)
					egress {
							from_port = 0
							to_port = 0
							protocol = "-1"
							cidr_blocks = ["0.0.0.0/0"]
					}
					tags = {
							Name = "terraform-eks-master-security-group"
					}
			}

			# マスターノード以外の各ノード用のセキュリティーグループの設定
			resource "aws_security_group" "terraform_eks_nodes_security_group" {
					name = "terraform-eks-nodes-security-group"
					description = "EKS node security group"
					vpc_id = "${aws_vpc.terraform_eks_vpc.id}"

					# インバウンドルール()
					ingress {
							description     = "Allow cluster master to access cluster node"
							from_port = 1025
							to_port = 65535
							protocol = "tcp"
							#cidr_blocks = ["0.0.0.0/0"]
							security_groups = ["${aws_security_group.terraform_eks_master_security_group.id}"]  # master ノードのセキュリティーグループ
					}
					# インバウンドルール(masterノードとの通信用<TCP/443>)
					ingress {
							description     = "Allow cluster master to access cluster node"
							from_port = 443
							to_port = 443
							protocol = "tcp"
							#cidr_blocks = ["0.0.0.0/0"]    # ? 不要
							security_groups = ["${aws_security_group.terraform_eks_master_security_group.id}"]  # master ノードのセキュリティーグループ
							self            = false     # ?
					}
					# インバウンドルール(pod間通信用)
					ingress {
							description = "Allow inter pods communication"
							from_port   = 0
							to_port     = 0
							protocol    = "-1"
							self        = true
					}
					# アウトバウンドルール(全開放)
					egress {
							from_port = 0
							to_port = 0
							protocol = "-1"
							cidr_blocks = ["0.0.0.0/0"]
					}
					tags = {
							Name = "terraform-eks-nodes-security-group"
					}
			}

			#-------------------------------
			# EKS クラスター
			#-------------------------------
			# EKS クラスター
			resource "aws_eks_cluster" "terraform_eks_cluster" {
				name     = "${local.cluster_name}"
				version  = "${local.cluster_version}"
				role_arn = "${aws_iam_role.terraform_eks_master_iam_role.arn}"    # master ノードの IAM role を割り当て

				# クラスタの VPC 設定
				vpc_config {
					subnet_ids = "${aws_subnet.terraform_eks_subnet.*.id}"
					security_group_ids = ["${aws_security_group.terraform_eks_master_security_group.id}"]
				}

				#
				depends_on = [
					"aws_iam_role_policy_attachment.terraform_eks_cluster_iam_policy_attachment",
					"aws_iam_role_policy_attachment.terraform_eks_service_iam_policy_attachment",
				]
			}

			#-------------------------------
			# EKSクラスター内のノード（EC2インスタンス）
			#-------------------------------
			# EKSクラスターの各ノードの AMI イメージ
			data "aws_ami" "terraform_aws_ami" {
				most_recent = true
				owners      = ["602401143452"]

				filter {
					name   = "name"
					values = ["amazon-eks-node-${aws_eks_cluster.terraform_eks_cluster.version}-v*"]
				}
			}

			# resource "aws_launch_configuration" {...} ブロックの `user_data_base64` で参照
			locals {
				userdata = <<EOF
			#!/bin/bash
			set -o xtrace
			/etc/eks/bootstrap.sh --apiserver-endpoint "${aws_eks_cluster.terraform_eks_cluster.endpoint}" --b64-cluster-ca "${aws_eks_cluster.terraform_eks_cluster.certificate_authority.0.data}" "${aws_eks_cluster.terraform_eks_cluster.name}"
			EOF
			}

			# オートスケーリング・グループ "aws_autoscaling_group" に使用される起動設定
			resource "aws_launch_configuration" "terraform_aws_launch_configuration" {
				associate_public_ip_address = true
				iam_instance_profile        = "${aws_iam_instance_profile.terraform_eks_node_iam_instance_profile.id}"
				image_id                    = "${data.aws_ami.terraform_aws_ami.image_id}"
				instance_type               = "${var.instance_type}"
				name_prefix                 = "terraform-aws-launch-configuration"
				key_name                    = "${var.key_name}"

				root_block_device {
					volume_type = "gp2"
					volume_size = "50"
				}

				security_groups  = ["${aws_security_group.terraform_eks_nodes_security_group.id}"]
				user_data_base64 = "${base64encode(local.userdata)}"

				lifecycle {
					create_before_destroy = true
				}
			}

			# オートスケール可能なEC2インスタンス
			resource "aws_autoscaling_group" "terraform_eks_autoscaling_group" {
				name                 = "EKS node autoscaling group"
				launch_configuration = "${aws_launch_configuration.terraform_aws_launch_configuration.id}"   # 必須パラメーター
				vpc_zone_identifier = "${aws_subnet.terraform_eks_subnet.*.id}"

				desired_capacity     = "1"
				min_size             = "1"
				max_size             = "2"

				tag {
					key                 = "Name"
					value               = "terraform-eks-autoscaling-group"
					propagate_at_launch = true
				}

				# EKSで使用する場合は､EC2インスタンスには下記のタグが必須
				tag {
					key                 = "kubernetes.io/cluster/${local.cluster_name}"
					value               = "owned"
					propagate_at_launch = true
				}
			}

			#resource "aws_eks_node_group" "terraform_eks_node_group" {
			#  cluster_name    = aws_eks_cluster.terraform_eks_cluster.name
			#  node_group_name = "terraform-eks-node-group"
			#  node_role_arn   = aws_iam_role.terraform_eks_node_iam_role.arn
			#  subnet_ids      = "${aws_subnet.terraform_eks_subnet.*.id}"
			#  ami_type        = "AL2_x86_64"
			#  instance_types  = "[${var.instance_type}]"
				
			#  remote_access {
			#    ec2_ssh_key  = var.key_name
			#    source_security_group_ids = ["${aws_security_group.terraform_eks_master_security_group.id}"]
			#  }
			
			#  scaling_config {
			#    desired_size = 1
			#    min_size     = 1
			#    max_size     = 2
			#  }
			
			#  depends_on = [
			#    aws_iam_role_policy_attachment.terraform_eks_worker_node_iam_policy_attachment,
			#    aws_iam_role_policy_attachment.terraform_eks_cni_iam_policy_attachment,
			#    aws_iam_role_policy_attachment.aws_iam_role_policy_attachment,
			#  ]
			#}
			```

		- `terraform/aws/eks/outputs.tf`
			```python
			locals {
				# <<EOF ~ EOF（ヒアドキュメント）で kubeconfig のk8s マニフェスト（yml形式）を定義
				# kubeconfig : どのクラスターにどのユーザーとして接続するのかの接続設定した k8s マニフェストファイル。通常は $HOME/.kube/config に存在するが、terraform で EKS クラスター作成
				kubeconfig = <<EOF
			apiVersion: v1
			kind: Config
			clusters:
			- cluster:
					server: ${aws_eks_cluster.terraform_eks_cluster.endpoint}
					certificate-authority-data: ${aws_eks_cluster.terraform_eks_cluster.certificate_authority.0.data}
				name: kubernetes
			contexts:
			- context:
					cluster: kubernetes
					user: aws
				name: aws
			current-context: aws
			preferences: {}
			users:
			- name: aws
				user:
					exec:
						apiVersion: client.authentication.k8s.io/v1alpha1
						command: aws-iam-authenticator
						args:
							- "token"
							- "-i"
							- "${local.cluster_name}"
			EOF

				# master と node を紐づけるための？ ConfigMap リソースを定義
				eks_configmap = <<EOF
			apiVersion: v1
			kind: ConfigMap
			metadata:
				name: aws-auth
				namespace: kube-system
			data:
				mapRoles: |
					- rolearn: ${aws_iam_role.terraform_eks_node_iam_role.arn}
						username: system:node:{{EC2PrivateDNSName}}
						groups:
							- system:bootstrappers
							- system:nodes
			EOF
			}

			output "kubeconfig" {
				value = "${local.kubeconfig}"
			}

			output "eks_configmap" {
				value = "${local.eks_configmap}"
			}
			```

		ポイントは、以下の通り

		- `eksctl` コマンドを使用して EKS クラスターを作成する場合は、IAM や VPC などの関連リソースも自動的に生成されるが、terraform を使用して EKS クラスターを作成する場合は、IAM や VPC などの関連リソースも明示的に定義して作成する必要がある

		- `terraform {...}` ブロック内で `backend "s3"{...}` ブロックを定義することにより、S3 パケット上に tfstate ファイルを保存するようにしている。これにより、複数人で terraform を実行できるようになる

		- IAM の作成<br>
			EKS クラスターやノードプール用の IAM role や IAM policy を作成する必要がある<br>

			- EKS クラスター用の IAM の作成
				- `resource "aws_iam_role"` ブロックを定義して、EKS クラスターにアクセス出来るための IAM role を作成する<br>				

					> `resource "aws_iam_role"` で作成されるリソースは、`aws iam create-role` コマンドで作成されるリソースと同様のものになる

					- `assume_role_policy` には、具体的な IAM role を定義する必要があるが、AWS での iam policy は json 形式で定義する必要があるので、ヒアドキュメント `<<EOF ~ EOF` の形式で定義する

						> ヒアドキュメント : 特殊な記号などを含む文字列リテラルをソースコード（今回の場合は terraform コード）中に記述するための特別な記法

				- `resource "aws_iam_role_policy_attachment"` ブロックで、上記作成した IAM role に EKS クラスターにアクセスできるようにするための IAM policy を（ARN形式で）付与する<br>
					> `resource "aws_iam_role_policy_attachment"` で作成されるリソースは、`aws iam attach-role-p` コマンドで作成されるリソースと同様のものになる

					- 具体的に付与する ARN は、`"arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"`, `"arn:aws:iam::aws:policy/AmazonEKSServicePolicy"` の２つになる

			- EKS クラスター内の ノード（EC2インスタンス）用の IAM の作成<br>
				- `resource "aws_iam_role"` ブロックを定義して、EKS クラスター内のノード（EC2インスタンス）にアクセス出来るための IAM role を作成する<br>

				- `resource "aws_iam_role_policy_attachment"` ブロックで、上記作成した IAM role に EKS クラスター内のノード（EC2インスタンス）にアクセスできるようにするための IAM policy を（ARN形式で）付与する<br>

				- `resource "aws_iam_instance_profile"`　ブロックで、IAM ロールを EC2 インスタンスに紐つけるためのインスタンスプロファイル？を作成する

	    	> AWS における IAM の仕組みの詳細は、「[【AWS】AWS の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/58)」を参考

		- EKS クラスター用の VPC の作成
			- VPC の作成<br>
				`resource "aws_vpc"` ブロックを定義して、VPC を作成する
				
				- EKS クラスターの VPC として使用するためには、`tags` に `"kubernetes.io/cluster/${var.cluster_name}" = "shared"` を追加する必要があることに注意

			- サブネットワークの作成<br>
				`resource "aws_subnet"` ブロックを使用して、上記作成した VPC ネットワークの中にサブネットを構築する。
				今回は `count=2` なので、VPC の中に２つのサブネットを構築している

				- サブネットが１つの場合は、`cidr_block` には、`10.0.1.0/24` などの固定値を設定すればいいが、今回は２つ以上のサブネットが存在するので、両方 `cidr_block = "10.0.1.0/24"` にするとアドレスが conflicts してしまう。そのため `cidrsubnet()` を使って各サブネットの CIDR がそれぞれ異なる（今回の場合は `10.0.0.0/24` と `10.0.1.0/24`）ようにする

				- 複数のサブネットが存在する場合に、`availability_zone` に、単一の zone を割り当てると `Error: error creating EKS Cluster (terraform-eks-cluster): InvalidParameterException: Subnets specified must be in at least two different AZs` のエラーがでるので、`availability_zone = "${element(data.aws_availability_zones.available.names, count.index % var.num_subnets)}"` として、複数 zone を割り当てている（今回の場合は `us-west-2a` と `us-west-2b` になる）

					ここで、`data.aws_availability_zones` は `data "aws_availability_zones" "available" {}` で定義された Data Source。

					>  Data Source : `data {...}` ブロックで定義されるリソースで、Terraform 外部で定義されたデータを取得して、tf ファイル内で利用することができる。

					> 特に `data "aws_availability_zones" {...}` を使用すると、プロバイダ `provider "aws"` で設定されたリージョン `region` 内の AWS アカウントでアクセス可能な AWS Availability Zones のリストにアクセスすることが可能になる
				
					また、`element(リスト,要素番号)` で、リストの要素を取得している

				- EKS クラスターのサブネットとして使用するためには、`tags` に `"kubernetes.io/cluster/${var.cluster_name}" = "shared"` を追加する必要があることに注意

			- インターネットゲートウェイの作成
				`resource "aws_internet_gateway"` ブロックを使用して、インターネット ↔ VPC 間のゲートウェイを設定する。

			- ルーティングテーブルの作成<br>
				xxx

			- セキュリティーグループの作成<br>
				xxx

		- EKS クラスターの作成<br>
			`resource "aws_eks_cluster"` ブロックで、EKS クラスターを作成する

			- `version` には k8s バージョンを指定すればよいが、`version = "1.10"` だと `Error: error creating EKS Cluster (terraform-eks-cluster): InvalidParameterException: unsupported Kubernetes version` のエラーが出たので、`version = "1.20"` にしている

			- `vpc_config` の `subnet_ids` に上記作成したサブネットを指定する必要がある。今回は２つ以上のサブネットが存在するので、`aws_subnet.terraform_eks_subnet.*` のように `*` で複数リソースを指定している。この際に、`subnet_ids = ["${aws_subnet.terraform_eks_subnet.*.id}"]` のように `[...]` で囲むとエラーになることに注意

			- kubeconfig は、どのクラスターにどのユーザーとして接続するのかの接続設定した k8s マニフェストファイルであり、`eksctl` コマンド等で EKS クラスターを構築した場合は `${HOME}/.kube/config` に自動的に書き込まれるファイルであるが、terraform を使用して EKS クラスターを構築する場合は、このディレクトリに自動的に書き込まれれないので、以下の手順で、EKS クラスターでこの kubeconfig を参照するようにしている。
			
				1. `outputs.tf` 内の `locals {...}` ブロックで kubeconfig の local 変数 `local.kubeconfig` を定義。
					> この際に、yml 形式の k8s マニフェストで定義する必要があるので、`<<EOF ~ EOF`（ヒアドキュメント）を使用して定義している
				1. `output "kubeconfig"{...}` ブロックを定義してコンソール出力するようにする
				1. `terraform output kubeconfig > ${HOME}/kube/config` コマンドで上記コンソール出力された内容を `${HOME}/.kube/config` に書き込む
			
			- 同様にして、k8s の ConfigMap リソースのローカル変数 `local.eks_configmap` も定義している。これは master と node を紐づけるため必要？

		- EKS クラスター内のノード（EC2 インスタンス）の作成<br>
			xxx

	1. terraform コンテナを起動する<br>
		```sh
		cd terraform/aws
		docker-compose -f docker-compose.yml stop
		docker-compose -f docker-compose.yml up -d
		```

	1. terraform init を実行する<br>
		作成した EKS クラスターの tf ファイル郡に対して、terraform init を実行し、terraform を初期化する。
		```sh
		docker exec -it terraform-aws-container /bin/sh -c "cd eks && terraform init"
		```

	1. terraform plan を実行する<br>
		作成した EKS クラスターの tf ファイル郡に対して、terraform plan を実行し、作成したテンプレートファイルの定義内容を確認する。
		```sh
		docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd eks && terraform plan"
		```

	1. terraform apply を実行する<br>
		作成した EKS クラスターの tf ファイル郡に対して、terraform apply を実行し、定義を適用してインスタンスを作成する
		```sh
		docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd eks && terraform apply"
		```

		以下の画面が出力されるので `yes` を入力する
		```
		Terraform will perform the actions described above.
		Only 'yes' will be accepted to approve.

		Enter a value: yes
		```
        
	1. 作成した EKS クラスターの kubeconfig を反映する<br>
		kubeconfig を `${HOME}/.kube/config` に書き込み、作成した EKS クラスターに切り替える
		```sh
		terraform output kubeconfig > ${HOME}/kube/config
		export KUBECONFIG='${HOME}/kube/config'
		```

	1. EKS クラスターの ConfigMap をデプロイする<br>
		master と node を紐づけるための ConfigMap をデプロイする
		```sh
		mkdir -p k8s
		terraform output eks_configmap > k8s/eks_configmap.yml
		kubectl apply -f k8s/eks_configmap.yaml
		```

## ■ 参考サイト

- https://qiita.com/samskeyti/items/5855f1f2b5262e27af6e
- https://dev.classmethod.jp/articles/terraform-eks-create/
- https://open-groove.net/aws-eks/terraform-mac-eks-cluster/