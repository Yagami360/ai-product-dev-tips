# Ambassador を使用して EKS クラスター上の Web-API の API Gateway を行う

Ambassador は、k8s で構成したマイクロサービス型 REST API 向けのサードパーティー製 APIGateway サービスで、以下のような機能や特徴がある

- AWS API Gateway のような API Gateway 機能をもつ

- nginx や k8s の Ingress のような Proxy 機能をもつ

- 細かなルーティング制御、正規表現ベースのルーティング、ホストルーティングなどが可能

- ルーティングとスケーリングを Envoy と Kubernetes に依存しているので、展開と操作が簡単

- Istio と連携してサービスメッシュ化が可能

## ■ 方法

1. AWS CLI をインストールする<br>
    - MacOS の場合<br>
        ```sh
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
        ```

    - Linux の場合<br>
        ```sh
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        ```

1. `eksctl` コマンドをインストールする
    EKS クラスターで多くの個別のタスクを自動化するために使用する AWS のコマンドラインツールである `eksctl` をインストールする

    - MacOS の場合<br>
        ```sh
        # Homebrew をインストール
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

        # Weaveworks Homebrew tap をインストール
        brew tap weaveworks/tap

        # brew 経由で eksctl をインストール
        brew install weaveworks/tap/eksctl
        ```

    - Linux の場合<br>
        ```sh
        curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
        sudo mv /tmp/eksctl /usr/local/bin
        ```

1. kubectl コマンドをインストールする
    - MacOS の場合
        ```sh
        # 最新版取得
        curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl

        # Ver指定(ex:1.40)
        curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.14.0/bin/darwin/amd64/kubectl

        # アクセス権限付与
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
        ```

    - Ubuntu の場合<br>
        ```sh
        curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"        
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
        ```

1. API のコードを作成する<br>
    今回は FastAPI を使用した API のコードを作成する。コア部分ではないので省略

1. API の Dockerfile を作成する<br>
    コア部分ではないので省略

