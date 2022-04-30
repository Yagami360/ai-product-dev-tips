#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004

REGION=us-central1
ZONE=us-central1-b
CPU_TYPE=n1-standard-1
DISK_SIZE=64
CLUSTER_NAME=fast-api-cluster
NUM_NODES=1
MIN_NODES=1
MAX_NODES=1
ENABLE_BUILD=1

SERVICE_ACCOUNT_NAME=cloud-armor-account
SECURITY_POLICY_NAME=clients-policy

HOST=0.0.0.0
PORT=5000

RATE_LIMIT_THRESHOLD_COUNT=100

#-----------------------------------------------
# GCP 環境のデフォルト値の設定
#-----------------------------------------------
gcloud config set project ${PROJECT_ID}
gcloud config list

#-----------------------------------------------
# Google Cloud Armor 用のサービスアカウントを作成する
#-----------------------------------------------
if [ ! -e "api/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
    # サービスアカウント作成権限のある個人アカウントに変更
    gcloud auth login

    # サービスアカウントを作成する
    if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
        gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
    fi

    # サービスアカウントに必要な権限（Google Cloud Armor セキュリティ ポリシーの IAM 権限）を付与する
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/compute.securityAdmin"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/compute.networkAdmin"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"

    # サービスアカウントの秘密鍵 (json) を生成する
    if [ ! -e "api/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
        mkdir -p api/key
        gcloud iam service-accounts keys create api/key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    fi

    # 作成した json 鍵を環境変数に反映
    #export GOOGLE_APPLICATION_CREDENTIALS="key/{SERVICE_ACCOUNT_NAME}.json"
    #gcloud auth activate-service-account SERVICEACCOUNTNAME@{PROJECT_ID}.iam.gserviceaccount.com --key-file ROOTDIR/api/key/{SERVICE_ACCOUNT_NAME}.json
    #gcloud auth list
fi

#-----------------------------------------------
# GKE 版 API を構築する
#-----------------------------------------------
# docker image を GCP の Container Registry にアップロード
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    gcloud builds submit --config cloudbuild.yml --timeout 3600
fi

# クラスタを作成
if [ "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ; then
    set +e
    gcloud container clusters delete ${CLUSTER_NAME} --region ${ZONE}
    set -e
fi

if [ ! "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ; then
  gcloud container clusters create ${CLUSTER_NAME} \
      --region ${ZONE} \
      --num-nodes ${NUM_NODES} \
      --machine-type ${CPU_TYPE} \
      --disk-size ${DISK_SIZE} \
      --enable-autoscaling --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
      --scopes=gke-default,logging-write
fi

# 作成したクラスタに切り替える
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${ZONE} --project ${PROJECT_ID}

# k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）の作成
kubectl apply -f k8s/fast_api.yml


#-----------------------------------------------
# セキュリティポリシーの作成
#-----------------------------------------------
# GKE のロードバランサーに適用するためのセキュリティポリシーを作成
gcloud compute security-policies create ${SECURITY_POLICY_NAME} --description "policy for external users"

# セキュリティーポリシーのルール（RateLimit 制限）を作成する
gcloud compute security-policies rules create 10 \
    --security-policy sec-policy    \
    --src-ip-ranges=="0.0.0.0/1"    \
    --action=throttle               \
    --rate-limit-threshold-count=${RATE_LIMIT_THRESHOLD_COUNT}  \
    --rate-limit-threshold-interval-sec=60  \
    --conform-action=allow          \
    --exceed-action=deny-429        \
    --enforce-on-key=IP

#-----------------------------------------------
# API を実行する
#-----------------------------------------------
<<COMMENTOUT
# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# health check
echo "[GET method] ヘルスチェック\n"
curl http://${HOST}:${PORT}/health
echo "\n"

# metadata 取得
echo "[GET method] metadata 取得\n"
curl http://${HOST}:${PORT}/metadata
echo "\n"

# GET method でのリクエスト処理
echo "[GET method] パスパラメーターで指定\n"
curl http://${HOST}:${PORT}/users_name/0
curl http://${HOST}:${PORT}/users_name/1
curl http://${HOST}:${PORT}/users_name/2
echo "\n"

echo "[GET method] クエリパラメーターで指定\n"
curl http://${HOST}:${PORT}/users_name/?users_id=0
curl http://${HOST}:${PORT}/users_name/?users_id=1
curl http://${HOST}:${PORT}/users_name/?users_id=2
echo "\n"

echo "[GET method] パスパラメーター & クエリパラメーターで指定\n"
curl http://${HOST}:${PORT}/users/name?users_id=0
curl http://${HOST}:${PORT}/users/age?users_id=0
curl http://${HOST}:${PORT}/users/name?users_id=1
curl http://${HOST}:${PORT}/users/age?users_id=1
curl http://${HOST}:${PORT}/users/name?users_id=2
curl http://${HOST}:${PORT}/users/age?users_id=2
echo "\n"

# POST method でのリクエスト処理
echo "[POST method] ユーザー追加\n"
curl -X POST -H "Content-Type: application/json" \
    -d '{"id":4, "name":"user4", "age":"100"}' \
    http://${HOST}:${PORT}/add_users/

echo "\n"

docker-compose logs --tail 50
COMMENTOUT