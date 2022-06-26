# 【GCP】 Kustomize を使用して GKE の k8s のリソース管理を行う

開発環境と本番環境で k8s マニフェストの一部のみが異なるケース（例えば、環境変数 `ENVIRONMENT` の値が `dev` -> `prod` に変わるだけ）は多々あるが、
開発環境と本番環境とで別々の k8s マニフェストファイルを書く方法をとっていると、k8s マニフェストファイルの数が肥大化して、管理が大変になるという問題が存在する。

このような問題に対しては、Kustomize を使用することで解決することが出来る。
具体的には、Kustomize では以下の図のように、共通部分のみ定義した k8s マニフェストと、環境間の差分部分のみを定義した k8s マニフェストを定義することで、k8s マニフェストの管理を行う。

<img width="751" alt="image" src="https://user-images.githubusercontent.com/25688193/175799502-8ee750d0-a2d2-4605-a459-cb9b866de6db.png">

ここでは、GKE 上の Web-API の k8s マニフェストファイルに対して、Kustomize を使用して k8s のリソース管理を行う方法を記載する。

尚、今回の例では GKE クラスタとノードプールの作成は、terraform を使用して作成しているが、terraform でなくても gcloud コマンド等で作成してもよい

## ■ 方法

1. Kustomize をインストールする。
	- MacOS の場合
		```sh
		brew install kustomize
		```

	- Linux の場合
		```sh
		curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
		kustomize completion bash >> ~/.bashrc
		```

1. Web-API のコードと Dockerfile を作成する<br>
	今回のコア部分ではないので、詳細は省略する

1. 環境別の k8s マニフェストファイルを作成する<br>
	<img width="751" alt="image" src="https://user-images.githubusercontent.com/25688193/175799502-8ee750d0-a2d2-4605-a459-cb9b866de6db.png">

	1. `base` ディレクトリ以下に、各環境で共通設定となる Web-API の k8s マニフェストを作成する<br>
		- `k8s/base/kustomization.yml`<br>
			```yml
			apiVersion: kustomize.config.k8s.io/v1beta1
			kind: Kustomization
			resources:
				- fast_api.yml
			```

		- `k8s/base/fast_api.yml`<br>
			```yml
			---
			# Pod
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
							# docker image を開発環境、本番環境で切り分け
			#        image: gcr.io/my-project2-303004/fast-api-image-gke:latest
			#        image: gcr.io/my-project2-303004/fast-api-image-gke-dev:latest
							ports:
							- containerPort: 5000
								name: http-server
							# 環境変数を開発環境、本番環境で切り分け
			#        env:
			#          - name: ENVIRONMENT
			#            value: "dev"
			#            value: "prod"
			#          - name: DEBUG
			#            value: "True"
							command: ["/bin/sh","-c"]
							args: ["gunicorn app:app --bind 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker --workers 1 --threads 1 --backlog 256 --timeout 1000000 --reload"]
							resources:
								requests:
									cpu: 100m
									memory: "0.1Gi"
			---
			# Service
			apiVersion: v1
			kind: Service
			metadata:
				name: fast-api-server
			spec:
				# IPアドレスを開発環境、本番環境で切り分け
				#type: LoadBalancer   # L4 ロードバランサーは使用しない。代わりに L7 ロードバランサーである Ingress を使用する
				ports:
					- port: 5000
						targetPort: 5000
						protocol: TCP
				selector:
					app: fast-api-pod
			```

			ポイントは、以下の通り

			- `kustomization.yml` では、`kustomize.config.k8s.io/v1beta1` リソースを定義する。このリソースには、kustomize で管理したい k8s マニフェストファイル（今回の場所は API のマニフェスト）情報を定義する

			- `base` ディレクトリ内の `kustomization.yml` では、`resources` タグで、共通部分の k8s マニフェストファイルのファイルパス（今回の場所は `k8s/base/fast_api.yml`）を指定する

			- `base` ディレクトリ内に、共通の部分の API の k8s マニフェスト（今回の場所は `k8s/base/fast_api.yml`）を定義する。今回は、｛docker image 名・環境変数・エンドポイントのIPアドレス｝を環境によって切り分けたいので、この部分以外の共通部分を定義している

			- ディレクトリ名は `base` でなくても、任意の名前で良い

	1. `dev` ディレクトリ以下に、開発環境用の Web-API の k8s マニフェストの差分部分を作成する<br>
		- `k8s/dev/kustomization.yml`<br>
			```yml
			apiVersion: kustomize.config.k8s.io/v1beta1
			kind: Kustomization
			bases:
				- ../base/
			namespace: dev
			patchesStrategicMerge:
				- ./fast_api.yml
			```

		- `k8s/dev/fast_api.yaml`<br>
			```yml
			---
			# Pod
			apiVersion: apps/v1
			kind: Deployment
			metadata:
				name: fast-api-pod
			spec:
				selector:
					matchLabels:
						app: fast-api-pod
				template:
					spec:
						containers:
						- name: fast-api-container
							image: gcr.io/my-project2-303004/fast-api-image-gke-dev:latest
							env:
								- name: ENVIRONMENT
									value: "dev"
								- name: DEBUG
									value: "True"
			---
			# Service
			apiVersion: v1
			kind: Service
			metadata:
				name: fast-api-server
			spec:
				# IPアドレスを開発環境、本番環境で切り分け
				type: LoadBalancer   # L4 ロードバランサーは使用しない。代わりに L7 ロードバランサーである Ingress を使用する
			```
		
		ポイントは、以下の通り

		- `dev` ディレクトリ以下の `kustomization.yml` には、`bases` タグに共通部分の k8s マニフェストを定義した `base` ディレクトリの場所を指定し、`patchesStrategicMerge` タグで開発環境用の差分を定義した k8s マニフェストファイルパスを指定する。また、`namespace` タグで開発環境用の名前空間を指定することもできる

		- `dev` ディレクトリ内に、開発環境での差分を定義した API の k8s マニフェスト（今回の場所は `k8s/dev/fast_api.yml`）を定義する。今回は、｛docker image 名・環境変数・エンドポイントのIPアドレス｝を環境によって切り分けたいので、この diff 部分のみを定義している

		- ディレクトリ名は `dev` でなくても、任意の名前で良い

	1. `prod` ディレクトリ以下に、本番環境用の Web-API の k8s マニフェストの差分部分を作成する<br>

		- `k8s/prod/kustomization.yml`<br>
			```yml
			apiVersion: kustomize.config.k8s.io/v1beta1
			kind: Kustomization
			bases:
				- ../base/
			namespace: prod
			patchesStrategicMerge:
				- ./fast_api.yml
			```

		- `k8s/prod/fast_api.yaml`<br>
			```yml
			---
			# Pod
			apiVersion: apps/v1
			kind: Deployment
			metadata:
				name: fast-api-pod
			spec:
				selector:
					matchLabels:
						app: fast-api-pod
				template:
					spec:
						containers:
						- name: fast-api-container
							image: gcr.io/my-project2-303004/fast-api-image-gke:latest
							env:
								- name: ENVIRONMENT
									value: "prod"
								- name: DEBUG
									value: "False"
			---
			# Service
			apiVersion: v1
			kind: Service
			metadata:
				name: fast-api-server
			spec:
				# IPアドレスを開発環境、本番環境で切り分け
				type: LoadBalancer   # L4 ロードバランサーは使用しない。代わりに L7 ロードバランサーである Ingress を使用する
			```

		ポイントは、以下の通り

		- `prod` ディレクトリ以下の `kustomization.yml` には、`bases` タグに共通部分の k8s マニフェストを定義した `base` ディレクトリの場所を指定し、`patchesStrategicMerge` タグで本番環境用の差分を定義した k8s マニフェストファイルパスを指定する。また、`namespace` タグで本番環境用の名前空間を指定することもできる

		- `prod` ディレクトリ内に、本番環境での差分を定義した API の k8s マニフェスト（今回の場所は `k8s/prod/fast_api.yml`）を定義する。今回は、｛docker image 名・環境変数・エンドポイントのIPアドレス｝を環境によって切り分けたいので、この diff 部分のみを定義している

		- ディレクトリ名は `prod` でなくても、任意の名前で良い

