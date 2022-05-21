# 【AWS】AWS の認証システム

## ■ 基本事項

<img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/169637727-58b0c88e-adf2-4d14-b5a6-3a063cc7dd44.png">

- IAM [Identity and Access Management]<br>
    AWS のリソースに対して、誰（メンバー）がどのようなアクセス権（ロール）を持つか定義し、アクセス制御を管理する機能

- IAM ポリシー<br>
    各種 AWS サービスに対してのどのようなアクセス権を持つかを json 形式で定義したもの。この IAM ポリシー を IAM ユーザーや IAM ロールに割り当てることで、「誰が」その権限を持つのかといったことを決定できる。

    作成済みの IAM ポリシーは、「[AWS の IAM のコンソール画面](https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/policies)」から確認できる

    IAM ポリシーには、以下の３つの種類がある

    1. AWS 管理ポリシー<br>
        AWS が元々用意している再利用可能なポリシー

    1. カスタマー管理ポリシー<br>
        ユーザーが作成した再利用可能なポリシー

    1. インラインポリシー<br>
        各 IAM ユーザー・IAMグループ・IAMロール専用に、ユーザーが個別作成するポリシー

    > - リソースポリシー
    > xxx

    > - 信頼ポリシー<br>
    > xxx

    > - AssumeRolePolicy<br>
    > xxx


    IAM ポリシーを定義した json ファイルの中身は、以下のようになる
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    ```
    - `"Version"` : `"2012-10-17"` で固定
    - `"StatementId"` : 省略可
    - `"Effenct"` : `"Allow"` or `"Deny"` を設定。`"Allow"` の場合は、`"Action"` を許可。`"Deny"` の場合は、`"Action"` を拒否
    - `"Action"` :  
    - `"Resource"` : Actionで設定した操作を適用できるリソース(範囲)を設定


- IAM ロール<br>
    （ユーザーやグループではなく）AWS サービス（EC2など）に対して、アクセス権（ロール）を付与するための機能。

    作成済みの IAM ロールは、「[AWS の IAM のコンソール画面](https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/roles)」から確認できる

- IAM ユーザ<br>
    xxx

- IAM グループ<br>
    xxx

- ARN [Amazon Resource Name]<br>
    ARN は、AWSサービスのリソースを一意に識別するための命名規則。<br>
    IAM ロールに IAM ポリシーを割り当てる際に AWS リソースを指定するケースなどで利用する
    ```sh
    # IAM ロールに IAM ポリシーを割り当てる。--policy-arn に ARN 形式で指定する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    ```

    ```sh
    # ARN の構文
    arn:partition:service:region:account-id:resource
    arn:partition:service:region:account-id:resourcetype/resource
    arn:partition:service:region:account-id:resourcetype:resource
    ```
    ```sh
    # ARN の例
    arn:aws:ec2:region:account-id:instance/instance-id
    arn:aws:ec2:region:account-id:volume/volume-id
    ```
    - `partition` : 基本的にAWS
    - `service` : AWS製品名

## ■ 参考サイト
- xxx