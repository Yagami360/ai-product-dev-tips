# 【GKE】GoogleマネージドSSL証明書を用いて、GKE 上の Web-API を https 化する

ここでは、GKE 上の Web-API を https 化するための方法として、k8s の Ingress を使用して Google マネージド SSL 証明書を構成し、外部ロードバランサーを作成することで実現する方法を記載する

> - Ingree（上り）<br>
>   k8s における Ingree とは、クラスター内の Service に対して外部からのアクセス(主にHTTP)を管理するAPIオブジェクト。<br>
>   <img src="https://user-images.githubusercontent.com/25688193/130346423-df660c14-cb25-45b0-a147-e10a24ad20c7.png" width="500"><br>

## ■ 方法

1. 固定 IP アドレス（グローバル）を取得する<br>
    ```sh
    $ gcloud compute addresses create ${IP_ADDRESS_NAME} --global
    ```
    ```sh
    $ gcloud compute addresses describe ${IP_ADDRESS_NAME} --global
    ```

1. Web-API のドメインを取得する<br>
    ここでは、[Freenom](https://www.freenom.com/ja/index.html) から無料のドメイン `graph-cut-api.ga` を取得する<br>
    <img src="https://user-images.githubusercontent.com/25688193/130347142-5d6c4542-45cf-433d-a2cd-7f016db9d3c3.png" width="500"><br>

1. SSL 証明書を作成および変更できるための IAM 権限を設定する
    ```sh
    ```

1. Google マネージド SSL 証明書の作成<br>
    1. GUI で行う場合<br>
        1. [Cloud Load Balancing のコンソール画面](https://console.cloud.google.com/net-services/loadbalancing/advanced/sslCertificates/list?hl=ja&_ga=2.120728651.238332542.1629617512-1000767715.1629617512&project=my-project2-303004&folder&organizationId&sslCertificateTablesize=50)に移動する<br>
        1. 「SSL 証明書を作成」ボタンをクリックする<br>
            <img src="https://user-images.githubusercontent.com/25688193/130346734-e42808f3-2928-49d6-87d1-7365e3fa0efa.png" width="500"><br>
        1. 「証明書の作成」画面で「証明書の名前」を入力する<br>
        1. 「Google 管理の証明書を作成する」を選択します。<br>
        1. 「ドメイン」に作成したドメインを入力する<br>
        1. 「作成」ボタンをクリックする<br>
            <img src="https://user-images.githubusercontent.com/25688193/130347326-c4267f76-a315-4169-b18c-fb8eac0fbd99.png" width="500"><br>

    1. CLI で行う場合
        ```sh
        $ gcloud compute ssl-certificates create ${CERTIFICATE_NAME} \
            --description=${DESCRIPTION} \
            --domains=${DOMAINS} \
            --global
        ```
        - `${CERTIFICATE_NAME}` : グローバル SSL 証明書の名前
        - `${DESCRIPTION}` : グローバル SSL 証明書の説明
        - `${DOMAINS}` : この証明書に使用する単一のドメイン名またはドメイン名のカンマ区切りリスト

1. 各種 k8s リソースファイルを作成する
    1. Deployment リソースを作成する
    1. ManagedCertificate リソースを作成する
        ```yaml
        # ManagedCertificate
        apiVersion: networking.gke.io/v1beta2
        kind: ManagedCertificate
        metadata:
            name: graph-cut-api-cert    # ManagedCertificateリソース名を指定
        spec:
            domains:
                - graph-cut-api.ga      # 取得したドメイン名を指定
        ```
    1. Ingress を作成する
        ```yaml
        # Ingress
        apiVersion: networking.k8s.io/v1beta1
        kind: Ingress
        metadata:
            name: graph-cut-api-ingress   # Ingress名を指定
            annotations:
                kubernetes.io/ingress.global-static-ip-name: graph-cut-api-ip       # 用意した静的IPの名前を指定(IPアドレス自体では無い)
                networking.gke.io/managed-certificates: graph-cut-api-cert          # ManagedCertificate で指定した ManagedCertificateリソース名 を指定
        spec:
            backend:
                serviceName: graph-cut-api-server   # Serviceリソースで指定したリソース名を指定
                servicePort: 5000                   # Serviceリソースの portで指定したポート(targetPortでは無い)
        ```
    1. Service リソースを作成する

        > 作成した固定 IP に対応した Service になるようにする

1. GKE 上に Web-API をデプロイする
    ```sh
    $ sh deploy_api_gke.sh
    ```

<!--
1. Google マネージド SSL 証明書を有効化する<br>
    Google マネージド SSL 証明書を有効化（`ACTIVE`）するには、Google マネージド SSL 証明書をロードバランサ、特にロードバランサのターゲットプロキシに関連付ける必要がある。<br>
    既に GKE クラスタを作成している場合は、[Cloud Load Balancing のコンソール画面](https://console.cloud.google.com/net-services/loadbalancing/loadBalancers/list?project=my-project2-303004&hl=ja) に、GKE クラスタ構築時のロードバランサーが作成されているので、このロードバランサーに作成したGoogle マネージド SSL 証明書を関連付け、Google マネージド SSL 証明書を有効化する。

    1. GUI で行う場合

    1. CLI で行う場合
        ```sh
        ```
-->

1. GKE 上の https 化した Web-API にリクエスト処理する
    ```sh
    $ sh run_request_gke.sh
    ```

## ■ 参考サイト
- https://qiita.com/tontoko/items/33faead6bb14370ecb17
- https://qiita.com/teekay/items/135dc67e39f24997019e
- https://cloud.google.com/load-balancing/docs/ssl-certificates/google-managed-certs?hl=ja
- https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs?hl=ja
