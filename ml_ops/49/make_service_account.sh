#!/bin/sh
#set -eu
ROOT_DIR=${PWD}
PROJECT_ID=my-project2-303004
SERVICE_ACCOUNT_NAME=cloud-monitoring

if [ ! -e "${ROOT_DIR}/api/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
    # サービスアカウント作成権限のある個人アカウントに変更
    gcloud auth login

    # GKE 上のコンテナ内で kubectl コマンドの 　Pod を認識させるためのサービスアカウントを作成する
    if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
        gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
    fi

    # サービスアカウントに必要な権限を付与する
    #gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/owner"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/monitoring.admin"

    # サービスアカウントの秘密鍵 (json) を生成する
    if [ ! -e "${ROOT_DIR}/api/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
        mkdir -p ${ROOT_DIR}/api/key
        gcloud iam service-accounts keys create ${ROOT_DIR}/api/key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    fi

    # 作成した json 鍵を環境変数に反映
    #export GOOGLE_APPLICATION_CREDENTIALS="ROOTDIR/key/{SERVICE_ACCOUNT_NAME}.json"
    #gcloud auth activate-service-account SERVICEACCOUNTNAME@{PROJECT_ID}.iam.gserviceaccount.com --key-file ROOTDIR/key/{SERVICE_ACCOUNT_NAME}.json
    #gcloud auth list
fi
