# 【GCP】GKE 上の Web-API に対して Google Cloud Armor の WAF 機能を使用してクライアントIP単位での RateLimit 制限を行う

多数のユーザーからアクセス数されるような API においては、RateLimit 制限を導入して、ユーザー度のリクエスト回数に制限を課すことで、API の処理負荷を軽減させるのは有効な方法の１つである。

ここでは、Google Cloud Armor の WAF 機能 [Web Application Firewall] を使用してクライアントIP単位での RateLimit 制限を行う方法を記載する。

ここで API は、GKE 上にデプロイするケースを考える。理由は Google Cloud Armor がロードバランサー（GKEだと自動的に構成される）に対して適用される機能であるためである。GCE で API を構築する場合は、別途ロードバランサーを組み込む必要があると思われる

> RateLimit：一定時間あたりにリクエストできる回数

> WAF [Web Application Firewall] : Web アプリケーションに対する "SQL インジェクション", "クロスサイトスクリプティング" といったアプリケーションレイヤの攻撃を検知し、防御するための仕組み。

## ■ 方法

1. gcloud コマンドを更新する<br>
	```sh
	$ sudo gcloud components update
	$ gcloud --version
	```

	> Google Cloud SDK 322.0.0 では後述の `gcloud compute security-policies rules create` コマンドが動作しなかったが、Google Cloud SDK 384.0.1 では動作した

1. Google Cloud Armor 用のサービスアカウントを作成する。<br>
	Google Cloud Armor 用のサービスアカウントを作成し、作成したサービスアカウントに Google Cloud Armor のセキュリティポリシーの IAM 権限を付与する<br>
	```sh
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
	fi
	```

	> `roles/compute.securityAdmin` が Google Cloud Armor のセキュリティポリシーの IAM 権限になるので、これを作成した

