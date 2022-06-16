# GitHub Actions, Terraform, ArgoCD を使用して GKE 上の Web-API の CI/CD を行う

- 対象レポジトリ
    - https://github.com/Yagami360/terraform-github-actions-argocd-gke-cicd-exercises

## ■ 方法

1. GCR 用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
    xxx

1. GKE クラスター用の Terraform のテンプレートファイル（*.tf形式）を作成する。<br>
    xxx

1. GitHub Actions の Workflow ファイルを作成する<br>

    ```yaml
    ```

    ポイントは、以下の通り

    - GCP の IAM ユーザーの認証情報を設定<br>
        定義済み action `google-github-actions/auth` を使用して、GCP の認証処理を行っている。

        - GitHub Actions 用のサービスアカウントの json キーを設定する場合<br>
            xxx

        - GitHub Actions 用のサービスアカウントに Workload Identity 連携を行う場合<br> 
            xxx


## ■ 参考サイト

- https://dev.classmethod.jp/articles/google-cloud-auth-with-workload-identity/