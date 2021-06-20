# Fluentd を使用して GCE 上の Web-API でのログデータを Cloud logging に転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + GKE での構成）

## ■ 方法

1. Cloud logging でロギングを行うためのサービスアカウント権限を設定する<br>
	1. Cloud logging でロギングを行うためのサービスアカウントを作成する
		```sh
		# サービスアカウントの作成
		$ gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
		```
	1. 作成したサービスアカウントにロギング権限を付与する<br>
		[ロギング] > [ログ書き込み]　と [モニタリング] > [モニタリング指標の書き込み] の権限を付与する
		```sh
		$ gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/logging.logWriter"
		$ gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/monitoring.metricWriter"
		```
	1. 作成したサービスアカウントの秘密鍵 (json) を生成する<br>
		```sh
		$ mkdir -p key
		$ gcloud iam service-accounts keys create key/key.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
		```
	1. 作成した json 鍵を環境変数に反映する<br>
		```sh
		$ export GOOGLE_APPLICATION_CREDENTIALS=${JSON_KEY_FILE}
		```
	1. 作成したサービスアカウントを GCE のサービスアカウントに紐づける？
		> GKE クラスタの場合はどうする？

1. リクエスト処理を行う<br>
1. ログデータを確認する<br>


## ■ 参考サイト
- https://qiita.com/ys_nishida/items/8b5274d8f3ec740ffa16