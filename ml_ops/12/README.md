# 【GCP】Cloud Build を用いて GCE 上で CI/CD を行う
Cloud Build　は、GCP での CI/CD サービスであるが、以下の図のように、GKE や Cloud Function, Cloud Run などの GCP が提供するサービスとの連携が容易であるというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/115101675-14977580-9f81-11eb-9b38-a66e46cdea1a.png" width="500"><br>

> 今回のケースでは、GCP サービスとして、GCE (ComputeEngine) のみ使用する。

- Cloud Build での CI/CD 練習用レポジトリ<br>
    - [cloud-build-exercises](https://github.com/Yagami360/cloud-build-exercises)

## ■ 手順

1. CI/CD を行う GitHub のレポジトリを作成する
    - ここでは、例として「[cloud-build-exercises](https://github.com/Yagami360/cloud-build-exercises)」というレポジトリ作成する
    - このレポジトリには Flask での api コード `app.py` と、その `dockerfile`、及び Container Registry での docker image の作成や CloudBuild での CI/CD パイプラインを記載したビルド構成ファイル `cloudbuild.yml` が含まれている。

1. 作成したレポジトリの Cloud Source Repositories への登録（ミラーリング）<br>
    1. [Cloud Source Repositories のコンソール画面](https://source.cloud.google.com/onboarding/welcome?hl=ja) に移動し、「リポジトリの追加」画面で、「外部レポジトリを接続」を選択する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101103-7d302380-9f7c-11eb-89fa-d76d1546f0af.png" width="400"><br>
    1. 「外部レポジトリを接続」ボタン選択後に移行する画面で、GCP から GitHub アクセスのための認証を行い、Cloud Source Repositories で管理する GitHub レポジトリを選択する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101325-13187e00-9f7e-11eb-88cc-1a804fb70e40.png" width="400"><br>
    1. レポジトリの接続に成功した場合、以下のような画面が表示される。最新の GitHun レポジトリの内容を反映させるためには、「設定 -> GitHub による同期」ボタンをクリックすればよい。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101438-1fe9a180-9f7f-11eb-9608-063b58a80c77.png" width="400"><br>

    > これらの処理を CLI で自動化できないか？

1. Cloud Build と GitHub の連携設定<br>
    1. [Cloud Build API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com&hl=ja&_ga=2.133252557.250387494.1618392272-443250432.1618392272) を有効化<br>
    1. [Cloud Build GitHub アプリ](https://github.com/marketplace/google-cloud-build) を GitHub に認証する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101875-7b695e80-9f82-11eb-8dd6-4107b46dbd18.png" width="300"><br>
    1. Cloud Build GitHub アプリの認証完了後、Cloud Build の GitHub レポジトリの接続設定画面が表示されるので、CI/CD を行う GitHub のレポジトリを設定する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/115101942-e61a9a00-9f82-11eb-86a5-1026f41a5fdf.png" width="500"><br>
    1. 登録した GitHub レポジトリが、Private 公開の場合は、[非公開 GitHub リポジトリへのアクセス](https://cloud.google.com/cloud-build/docs/access-private-github-repos?hl=ja) 記載の方法で ssh 鍵等の設定を行い、Cloud Build からアクセスできるようにする。

    > これらの処理を CLI で自動化できないか？

1. CI/CD を行う GCP サービスの IAM 権限設定<br>
    「[Cloud Build のサービス アカウント権限](https://console.cloud.google.com/cloud-build/settings/service-account?folder=&organizationId=&project=my-project2-303004)」のページで、Cloud Build で CI/CD を行う GCP サービスの IAM 権限を有効化する。<br>
    
    > 今回は GCE (ComputeEngine) のみ使用するので、ComputeEngine のみ有効化する

<!--
    CLI で行う場合は、以下のようなコマンドで実行できる？
    ```sh
    PROJECT_NUMBER="$(gcloud projects describe ${PROJECT_ID} --format='get(projectNumber)')"
    gcloud projects add-iam-policy-binding ${PROJECT_NUMBER} \
        --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
        --role=roles/container.developer
    ```
-->

1. `cloudbuild.yml` の作成<br>
    Cloud Build がビルドを行うためのビルド構成ファイル `cloudbuild.yml` を作成する。

    > この `cloudbuild.yml` は、Container Registry で docker image を作成するためだけのビルド構成ファイルではなく、｛docker image の作成 ・GCE, GKE, CloudFunctioin などのリソース確保・APIコードの実行・テストコードの実行｝などを含めた、総合的な CI/CD パイプラインを定義したビルド構築ファイルになることに注意

    - `cloudbuild.yml` の構成例（GCE インスタンスで CI/CD を行う場合）
        ```yaml
        ```

1. CI/CD を行うトリガーと `cloudbuild.yml` の設定<br>
    1. [Cloud Build のコンソール画面](https://console.cloud.google.com/cloud-build/triggers?folder=&organizationId=&project=my-project2-303004) から、CI/CD を行うトリガー（git push など）の設定と作成した `cloudbuild.yml` の反映を行う。

    > README.md や .gitignore などのトリガーに含またくないファイルに関しても、この画面の「無視されるファイルフィルタ」から設定できる。

    <img src="https://user-images.githubusercontent.com/25688193/115104516-e66f6100-9f93-11eb-985c-2077ffb99357.png" width="400"><br>


## ■ 参考サイト
- https://cloud.google.com/build/docs/automating-builds/run-builds-on-github?hl=ja
- https://cloud.google.com/kubernetes-engine/docs/tutorials/gitops-cloud-build?hl=ja#shell
- https://cloud.google.com/cloud-build/docs/access-private-github-repos?hl=ja