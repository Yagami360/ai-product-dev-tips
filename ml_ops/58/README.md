# 【AWS】AWS Lambda を使用してサーバレス Web-API を構築する

AWS Lambda は、GCP でいうところの Cloud Function に該当するもので、あたかもサーバレスでスクリプトの処理を実行できる機能である。

サーバレスなので、起動中は継続的に料金が発生する EC2 インスタンスとは違い、AWS Lambda にアップロードしたスクリプトの処理中にしか料金が発生せず、コスト削除ができるメリットがある。

ここでは、AWS Lambda を使用してサーバレス Web-API を構築する方法を記載するが、AWS Lambda の実行トリガーには、APIへのリクエスト要求以外にも、様々な実行トリガーが指定可能になっている。

## ■ 方法

### ◎ GUI で行う場合

1. Lambda 関数を作成する<br>
    1. 「[AWS Lambda コンソール画面](https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions)」から「関数を作成」ボタンをクリックする<br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/169259070-f96281ce-866b-469c-ae80-f0bb1b62ddb8.png"><br>
    1. 今回は、FastAPI での API コードを１から作成するので、「１から作成」を選択し、ランタイムを「Python」に選択する。また「関数 URL を有効化」をクリックする。最後に「関数を作成」ボタンをクリックし、Lambda 関数を作成する<br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/169259350-e12cbdbb-760a-421e-aad0-c07566d5e087.png"><br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/169260971-951bd9c3-80f3-4745-9aab-b7b6ec4c1686.png"><br>

        > ランタイムには、他にも Node.js などを選択可能

    1. xxx

1. API のコードを修正する<br>
    xxx

1. Lambda 関数を呼び出す<br>
    xxx

### ◎ CLI で行う場合

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

1. Lambda 関数実行のための IAM 権限を作成する<br>
    1. IAM 権限の内容を定義した json ファイルを作成<br>
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
    1. `aws iam create-role` コマンドで IAM 権限を作成<br>
        ```sh
        aws iam create-role \
            --role-name ${IAM_ROLE_NAME} \
            --assume-role-policy-document "file://${IAM_ROLE_FILE_PATH}"
        ```
    1. 作成した IAM 権限にアクセス権限を付与する<br>
        ```sh
        aws iam attach-role-policy \
            --role-name ${IAM_ROLE_NAME} \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        ```

1. API のコードを作成する<br>
    ```python
    import json

    def lambda_handler(event, context):
        # TODO implement
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    ```

1. API コードを zip ファイルにする<br>
    ```sh
    zip -r app.zip app.py
    ```

1. Lambda 関数を作成する<br>
    [`aws lambda create-function`](https://docs.aws.amazon.com/cli/latest/reference/lambda/create-function.html) コマンドを使用して、Lambda 関数を作成する
    ```sh
    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --runtime python3.9 \
        --zip-file fileb://app.zip  \
        --handler "lambda_handler" \
        --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${IAM_ROLE_NAME}
    ```
    - `--zip-file` : Lambda 関数のスクリプトを zip 化したファイル
    - `--handler` : Lambda 関数のスクリプト内のエントリーポイントの関数名

1. Lambda 関数を呼び出す<br>
    ```sh
    aws lambda invoke \
        --invocation-type Event \
        --function-name ${FUNCTION_NAME} \
        --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
        outputfile.txt
    ```

<!--
1. API Gatewayの設定<br>
-->

## ■ 参考サイト
- https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/services-apigateway.html
- https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/gettingstarted-awscli.html
- https://qiita.com/ekzemplaro/items/7dc187885dffe0be6341