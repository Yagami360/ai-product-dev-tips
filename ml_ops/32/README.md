# Fluentd を使用して GKE 上の Web-API でのログデータを Cloud logging に転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + GKE での構成）


## ■ 方法

1. Web-API の設定<br>
	1. Web-API のコードを作成する
	1. GKE にデプロイする docker image ための Dockerfile を作成する

1. k8s の各種設定ファイルの作成<br>
	1. Web API と fluentd サーバーのデプロイメント定義ファイルを作成する<br>
		```yml
		```

		> ポイントは、以下の通り<br>
		> - fluentd サーバーでの Web-API からのログデータの転送を可能にするためには、Web-API のコンテナと fluentd サーバーのコンテナ間でディスクを共有する必要があるので、k8s のサイドカーを使って、Web-API のコンテナと fluentd サーバーのコンテナ間でディスクを共有するようにする
		> - Fluentd を使用してログデータを Cloud logging に転送するには、`fluent-plugin-google-cloud` をインストールした Fluentd の Docker image が必要になるので、`fluent/fluentd` ではなく `k8s.gcr.io/fluentd-gcp` の docker image を使用する

	1. fluentd サーバーの設定のための Config Map 定義ファイルを作成する<br>
		k8s の場合は、fluentd サーバーの設定ファイル `fluent.conf` を ConfigMap で定義する方法が最適である
		```yml
		```

		> Cloud logging への転送を行うために、`type google_cloud` での match ディレクティブを追加している点がポイント

	1. Web API のサービス定義ファイルを作成する<br>

	1. Web-API のビルド構築ファイルを作成する<br>

1. GKE クラスタの構築<br>
	1. ビルド構成ファイルを元に docker image を ビルドし、Google Container Registry に push する<br>
	1. GKE クラスタを作成する<br>
	1. Pod を作成する<br>
	1. ConfigMap を作成する<br>
	1. サービスを作成する<br>

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
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/load_test_pattern
- https://qiita.com/ys_nishida/items/8b5274d8f3ec740ffa16