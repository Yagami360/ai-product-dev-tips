#!/bin/sh
#set -eu
ROOT_DIR=${PWD}
CONTAINER_NAME="terraform-gcp-container"
PROJECT_ID=my-project2-303004
REGION=us-central1
ZONE=us-central1-b
CLUSTER_NAME=fast-api-terraform-cluster
API_IMAGE_NAME="fast-api-image-gke"

#-----------------------------
# OS判定
#-----------------------------
if [ "$(uname)" = 'Darwin' ]; then
  OS='Mac'
  echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
  OS='Linux'
  echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then                                                                                           
  OS='Cygwin'
  echo "Your platform is Cygwin."  
else
  echo "Your platform ($(uname -a)) is not supported."
  exit 1
fi

#-----------------------------
# gcloud コマンドをインストールする
#-----------------------------
gcloud -v &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        # Cloud SDKのパッケージをダウンロード
        cd ${HOME}
        curl -OL https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-308.0.0-darwin-x86_64.tar.gz
        tar -zxvf google-cloud-sdk-308.0.0-darwin-x86_64.tar.gz
        rm -rf google-cloud-sdk-308.0.0-darwin-x86_64.tar.gz

        # Cloud SDKのパスを通す
        ./google-cloud-sdk/install.sh
        source ~/.zshrc

        # Cloud SDK の初期化
        gcloud init
        cd ${ROOT_DIR}
    fi
fi
echo "gcloud version : `gcloud -v`"

# デフォルト値の設定
#sudo gcloud components update
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config list

#-----------------------------
# kubectl コマンドをインストールする
#-----------------------------
kubectl version --client &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        # 最新版取得
        curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl

        # Ver指定(ex:1.40)
        curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.14.0/bin/darwin/amd64/kubectl

        # アクセス権限付与
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
    elif [ ${OS} = "Linux" ] ; then
        curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"        
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
    fi
fi

echo "kubectl version : `kubectl version`"

#-----------------------------
# Kustomize のインストール
#-----------------------------
kustomize version --client &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        brew install kustomize
    elif [ ${OS} = "Linux" ] ; then
        curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        kustomize completion bash >> ~/.bashrc
    fi
fi

echo "kustomize version : `argokustomizecd version`"

#-----------------------------
# terraform コンテナ起動
#-----------------------------
cd terraform

# terraform コンテナ起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

# GCP プロジェクト設定
docker exec -it ${CONTAINER_NAME} /bin/sh -c "gcloud config set project ${PROJECT_ID}"

#-----------------------------
# docker image を GCR に push
#-----------------------------
cd ${ROOT_DIR}

# dev
bash -c 'docker pull gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}-dev:latest || exit 0'
docker build -t gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}-dev:latest --cache-from gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}-dev:latest -f api/Dockerfile .
docker push gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}-dev:latest

# prod
bash -c 'docker pull gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest || exit 0'
docker build -t gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest --cache-from gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest -f api/Dockerfile .
docker push gcr.io/${PROJECT_ID}/${API_IMAGE_NAME}:latest

#-----------------------------
# GCS パケットを作成する
#-----------------------------
# terraform を初期化する。
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform init"

# 作成したテンプレートファイルの定義内容を確認する
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform plan"

# 定義を適用してインスタンスを作成する
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform apply -auto-approve"

# terraform が作成したオブジェクトの内容を確認
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gcs && terraform show"

#-----------------------------
# GKE クラスタとノードプールを作成する
#-----------------------------
# terraform を初期化する。
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gke && terraform init"

# 作成したテンプレートファイルの定義内容を確認する
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gke && terraform plan"

# 定義を適用してインスタンスを作成する
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gke && terraform apply -auto-approve"

# terraform が作成したオブジェクトの内容を確認
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd gcp/gke && terraform show"

#-----------------------------
# 各種 k8s リソースをデプロイする
#-----------------------------
cd ${ROOT_DIR}
# 作成したクラスタに切り替える
gcloud container clusters get-credentials ${CLUSTER_NAME} --project ${PROJECT_ID} --region ${ZONE}

# 環境別の k8s マニフェストの確認
echo -e "------------------\nk8s manifest [base]\n------------------\n"
echo "`kustomize build k8s/base`"
echo -e "------------------\nk8s manifest [dev]\n------------------\n"
echo "`kustomize build k8s/dev`"
echo -e "------------------\nk8s manifest [prod]\n------------------\n"
echo "`kustomize build k8s/prod`"

# 環境別に API の k8s リソースのデプロイ
kubectl create namespace dev && kubectl apply -k k8s/dev
kubectl create namespace prod && kubectl apply -k k8s/prod