1. Amazon ECR [Elastic Container Registry] に Docker image を push する<br>
    1. API の Docker image を作成する<br>
        ```sh
        cd api/predict-server
        docker build./  -t ${IMAGE_NAME}
        cd ../..
        ```
    1. ECR リポジトリを作成する<br>
        ```sh
        aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --image-scanning-configuration scanOnPush=true
        ```
    1. ECR にログインする<br>
        ```sh
        aws ecr get-login-password --profile ${AWS_PROFILE} --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
        ```
        > ECR を使用する場合は、`docker login` コマンドの `--username` オプションのユーザー名は `AWS` になる

        > `--profile` の値は `cat ~/.aws/config` で確認できる

    1. ローカルの docker image に ECR リポジトリ名での tag を付ける<br>
        ECR での docker image 名は ``${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest` になるので、`docker tag` でローカルにある docker image に別名をつける
        ```sh
        docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
        ```
    1. ECR に Docker image を push する<br>
        ```sh
        docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
        ```

1. EKS クラスターを作成する<br>
	```sh
	eksctl create cluster --name ${CLUSTER_NAME} \
			--fargate \
			--node-type ${CLUSTER_NODE_TYPE} \
			--nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES}
	```
	- `--fargate` : 指定した場合は AWS Fargate で Linux アプリケーションを実行。指定しない場合はマネージド型ノードになる<br>

			> Fargate : Amazon EC2 インスタンスを管理せずに Kubernetes ポッドをデプロイできるサーバーレスコンピューティングエンジン

			> マネージド型ノード : Amazon EC2 インスタンスで Amazon Linux アプリケーションを実行する

	> Amazon EKS クラスターを使用するには、`[AmazonEKSClusterPolicy](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AmazonEKSClusterPolicy$jsonEditor)` という IAM ポリシーをもつ IAM ロールや VPC などが必要であるが、`eksctl` コマンドで EKS クラスターを作成すれば、この IAM ポリシー `AmazonEKSClusterPolicy` をもつ IAM ロールや VPC などが全て自動的に作成される。

	>`aws` コマンドで EKS クラスターを作成する場合は、EKS 用の VPC や IAM ロールを自分で作成する必要がある

1. Ambassador の k8s リソースをデプロイする<br>
	```sh
	kubectl apply -f https://getambassador.io/yaml/ambassador/ambassador-rbac.yaml
	```

	- `ambassador-rbac.yaml`
		```yml
		apiVersion: v1
		kind: Service
		metadata:
			labels:
				service: ambassador-admin
			name: ambassador-admin
		spec:
			type: NodePort
			ports:
			- name: ambassador-admin
				port: 8877
				targetPort: 8877
			selector:
				service: ambassador
		---
		apiVersion: rbac.authorization.k8s.io/v1beta1
		kind: ClusterRole
		metadata:
			name: ambassador
		rules:
		- apiGroups: [""]
			resources:
			- services
			verbs: ["get", "list", "watch"]
		- apiGroups: [""]
			resources:
			- configmaps
			verbs: ["create", "update", "patch", "get", "list", "watch"]
		- apiGroups: [""]
			resources:
			- secrets
			verbs: ["get", "list", "watch"]
		---
		apiVersion: v1
		kind: ServiceAccount
		metadata:
			name: ambassador
		---
		apiVersion: rbac.authorization.k8s.io/v1beta1
		kind: ClusterRoleBinding
		metadata:
			name: ambassador
		roleRef:
			apiGroup: rbac.authorization.k8s.io
			kind: ClusterRole
			name: ambassador
		subjects:
		- kind: ServiceAccount
			name: ambassador
			namespace: default
		---
		apiVersion: extensions/v1beta1
		kind: Deployment
		metadata:
			name: ambassador
		spec:
			replicas: 3
			template:
				metadata:
					annotations:
						sidecar.istio.io/inject: "false"
					labels:
						service: ambassador
				spec:
					serviceAccountName: ambassador
					containers:
					- name: ambassador
						image: quay.io/datawire/ambassador:0.40.2
						resources:
							limits:
								cpu: 1
								memory: 400Mi
							requests:
								cpu: 200m
								memory: 100Mi
						env:
						- name: AMBASSADOR_NAMESPACE
							valueFrom:
								fieldRef:
									fieldPath: metadata.namespace
						ports:
						- name: http
							containerPort: 80
						- name: https
							containerPort: 443
						- name: admin
							containerPort: 8877
						livenessProbe:
							httpGet:
								path: /ambassador/v0/check_alive
								port: 8877
							initialDelaySeconds: 30
							periodSeconds: 3
						readinessProbe:
							httpGet:
								path: /ambassador/v0/check_ready
								port: 8877
							initialDelaySeconds: 30
							periodSeconds: 3
					restartPolicy: Always
		```

		ポイントは、以下の通り

		- Ambassador の実体は、単に k8s リソースである

		- ambassador コンテナを定義した Pod を NodePort の Service に関連付けて、ポート番号 `80`（http）、`443`（https）、`8877` で外部公開している

	上記コマンド実行後、以下のような k8s リソースがデプロイされている状態になる
	```sh
	~/GitHub/ai-product-dev-tips/ml_ops/90 $ kubectl get pods
	NAME                                READY   STATUS    RESTARTS   AGE
	ambassador-57f976bbf8-blvnt         0/1     Running   0          32s
	ambassador-57f976bbf8-lv5ds         0/1     Running   0          32s
	ambassador-57f976bbf8-pv4cr         0/1     Running   0          32s
	ambassador-agent-5586d5794b-qfltx   1/1     Running   0          30s
	```
	```sh
	~/GitHub/ai-product-dev-tips/ml_ops/90 $ kubectl get svc
	NAME               TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)                         AGE
	ambassador-admin   NodePort    10.100.15.8   <none>        8877:30659/TCP,8005:30100/TCP   69s
	kubernetes         ClusterIP   10.100.0.1    <none>        443/TCP                         13m
	```

1. 【オプション】LoadBalancer の Service を定義した ambassador 用 k8s マニフェストを作成しデプロイする<br>
	`ambassador-rbac.yaml` で定義している `ambassador-admin` という名前の Service は NodePort であるので、LoadBalancer の Service を作成したい場合は、以下のような k8s マニフェストを別途作成する。
	
	- `ambassador-service.yaml`
		```sh
		apiVersion: v1
		kind: Service
		metadata:
			name: ambassador
		spec:
			type: LoadBalancer
			ports:
			- port: 80
			selector:
				service: ambassador				
		```

	その後、以下のコマンドで Service をデプロイする
	```sh
	kubectl apply -f ambassador-service.yaml
	```
	
	上記コマンド実行後、以下のような k8s リソースがデプロイされている状態になる
	```sh
	~/GitHub/ai-product-dev-tips/ml_ops/90 $ kubectl get svc
	NAME               TYPE           CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)                         AGE
	ambassador         LoadBalancer   10.100.155.85   a692e46435d0541ef849637734c86849-1124348952.us-west-2.elb.amazonaws.com   80:30093/TCP                    4s
	ambassador-admin   NodePort       10.100.15.8     <none>                                                                    8877:30659/TCP,8005:30100/TCP   7m7s
	kubernetes         ClusterIP      10.100.0.1      <none>                                                                    443/TCP                         19m
	```

	> `ambassador` という名前の Service が LoadBalancer になっており、EXTERNAL-IP が割り当てられている

	> この LoadBalancer の Servie を作成した時点で、AWS の ELB（L4/L7ロードバランサー）も自動的に作成される
	> <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184896740-914a26cc-d5ef-4314-817a-4571901fd100.png">

1. API の k8s マニフェストを作成する<br>
	```yaml
	---
	# Pod
	apiVersion: apps/v1
	kind: Deployment
	metadata:
			name: predict-pod
			labels:
					app: predict-pod
	spec:
			replicas: 1
			selector:
					matchLabels:
					app: predict-pod
			template:
					metadata:
					labels:
							app: predict-pod
					spec:
					containers:
					- name: predict-container
							image: 735015535886.dkr.ecr.us-west-2.amazonaws.com/predict-server-image-eks:latest
							command: ["/bin/sh","-c"]
							args: ["gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5001 --workers 1 --threads 1 --backlog 256 --reload"]
	---
	# Service
	apiVersion: v1
	kind: Service
	metadata:
		name: predict-server
		# `metadata.annotations` タグに、ルーティングの設定を定義した `getambassador.io/config` を設定することで、Ambassador を API Gateway として経由し、API にアクセスできるようにする
		annotations:
			getambassador.io/config: |
				---
				apiVersion: ambassador/v0
				kind: Mapping
				name: api-mapping
				prefix: /health
				service: 44.225.109.227:80
				#host_rewrite: xxx
	spec:
		#type: NodePort
		type: LoadBalancer
		loadBalancerIP: 44.225.109.227   # IP アドレス固定
		ports:
			- port: 5001
				targetPort: 5001
				protocol: TCP
		selector:
			app: predict-pod
	```

	ポイントは、以下の通り

	- API の Service の `metadata.annotations` タグに、ルーティングの設定を定義した `getambassador.io/config` を設定することで、Ambassador を API Gateway として経由し、API にアクセスできるようにしている。

	> EKS において `type: LoadBalancer` で Service リソースをデプロイした場合、`aacde1380ec0149da89649c5eebf63ab-1308085615.us-west-2.elb.amazonaws.com` のような URL で `EXTERNAL-IP` が割り当てられる。

	> [ToDo] 但し、この `EXTERNAL-IP` の URL に外部アクセスできなかった。原因は不明。URL で外部アクセスできるようにする

	> [ToDo] そのため、Elastic IP で作成した固定 IP を割り当てが、今度は `EXTERNAL-IP` が pending のままになってしまう。Elastic IP で外部アクセスできるようにする

1. API の各種 k8s リソースをデプロイする<br>
	```sh
	kubectl apply -f k8s/predict.yml
	```

1. EKS 上の Web-API に対してリクエストを行い、ambassador でのルーティング機能を確認する<br>
	xxx

## ■ 参考サイト

- https://qiita.com/t-sato/items/e4b8bd59cd32cf0ce102