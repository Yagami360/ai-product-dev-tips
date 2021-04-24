# 【GCP】Cloud Build を用いて GKE（CPU動作）上で CI/CD を行う
Cloud Build　は、GCP で提供されている docker image などのビルドサービスであるが、CI/CD ツールとしても利用できる。<br>
Cloud Build を利用した CI/CD では、以下の図のように、GKE や Cloud Function, Cloud Run などの GCP が提供するサービスとの連携が容易であるというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/115104771-94c7d600-9f95-11eb-913c-a43b578b75b5.png" width="500"><br>

- Cloud Build での CI/CD 練習用レポジトリ<br>
    - [cloud-build-exercises](https://github.com/Yagami360/cloud-build-exercises)

## ■ 手順

1. 各種API（Cloud Build, Google Kubernetes Engine, Container Registry, Resource Manager API） を有効化する。
    - GUI で行う場合
        [APIを有効化](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com%2Crun.googleapis.com%2Ccontainerregistry.googleapis.com%2Ccloudresourcemanager.googleapis.com&%3Bredirect=https%3A%2F%2Fcloud.google.com%2Fbuild%2Fdocs%2Fdeploying-builds%2Fdeploy-cloud-run&hl=ja&_ga=2.252325641.1289183255.1618713667-178468341.1618713667) ページにアクセス

    - CLI で行う場合
        ```sh
        # cloudbuild.googleapis.com : Cloud Build API
        # container.googleapis.com : Kubernetes Engine AP
        # containerregistry.googleapis.com : Container Registry API
        # cloudresourcemanager.googleapis.com : Cloud Resource Manager API
        $ gcloud services enable \
            cloudbuild.googleapis.com \
            container.googleapis.com \
            containerregistry.googleapis.com \
            cloudresourcemanager.googleapis.com
        ```

        > 各種APIサービスは `gcloud services list` で確認可能

1. CI/CD を行う GitHub のレポジトリを作成する
    - ここでは、例として「[cloud-build-exercises](https://github.com/Yagami360/cloud-build-exercises)」というレポジトリ作成する
    - このレポジトリには Flask での api コード `app.py` と、その `dockerfile`、k8s 用のデプロイメント定義ファイル `deployment.yml` とサービス定義ファイル `service.yml`、及び Container Registry での docker image の作成や CloudBuild での CI/CD パイプラインを記載したビルド構成ファイル `cloudbuild.yml` が含まれている。

1. GKE 設定ファイルの作成<br>
    上記 GitHub レポジトリ内に、各種 GKE 設定ファイル（デプロイメント定義ファイル、サービス定義ファイルなど）を作成する。

    - デプロイメント定義ファイルの例<br>
        ```yaml
        apiVersion: apps/v1         # Deployment の API バージョン。kubectl api-resources | grep Deployment と kubectl api-versions  | grep apps で確認可能  
        kind: Deployment            # デプロイメント定義ファイルであることを明示
        metadata:
        name: cloud-build-pod     # 識別名
        spec:
        replicas: 1               # Pod の数
        selector:
            matchLabels:
            app: cloud-build-pod  # template:metadata:labels:app と同じ値にする必要がある
        template:                 # Pod のテンプレート。このテンプレートをもとに ReplicaSet がレプリカ数の Pod を作成する
            metadata:
            labels:                 # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
                app: cloud-build-pod  # 識別名。selector:matchLabels:app と同じ値にする必要がある
            spec:
            containers:           # Pod 内で動作させるコンテナ群の設定
            - image: gcr.io/my-project2-303004/api-sample-image:latest     # Container Registry にアップロードした docker image
                name: api-sample-container                                 # コンテナ名
                ports:
                - containerPort: 8080
                name: http-server
        ```

        > ここでは、docker image のタグ名を `latest` にしているが、`cloudbuild.yml` の `${SHORT_SHA}` と同じ値にできないか？

    - サービス定義ファイルの例
        ```yaml
        apiVersion: v1
        kind: Service
        metadata:
        name: cloud-build-service
        spec:
        type: LoadBalancer
        ports:
            - port: 8080
            targetPort: 8080
            protocol: TCP
        selector:
            app: cloud-build-pod  # デプロイメント定義ファイルで定義した Pod の識別名。app:sample-pod のラベルがつけられた Pod を通信先とする
        ```

1. 作成したレポジトリの Cloud Source Repositories への登録（ミラーリング）<br>
    1. [Cloud Source Repositories のコンソール画面](https://source.cloud.google.com/onboarding/welcome?hl=ja) に移動し、「リポジトリの追加」画面で、「外部レポジトリを接続」を選択する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101103-7d302380-9f7c-11eb-89fa-d76d1546f0af.png" width="400"><br>
    1. 「外部レポジトリを接続」ボタン選択後に移行する画面で、GCP から GitHub アクセスのための認証を行い、Cloud Source Repositories で管理する GitHub レポジトリを選択する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101325-13187e00-9f7e-11eb-88cc-1a804fb70e40.png" width="400"><br>
    1. レポジトリの接続に成功した場合、以下のような画面が表示される。最新の GitHun レポジトリの内容を反映させるためには、「設定 -> GitHub による同期」ボタンをクリックすればよい。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101438-1fe9a180-9f7f-11eb-9608-063b58a80c77.png" width="400"><br>

    > これらの処理を CLI で自動化できないか？

1. Cloud Build と GitHub の連携設定<br>
    1. [Cloud Build GitHub アプリ](https://github.com/marketplace/google-cloud-build) を GitHub に認証する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101875-7b695e80-9f82-11eb-8dd6-4107b46dbd18.png" width="300"><br>
    1. Cloud Build GitHub アプリの認証完了後、Cloud Build の GitHub レポジトリの接続設定画面が表示されるので、CI/CD を行う GitHub のレポジトリを設定する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101942-e61a9a00-9f82-11eb-86a5-1026f41a5fdf.png" width="500"><br>
    1. 登録した GitHub レポジトリが、Private 公開の場合は、[非公開 GitHub リポジトリへのアクセス](https://cloud.google.com/cloud-build/docs/access-private-github-repos?hl=ja) 記載の方法で ssh 鍵等の設定を行い、Cloud Build からアクセスできるようにする。

    > これらの処理を CLI で自動化できないか？

1. CI/CD を行う GCP サービスの IAM 権限設定<br>
    Cloud Build サービスアカウントに「Kubernetes Engine 開発者」と「Kubernetes Engine 管理者」のロールを追加する。

    - GUI で行う場合<br>
        「[Cloud Build のサービス アカウント権限](https://console.cloud.google.com/cloud-build/settings/service-account?folder=&organizationId=&project=my-project2-303004)」のページで、Cloud Build で CI/CD を行う GCP サービスの IAM 権限を有効化する。<br>
        
        > 今回のケースでは、GKE 上で CI/CD を行うので、Kubernetes Engine サービスを有効化する

        上記 IAM 権限設定で「Kubernetes Engine 開発者」の権限は追加さえる、この権限のみでは `cloudbuild.yml` 内で GKE クラスタを作成するようにした場合に、以下のエラーが発生する。
        ```sh
        ERROR: (gcloud.container.clusters.create) ResponseError: code=403, message=Required "container.clusters.create" permission(s) for "projects/85607256401".
        ```
        そのため、「[IAM](https://console.cloud.google.com/iam-admin/iam?hl=ja&project=my-project2-303004)」のページから、Cloud Build サービスアカウント `xxx@cloudbuild.gserviceaccount.com` の編集ボタンをクリックし、「Kubernetes Engine 管理者」のロールも追加する必要がある。

    - CLI で行う場合<br>
        ```sh
        $ PROJECT_NUMBER="$(gcloud projects describe ${PROJECT_ID} --format='get(projectNumber)')"
        # Cloud Build サービスアカウントに「Kubernetes Engine 開発者」のロールを追加
        $ gcloud projects add-iam-policy-binding ${PROJECT_NUMBER} \
            --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
            --role=roles/container.developer

        # Cloud Build サービスアカウントに「Kubernetes Engine 管理者」のロールを追加
        $ gcloud projects add-iam-policy-binding ${PROJECT_NUMBER} \
            --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
            --role=roles/container.admin
        ```

1. `cloudbuild.yml` の作成<br>
    Cloud Build がビルドを行うためのビルド構成ファイル `cloudbuild.yml` を作成する。

    > この `cloudbuild.yml` は、Container Registry で docker image を作成するためだけのビルド構成ファイルではなく、｛docker image の作成 ・GCE, GKE, CloudFunctioin などのリソース確保・APIコードの実行・テストコードの実行｝などを含めた、総合的な CI/CD パイプラインを定義したビルド構築ファイルになることに注意

    - `cloudbuild.yml` の構成例
        ```yaml
        apiVersion: apps/v1         # Deployment の API バージョン。kubectl api-resources | grep Deployment と kubectl api-versions  | grep apps で確認可能  
        kind: Deployment            # デプロイメント定義ファイルであることを明示
        metadata:
        name: cloud-build-pod     # 識別名
        spec:
        replicas: 1               # Pod の数
        selector:
            matchLabels:
            app: cloud-build-pod  # template:metadata:labels:app と同じ値にする必要がある
        template:                 # Pod のテンプレート。このテンプレートをもとに ReplicaSet がレプリカ数の Pod を作成する
            metadata:
            labels:                 # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
                app: cloud-build-pod  # 識別名。selector:matchLabels:app と同じ値にする必要がある
            spec:
            containers:           # Pod 内で動作させるコンテナ群の設定
            - image: gcr.io/my-project2-303004/api-sample-image:latest      # Container Registry にアップロードした docker image
                name: api-sample-container                                    # コンテナ名
                ports:
                - containerPort: 8080
                name: http-server
        ```

        > デフォルトで用意されている定数
        > - `${PROJECT_ID}` : GCP のプロジェクトの ID
        > - `${BUILD_ID}` : ビルドの ID
        > - `${COMMIT_SHA}` : ビルドに関連付けられた commit ID
        >   - docker image 名の tag に指定することで、docker image の tag 名と commit ID を結びつけて管理できるようになる
        > - `${REVISION_ID}` : ビルドに関連付けられた commit ID
        > - `${SHORT_SHA}` : COMMIT_SHA の最初の 7 文字
        > - `${REPO_NAME}` : リポジトリの名前
        > - `${BRANCH_NAME}` : ブランチの名前
        > - `${TAG_NAME}` : タグの名前

        > デプロイメント定義ファイルの docker image のタグ名は、`latest` なので、タグ名として `${SHORT_SHA}` だけでなく、`latest` も付与している

1. CI/CD を行うトリガーと `cloudbuild.yml` の反映<br>
    - GUI で行う場合<br>
        [Cloud Build のコンソール画面](https://console.cloud.google.com/cloud-build/triggers?folder=&organizationId=&project=my-project2-303004) から、CI/CD を行うトリガー（git push など）の設定と作成した `cloudbuild.yml` の反映を行う。

        > README.md や .gitignore などのトリガーに含またくないファイルに関しても、このコンソール画面の「無視されるファイルフィルタ」から設定できる。

    - CLI で行う場合<br>
        ```sh
        $ gcloud beta builds triggers create github \
            --repo-name=${REPO_NAME} \
            --repo-name=${REPO_NAME} \
            --repo-owner=${REPO_OWNER} \
            --branch-pattern=${BRANCH_PATTERN} \
            --build-config=${BUILD_CONFIG_FILE} \
        ```
        - `${TRUGER_NAME}` : トリガー名
        - `${REPO_NAME}` : GitHub のレポジトリ名
        - `${REPO_OWNER}` : GitHub のユーザー名
        - `${BRANCH_PATTERN}` : CI/CD トリガーを発行する git ブランチ名
        - `${BUILD_CONFIG_FILE}` : ビルド構成ファイル `cloudbuild.yml` のパス
    
1. CI/CD を行うトリガーを発行する
    例えば、`gke` ブランチへの push をトリガーとしている場合は、以下のコマンドを実行することで、CloudBuild がトリガー検知し、`cloudbuild.yml` に基づく CI/CD が自動的に実行される。
    ```sh
    $ git checkout -b gke
    $ git add .
    $ git commit -m "a"
    $ git push origin master
    ```

1. ビルドログを確認する
    [ビルド履歴の画面](https://console.cloud.google.com/cloud-build/builds?project=my-project2-303004) からビルドログを確認し、うまく CI/CD できているか確認する<br>
    CLIで確認する場合は、以下のコマンドで確認できる
    ```sh
    $ gcloud builds describe ${BUILD_ID}
    ```

1. テスト用コードを実行し、動作確認する<br>
    ビルド成功後、テスト用コードを実行し動作確認する<br>
    例えば、作成した Cloud Run に `curl` コマンドでリクエスト処理するテストコードの場合は、以下のコマンドで動作確認できる。
    ```sh
    $ EXTERNAL_IP=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
    $ curl -X POST http://${EXTERNAL_IP}:${PORT} -H "Content-Type: application/json" -d '{"message" : "Hello Cloud Build on GKE !!!"}'
    ```
    - `${SERVICE_NAME}` : 作成した Cloud Run の名前


## ■ 参考サイト
- https://cloud.google.com/build/docs/deploying-builds/deploy-gke?hl=ja
- https://cloud.google.com/kubernetes-engine/docs/tutorials/gitops-cloud-build?hl=ja#shell