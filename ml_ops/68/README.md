# GitHub Actions, Terraform, ArgoCD を使用して GKE 上の Web-API の CI/CD を行う

- 対象レポジトリ
    - https://github.com/Yagami360/terraform-github-actions-argocd-gke-cicd-exercises

## ■ 方法

1. Web-API のコードと Dockerfile と k8s マニフェストを作成する<br>
    - `app.py`<br>
        ```ptyhon
        ```

    - `Dockerfile`<br>
        ```Dockerfile
        ```

    - `k8s/fast_api.yaml`<br>
        ```yml
        ```

1. ローカル環境で terraform を実行するための Dockefile & docker-compose.yml を作成する
    ```Dockerfile
    #FROM alpine:3.10
    FROM python:3.8-slim

    # Install basic
    ENV DEBIAN_FRONTEND noninteractive
    RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
        sudo \
        wget \
        unzip \
        curl \
        python3-pip \
        # imageのサイズを小さくするためにキャッシュ削除
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    RUN pip3 install --upgrade pip

    # Install terraform
    ARG terraform_version="1.2.3"
    RUN wget https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_linux_amd64.zip \
        && unzip ./terraform_${terraform_version}_linux_amd64.zip -d /usr/local/bin/ \
        && rm -rf ./terraform_${terraform_version}_linux_amd64.zip

    # install gcloud
    RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
    RUN mkdir -p /usr/local/gcloud \
    && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
    && /usr/local/gcloud/google-cloud-sdk/install.sh
    ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

    # コンテナ起動後の作業ディレクトリ
    WORKDIR /.config/gcloud
    WORKDIR /terraform
    ```

    ```yaml
    version: '3'
    services:
      terraform-gcp-service:
        container_name: terraform-gcp-container
        image: terraform-gcp-image
        build:
          context: "."
          dockerfile: Dockerfile
        volumes:
        - ${PWD}:/terraform
        - ${HOME}/.config/gcloud/:/.config/gcloud   # ~/.config/gcloud/application_default_credentials.json を同期
        tty: true
        environment:
          TZ: "Asia/Tokyo"
          LC_ALL: C.UTF-8
          LANG: C.UTF-8
          GOOGLE_APPLICATION_CREDENTIALS: /.config/gcloud/application_default_credentials.json  # terraform で各種 GCP サービスを認識できるようにする
    ```

    ポイントは、以下の通り

    - 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` での GCP 認証を行えるようにするために、terraform のインストールの他に gcloud のインストールも行っている。

    - 環境変数 `GOOGLE_APPLICATION_CREDENTIALS` に、ローカル環境の `application_default_credentials.json` を設定する
    
        > この設定を行わないと、後述の `terraform plan` or `terraform apply` 実行時にエラーが発生して、`*.tf` ファイルに記述した GCP リソースを認証できなくなる


1. `*.tfstate` ファイルを保存するための GCS パケットを作成する<br>
    `terraform apply` を実行すると、tf ファイルに基づいて、各種インフラが作成されるが、そのインフラ情報が、`*.tfstate` ファイル（json形式）に自動的に保存され（場所は、tf ファイルと同じディレクトリ内）、次回の `terraform apply` 実行時等で前回のインフラ状態との差分をみる際に利用される。

    そのため、tfstate ファイルをローカルに置いたままでは複数人で terraform を実行できなくなってしまう。この問題を解決するために、tfstate ファイルを GCS パケット上に保管するようにする。

    - terraform を使用して作成する場合
        1. GCS パケット用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>        
            ```python
            #-------------------------------
            # プロバイダー設定
            #-------------------------------
            provider "google" {
                project = "my-project2-303004"
                region  = "us-central1"
            }

            #-------------------------------
            # 実行する Terraform 環境情報
            #-------------------------------
            terraform {
                # バックエンドを GCS にする（初回の GCS パケット未作成時はエラーになるのでコメントアウト）
                #  backend "gcs" {
                #    bucket = "terraform-tf-states-bucket"
                #    prefix = "gcp/gcs"
                #  }

                # プロバイダー情報
                #  required_providers {
                #    google = {
                #      version = "~> 4.13.0"
                #    }
                #  }
            }

            #-------------------------------
            # 各種 GCP サービス有効化
            #-------------------------------
            resource "google_project_service" "enable_iamcredentials" {
                service = "iamcredentials.googleapis.com"
            }

            resource "google_project_service" "enable_secretmanager" {
                service = "secretmanager.googleapis.com"
            }

            resource "google_project_service" "enable_cloudresourcemanager" {
                service = "cloudresourcemanager.googleapis.com"
            }

            #-------------------------------
            # GCS パケット
            #-------------------------------
            # tfstate ファイルを保存する GCS パケット
            # terraform apply で作成したインフラ情報は、*.tfstate ファイルに保存され、次回の terraform apply 実行時等で前回のインフラ状態との差分をみる際に利用されるが、
            # tfstate ファイルをローカルに置いたままでは複数人で terraform を実行できなくなってしまうので、GCS に保存する
            resource "google_storage_bucket" "terraform-tf-states" {
                name          = "terraform-tf-states-bucket"
                location      = "ASIA"
                versioning {
                    enabled = true
                }
            }

            output bucket_name {
                value       = google_storage_bucket.terraform-tf-states.name
                description = "terraform *.tfstate files"
            }
            ```

        1. ローカル環境から terraform を使用して GCS パケットを作成する
            ```sh
            #!/bin/sh
            set -eu
            ROOT_DIR=${PWD}
            PROJECT_ID=my-project2-303004
            CONTAINER_NAME="terraform-gcp-container"

            #-----------------------------
            # terraform
            #-----------------------------
            cd terraform

            # terraform コンテナ起動
            docker-compose -f docker-compose.yml stop
            docker-compose -f docker-compose.yml up -d

            # GCP プロジェクト設定
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "gcloud config set project ${PROJECT_ID}"

            # terraform を初期化する。
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform init"

            # 作成したテンプレートファイルの定義内容を確認する
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform plan"

            # 定義を適用してインスタンスを作成する
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform apply"

            # terraform が作成したオブジェクトの内容を確認
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform show"
            ```

    - gcloud コマンドで作成する場合<br>
        ```sh
        ```

    ポイントは、以下の通り

    - `terraform {...}` 内で `backend "gcs"` として、terraform のバックエンドを GCS にすることで、tfstate ファイルが GCS パケット上に保存されるようになるが、GCS パケット未作成の時点では tfstate ファイルを保存できないので、GCS パケットに関する tfstate ファイルに関しては GCS ではなくローカルに保存するようにしている

        > 但し、初回の GCS パケット作成後は、各種 GCS リソースの tfstate ファイルを GCS に保存するようにする
    
1. GitHub Actions 用サービスアカウントと Workload Identity を作成する<br>
    - terraform を使用して作成する場合
        1. GitHub Actions 用サービスアカウントと Workload Identity 用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
            ```python
            #-------------------------------
            # プロバイダー設定
            #-------------------------------
            provider "google" {
                project = "my-project2-303004"
                region  = "us-central1"
            }

            #-------------------------------
            # 実行する Terraform 環境情報
            #-------------------------------
            terraform {
                # バックエンドを GCS にする
                backend "gcs" {
                    bucket = "terraform-tf-states-bucket"
                    prefix = "gcp/iam"
                }

                # プロバイダー情報
                #  required_providers {
                #    google = {
                #      version = "~> 4.13.0"
                #    }
                #  }
            }

            #-------------------------------
            # サービスアカウント
            #-------------------------------
            # ローカル変数
            locals {
                repository_owner = "Yagami360"
                repository_name = "terraform-github-actions-argocd-gke-cicd-exercises"
            }

            # GitHub Actions 用のサービスアカウント
            resource "google_service_account" "github_actions_service_account" {
                project      = "my-project2-303004"
                account_id   = "github-actions-sa"
                display_name = "GitHub Actions of Terraform"
            }

            # GitHub Actions 用のサービスアカウントの IAM 権限設定（サービスアカウントに必要な権限を付与する）
            resource "google_project_iam_member" "github_actions_iam" {
                role    = "roles/owner"
                member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
            }

            # Workload Identity プール（外部IDとGoogle Cloudとの紐付けを設定した Workload Identity プロバイダをグループ化し、管理するためのもの）
            resource "google_iam_workload_identity_pool" "github_actions_workload_identity_pool" {
                provider                  = google-beta
                workload_identity_pool_id = "github-actions-pool"
                display_name              = "Terraform GitHub Actions"
                description               = "Used by GitHub Actions"
            }

            # Workload Identity プロバイダー（GitHub Actionsのワークフローで利用するために必要）
            resource "google_iam_workload_identity_pool_provider" "github_actions_workload_identity_provider" {
                provider                           = google-beta
                workload_identity_pool_id          = google_iam_workload_identity_pool.github_actions_workload_identity_pool.workload_identity_pool_id
                workload_identity_pool_provider_id = "github-actions-provider"
                attribute_mapping                  = {
                    "google.subject"       = "assertion.sub"
                    "attribute.actor"      = "assertion.actor"
                    "attribute.aud"        = "assertion.aud"
                    "attribute.repository" = "assertion.repository"
                }

                oidc {
                    allowed_audiences = []
                    issuer_uri        = "https://token.actions.githubusercontent.com"
                }
            }

            # WorklWorkload Identity と GitHub Actions 用サービスアカウントの連携
            resource "google_service_account_iam_member" "bind_sa_to_repo" {
                service_account_id = google_service_account.github_actions_service_account.name
                role               = "roles/iam.workloadIdentityUser"
                member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_actions_workload_identity_pool.name}/attribute.repository/${local.repository_owner}/${local.repository_name}"
            }
            ```

        1. ローカル環境から terraform を使用して、GitHub Actions 用サービスアカウントと Workload Identity を作成する
            ```sh
            #!/bin/sh
            #set -eu
            ROOT_DIR=${PWD}
            PROJECT_ID=my-project2-303004
            CONTAINER_NAME="terraform-gcp-container"

            #-----------------------------
            # terraform
            #-----------------------------
            cd terraform

            # terraform コンテナ起動
            docker-compose -f docker-compose.yml stop
            docker-compose -f docker-compose.yml up -d

            # GCP プロジェクト設定
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "gcloud config set project ${PROJECT_ID}"

            # terraform を初期化する。
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/iam && terraform init"

            # 作成したテンプレートファイルの定義内容を確認する
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/iam && terraform plan"

            # 定義を適用してインスタンスを作成する
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/iam && terraform apply"

            # terraform が作成したオブジェクトの内容を確認
            docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/iam && terraform show"
            ```
    
    - gcloud コマンドで作成する場合<br>
        ```sh
        #!/bin/sh
        #set -eu
        ROOT_DIR=${PWD}
        PROJECT_ID=my-project2-303004
        SERVICE_ACCOUNT_NAME=github-actions-sa-2
        WORKLOAD_IDENTITY_POOL_NAME=github-actions-pool-2
        WORKLOAD_IDENTITY_PROVIDER_NAME=github-actions-provider-2
        GITHUB_REPOSITORY_NAME=terraform-github-actions-argocd-gke-cicd-exercises

        # サービスアカウント作成権限のある個人アカウントに変更
        gcloud auth login
        gcloud config set project ${PROJECT_ID}

        # GKE 上のコンテナ内で kubectl コマンドの 　Pod を認識させるためのサービスアカウントを作成する
        if [ "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ; then
            gcloud iam service-accounts delete ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
        fi
        gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}

        # サービスアカウントに必要な権限を付与する (GCS 等様々なサービスを使用するのでオーナー権限で作成)
        gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/owner"
        #gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser" 

        # サービスアカウントの秘密鍵 (json) を生成する
        rm -rf ${ROOT_DIR}/.key
        mkdir -p ${ROOT_DIR}/.key
        gcloud iam service-accounts keys create ${ROOT_DIR}/.key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
        echo "GCP_SA_KEY (cat ${SERVICE_ACCOUNT_NAME}.json | base64) : "
        cat ${ROOT_DIR}/.key/${SERVICE_ACCOUNT_NAME}.json | base64

        # サービスアカウントの一時的な認証情報を作成できるようにするために、IAM Service Account Credentials APIを有効化
        gcloud services enable iamcredentials.googleapis.com --project ${PROJECT_ID}

        # Workload Identity プール（Workload Identityプールは外部IDとGoogle Cloudとの紐付けを設定したWorkload Identityプロバイダをグループ化し、管理するためのもの）を作成
        if [ "$(gcloud iam workload-identity-pools list --location global | grep ${WORKLOAD_IDENTITY_POOL_NAME})" ] ; then
            gcloud iam workload-identity-pools delete ${WORKLOAD_IDENTITY_POOL_NAME}
        fi
        gcloud iam workload-identity-pools create ${WORKLOAD_IDENTITY_POOL_NAME} --project="${PROJECT_ID}" --location="global"
        export WORKLOAD_IDENTITY_POOL_ID=$( gcloud iam workload-identity-pools describe "${WORKLOAD_IDENTITY_POOL_NAME}" --project="${PROJECT_ID}" --location="global" --format="value(name)" )
        echo "WORKLOAD_IDENTITY_POOL_ID : ${WORKLOAD_IDENTITY_POOL_ID}"

        # Workload Identity プールの中に Workload Identity プロバイダーを作成。Workload Identity プロバイダーと GitHub Actions のワークフローで指定する必要がある
        if [ "$(gcloud iam workload-identity-pools providers list --workload-identity-pool ${WORKLOAD_IDENTITY_POOL_NAME} --location global | grep ${WORKLOAD_IDENTITY_PROVIDER_NAME})" ] ; then
            gcloud iam workload-identity-pools providers delete ${WORKLOAD_IDENTITY_PROVIDER_NAME} --workload-identity-pool=${WORKLOAD_IDENTITY_POOL_NAME} --location="global"
        fi
        gcloud iam workload-identity-pools providers create-oidc ${WORKLOAD_IDENTITY_PROVIDER_NAME} \
            --project="${PROJECT_ID}" \
            --location="global" \
            --workload-identity-pool=${WORKLOAD_IDENTITY_POOL_NAME} \
            --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor,attribute.aud=assertion.aud" \
            --issuer-uri="https://token.actions.githubusercontent.com"

        # Workload Identity と GitHub Actions 用サービスアカウントの連携
        gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
            --project="${PROJECT_ID}" \
            --role="roles/iam.workloadIdentityUser" \
            --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPOSITORY_NAME}"

        # Workload Identity プロバイダの名前（projects/${PROJECT_ID}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME} の形式）を取得
        gcloud iam workload-identity-pools providers describe ${WORKLOAD_IDENTITY_PROVIDER_NAME} \
            --project="${PROJECT_ID}" \
            --location="global" \
            --workload-identity-pool=${WORKLOAD_IDENTITY_POOL_NAME} \
            --format='value(name)'
        ```

        ポイントは、以下の通り

        - workload identiry を使用することで、xxx


1. GKE クラスター用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
    ```python
    #-------------------------------
    # プロバイダー設定
    #-------------------------------
    provider "google" {
        project = "my-project2-303004"
        region  = "us-central1"
        zone = "us-central1-b"
    }

    #-------------------------------
    # 実行する Terraform 環境情報
    #-------------------------------
    terraform {
        # terraform のバージョン
        #  required_version = "~> 1.2.0"

        # バックエンドを GCS にする  
        backend "gcs" {
            bucket = "terraform-tf-states-bucket"
            prefix = "gcp/gke"
        }

        # プロバイダー情報
        required_providers {
            google = {
            version = "~> 4.13.0"   # Spot VM は、4.13.0 以上で使用可能
            }
        }
    }

    #-------------------------------
    # 各種 GCP サービス有効化
    #-------------------------------
    resource "google_project_service" "enable_iamcredentials" {
        service = "iamcredentials.googleapis.com"
    }

    resource "google_project_service" "enable_secretmanager" {
        service = "secretmanager.googleapis.com"
    }

    resource "google_project_service" "enable_cloudresourcemanager" {
        service = "cloudresourcemanager.googleapis.com"
    }

    #-------------------------------
    # GKE クラスタ
    #-------------------------------
    resource "google_container_cluster" "fast_api_terraform_cluster" {
        name     = "fast-api-terraform-cluster"
        location = "us-central1-b"
        #  node_locations = [   # マルチゾーンクラスタの場合
        #    "us-central1-a", "us-central1-b", "us-central1-f"
        #  ]

        remove_default_node_pool = true   # デフォルトのノードプールを削除する
        initial_node_count       = 1

        network = "default"

        #min_master_version = "1.21.10-gke.2000"
        #node_version       = "1.12.6-gke.7"

        #  master_auth {
        #    username = ""      # Kubernetes master (mster ノード?) にアクセスするときの basic 認証に使用するユーザ名
        #    password = ""      # Kubernetes master (mster ノード?) にアクセスするときの basic 認証に使用するパスワード

        #    client_certificate_config {
        #      issue_client_certificate = false
        #    }
        #  }
    }

    #-------------------------------
    # ノードプール
    #-------------------------------
    resource "google_container_node_pool" "fast_api_cpu_pool" {
        name       = "fast-api-cpu-pool"
        location   = "${google_container_cluster.fast_api_terraform_cluster.location}"
        #  node_locations = [   # マルチゾーンクラスタの場合
        #    "us-central1-a", "us-central1-b", "us-central1-f"
        #  ]
        cluster    = "${google_container_cluster.fast_api_terraform_cluster.name}"
        
        node_count = "1"
        autoscaling {
            min_node_count = 0
            max_node_count = 1
        }

        management {
            auto_repair = true    # true の場合ノードが自動修復される
            auto_upgrade = true   # true の場合ノードが自動更新される
        }

        node_config {
            machine_type = "n1-standard-1"
            #machine_type = "n1-standard-4"
            
            #preemptible  = false         # プリミティブ VM
            #spot = true                  # Spot VM

            # デフォルトサービスアカウントが利用できる Google API のスコープ
            oauth_scopes = [
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
            "https://www.googleapis.com/auth/service.management.readonly",
            "https://www.googleapis.com/auth/servicecontrol",
            "https://www.googleapis.com/auth/trace.append",
            ]

            # GPU ノードプールの場合
        #    guest_accelerator {
        #      type  = "nvidia-tesla-t4"
        #      count = 1
        #    }
        }
    }
    ```

    ポイントは、以下の通り

    - xxx

1. GitHub Actions の Workflow ファイルを作成する<br>

    1. workload identity を使用する場合<br>
        ```yaml
		# ワークフローの名前
		name: terrafform workflow for gke
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
					- '.github/workflows/terrafform-gke-workflow.yml'  
					- 'api/app.py'
					- 'api/Dockerfile'
					- 'terraform/gcp/gke/*.tf'
					- 'k8s/*.yml'
					- 'k8s/*.yaml'
			# main ブランチに PR された時にトリガー
			pull_request:
				branches:
					- main
				paths:
					- '.github/workflows/terrafform-gke-workflow.yml'  
					- 'api/app.py'
					- 'api/Dockerfile'
					- 'terraform/gcp/gke/*.tf'
					- 'k8s/*.yml'
					- 'k8s/*.yaml'
		#------------------------------------------------------
		# GitHub レポジトリへの権限設定
		#------------------------------------------------------
		permissions:
			contents: "read"
			id-token: "write"
			issues: "write"
			pull-requests: "write"                # Pull Request へのコメントを可能にする
		#------------------------------------------------------
		# job（ワークフローの中で実行される処理のひとまとまり）を定義
		#------------------------------------------------------
		jobs:
			terraform-gke-job:                    # job ID
				name: terraform job for gke         # job 名
				runs-on: ubuntu-latest              # ジョブを実行するマシン
				#-----------------------------
				# 環境変数の設定
				#-----------------------------
				env:
					GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}     # GitHub レポジトリへのアクセストークンを設定し、GitHub レポジトリへのコメントが可能にする / secrets は、github レポジトリの project の setting > secrets から登録する
					PROJECT_ID: my-project2-303004
					API_IMAGE_NAME: fast-api-image-gke
					CLUSTER_NAME: fast-api-terraform-cluster
					REGION: us-central1
					ZONE: us-central1-b
				#-----------------------------
				# ジョブの中で実行される一連のタスク
				#-----------------------------
				steps:
					#-----------------------------
					# ブランチを切る
					#-----------------------------
					- uses: actions/checkout@v3       # use タグで Actions（一連の定義済み処理）を指定 / actions/checkout@v2 : actions/v2 という GitHub リポジトリにあるアクションの v2 ブランチのコードを使用し、指定したリポジトリからソースコードを git checkout する
					#-----------------------------
					#  diff があるか確認
					#-----------------------------
					- name: Check diff for *.workflow files
						id: diff_workflow
						uses: technote-space/get-diff-action@v4.0.2
						with:
							PATTERNS: |
								'.github/workflows/terrafform-gke-workflow.yml'
					- name: Check diff for api
						id: diff_api
						uses: technote-space/get-diff-action@v4.0.2
						with:
							PATTERNS: |
								app/app.py
								app/Dockerfile
					- name: Check diff for *.tf files
						id: diff_tf
						uses: technote-space/get-diff-action@v4.0.2
						with:
							PATTERNS: |
								terraform/gcp/gke/*.tf
					- name: Check diff for k8s files
						id: diff_k8s
						uses: technote-space/get-diff-action@v4.0.2
						with:
							PATTERNS: |
								k8s/*.yml
								k8s/*.yaml
					#-----------------------------
					# GCP の認証処理
					#-----------------------------
		#      - name: "authenticate to gcp"
		#        uses: "google-github-actions/auth@v0.4.0"
		#        with:
		#          create_credentials_file: "true"
		#          activate_credentials_file: "true"
					#-----------------------------
					# gclould のインストール
					#-----------------------------
					- name: "install gcloud"
						uses: google-github-actions/setup-gcloud@v0.2.0
						with:
							project_id: ${{ env.PROJECT_ID }}
							service_account_key: ${{ secrets.GCP_SA_KEY }}
							export_default_credentials: true
					- name: gcloud auth
						run: gcloud auth configure-docker
					- name: gcloud config list
						run: gcloud config list
					#-----------------------------
					# docker image 作成 & GCR に push
					#-----------------------------
					- name: 'docker pull from gcr for api'
						if: steps.diff_api.outputs.diff
						run: "bash -c 'docker pull gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest || exit 0'"
					- name: 'docker build for api'
						if: steps.diff_api.outputs.diff
						run: 'docker build -t gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest --cache-from gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest -f api/Dockerfile .'
					- name: 'docker push to gcr for api'
						if: steps.diff_api.outputs.diff
						run: 'docker push gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest'
					#-----------------------------
					# terraform のインストール
					#-----------------------------
					- name: install terraform
						if: steps.diff_tf.outputs.diff
						uses: hashicorp/setup-terraform@v1
						with:
							terraform_version: 1.2.3
					#-----------------------------
					# GKE クラスターとノードプール作成
					#-----------------------------
					# terraform init
					- name: terraform init for gke
						if: steps.diff_tf.outputs.diff
						run: terraform -chdir="terraform/gcp/gke" init
					# terraform plan
					- name: terraform plan for gke
						if: steps.diff_tf.outputs.diff
						id: plan
						run: terraform -chdir="terraform/gcp/gke" plan -out workspace.plan
					# PR に terraform plan の内容を投稿
					- name: post PR terraform plan for gke
						if: always() && steps.diff_tf.outputs.diff && github.event_name == 'pull_request'
						uses: robburger/terraform-pr-commenter@v1
						with:
							commenter_type: plan
							commenter_input: ${{ format('{0}{1}', steps.plan.outputs.stdout, steps.plan.outputs.stderr) }}
							commenter_exitcode: ${{ steps.plan.outputs.exitcode }}
					# terraform apply
					- name: terraform apply for gke
						if: steps.diff_tf.outputs.diff && github.event_name == 'push'
						run: terraform -chdir="terraform/gcp/gke" apply workspace.plan
					#-----------------------------
					# 各種 k8s リソースを GKE にデプロイ
					#-----------------------------
					# kubectl コマンドのインストール
					- name: install kubectl
						if: steps.diff_k8s.outputs.diff
						uses: azure/setup-kubectl@v1
					# 作成したクラスタに切り替える
					- name: get-credentials for gke clusters
						if: steps.diff_k8s.outputs.diff
						run: gcloud container clusters get-credentials ${CLUSTER_NAME} --project ${PROJECT_ID} --region ${ZONE}
					# API の k8s リソースのデプロイ（k8s リソースの CD は ArgoCD で行うのでコメントアウト）
		#      - name: deploy k8s resources for api
		#        if: steps.diff_k8s.outputs.diff
		#        run: kubectl apply -f k8s/fast_api.yml
					# ArgoCD の k8s リソースのデプロイ
					- name: deploy k8s resources for argocd
						if: steps.diff_k8s.outputs.diff
						run: kubectl create namespace argocd || kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
        ```

    1. workload identity を使用しない場合<br>
        ```yaml
		# ワークフローの名前
		name: terrafform workflow for gke with workload identity
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
				- '.github/workflows/terrafform-gke-workflow_wi.yml'  
				- 'api/app.py'
				- 'api/Dockerfile'
				- 'terraform/gcp/gke/*.tf'
		# main ブランチに PR された時にトリガー
		pull_request:
			branches:
				- main
			paths:
				- '.github/workflows/terrafform-gke-workflow_wi.yml'  
				- 'api/app.py'
				- 'api/Dockerfile'
				- 'terraform/gcp/gke/*.tf'
		#------------------------------------------------------
		# GitHub レポジトリへの権限設定
		#------------------------------------------------------
		permissions:
			contents: "read"
			id-token: "write"
			issues: "write"
			pull-requests: "write"                # Pull Request へのコメントを可能にする
		#------------------------------------------------------
		# job（ワークフローの中で実行される処理のひとまとまり）を定義
		#------------------------------------------------------
		jobs:
			terraform-gke-job:                                          # job ID
				name: terraform job for gke with workload identity        # job 名
				runs-on: ubuntu-latest                                    # ジョブを実行するマシン
				#-----------------------------
				# 環境変数の設定
				#-----------------------------
				env:
					GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}     # GitHub レポジトリへのアクセストークンを設定し、GitHub レポジトリへのコメントが可能にする / secrets は、github レポジトリの project の setting > secrets から登録する
					PROJECT_ID: my-project2-303004
					SERVICE_ACCOUNT: github_actions_sa-2@my-project2-303004.iam.gserviceaccount.com                                                       # GitHub Actions 用のサービスアカウント
					WORKLOAD_IDENTITY_PROVIDER: "projects/85607256401/locations/global/workloadIdentityPools/github-actions-pool-2/providers/github-actions-provider-2"  # GitHub Actions 用のサービスアカウントと接続する Workload Identity プロバイダーの名前
					API_IMAGE_NAME: fast-api-image-gke
					CLUSTER_NAME: fast-api-terraform-cluster
					REGION: us-central1
					ZONE: us-central1-b
				#-----------------------------
				# ジョブの中で実行される一連のタスク
				#-----------------------------
				steps:
					#-----------------------------
					# ブランチを切る
					#-----------------------------
					- uses: actions/checkout@v3       # use タグで Actions（一連の定義済み処理）を指定 / actions/checkout@v2 : actions/v2 という GitHub リポジトリにあるアクションの v2 ブランチのコードを使用し、指定したリポジトリからソースコードを git checkout する
					#-----------------------------
					#  diff があるか確認
					#-----------------------------
					- name: Check diff for *.workflow files
					  id: diff_workflow
					  uses: technote-space/get-diff-action@v4.0.2
					  with:
					    PATTERNS: |
						  .github/workflows/terrafform-gke-workflow_wi.yml
					- name: Check diff for api
					  id: diff_api
					  uses: technote-space/get-diff-action@v4.0.2
					  with:
						PATTERNS: |
						  app/app.py
						  app/Dockerfile
					- name: Check diff for gke *.tf
					  id: diff_tf
					  uses: technote-space/get-diff-action@v4.0.2
					  with:
						PATTERNS: |
						  terraform/gcp/gke/*.tf
					#-----------------------------
					# GCP の認証処理
					#-----------------------------
					# Workload Identity を使用した認証
					- name: "authenticate to gcp"
					  uses: "google-github-actions/auth@v0.4.0"
					  with:
						workload_identity_provider: ${{ env.WORKLOAD_IDENTITY_PROVIDER }}
						service_account: ${{ env.SERVICE_ACCOUNT }}
						create_credentials_file: "true"
						activate_credentials_file: "true"
					- name: gcloud config list
					  run: gcloud config list
					#-----------------------------
					# gclould のインストール
					#-----------------------------
					- name: "install gcloud"
					  uses: google-github-actions/setup-gcloud@v0.2.0
					  with:
						project_id: ${{ env.PROJECT_ID }}
						workload_identity_provider: ${{ env.WORKLOAD_IDENTITY_PROVIDER }}
						service_account: ${{ env.SERVICE_ACCOUNT }}
						create_credentials_file: 'true'
					- name: gcloud config list
					  run: gcloud config list
					- name: gcloud auth
					  run: gcloud auth configure-docker
					- name: gcloud config list
					  run: gcloud config list
					#-----------------------------
					# docker image 作成 & GCR に push
					#-----------------------------
					- name: 'docker pull from gcr for api'
					  if: steps.diff_api.outputs.diff
					  run: "bash -c 'docker pull gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest || exit 0'"
					- name: 'docker build for api'
					  if: steps.diff_api.outputs.diff
					  run: 'docker build -t gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest --cache-from gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest -f api/Dockerfile .'
					- name: 'docker push to gcr for api'
					  if: steps.diff_api.outputs.diff
					  run: 'docker push gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest'
					#-----------------------------
					# terraform のインストール
					#-----------------------------
					- name: install terraform
					  if: steps.diff_tf.outputs.diff
					  uses: hashicorp/setup-terraform@v1
					  with:
						terraform_version: 1.2.3
					#-----------------------------
					# GKE クラスターとノードプール作成
					#-----------------------------
					# terraform init
					- name: terraform init
					  if: steps.diff_tf.outputs.diff
					  run: terraform -chdir="terraform/gcp/gke" init
					# terraform plan
					- name: terraform plan
					  if: steps.diff_tf.outputs.diff
					  id: plan
					  run: terraform -chdir="terraform/gcp/gke" plan -out workspace.plan
					# PR に terraform plan の内容を投稿
					- name: post PR terraform plan
					  if: always() && steps.diff_tf.outputs.diff && github.event_name == 'pull_request'
					  uses: robburger/terraform-pr-commenter@v1
					  with:
						commenter_type: plan
						commenter_input: ${{ format('{0}{1}', steps.plan.outputs.stdout, steps.plan.outputs.stderr) }}
						commenter_exitcode: ${{ steps.plan.outputs.exitcode }}
					# terraform apply
					- name: terraform apply
					  if: steps.diff_tf.outputs.diff && github.event_name == 'push'
					  run: terraform -chdir="terraform/gcp/gke" apply workspace.plan
					#-----------------------------
					# 各種 k8s リソースを GKE にデプロイ
					#-----------------------------
					# kubectl コマンドのインストール
					- name: install kubectl
					  if: steps.diff_k8s.outputs.diff
					  uses: azure/setup-kubectl@v1
					# 作成したクラスタに切り替える
					- name: get-credentials for gke clusters
					  if: steps.diff_k8s.outputs.diff
					  run: gcloud container clusters get-credentials ${CLUSTER_NAME} --project ${PROJECT_ID} --region ${ZONE}
					# API の k8s リソースのデプロイ
					- name: deploy k8s resources for api
					  if: steps.diff_k8s.outputs.diff
					  run: kubectl apply -f k8s/fast_api.yml
					# ArgoCD の k8s リソースのデプロイ
					- name: deploy k8s resources for argocd
					  if: steps.diff_k8s.outputs.diff
					  run: kubectl create namespace argocd || kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
        ```

    ポイントは、以下の通り

    - GCP の IAM ユーザーの認証情報を設定<br>
        定義済み action `google-github-actions/auth` を使用して、GCP の認証処理を行っている。

        - GitHub Actions 用のサービスアカウントの json キーを設定する場合<br>
            xxx

        - GitHub Actions 用のサービスアカウントに Workload Identity 連携を行う場合<br> 
            xxx

    - docker image の GCR への push

    - terraffom コマンドで GKE クラスタ & ノードプール作成

    - kubectl の設定

1. ArgoCD CLI をインストールする<br>
    - MacOS の場合<br>    
        ```sh
        brew install argocd
        ```

    - Linux の場合<br>
        ```sh
        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /usr/local/bin/argocd
        ```

1. ArgoCD API Server のドメインを取得する<br>
    ArgoCD API Server の Service を `"type": "LoadBalancer"` に変更して、`EXTERNAL-IP` を発行し、ArgoCD API Server のドメインを取得する

    ```sh
    kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
    ARGOCD_SERVER_DOMAIN=`kubectl describe service argocd-server | grep "LoadBalancer Ingress" | awk '{print $3}'`
    ```

1. ArgoCD にログインする<br>
    ```sh
    argocd login ${ARGOCD_SERVER_DOMAIN} --name admin --password ${ARGOCD_PASSWARD}
    ```
    - `--name` : ログインユーザー名。デフォルトでは `admin`
    - `--password` : ログインパスワード。デフォルトでは、`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d` で取得可能

    > 初期ログインのアカウントは、作成した ArgoCD k8s リソースの Secret リソースに記載されている

1. ArgoCD コンソール画面にブラウザアクセスする<br>
    ArgoCD の k8s リソースデプロイ時に作成される ArgoCD の Service (ArgoCD API Server) にアクセスすることで、ArgoCD のコンソール画面に移動することができる

    ```sh
    open "https://${ARGOCD_SERVER_DOMAIN}"
    ```

1. クラスター名を表示する<br>
    ```sh
    argocd cluster add
    ```

1. ArgoCD で管理するクラスターを選択し設定する<br>
    ```sh
    argocd cluster add ${K8S_CLUSTER_NAME}
    ```
    - `K8S_CLUSTER_NAME` : `argocd cluster add` コマンドで表示されるクラスター名

1. ArgoCD アプリを作成する<br>
    ArgoCD アプリを作成し、ArgoCD で管理したい GitHub レポジトリの k8s マニフェストファイルを関連付ける。

    - CLI で行う場合<br>
        ```sh
        argocd app create ${ARGOCD_APP_NAME} \
            --repo ${REPOSITORY_URL} \
            --path ${K8S_MANIFESTS_DIR} \
            --dest-server https://kubernetes.default.svc \
            --dest-namespace default \
            --sync-policy automated
        ```
        - `${ARGOCD_APP_NAME}` : ArgoCD アプリ名（プロジェクト名） 
        - `${REPOSITORY_URL}` : ArgoCD で管理する GitHub レポジトリ
        - `${K8S_MANIFESTS_DIR}` : ArgoCD で管理する GitHub の k8s マニフェストファイルのフォルダーを設定

    - k8s マニフェストで行う場合<br>
        1. k8s マニフェストを作成する<br>
            ArgoCD アプリの k8s マニフェストを作成する
            ```yaml
            apiVersion: argoproj.io/v1alpha1
            kind: Application
            metadata:
              name: argocd-config
              namespace: argocd
            spec:
              project: default
              source:
                repoURL: https://github.com/Yagami360/terraform-github-actions-argocd-gke-cicd-exercises.git
                targetRevision: main
                path: k8s
              destination:
                server: https://kubernetes.default.svc
                namespace: argocd
              syncPolicy:
                automated:
                  prune: true
                  selfHeal: true
            ```

        1. k8s マニフェストデプロイする<br>
            作成した ArgoCD アプリの k8s マニフェストをデプロイすることで、ArgoCD アプリが自動的に作成される
            ```sh
            kubectl apply -f k8s/argocd-app.yml
            ```

    > 実際の運用では、ArgoCD アプリの作成は、後者の k8s マニフェストで行うことが多い。後者の方法では複数の ArgoCD アプリをまとめて管理できるなどのメリットがある

1. ArgoCD と GitHub レポジトリの同期を行う<br>
    作成した ArgoCD アプリに対して、ArgoCD で管理したい k8s マニフェストファイルと Git リポジトリーの同期を行う
    ```sh
    argocd app sync ${ARGOCD_APP_NAME}
    ```

    ArgoCD と GitHub レポジトリの同期が成功している場合は、ArgoCD のコンソール画面は、以下のようになる

    xxx

1. Web-API のコード or GKE の `*.tf` ファイル or k8s マニフェストを修正する<br>
    `api/` ディレクトリ以下にある Web-API のコードを修正する。又は、GKE に対しての tf ファイル `terraform/gcp/gke/main.tf` を修正する
    又は、`k8s/` ディレクトリ以下にある Web-API の k8s マニフェストを修正する

1. Pull Request を発行する。<br>
    GitHub レポジトリ上で main ブランチに対しての [PR](https://github.com/Yagami360/terraform-github-actions-aws-cicd-exercises/pulls) を出す。

1. PR の内容を `main` ブランチに merge し、GKE 上の Web-API に対しての CI/CD を行う。<br>
    PR の内容に問題なければ、`main` ブランチに merge する。
    merge 処理後、`.github/workflows/terrafform-gke-workflow.yml` で定義したワークフローが実行され 、GKE 上の Web-API に対しての CI/CD が自動的に行われる。

1. [GitHub リポジトリの Actions タブ](https://github.com/Yagami360/terraform-github-actions-aws-cicd-exercises/actions)から、実行されたワークフローのログを確認する
    

1. GKE 上の Web-API に対して、リクエスト処理を行う<br>
    ```sh
    sh resuest_api.sh
    ```

## ■ 参考サイト

- GitHub Actions 上での GCP の認証
    - workload identity を使用する場合
        - https://dev.classmethod.jp/articles/google-cloud-auth-with-workload-identity/

    - workload identity を使用しない場合
        - https://zenn.dev/rince/scraps/4e3cbba78d2cd1
        - https://albatrosary.hateblo.jp/entry/2020/06/22/173731

- terraform を使用した GKE クラスタとノードプールの作成
    - https://qiita.com/kawakawaryuryu/items/c74a7a90a8b4e7e01c1f

- ArgoCD
    - https://github.com/Yagami360/argocd-exercises
