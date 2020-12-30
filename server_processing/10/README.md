# Kubernetes (k8s) の基本事項

## ■ Kubernetes (k8s) の基本事項

Kubernetes（クーベネティス）は、コンテナの運用管理と自動化（＝コンテナオーケストレーション）を行うシステム。<br>
具体的には、以下のような機能を持つ

- 複数のDockerホストの管理
- コンテナのスケジューリング
- オートスケーリング、ロードバランシング
- ロードバランシング
- コンテナの死活監視
- 障害時のセルフヒーリング
- ログの管理

多数のコンテナから構成され、それらを適切にスケーリングする必要があるシステムにおいて、Kubernetes を導入することで、システムの管理が用意になるというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/103282973-a99a5100-4a1a-11eb-8c1b-9a3511616e58.png" width=915>

上図は Kubernetes のアーキテクチャを示した図である。<br>
Kubernetes は、以下のようなコンポーネントから構成される

- Node : Dockerが動くマシンのこと。
- Pod : コンテナを配置する入れ物で１つ以上のコンテナを持つ。この単位でスケーリングされる。Pod の設定は yaml で記述
- Proxy : コンテナとの通信を経由するプロキシ。
- Deployments : Pod（コンテナ）を複数集めて管理するもの。
- Service : Deployment に対して外部からアクセス可能な IP アドレスを付与し、外部からアクセスできるようにしたもの。Pod群（Deployment）へのロードバランシングやサービスディスカバリを行う

「クラスター > Deployments > Pod > コンテナ」の包含関係？

### ◎ 参考サイト
- https://www.kagoya.jp/howto/rentalserver/kubernetes/

## ■ Kubernetes の構築手順

- yaml ファイルなしで手軽に Pod と Service を作成する場合
    1. GKE でクラスタ作成（GKE使用時）
    1. yaml ファイルなしで Pod と Deployment を作成
    1. Service の作成
    1. 作成した Service の外部 IP アドレスにアクセス
- yaml ファイルでカスタマイズした Pos と Service を作成する場合
    1. GKE でクラスタ作成（GKE使用時）
    1. yaml ファイルなしで Pod を作成
    1. xxx

### ◎ yaml ファイルなしで手軽に Pod と Service を作成する場合

#### 1. GKE でクラスタ作成
Kubernetes マネージドツールとして GKE を使用する場合は、以下のコマンドでクラスターを作成できる

```sh
$ gcloud container clusters create ${CLUSTER_NAME} --num-nodes=
```
- `${CLUSTER_NAME}` : 作成するクラスターの名前（`_` は使用できないことに注意）
- `--nodes` : ノード数（デフォルトでは３）
    - ノートは GCP での VM インスタンスに相当

```sh
# 例
$ gcloud container clusters create k0
```

#### 2. yaml ファイルなしで Pod と Deployment を作成
以下のコマンドで、yaml ファイルなしに手軽に Pod と Deployment を作成できる。

```sh
$ kubectl run  ${DEPLOYMENT NAME/POD NAME PREFIX} --image=${イメージ名}
```
```sh
# 例）nginx を起動する場合
$ kubectl run nginx --image=nginx:1.11.3
```

作成した Pod は、以下のコマンドで確認可能
```sh
$ kubectl get pods
NAME                     READY   STATUS    RESTARTS   AGE
nginx-6968d4c7ff-mtp2s   1/1     Running   0          3m25s
```

#### 3. Service の作成
Service を作成していない状態では、Node 内でコンテナが動いているだけであり、外部からアクセスすることができない状態になっている。<br>
以下のコマンドで Deployment を公開することで、Service とロードバランサーが作成され、外部から指定したIPアドレスにアクセスできるようになる。

```sh
$ kubectl expose deployment ${CLUSTER_NAME} --type LoadBalancer --port ${PORT} --target-port ${TARGET_PORT}
```
- `${PORT}` : インターネット用公開ポート / ex `80`
- `${TARGET_PORT}` : アプリケーション用のポート / ex `8080`

```sh
# 例
$ kubectl expose deployment nginx --port 80 --type LoadBalancer
```

#### 4. 作成した Service の外部 IP アドレスにアクセス
実行中の Service は、以下のコマンドで確認可能
```
$ kubectl get services
NAME         TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)        AGE
kubernetes   ClusterIP      10.107.240.1     <none>         443/TCP        25m
nginx        LoadBalancer   10.107.247.208   34.84.167.20   80:30830/TCP   60s
```

`EXTERNAL-IP` のアドレスに `http://${EXTERNAL-IP}/` でアクセスする(今の場合 http://34.84.167.20/ ) ことで、実行中の Service の動作確認をすることが出来る

作成した Pod のコンテナ内部にアクセスしたい場合は、以下のコマンドでアクセスできる
```sh
$ kubectl exec -it ${Pod名} /bin/bash
```
- ※ node のインスタンスではなく、master のインスタンスにアクセスしている状態になることに注意


Pod 名は、以下のコマンドで確認可能
```
$ kubectl get pod
```


### ◎ yaml ファイルでカスタマイズした Pos と Service を作成する場合
`deployment.yml` に Pod の設定、`service.yml` に Service の設定を記述する。

```yml
# deployment.yml の例
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: web-server
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
  template:
    metadata:
      labels:
        name: web-server
        tier: backend
    spec:
      containers:
      - name: go-server             # コンテナ内：
        image: techeten/go-server
        ports:
        - containerPort: 8080
          protocol: TCP
        imagePullPolicy: Always
      - name: nginx
        image: techeten/nginx
        ports:
        - containerPort: 80
          protocol: TCP
          name: http
        imagePullPolicy: Always
        readinessProbe:
          httpGet:
            # Path to probe; should be cheap, but representative of typical behavior
            path: /readiness.html
            port: 80
          initialDelaySeconds: 30
          timeoutSeconds: 1
```

```yml
# service.yml の例
apiVersion: v1
kind: Service
metadata:
  name: web-server
  labels:
    name: web-server
spec:
  selector:
    name: web-server    # 対象 Pod の label 名を指定
  type: LoadBalancer
  ports:
    - port: 80          # インターネット用公開ポート
      name: http
      targetPort: 80    # アプリケーション用のポート

```

作成した `deployment.yml` に基づき、以下のコマンドで Pod を作成する
```sh
$ kubectl apply -f deployment.yml
```

```sh
# 使用時
$ kubectl apply -f k8s/deployment.yml
```

作成した `service.yml` に基づき、以下のコマンドで Service を作成する
```sh
$ kubectl apply -f service.yml
```

```sh
# 使用時
$ kubectl apply -f k8s/service.yml
```

<!--
## ■ kubectl 基本コマンド

### ◎ yaml ファイルなしで Pod を作成
- `$ kubectl run  ${DEPLOYMENT NAME/POD NAME PREFIX} --image=${イメージ名}`
    ```sh
    # 使用例
    $ kubectl run nginx --image=nginx:1.11.3
    ```
### ◎ 作成済みの Pod を確認
- `$ kubectl get pods`

-->