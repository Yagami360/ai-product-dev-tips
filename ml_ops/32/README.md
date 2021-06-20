# Fluentd を使用して GKE 上の Web-API でのログデータを Cloud logging に転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + GKE での構成）

GKE で構成された Web-API では、GKE のオートスケールや Pod の自動復旧機能なのによって、Web-API 駆動中もコンテナが動作する GCE インスタンスが削除されたり、別の GCE インスタンスに配置されたりする。
従って、Web-API のログデータを GCE のディスクに書き込んでそのログデータを確認する方法では、GCE 自体が途中で削除されてログデータが保存されたディスクデータがなくなるという問題に対処できない。

GKE で構成された Web-API でうまくロギング処理をおこなためには、Fluentd などを使用してログデータを Cloud logging に転送する必要がある。

## ■ 方法

1. Web-API の設定<br>
	1. Web-API のコードを作成する
		Python の `logging` モジュールなどを使用して Web-API のログデータを出力する Web-API のコードを作成する

	1. GKE にデプロイする docker image ための Dockerfile を作成する

1. k8s の各種設定ファイルの作成<br>
	1. Web API と fluentd サーバーのデプロイメント定義ファイルを作成する<br>
		```yml
		# Fast API
		apiVersion: apps/v1
		kind: Deployment
		metadata:
		name: fast-api-pod
		labels:
			app: fast-api-pod
		spec:
		replicas: 1
		selector:
			matchLabels:
			app: fast-api-pod
		template:
			metadata:
			labels:
				app: fast-api-pod
			spec:
			containers:
			- name: fast-api-container
				image: gcr.io/my-project2-303004/fast-api-image-gke:latest
				imagePullPolicy: Always
				ports:
				- containerPort: 5000
				name: http-server
				command: ["/bin/sh","-c"]
				args: ["gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
				volumeMounts:                         
				- name: varlog-volume               # /var/log ディレクトリを fluentd コンテナと共有
					mountPath: /var/log
				- name: apilog-volume               # /api/log ディレクトリを fluentd コンテナと共有
					mountPath: /api/log            
			- name: fluentd-container               # FastAPI コンテナのサイドカー（FastAPI コンテナとディスクを共有するコンテナ）
				image: k8s.gcr.io/fluentd-gcp:1.30
				env:
				- name: FLUENTD_ARGS                # /etc/fluentd/fluentd.conf にある設定ファイルで fluentd サーバーを起動するための環境変数
					value: -c /etc/fluentd/fluentd.conf   
				volumeMounts:
				- name: varlog-volume               # /var/log ディレクトリを FastAPI コンテナと共有
					mountPath: /var/log
				- name: apilog-volume               # /api/log ディレクトリを FastAPI コンテナと共有
					mountPath: /api/log            
				- name: fluentd-configmap-volume    # fluentd-configmap を /etc/fluentd ディレクトリにマウント
					mountPath: /etc/fluentd
			volumes:
				- name: varlog-volume
				emptyDir: {}
				- name: apilog-volume
				emptyDir: {}
				- name: fluentd-configmap-volume
				configMap:
					name: fluentd-configmap
		```

		> ポイントは、以下の通り<br>
		> - fluentd サーバーでの Web-API からのログデータの転送を可能にするためには、Web-API のコンテナと fluentd サーバーのコンテナ間でディスクを共有する必要があるので、k8s のサイドカーを使って、Web-API のコンテナと fluentd サーバーのコンテナ間でディスクを共有するようにする	
		> - Fluentd を使用してログデータを Cloud logging に転送するには、`fluent-plugin-google-cloud` をインストールした Fluentd の Docker image が必要になるので、`fluent/fluentd` ではなく `k8s.gcr.io/fluentd-gcp` の docker image を使用する

	1. fluentd サーバーの設定のための Config Map 定義ファイルを作成する<br>
		k8s の場合は、fluentd サーバーの設定ファイル `fluent.conf` を ConfigMap で定義する方法が最適である
		```yml
		# fluentd.conf の ConfigMap
		apiVersion: v1
		kind: ConfigMap
		metadata:
		name: fluentd-configmap
		data:
		fluentd.conf: |
			# Web-API log file -> fluentd log file
			<source>
			type tail
			format none
			#path /var/log/app.log
			path /api/log/app.log
			pos_file /api/log/app.log
			tag app.log
			</source>

			#<match app.**>
			#  type file
			#  path /etc/fluentd/log/app.*.log
			#</match>

			# Web-API logfile -> Cloud logging
			<match **>
			type google_cloud
			</match>
		```

		> Cloud logging への転送を行うために、`type google_cloud` での match ディレクティブを追加している点がポイント。
		> この `type google_cloud` は、`fluent-plugin-google-cloud` をインストールされたマシン上でのみ有効になるが、今の fluentd コンテナの docker image `k8s.gcr.io/fluentd-gcp:1.30` にはこの `fluent-plugin-google-cloud` がインストールされているので、実行可能になる

	1. Web API のサービス定義ファイルを作成する<br>
		```yml
		# Fast API
		apiVersion: v1
		kind: Service
		metadata:
		name: fast-api-server
		spec:
		type: LoadBalancer
		ports:
			- port: 5000
			targetPort: 5000
			protocol: TCP
		selector:
			app: fast-api-pod
		```

	1. Web-API のビルド構築ファイルを作成する<br>
		```yml
		# 変数値の置換
		substitutions:
		_IMAGE_NAME: fast-api-image-gke                 # docker image 名

		steps:
		# キャッシュされたイメージを Container Registry から pull
		# 初めてイメージをビルドする際は docker pull で pull できる既存のイメージがないため、entrypoint を bash に設定し、コマンドの実行で返されるエラーを無視できるようにしている
		- name: 'gcr.io/cloud-builders/docker'
			entrypoint: 'bash'
			args: ['-c', 'docker pull gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:latest || exit 0']

		# Container Registry 上で docker image 作成 
		- name: 'gcr.io/cloud-builders/docker'
			id: docker build
			args: [
			'build', 
			'-t', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:latest', 
			'--cache-from', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:latest',
			'-f', 'Dockerfile',
			'.'
			]

		# Container Registry 上に docker image を登録
		- name: 'gcr.io/cloud-builders/docker'
			id: docker push
			args: ['push', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:latest']

		images: ['gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:latest']
		timeout: 3600s
		```

