# Vertex AI 経由で Claude Code GitHub Actions を利用し Claude API の請求先を GCP にする

## 方法

1. Vertex AI を有効化する

1. Vertex AI 内の Claude モデルの有効化する

    Model Garden から有効化する

    https://console.cloud.google.com/vertex-ai/publishers/anthropic/model-garden/claude-3-7-sonnet

1. カスタム GitHub アプリを作成する

    https://github.com/settings/apps/new

    <img width="500" height="730" alt="Image" src="https://github.com/user-attachments/assets/9b637329-4c83-4e00-b172-266366c9f75b" />

    - Webhooks: 「Active」のチェックを外す
    - Contents: Read & Write
    - Issues: Read & Write
    - Pull requests: Read & Write

    アプリを作成後に、秘密鍵（.pemファイル）を生成してダウンロードし、App ID をメモする

1. 作成した GitHub Appをリポジトリにインストールする

    <img width="500" height="331" alt="Image" src="https://github.com/user-attachments/assets/5cbf0534-8de5-49cb-90fa-e5c1e5eff5d8" />

1. Workload Identity 作成を行なう

    1. Workload Identity Pool の作成

        <img width="500" height="734" alt="Image" src="https://github.com/user-attachments/assets/07ac1fa9-128c-43ec-ad63-69f48fec2675" />

        「IAMと管理」->「Workload Identity連携」から作成可能

        <img width="500" height="734" alt="Image" src="https://github.com/user-attachments/assets/8aee5c42-ade4-4222-85a5-103619ce34fb" />

        - プロバイダー：OIDC
        - プロバイダー詳細：GitHub
        - 発行元： https://token.actions.githubusercontent.com

        <img width="500" height="734" alt="Image" src="https://github.com/user-attachments/assets/f8540262-367a-4d37-ae59-521547c3a934" />

        属性のマッピング

        - google.subject: assertion.sub
        - attribute.repository_owner: assertion.repository_owner
        - attribute.actor: assertion.actor
        - attribute.repository: assertion.repository

        属性条件

        ```bash
        assertion.repository_owner == "Yagami360" && attribute.repository in ["Yagami360/ai-product-dev-tips"]
        ```

    > Workload Identity: GCP が提供するセキュリティ機能で、外部のワークロード（GitHub ActionsやKubernetesのPodなど）がGCPリソースに安全にアクセスできるようにする仕組み。

    > Workload Identity Pool: 外部IDとGoogle Cloudとの紐付けを管理するグループ

    > Workload Identity Provider: 特定の外部IDプロバイダー（例：GitHub Actions）との連携を定義

1. サービスアカウントの作成し、Workload Identity と連携する

    ```bash
    PROJECT_ID=xxx
    PROJECT_NUMBER=1111111111111
    POOL_ID="claude-code-actions-wi-pool"
    SA_NAME="claude-code-actions-sa"
    GITHUB_OWNER="Yagami360"
    REPO_NAME="ai-product-dev-tips"

    # gcloud auth login
    gcloud config set project ${PROJECT_ID}

    # サービスアカウントの作成
    gcloud iam service-accounts create $SA_NAME --display-name $SA_NAME
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

    # 権限を付与
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/aiplatform.user"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/iam.workloadIdentityUser"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="roles/iam.serviceAccountTokenCreator"

    # サービスアカウントをプールに接続
    gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
        --role="roles/iam.workloadIdentityUser" \
        --member="principal://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/subject/${GITHUB_OWNER}/${REPO_NAME}"
    ```

1. GitHub シークレットを追加する

    - `APP_ID`
    - `APP_PRIVATE_KEY` : ダウンロードした秘密鍵（.pemファイル）の内容
    - `GCP_SERVICE_ACCOUNT`: サービスアカウント名
    - `GCP_WORKLOAD_IDENTITY_PROJECT_ID`: Workload Identityを作成した GCP プロジェクトID
    - `GCP_WORKLOAD_IDENTITY_PROVIDER`: `projects/<Google Cloudのプロジェクト番号>/locations/global/workloadIdentityPools/<Workload Identity プール ID>/providers/<Workload Identity プロバイダの表示名またはID>`<br>
        以下のコマンドで取得可能

        ```bash
        gcloud iam workload-identity-pools providers list \
            --workload-identity-pool="claude-code-actions-wi-pool" \
            --location="global"
        ```

1. VertexAI 経由での Claude Code Action の GitHub Action ワークフローを作成する

    [.github/workflows/claude-vertex.yml](../../.github/workflows/claude-vertex.yml)

## 参考サイト

- https://zenn.dev/kimkiyong/articles/0606133ada86f7
- https://techblog.zest.jp/entry/2025/06/23/090000