1. GKE のロードバランサーに適用するためのセキュリティポリシーを作成する<br>
	GKE の外部 HTTP(S) ロードバランサーに適用するためのセキュリティポリシーを作成する。

	```sh
	$ gcloud compute security-policies create ${SECURITY_POLICY_NAME}
	```

	> 作成したセキュリティーポリシーは、「[GCP の Cloud Armor のコンソール画面](https://console.cloud.google.com/net-security/securitypolicies/list?_ga=2.209172050.199022831.1651215887-1079843928.1651215303&project=my-project2-303004)」から確認できる

1. セキュリティーポリシーのルール（RateLimit 制限）を作成する<br>
	作成した GKE のロードバランサーに適用するためのセキュリティポリシーに対して、セキュリティーポリシーのルール（ここでは、RateLimit 制限）を設定する
	```sh
	$ gcloud compute security-policies rules create ${PRIORITY}
		--security-policy=${SECURITY_POLICY_NAME}
		(--expression=${EXPRESSION} | --src-ip-ranges=${SRC_IP_RANGE})
		--action "throttle"
		--rate-limit-threshold-count=$RATE_LIMIT_THRESHOLD_COUNT
		--rate-limit-threshold-interval-sec=$RATE_LIMIT_THRESHOLD_INTERVAL_SEC
		--conform-action=[allow]
		--exceed-action=[deny-403|deny-404|deny-429|deny-502|redirect]
		--exceed-redirect-type=[google-recaptcha|external-302]
		--exceed-redirect-target=$REDIRECT_URL
		--enforce-on-key=[IP | ALL | HTTP-HEADER | XFF-IP | HTTP-COOKIE]
		--enforce-on-key-name=[$HTTP_HEADER_NAME|$HTTP_COOKIE_NAME]
	```
	```sh
	# 例
	gcloud compute security-policies rules create 10 \
		--security-policy clients-policy     \
		--src-ip-ranges="0.0.0.0/1"     \
		--action=throttle                \
		--rate-limit-threshold-count=100 \
		--rate-limit-threshold-interval-sec=60 \
		--conform-action=allow           \
		--exceed-action=deny-429         \
		--enforce-on-key=IP
	```

	- `${PRIORITY}` : セキュリティールールの優先度
	- `--src-ip-ranges` : RateLimit 制限をかけるクライアントIPの範囲（CIDR 表記で指定）。`*` を設定した場合は、全ての IP アドレスになる？
	- `--rate-limit-threshold-count` : 指定された時間間隔 `--rate-limit-threshold-interval-sec` 内で許可される１クライアントあたりのリクエスト数。最小値は 1、最大値は 10,000 です。
	- `--rate-limit-threshold-interval-sec` : 時間間隔の秒数。値は 60、120、180、240、300、600、900、1200、1800、2700、3600 秒のいずれかにする必要があります。
	- `--enforce-on-key` : RateLimit 制限対象のクライアントを特定するための値
		- `ALL` : リクエストがルールの一致条件を満たすすべてのクライアントの単一キー。
		- `IP` : リクエストがルールの一致条件を満たすクライアントの送信元 IP アドレスごとに一意のキー。
		- `HTTP-HEADER` : 
		- `XFF-IP` : クライアントのオリジナルの送信元 IP アドレス
		- `HTTP-COOKIE` : 

	> RateLimit 制限をかけるクライアントIPの範囲 `--src-ip-ranges` を設定しないといけないので、クライアントIPをリクエスト時ではなく、デプロイ時に予め知っておく必要がある。`--src-ip-ranges` の範囲を増やせば、全クライアントに対して RateLimit 制限をかけることが可能？

	> - CIDR 表記<br>
	> `198.51.100.xxx/24` のような形で、IPアドレスの後ろに `/` と２進数のサブネットマスクにおける１の個数を書く表記方法。<br>
	> 例えば、/16 => 11111111.11111111.00000000.00000000 => 255.255.0.0 のサブネットマスクとなり、<br>
	> /24 => 11111111.11111111.11111111.00000000 => 255.255.255.0 のサブネットマスクとなる。<br>

1. GKE 上で動作するする API をデプロイする<br>
	1. Web-API のコードを作成する<br>
		```python
		```

	1. Web-API サーバーの Dockerfile を作成する<br>
		```dockerfile
		```

	1. Web-API サーバーの k8s マニフェストファイルを作成する<br>
		- Pod<br>
			```yaml
			# Pod
			apiVersion: apps/v1
			kind: Deployment
			metadata:
			name: fast-api-rate-limit-pod
			labels:
				app: fast-api-rate-limit-pod
			spec:
			replicas: 1
			selector:
				matchLabels:
				app: fast-api-rate-limit-pod
			template:
				metadata:
				labels:
					app: fast-api-rate-limit-pod
				spec:
				containers:
				- name: fast-api-container
					image: gcr.io/my-project2-303004/fast-api-rate-limit-image-gke:latest
					ports:
					- containerPort: 5000
					name: http-server
					env:
					- name: DEBUG
						value: "True"
					command: ["/bin/sh","-c"]
					args: ["bash setup_gke.sh ; gunicorn app:app --bind 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker --workers 1 --threads 1 --backlog 100 --timeout 1000000 --reload"]
			```

		- Service<br>
			```yaml
			# Service
			apiVersion: v1
			kind: Service
			metadata:
			name: fast-api-rate-limit-server
			annotations:
				cloud.google.com/backend-config: '{"default": "fast-api-rate-limit-backendconfig"}'  # annotations で BackendConfig を関連付ける
			spec:
			#  type: LoadBalancer   # L4 ロードバランサーは使用しない。代わりに L7 ロードバランサーである Ingress を使用する
			type: NodePort
			ports:
				- port: 5000
				targetPort: 5000
				protocol: TCP
			selector:
				app: fast-api-rate-limit-pod
			```

		- Ingress<br>
			```yaml
			# Ingress
			apiVersion: networking.k8s.io/v1beta1
			kind: Ingress
			metadata:
			name: fast-api-rate-limit-ingress
			spec:
			backend:
				serviceName: fast-api-rate-limit-server
				servicePort: 5000
			```

		- BackendConfig<br>
			```yaml
			# BackendConfig
			apiVersion: cloud.google.com/v1
			kind: BackendConfig
			metadata:
			name: fast-api-rate-limit-backendconfig
			spec:
			securityPolicy:
				name: rate-limit-policy  # `gcloud compute security-policies create` コマンドで作成した security policy の名前
			```

		ポイントは、以下の通り

		- RateLimit 機能のようなアプリケーション固有のロードバランシング処理を行うためには、L4 ロードバランサーである Service (ServiceType : LoadBalancer) ではなく、L7 ロードバランサーである Ingress を使用する必要がある

			> - L4 ロードバランサーと L7 ロードバランサー<br>
			>   ここでの L4, L7 は、通信プロトコルにおける L4（トランスポート層）と L7（アプリケーション層）のこと。<br>
			>   L4 ロードバランサーは、L4（トランスポート層）で定義されている基本的なロードバランシングの機能のみを持ったロードバランサー<br>
			>   L7 ロードバランサーは、L7（アプリケーション層）で定義されている機能も持ったロードバランサーなので、アプリケーションやWebブラウザごとにロードバランシング先を決めることもできる<br>

		- BackendConfig と呼ばれる GKE 用の k8s カスタムリソースの設定を行うことで、Cloud Armor のセキュリティーポリシーを Ingress で作成した L7 ロードバランサーの構成を Service に追加することができる。

	1. Google Container Registry 上に Web-API の docker image をデプロイする<br>
		```sh
		gcloud builds submit --config cloudbuild.yml --timeout 3600
		```

	1. GKE クラスタを作成する<br>
		```sh
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
		```

	1. 各種 k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）をデプロイする<br>
		```sh
		# k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）の作成
		kubectl apply -f k8s/fast_api_rate_limit.yml
		```

	1. 【オプション】作成した Pod の動作確認<br>
		作成した Pod の動作確認したい場合は、以下のコマンドで確認できる。

		- 作成した Pod のコンテナログを確認
			```sh
			# 作成した Pod のコンテナログを確認
			kubectl logs `kubectl get pods | grep "fast-api-rate-limit-pod" | awk '{print $1}'`
			```

		- 作成した Pod のコンテナにアクセス
			```sh
			# 作成した Pod のコンテナにアクセス
			kubectl exec -it `kubectl get pods | grep "fast-api-rate-limit-pod" | awk '{print $1}'` /bin/bash
			```

1. GKE クラスタのコンテナにサービスアカウントを適用する<br>
	Web-API のコンテナ内で以下のスクリプトを実行して、Google Cloud Armor 用のサービスアカウントを適用する

	```sh
	PROJECT_ID=my-project2-303004
	SERVICE_ACCOUNT_NAME=cloud-armor-account
	CLUSTER_NAME=fast-api-cluster
	REGION=us-central1

	# GCE サービスアカウント -> API 用サービスアカウントへの切替え
	export GOOGLE_APPLICATION_CREDENTIALS="/api/key/${SERVICE_ACCOUNT_NAME}.json"
	gcloud auth activate-service-account ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --key-file /api/key/${SERVICE_ACCOUNT_NAME}.json
	gcloud auth list

	# 作成したクラスタに切り替える
	gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${REGION} --project ${PROJECT_ID}
	```

1. 【オプション】セキュリティポリシーをバックエンドサービス（L7ロードバランサー）に接続する<br>
	k8s の BackendConfig リソースを使用した場合は、自動的に、作成したセキュリティポリシーがバックエンドサービス（L7ロードバランサー）に接続される。<br>
	<img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/167101666-f4228f4a-0f87-425d-9ab7-58b2ba025c5a.png">

	作成したセキュリティポリシーのバックエンドサービス（L7ロードバランサー）への接続を手動で行いたい場合は、以下のコマンドで実行できる

	```sh
	$ gcloud compute backend-services update ${BACKEND_SERVICE_NAME} \
    	--security-policy ${SECURITY_POLICY_NAME}
	```
	- `${BACKEND_SERVICE_NAME}` : L7 ロードバランサーの名前
	
		> Ingress で生成した L7 ロードバランサーのみ指定可能。Service (ServiceType : LoadBalancer) で生成されるロードバランサーは L4 ロードバランサーなので指定不可なことに注意

1. リクエスト処理を送信する<br>
	`curl` コマンドなどで、起動した API サーバーのエンドポイントに繰り返しリクエスト処理を行い、RateLimit 制限が適切に機能しているか確認する
	```sh
	INGRESS_NAME=fast-api-rate-limit-ingress
	HOST=`kubectl get ingress | grep ${INGRESS_NAME} | awk '{print $4}'`

	N_REQUESTS=15
	INTERVAL_SEC=1

	# health check
	echo "[GET method] ヘルスチェック\n"
	for i in `seq 1 ${N_REQUESTS}`
	do
		curl http://${HOST}/health
		echo "\n"
		sleep ${INTERVAL_SEC}
	done
	```

	- 出力結果
		```sh
		request 1 : 
		{"health":"ok"}
		request 2 : 
		{"health":"ok"}
		request 3 : 
		{"health":"ok"}
		request 4 : 
		{"health":"ok"}
		request 5 : 
		{"health":"ok"}
		request 6 : 
		{"health":"ok"}
		request 7 : 
		{"health":"ok"}
		request 8 : 
		{"health":"ok"}
		request 9 : 
		{"health":"ok"}
		request 10 : 
		{"health":"ok"}
		request 11 : 
		<!doctype html><meta charset="utf-8"><meta name=viewport content="width=device-width, initial-scale=1"><title>429</title>429 Too Many Requests
		request 12 : 
		<!doctype html><meta charset="utf-8"><meta name=viewport content="width=device-width, initial-scale=1"><title>429</title>429 Too Many Requests
		request 13 : 
		<!doctype html><meta charset="utf-8"><meta name=viewport content="width=device-width, initial-scale=1"><title>429</title>429 Too Many Requests
		request 14 : 
		<!doctype html><meta charset="utf-8"><meta name=viewport content="width=device-width, initial-scale=1"><title>429</title>429 Too Many Requests
		request 15 : 
		<!doctype html><meta charset="utf-8"><meta name=viewport content="width=device-width, initial-scale=1"><title>429</title>429 Too Many Requests
		```

		> `--rate-limit-threshold-count=10`, `--rate-limit-threshold-interval-sec=60` で設定したインターバル時間以上リクエストを行うと RateLimit 制限がかかっている

## ■ 参考サイト
- https://cloud.google.com/armor/docs/rate-limiting-overview
- https://cloud.google.com/armor/docs/configure-security-policies#gcloud
- https://qiita.com/irotoris/items/8d6be7b0afd9b8afc321