1. GKE クラスタの構築<br>
	1. ビルド構成ファイルを元に docker image を ビルドし、Google Container Registry に push する<br>
		```sh
		$ gcloud builds submit --config cloudbuild.yml
		```

	1. GKE クラスタを作成する<br>
		```sh
		$ gcloud container clusters create ${CLUSTER_NAME} \
			--region ${ZONE} \
			--machine-type ${CPU_TYPE} \
			--num-nodes ${NUM_NODES} \
			--min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
			--enable-autoscaling
		```

		> GCE から Cloud Logging へのログデータの書き込み（転送）を有効化するには、Cloud Logging への書き込み権限ありサービスアカウントを作って、GCE に付与するというった処理が必要となるが、GKE の場合は、`gcloud container clusters create` コマンドの `--scopes` 引数のデフォルト値 `gke-default` に、Cloud Logging への書き込み権限が含まれているので、このような処理は特に必要ない

	1. ConfigMap を作成する<br>
		`fluent.conf` を定義した ConfigMap を作成する
		```sh
		$ kubectl apply -f k8s/configmap.yml
		```

	1. Pod を作成する<br>
		```sh
		$ kubectl apply -f k8s/deployment.yml
		```

	1. サービスを作成する<br>
		```sh
		$ kubectl apply -f k8s/service.yml
		```

1. リクエスト処理を行う<br>
	Web-API に対して、リクエスト処理を行う。

1. [Option] fluentd サーバーのコンテナログを確認する<br>
	```sh
	$ kubectl logs `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` fluentd-container
	```

	Web-API のログデータ `/api/log/app.log` を、正常に Cloud Logging に転送できている場合は、以下のようなコンテナログが
	```sh
	2021-06-20 07:06:16 +0000 [info]: Detected GCE platform
	2021-06-20 07:06:16 +0000 [info]: Logs viewer address: https://console.developers.google.com/project/my-project2-303004/logs?service=container.googleapis.com&key1=instance&key2=657336926711535358
	2021-06-20 07:06:16 +0000 [info]: adding source type="tail"
	2021-06-20 07:06:16 +0000 [info]: using configuration file: <ROOT>
	<source>
		type tail
		format none
		path /api/log/app.log
		pos_file /api/log/app.log
		tag app.log
	</source>
	<match **>
		type google_cloud
	</match>
	</ROOT>
	2021-06-20 07:06:16 +0000 [info]: following tail of /api/log/app.log
	2021-06-20 07:09:17 +0000 [info]: Successfully sent to Google Cloud Logging API.
	```

1. Cloud Logging 上のログデータを確認する<br>
	「[Cloud Logging コンソール画面](https://console.cloud.google.com/logs/query?hl=ja&project=my-project2-303004)」に移動し、以下のクエリを実行する
	```sh
	resource.type="container" resource.labels.cluster_name="fastapi-cluster"
	```
	
	クエリ実行後に、Web-API のログデータ `/api/log/app.log` の内容が Cloud Logging 上で表示されているか確認する<br>
	<img src="https://user-images.githubusercontent.com/25688193/122665639-5643d700-d1e3-11eb-8304-fcc68277a9df.png" width="500"><br>


## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/load_test_pattern
- https://qiita.com/ys_nishida/items/8b5274d8f3ec740ffa16