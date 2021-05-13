# 【GCP】【GCP】Cloud Build を用いて Cloud Run 上で CI/CD を行う
Cloud Build　は、GCP で提供されている docker image などのビルドサービスであるが、CI/CD ツールとしても利用できる。<br>
Cloud Build を利用した CI/CD では、以下の図のように、GKE や Cloud Function, Cloud Run などの GCP が提供するサービスとの連携が容易であるというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/115104771-94c7d600-9f95-11eb-913c-a43b578b75b5.png" width="500"><br>

ここでは、Cloud Build での CI/CD 処理のデプロイ先として Cloud Run を選んだ場合の手順を示す。

- 【参考】Cloud Build での CI/CD 練習用レポジトリ<br>
    - [cloud-build-exercises](https://github.com/Yagami360/cloud-build-exercises)

## ■ 手順

1. 各種API（Cloud Build, Cloud Run, Container Registry, Resource Manager API） を有効化する。
    - GUI で行う場合
        [APIを有効化](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com%2Crun.googleapis.com%2Ccontainerregistry.googleapis.com%2Ccloudresourcemanager.googleapis.com&%3Bredirect=https%3A%2F%2Fcloud.google.com%2Fbuild%2Fdocs%2Fdeploying-builds%2Fdeploy-cloud-run&hl=ja&_ga=2.252325641.1289183255.1618713667-178468341.1618713667) ページにアクセス

    - CLI で行う場合
        ```sh
        # cloudbuild.googleapis.com : Cloud Build API
        # run.googleapis.com : Cloud Run Admin API
        # containerregistry.googleapis.com : Container Registry API
        # cloudresourcemanager.googleapis.com : Cloud Resource Manager API
        $ gcloud services enable \
            cloudbuild.googleapis.com \
            run.googleapis.com \
            containerregistry.googleapis.com \
            cloudresourcemanager.googleapis.com
        ```

        > 各種APIサービスは `gcloud services list` で確認可能

1. CI/CD を行う GitHub のレポジトリを作成する
    - ここでは、例として「[cloud-build-exercises](https://github.com/Yagami360/cloud-build-exercises)」というレポジトリ作成する
    - このレポジトリには Flask での api コード `app.py` と、その `dockerfile`、及び Container Registry での docker image の作成や CloudBuild での CI/CD パイプラインを記載したビルド構成ファイル `cloudbuild.yml` が含まれている。

    > Cloud Run でのポート番号は、デフォルトで `8080` 番ポートになるので、dockerfile での開放ポート番号は `8080` 番ポートにする必要があることに注意

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
    - GUI で行う場合
        「[Cloud Build のサービス アカウント権限](https://console.cloud.google.com/cloud-build/settings/service-account?folder=&organizationId=&project=my-project2-303004)」のページで、Cloud Build で CI/CD を行う GCP サービスの IAM 権限を有効化する。<br>
        
        > 今回のケースでは、Cloud Run 上で CI/CD を行うので、Cloud Run サービスを有効化する

    - CLI で行う場合<br>
        > これらの処理を CLI で自動化できないか？<br>
        > `gcloud projects add-iam-policy-binding ${PROJECT_NUMBER}` で可能？

1. `cloudbuild.yml` の作成<br>
    Cloud Build がビルドを行うためのビルド構成ファイル `cloudbuild.yml` を作成する。

    > この `cloudbuild.yml` は、Container Registry で docker image を作成するためだけのビルド構成ファイルではなく、｛docker image の作成 ・GCE, GKE, CloudFunctioin などのリソース確保・APIコードの実行・テストコードの実行｝などを含めた、総合的な CI/CD パイプラインを定義したビルド構築ファイルになることに注意

    - `cloudbuild.yml` の構成例
        ```yaml
        # 変数値の置換
        substitutions:
        _IMAGE_NAME: api-sample-image       # docker image 名
        _SERVICE_NAME: cloud-build-sample   # 作成する cloud run 名
        _REGION: us-central1                # cloud run を作成するリージョン

        # name タグ : コマンドを実行するコンテナイメージ
        # entrypoint タグ : name で指定したコンテナイメージのデフォルトのエントリーポイント（dockerコンテナなら docker コマンドなど）を使用しない場合に指定
        steps:
        # キャッシュされたイメージを Container Registry から pull
        # 初めてイメージをビルドする際は docker pull で pull できる既存のイメージがないため、entrypoint を bash に設定し、コマンドの実行で返されるエラーを無視できるようにしている
        - name: 'gcr.io/cloud-builders/docker'
            entrypoint: 'bash'
            args: ['-c', 'docker pull gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:${COMMIT_SHA} || exit 0']

        # Container Registry 上で docker image 作成
        - name: 'gcr.io/cloud-builders/docker'  # Docker を実行するコンテナイメージ
            id: docker build
            args: [
                'build', 
                '-t', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:${COMMIT_SHA}', 
                '--cache-from', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:${COMMIT_SHA}',
                './api'
            ]

        # Container Registry 上で docker image を登録
        - name: 'gcr.io/cloud-builders/docker'
            id: docker push
            args: ['push', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:${COMMIT_SHA}']

        # Cloud Run 作成し、docker image を Cloud Run にデプロイ
        - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
            entrypoint: gcloud
            args: [
                'run', 'deploy', '${_SERVICE_NAME}', 
                '--image', 'gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:${COMMIT_SHA}', 
                '--region', '${_REGION}', 
                '--platform', 'managed',
                '--allow-unauthenticated'   # IAM 認証なし
            ]

        # ビルド完了後の docker image を Container Registry に保管
        images: ['gcr.io/${PROJECT_ID}/${_IMAGE_NAME}:${COMMIT_SHA}']
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

1. CI/CD を行うトリガーと `cloudbuild.yml` の反映<br>
    - GUI で行う場合<br>
        [Cloud Build のコンソール画面](https://console.cloud.google.com/cloud-build/triggers?folder=&organizationId=&project=my-project2-303004) から、CI/CD を行うトリガー（git push など）の設定と作成した `cloudbuild.yml` の反映を行う。

        > README.md や .gitignore などのトリガーに含またくないファイルに関しても、このコンソール画面の「無視されるファイルフィルタ」から設定できる。

    - CLI で行う場合<br>
        ```sh
        ```sh
        $ gcloud beta builds triggers create github \
            --repo-name=${REPO_NAME} \
            --repo-name=${REPO_NAME} \
            --repo-owner=${REPO_OWNER} \
            --branch-pattern="^${TRIGER_BRANCH_NAME}$" \
            --build-config=${BUILD_CONFIG_FILE} \
        ```
        - `${TRUGER_NAME}` : トリガー名
        - `${REPO_NAME}` : GitHub のレポジトリ名
        - `${REPO_OWNER}` : GitHub のユーザー名
        - `${BRANCH_PATTERN}` : CI/CD トリガーを発行する git ブランチ名（正規表現で複数のブランチも指定可能）
        - `${BUILD_CONFIG_FILE}` : ビルド構成ファイル `cloudbuild.yml` のパス


1. CI/CD を行うトリガーを発行する
    例えば、`cloud_run` ブランチへの push をトリガーとしている場合は、以下のコマンドを実行することで、CloudBuild がトリガー検知し、`cloudbuild.yml` に基づく CI/CD が自動的に実行される。
    ```sh
    $ git checkout -b cloud_run
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
    $ CLOUD_RUN_URL=`gcloud run services list --platform managed | grep ${SERVICE_NAME} | awk '{print $4}'`
    $ curl -X POST ${CLOUD_RUN_URL} -H "Content-Type: application/json" -d '{"message" : "Hello Cloud Build on Cloud Run !!!"}'
    ```
    - `${SERVICE_NAME}` : 作成した Cloud Run の名前


## ■ 参考サイト
- https://cloud.google.com/build/docs/deploying-builds/deploy-cloud-run?hl=ja