1. API の k8s マニフェストを確認する<br>
	`kustomize build` コマンドを実行することで、各環境の k8s マニフェスト全体を確認することが出来る

	- base 環境の k8s マニフェストを確認する場合<br>
		```sh
		kustomize build k8s/base
		```

	- 開発環境の k8s マニフェストを確認する場合<br>
		```sh
		kustomize build k8s/dev
		```

		出力結果
		```yml
		apiVersion: v1
		kind: Service
		metadata:
			name: fast-api-server
			namespace: dev
		spec:
			ports:
			- port: 5000
				protocol: TCP
				targetPort: 5000
			selector:
				app: fast-api-pod
			type: LoadBalancer
		---
		apiVersion: apps/v1
		kind: Deployment
		metadata:
			labels:
				app: fast-api-pod
			name: fast-api-pod
			namespace: dev
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
					- args:
						- gunicorn app:app --bind 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker --workers
							1 --threads 1 --backlog 256 --timeout 1000000 --reload
						command:
						- /bin/sh
						- -c
						env:
						- name: ENVIRONMENT
							value: dev
						- name: DEBUG
							value: "True"
						image: gcr.io/my-project2-303004/fast-api-image-gke-dev:latest
						name: fast-api-container
						ports:
						- containerPort: 5000
							name: http-server
						resources:
							requests:
								cpu: 100m
								memory: 0.1Gi
		```

	- 本番環境の k8s マニフェストを確認する場合<br>
		```sh
		kustomize build k8s/prod
		```

1. ローカル環境で terraform を実行するための Dockefile & docker-compose.yml を作成する<br>
	今回のコア部分ではないので、詳細は省略する

1. GKE クラスター用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
	今回のコア部分ではないので、詳細は省略する

1. API の k8s マニフェストをデプロイする
	 - 開発環境
		```sh
		kubectl create namespace dev
		kubectl apply -k k8s/dev
		```

	 - 本番環境
		```sh
		kubectl create namespace prod
		kubectl apply -k k8s/prod
		```

	> 今回は開発環境と本番環境で別の namespace にしているので、`kubectl create namespace` で名前空間を作成しているが、どちらも `default` の名前空間にデプロイする場合は、`kubectl create namespace` で名前空間を作成する必要はない。

1. GKE 上の Web-API に対して、リクエスト処理を行う<br>
	本番環境の API と開発開発の API それぞれに対してリクエスト処理を行う
	```sh
	sh resuest_api.sh
	```


## ■ 参考サイト

- https://qiita.com/oguogura/items/af3860ca32cd0264ca93