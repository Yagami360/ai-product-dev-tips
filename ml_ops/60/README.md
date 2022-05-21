# 【AWS】Amazon EKS を用いて Web API を構築する


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

1. Amazon EKS クラスタにアクセスするための IAM を作成する<br>
    1. IAM ポリシーの内容を定義した json ファイルを作成<br>
        IAM ロールに割り当てるための IAM ポリシーの内容を定義した json ファイルを作成する
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
        - `` : xxx

    1. IAM ロールを作成<br>
        `aws iam create-role` コマンドを使用して、Lambda 関数実行のための IAM ロールを作成する
        ```sh
        aws iam create-role \
            --role-name ${IAM_ROLE_NAME} \
            --assume-role-policy-document "file://${IAM_ROLE_FILE_PATH}"
        ```
        - `--assume-role-policy-document` : IAM ポリシーの内容を定義した json ファイルを指定。

    1. 作成した IAM ロールにアクセス権限を付与する<br>
        作成した IAM ロールに、Lambda サービスにアクセスできるようにするための IAM ポリシーを付与する
        ```sh
        aws iam attach-role-policy \
            --role-name ${IAM_ROLE_NAME} \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        ```

    > IAM の詳細は、「[【AWS】AWS の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/58)」を参考



## ■ 参考サイト
- xxx