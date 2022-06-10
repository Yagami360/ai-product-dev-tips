# Terraform と GitHub Actions を使用して AWS インスタンスの CI/CD を行う

## ■ 方法

1. `aws configure` コマンドで認証情報を設定する。<br>
    ```sh
    $ aws configure
    ```
    ```sh
    # プロファイル名を別に設定する場合
    $ aws configure --profile ${プロファイル名}
    ```
    - AWS Access Key ID : [AWS の IAM](https://console.aws.amazon.com/iam/home?#/security_credentials) ページの「セキュリティ認証情報」→「アクセスキー (アクセスキー ID とシークレットアクセスキー)」から取得した "アクセスキーID"
    - AWS Secret Access Key : [AWS の IAM](https://console.aws.amazon.com/iam/home?#/security_credentials) ページの「セキュリティ認証情報」→「アクセスキー (アクセスキー ID とシークレットアクセスキー)」から取得した "シークレットアクセスキー"
    - Default region name : EC2インスタンスのリージョン（us-west-2 など）
    - Default output format : "text","json","table" のどれかを指定

    > 上記コマンドで作成された認証情報は、`${HOME}/.aws/credentials` ファイル内に保管される。

1. terraform 用の Dockerfile を作成する
    ```dockerfile
    ```

1. terraform 用の docker-compose を作成する
    ```yaml
    ```

    ポイントは、以下の通り

    - 環境変数 `AWS_ACCESS_KEY_ID`, `` に

    - 但し `docker-compose.yml` にこれら環境変数の値を設定するとキー情報が GitHub 上に公開されてしまうので、`aws_key.env` に、これら環境変数の値を定義し、`aws_key.env` を gitignore するようにしている

    > `cat ${HOME}/.aws/credentials` で確認できる

1. terraform コンテナを起動する
    ```sh
    docker-compose -f docker-compose.yml stop
    docker-compose -f docker-compose.yml up -d
    ```

1. xxx
