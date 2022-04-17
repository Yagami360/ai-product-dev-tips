#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
SERVICE_ACCOUNT_NAME=vertex-ai-account
GCS_BUCKET_NAME=vertex-ai-bucket-360


# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config list

#-----------------------------------------------
# Vertex AI and Cloud Storage API を有効化する
#-----------------------------------------------

#-----------------------------------------------
# Vertex Pipelines 用のサービスアカウントを作成する
#-----------------------------------------------
if [ ! -e "key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
    # サービスアカウント作成権限のある個人アカウントに変更
    gcloud auth login

    # サービスアカウントを作成する
    if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
        gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
    fi

    # サービスアカウントに必要な権限を付与する
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/aiplatform.user"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"

    # サービスアカウントの秘密鍵 (json) を生成する
    if [ ! -e "key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
        mkdir -p key
        gcloud iam service-accounts keys create key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    fi

    # 作成した json 鍵を環境変数に反映
    #export GOOGLE_APPLICATION_CREDENTIALS="key/{SERVICE_ACCOUNT_NAME}.json"
    #gcloud auth activate-service-account SERVICEACCOUNTNAME@{PROJECT_ID}.iam.gserviceaccount.com --key-file ROOTDIR/api/key/{SERVICE_ACCOUNT_NAME}.json
    #gcloud auth list
fi

#-----------------------------------------------
# Vertex AI Pipelines 用の GCS パケットを作成する
#-----------------------------------------------
if [ ! "$(gsutil list | grep "gs://${GCS_BUCKET_NAME}/")" ] ;then
    # GCS パケットを作成する
    #gsutil rb gs://${GCS_BUCKET_NAME}/
    gsutil mb -p ${PROJECT_ID} gs://${GCS_BUCKET_NAME}/

    # Vertex AI 用サービスアカウントに作成した GCS パケットへの読み書きアクセス権限を付与
    gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectCreator,objectViewer gs://${GCS_BUCKET_NAME}
    gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectViewer gs://${GCS_BUCKET_NAME}

    # GCE デフォルトサービスアカウントに、GCS パケットへの読み書きアクセス権限を付与
    gsutil iam ch 85607256401-compute@developer.gserviceaccount.com:roles/storage.objectCreator,objectViewer gs://${GCS_BUCKET_NAME}
    gsutil iam ch 85607256401-compute@developer.gserviceaccount.com:roles/storage.objectViewer gs://${GCS_BUCKET_NAME}
fi

#-----------------------------------------------
# 各種 SDK のインストール
#-----------------------------------------------
# Kubeflow Pipelines SDK をインストールする
if [ ! "$(pip3 list | grep "kfp")" ] ; then
    #pip install kfp
    pip3 install kfp
fi

# Vertex AI SDK をインストールする
if [ ! "$(pip3 list | grep "google-cloud-aiplatform")" ] ; then
    pip3 install google-cloud-aiplatform
fi

# Kubeflow の Google Cloud Pipeline Components をインストール
if [ ! "$(pip3 list | grep "google-cloud-pipeline-components")" ] ; then
    pip3 install -U google-cloud-pipeline-components
fi

pip3 list

#-----------------------------------------------
# パイプラインの JSON ファイルを作成&送信し、パイプラインを実行する
#-----------------------------------------------
cd pipelines
python3 pipeline.py --project_id ${PROJECT_ID} --pipeline_root_path "gs://${GCS_BUCKET_NAME}/"

#-----------------------------------------------
# モデルのエンドポイントを呼び出し、推論処理を行う
#-----------------------------------------------
# パイプラインの実行完了待ち

# curl コマンドでエンドポイントをたたく
