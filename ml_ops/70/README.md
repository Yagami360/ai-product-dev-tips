# Terraform を利用して Amazon EKS クラスターを構築する（docker 使用時）


## ■ 未解決事項
- [ ] tf ファイルで EKS クラスター作成時に `
Error: error creating EKS Cluster (terraform-eks-cluster): InvalidParameterException: unsupported Kubernetes version` のエラーがでる問題の解決

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
	WORKDIR /terraform
	```

	ポイントは、以下の通り

	- terraform のバージョンが古いと、tf ファイルで EKS クラスター作成時に `
Error: error creating EKS Cluster (terraform-eks-cluster): InvalidParameterException: unsupported Kubernetes version` のエラーがでるので、比較的新しいバージョン `1.2.3` をインストールするようにしている

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
				- ${PWD}/terraform:/terraform
				- ${HOME}/.ssh/:/.ssh
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

	<img width="934" alt="image" src="https://user-images.githubusercontent.com/25688193/176822196-6be41790-6805-4e1f-b8f8-706f14248b3d.png">

	> VPC [Virtual Private Cloud] : AWS専用の仮想ネットワーク。インターネットを利用する際、ルーターやゲートウェイなどのネットワーク機器が必要となるが、VPCはそれらの機器を仮想的に用意し、ネットワーク環境を構築できるようにしている。

	> サブネットワーク: １つの大きなネットワーク（今の場合はVPC）を管理しやすくするために、より小さなネットワークに分割したときのサブネットワークのこと。

	> インターネットゲートウェイ : コンピュータネットワークにおいて、通信プロトコルが異なるネットワーク同士がデータをやり取りする際、中継する役割を担うルータのような機能を備えた機器やそれに関するソフトウェア

	> ルーティングテーブル : ルーターに記録される経路情報で、ルーティング処理を行う際に参照されるテーブルデータ。インターネットゲートウェイ経由で VPC へアクセスできるようにするために必要になる

	1. EKS クラスターの terraform `*.tf` ファイルを作成する<br>

		- `terraform/aws/eks/variables.tf`
			```python
			```

		- `terraform/aws/eks/main.tf`
			```python
			```

		- `terraform/aws/eks/outputs.tf`
			```python
			```

		ポイントは、以下の通り

		- `eksctl` コマンドを使用して EKS クラスターを作成する場合は、IAM や VPC などの関連リソースも自動的に生成されるが、terraform を使用して EKS クラスターを作成する場合は、IAM や VPC などの関連リソースも明示的に定義して作成する必要がある

		- `terraform {...}` ブロック内で `backend "s3"{...}` ブロックを定義することにより、S3 パケット上に tfstate ファイルを保存するようにしている。これにより、複数人で terraform を実行できるようになる

		- IAM の作成<br>
			EKS クラスターやノードプール用の IAM role や IAM policy を作成する必要がある<br>

			- EKS クラスターの master ノード用？の IAM の作成
				- `resource "aws_iam_role"` ブロックを定義して、EKS クラスターの master ノード？にアクセス出来るための IAM role を作成する<br>				

					> `resource "aws_iam_role"` で作成されるリソースは、`aws iam create-role` コマンドで作成されるリソースと同様のものになる

					- `assume_role_policy` には、具体的な IAM role を定義する必要があるが、AWS での iam policy は json 形式で定義する必要があるので、ヒアドキュメント `<<EOF ~ EOF` の形式で定義する

						> ヒアドキュメント : 特殊な記号などを含む文字列リテラルをソースコード（今回の場合は terraform コード）中に記述するための特別な記法

				- `resource "aws_iam_role_policy_attachment"` ブロックで、上記作成した IAM role に EKS クラスターにアクセスできるようにするための IAM policy を（ARN形式で）付与する<br>
					> `resource "aws_iam_role_policy_attachment"` で作成されるリソースは、`aws iam attach-role-p` コマンドで作成されるリソースと同様のものになる

					- 具体的に付与する ARN は、`"arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"`, `"arn:aws:iam::aws:policy/AmazonEKSServicePolicy"` の２つになる

			- EKS クラスターのノードプール用？（or 非 master ノード用？）の IAM の作成<br>
				- `resource "aws_iam_role"` ブロックを定義して、EKS クラスターのノードプール？（or 非 master ノード？）にアクセス出来るための IAM role を作成する<br>

				- `resource "aws_iam_role_policy_attachment"` ブロックで、上記作成した IAM role に EKS クラスターのノードプール？（非 master ノード？）にアクセスできるようにするための IAM policy を（ARN形式で）付与する<br>

				- `resource "aws_iam_instance_profile"`　ブロックで、IAM ロールを EC2 インスタンスに紐つけるためのインスタンスプロファイル？を作成する

	    	> AWS における IAM の仕組みの詳細は、「[【AWS】AWS の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/58)」を参考

		- EKS クラスター用の VPC の作成
			- VPC の作成<br>
				`resource "aws_vpc"` ブロックを定義して、VPC を作成する
				
				- EKS クラスターの VPC として使用するためには、`tags` に `"kubernetes.io/cluster/${var.cluster_name}" = "shared"` を追加する必要があることに注意

			- サブネットワークの作成<br>
				`resource "aws_subnet"` ブロックを使用して、上記作成した VPC ネットワークの中にサブネットを構築する。
				今回は `count=2` なので、VPC の中に２つのサブネットを構築している

				- サブネットが１つの場合は、`cidr_block` には、`10.0.1.0/24` の固定値を設定すればいいが、今回は２つ以上のサブネットが存在するので、両方 `cidr_block = "10.0.1.0/24"` にするとアドレスが conflicts してしまう。そのため `cidrsubnet()` を使って各サブネットの CIDR がそれぞれ異なるようにする

				- EKS クラスターのサブネットとして使用するためには、`tags` に `"kubernetes.io/cluster/${var.cluster_name}" = "shared"` を追加する必要があることに注意

			- インターネットゲートウェイの作成
				`resource "aws_internet_gateway"` ブロックを使用して、インターネット ↔ VPC 間のゲートウェイを設定する。

			- ルーティングテーブルの作成<br>


			- セキュリティーグループの作成<br>

		- EKS クラスターの作成<br>
			`resource "aws_eks_cluster"` ブロックで、EKS クラスターを作成する

			- `vpc_config` の `subnet_ids` に上記作成したサブネットを指定する必要がある。今回は２つ以上のサブネットが存在するので、`aws_subnet.terraform_eks_subnet.*` のように `*` で複数リソースを指定している。この際に、`subnet_ids = ["${aws_subnet.terraform_eks_subnet.*.id}"]` のように `[...]` で囲むとエラーになることに注意

			- kubeconfig は、どのクラスターにどのユーザーとして接続するのかの接続設定した k8s マニフェストファイルであり、`eksctl` コマンド等で EKS クラスターを構築した場合は `${HOME}/.kube/config` に自動的に書き込まれるファイルであるが、terraform を使用して EKS クラスターを構築する場合は、このディレクトリにジオ書き込まれれない？ので、以下の手順で、EKS クラスターでこの kubeconfig を参照するようにしている。
			
				1. `outputs.tf` 内の `locals {...}` ブロックで kubeconfig の local 変数 `local.kubeconfig` を定義。
					> この際に、yml 形式の k8s マニフェストで定義する必要があるので、`<<EOF ~ EOF`（ヒアドキュメント）を使用して定義している
				1. `output "kubeconfig"{...}` ブロックを定義してコンソール出力するようにする
				1. `terraform output kubeconfig > ${HOME}/kube/config` コマンドで上記コンソール出力された内容を `${HOME}/.kube/config` に書き込む
			
			- 同様にして、k8s の ConfigMap リソースのローカル変数 `local.eks_configmap` も定義している。これは master と node を紐づけるため必要？

		- ノードプールの作成<br>
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