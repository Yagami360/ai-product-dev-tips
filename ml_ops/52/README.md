# 【Datadog】GCE の各種メトリクスとログデータを Datadog で表示する 

<img width="929" alt="image" src="https://user-images.githubusercontent.com/25688193/159199555-ea76ea74-74fb-4841-9e9a-e62eee373508.png">

## ■ 方法

1. [Datadog サイト](https://www.datadoghq.com/ja/) から「無料トライアルを開始」ボタンをクリックして、ユーザー登録を行う<br>

	> 無料トライアルの場合でも、会社名の記載が必要であることに注意

	> Google アカウントでサインインすれば、会社名の記入不要でおすすめ

1. 「Your Stack」に GCP を追加し、「Next」ボタンをクリックする<br>
    <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159150523-c5497c0b-68fd-45ce-aed3-dd9fd88e4460.png"><br>
    <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159150558-65e53cc6-3102-43bb-b479-fd254ab69810.png"><br>

1. GCE インスタンスを作成する<br>
	今回は、Debian をベースイメージとした GCE インスタンスを作成する
	ファイアウォール設定で、Datadog Agent が通信を行うためのポート `10516` を開放させておく。

1. Datadog Agent を GCE インスタンスにインストールする<br>
	Debian をベースイメージとした GCE インスタンスの場合は、Debian を選択後、画面右側に赤枠に表示されるインストールコマンドをコピペして、GCE インスタンス（Debian）に Datadog Agent をインストールする

	```sh
	DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=e22df3d0958810817576e2d94c0bedfb DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
	```

	<img width="1197" alt="image" src="https://user-images.githubusercontent.com/25688193/159151213-ae6bd767-d8d1-4aa8-84ed-7789c516b94e.png">

	> GCE インスタンスのポート `10514` または `10516` を開放していない場合は、`/etc/datadog-agent/datadog.yaml` に次の設定を追加することで、http 通信で Datadog Agent がログを転送するよう構成することができる。（`datadog.yaml` は、sudo権限のファイルなので、`sudo vi /etc/datadog-agent/datadog.yaml` などで編集可能）
	> ```yaml
	> logs_config:
  	>     use_http: true
	> ```
	> 尚、修正した `datadog.yaml` を有効化するためには、`sudo service datadog-agent restart` コマンドで Datadog Agent を再起動する必要があることに注意

	- Datadog Agent のステータス確認コマンド
		```sh
		$ sudo service datadog-agent status
		```

	- Datadog Agent の再起動コマンド
		```sh
		$ sudo service datadog-agent restart
		```

1. Datadog　から各種 GCP サービスにアクセスするためのサービスアカウントを作成する。<br>
    Datadog　から各種 GCP サービスにアクセスするためのサービスアカウントを作成し、サービスアカウントの json 鍵を作成する。このとき、サービスアカウントには、「Compute 閲覧者」、「モニタリング閲覧者」、「クラウドアセット閲覧者」の権限を付与する

	- CLI で行う場合<br>
		```sh
		#!/bin/sh
		#set -eu
		ROOT_DIR=${PWD}
		PROJECT_ID=my-project2-303004
		SERVICE_ACCOUNT_NAME=datadog

		if [ ! -e "${ROOT_DIR}/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
			# サービスアカウント作成権限のある個人アカウントに変更
			gcloud auth login

			# GKE 上のコンテナ内で kubectl コマンドの 　Pod を認識させるためのサービスアカウントを作成する
			if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
				gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
			fi

			# サービスアカウントに必要な権限を付与する
			gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/compute.viewer"
			gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/monitoring.viewer"
			gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/cloudasset.viewer"

			# サービスアカウントの秘密鍵 (json) を生成する
			if [ ! -e "${ROOT_DIR}/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
				mkdir -p ${ROOT_DIR}/key
				gcloud iam service-accounts keys create ${ROOT_DIR}/key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
			fi
		fi	
		```

	- GUI で行う場合<br>
		xxx

1. DataDog の Welcome ページにて、作成したサービスアカウントの json 鍵をアップロードする<br>
	Datadog のコンソール画面の「Cloud Providers」から GCP の「Add」ボタンをクリックし、作成したサービスアカウントの json 鍵をアップロードする

	<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159151983-12183737-2f3b-41ec-8f40-abbc91ef631a.png"><br>
	<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159151990-3c34e5af-ed63-42f1-9072-72b7f1fc9408.png"><br>

	> これらの作業を CLI で自動化できないのか？ Datadog の CLI は存在しないのか？

1. Datadog 左メニューの「Logs」→「Getting Started」→「Cloud」→「Google Cloud Platform」をクリックして選択すると、下記画像のページが出るので、記載された内容を実施していく<br>

	<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159152104-ecc449fd-e144-4f0d-8d2a-3b802c695e2f.png"><br>
	<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159152113-91ccf9c4-6554-48ad-8740-d04191d96efc.png"><br>


	1. GCE のメトリクスやログデータを Datadog に転送するための Cloud Pub/Sub の作成を行い、PUSH 型のサブスクリプションを作成する<br>

		> このときの PUSH 型のサブスクリプションのエンドポイント URL には、先の画面に表示されている `https://gcp-intake.logs.datadoghq.com/v1/input/${DATADOG_API_KEY}を入力する`

		> Cloud Pub/Sub については、「[【GCP】Google Cloud Pub/Sub の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/18)」を参考のこと

		- CLI で行う場合<br>
			```sh
			#!/bin/sh
			set -eu

			PROJECT_ID=my-project2-303004
			TOPIC_NAME=export-logs-to-datadog
			SUBSCRIPTION_NAME=datadog-sub
			DATADOG_API_KEY=e22df3d0958810817576e2d94c0bedfb

			# Cloud Pub/Sub 作成権限のある個人アカウントに変更
			#gcloud auth login

			# API を有効化する

			# トピックを作成する
			if [ ! "$(gcloud pubsub topics list | grep "name: projects/${PROJECT_ID}/topics/${TOPIC_NAME}")" ] ;then
				gcloud pubsub topics create ${TOPIC_NAME}
			fi

			gcloud pubsub topics list

			# PUSH 型のサブスクリプション（受信側）を作成する
			if [ ! "$(gcloud pubsub subscriptions list | grep "name: projects/${PROJECT_ID}/subscriptions/${SUBSCRIPTION_NAME}")" ] ;then
				gcloud pubsub subscriptions create ${SUBSCRIPTION_NAME} \
					--topic ${TOPIC_NAME} \
					--push-endpoint https://gcp-intake.logs.datadoghq.com/v1/input/${DATADOG_API_KEY} \
					--ack-deadline 10
			fi

			gcloud pubsub subscriptions list
			```

		- GUI で行う場合<br>
			xxx

	1. Cloud Logging（旧 StackDriver）経由で Cloud Pub/Sub へログを転送するための設定（ログルーティングとシンク）を行う<br>

		> Cloud Logging におけるログルーティングとシンクについては、https://blog.g-gen.co.jp/entry/cloud-logging-explained を参考のこと

		- CLI で行う場合<br>
			```sh
			#!/bin/sh
			set -eu

			PROJECT_ID=my-project2-303004
			SINK_NAME=export-logs-to-datadog-sink
			TOPIC_NAME=export-logs-to-datadog

			# シンク作成権限のある個人アカウントに変更
			#gcloud auth login

			# API を有効化する

			# ClloudLogging の「ログルータ」からシンクを作成する
			gcloud logging sinks create \
				${SINK_NAME} \
				pubsub.googleapis.com/projects/${PROJECT_ID}/topics/${TOPIC_NAME}

			gcloud logging sinks list
			```

		- GUI で行う場合<br>
			xxx

1. Datadog Dashboard から GCP の各種メトリクスを確認する<br>
	<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159153255-583316e5-cb1f-43d0-b26e-437748f9ca98.png">

	- GCP のメトリクス画面<br>
		<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159153319-15aa0b5d-2fc6-4152-8e65-15087aa24739.png">

	- GCE のメトリクス画面<br>
		<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/159153358-d6eb58fd-76ea-4dbf-8101-18f48140cc59.png">

1. Datadog Logs から GCP の各種ログデータを確認する<br>


> これらの操作を teraform で自動化することは可能？

## ■ 参考サイト

- https://qiita.com/suzuyui/items/b18a7e686bab69d9ecd2
- https://docs.datadoghq.com/ja/integrations/google_cloud_platform/?tab=datadogussite
- https://docs.datadoghq.com/ja/logs/guide/log-collection-troubleshooting-guide/