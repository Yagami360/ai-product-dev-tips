# 【AWS】AWS Lambda を使用してサーバレス Web-API を構築する

AWS Lambda は、GCP でいうところの Cloud Function に該当するもので、あたかもサーバレスでスクリプトの処理を実行できる機能である。

サーバレスなので、起動中は継続的に料金が発生する EC2 インスタンスとは違い、AWS Lambda にアップロードしたスクリプトの処理中にしか料金が発生せず、コスト削除ができるメリットがある。

ここでは、AWS Lambda を使用してサーバレス Web-API を構築する方法を記載するが、AWS Lambda の実行トリガーには、APIへのリクエスト要求以外にも、様々な実行トリガーが指定可能になっている。

尚、AWS Lambda を使用してサーバレス Web-API を構築するには、API Gateway を併用する方法もあるが、今回の例では、API Gateway を使用せず 関数 URL を使用した方法を記載する

## ■ 方法

### ◎ GUI で行う場合

1. Lambda 関数を作成する<br>
    1. 「[AWS Lambda コンソール画面](https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions)」から「関数を作成」ボタンをクリックする<br>
        <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/169259070-f96281ce-866b-469c-ae80-f0bb1b62ddb8.png"><br>
    1. 「関数の作成」画面から各種必要な値を設定する<br>
        今回は、Python での API コードを１から作成するので、「１から作成」を選択し、ランタイムを「Python」に選択する。<br>
        <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/169259350-e12cbdbb-760a-421e-aad0-c07566d5e087.png"><br>
        > ランタイムには、他にも Node.js などを選択可能

        また「関数 URL を有効化」をクリックする。最後に「関数を作成」ボタンをクリックし、Lambda 関数を作成する<br>
        <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/169260971-951bd9c3-80f3-4745-9aab-b7b6ec4c1686.png"><br>

1. API のコードを修正する<br>
    「[AWS Lambda コンソール画面](https://us-west-2.console.aws.amazon.com/lambda/home?region=us-west-2#/functions)」から、作成した関数を選択し、「コード」タブにあるコードエディター上から、API のコードを修正する
    
    <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/169514981-42f92969-c6ab-46bb-b916-d4046477d0a4.png"><br>

    ```python
    import json

    def lambda_handler(event, context):
        # TODO implement
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    ```

    > API のコードを Docker イメージ化して、その Docker image をアップロードする方法もあるが、今回は AWS のコードエディター上で直接コードを編集する方法を記載している

1. Lambda 関数を呼び出す<br>
    `aws lambda invoke` コマンドを使用すれば、作成した Lambda 関数を呼び出すことができる。或いは、関数 URL を生成した場合は、関数 URL を `curl` コマンドで叩くことでも Lambda 関数を呼び出すこともできる

    - 同期呼び出しする場合<br>
        ```sh
        aws lambda invoke \
            --function-name ${FUNCTION_NAME} \
            --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
            --cli-binary-format raw-in-base64-out response.json
        ```
        - `--cli-binary-format` : `--payload` のフォーマット
            - `raw-in-base64-out` : base64 変換前のフォーマットを base64 に変換

    - 非同期呼び出しする場合<br>
        ```sh
        aws lambda invoke \
            --invocation-type Event \
            --function-name ${FUNCTION_NAME} \
            --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
            --cli-binary-format raw-in-base64-out response.json
        ```

    - 関数 URL を使用する場合<br>
        関数 URL を生成した場合は、関数 URL を `curl` コマンドで叩くことでも Lambda 関数を呼び出すこともできる
        ```sh
        FUNCTION_URL=`aws lambda get-function-url-config --function-name ${FUNCTION_NAME} --query FunctionUrl`
        curl ${FUNCTION_URL}
        ```

        > クエリパラメータなどは、 `curl https://xxx.lambda-url.${REGION}.on.aws/?param1=hoge` のような形式で渡せば良い


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

1. Lambda 関数実行のための IAM を作成する<br>
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

1. API のコードを作成する<br>
    API のコード `lambda_function.py` を作成する
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
    zip -r lambda_function.zip lambda_function.py
    ```

1. Lambda 関数を作成する<br>
    [`aws lambda create-function`](https://docs.aws.amazon.com/cli/latest/reference/lambda/create-function.html) コマンドを使用して、Lambda 関数を作成する
    ```sh
    aws lambda create-function \
        --function-name ${FUNCTION_NAME} \
        --runtime python3.9 \
        --zip-file fileb://lambda_function.zip  \
        --handler "lambda_function.lambda_handler" \
        --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${IAM_ROLE_NAME}
    ```
    - `--zip-file` : Lambda 関数のスクリプトを zip 化したファイル
    - `--handler` : Lambda 関数のスクリプトとエントリーポイントの関数名。`スクリプトのファイル名.エントリーポイントの関数名` の形式で指定する

    > `--role arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-url-role` も必要？

    > ARN [Amazon Resource Name] : AWSサービスのリソースを一意に識別するための命名規則。<br>
    > ```sh
    > # ARN の構文
    > arn:partition:service:region:account-id:resource
    > arn:partition:service:region:account-id:resourcetype/resource
    > arn:partition:service:region:account-id:resourcetype:resource
    > ```
    > ```sh
    > # ARN の例
    > arn:aws:ec2:region:account-id:instance/instance-id
    > arn:aws:ec2:region:account-id:volume/volume-id
    > ```
    > - `partition` : 基本的にAWS
    > - `service` : AWS製品名

1. 関数 URL のエンドポイント作成<br>
    作成した Lambda 関数を関数 URL でアクセスできるようにするためのエンドポイントを作成する
    ```sh
    aws lambda create-function-url-config \
        --function-name ${FUNCTION_NAME} \
        --auth-type NONE
    ```
    - `--auth-type` : 関数 URL の認証タイプ
        - `NONE` : 関数 URL へのリクエストに対して IAM 認証を実行しない。<br>
            内部動作的には、`NONE` を指定した場合、以下の IAM ポリシーが自動的に生成され適用され、これにより関数URLに外部アクセスできるようになる
            ```json
            {
                "StatementId": "FunctionURLAllowPublicAccess",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "lambda:InvokeFunctionUrl",
                "Resource": "arn:aws:lambda:ap-northeast-1:123456789012:function:Lambda_Function_URLs_Policy_Test",
                "Condition": {
                    "StringEquals": {
                       "lambda:FunctionUrlAuthType": "NONE"
                    }
                }
            }
            ```

            > `--auth-type=NONE` を指定して生成した場合、上記 IAM ポリシーが自動的に適用されない動作になり、関数 URL に外部アクセスできなかった。そのため、後述するように、`aws lambda add-permission` コマンドを使用して `--auth-type=NONE` で作成した Lambda 関数に対して、関数URLにアクセスできるようにするためのリソースポリシーを追加する必要がある

        - `AWS_IAM` : 認証された IAM ユーザーとロールのみが、関数 URL にリクエストを行うことができます。

    - `--cors` : CORS 設定
        - 設定例 : `'AllowCredentials=false,AllowMethods=GET,AllowOrigins=*'` : GET メソッドでの全アクセス許可

1. Lambda 関数にリソースポリシーを追加する<br>
    `--auth-type=NONE` で作成した Lambda 関数に対して、関数URLにアクセスできるようにするためのリソースポリシーを追加する
    ```sh
    aws lambda add-permission \
        --function-name ${FUNCTION_NAME} \
        --function-url-auth-type NONE \
        --statement-id FunctionURLAllowPublicAccess \
        --principal "*" \
        --action lambda:InvokeFunctionUrl
    ```

1. Lambda 関数を呼び出す<br>
    `aws lambda invoke` コマンドを使用すれば、作成した Lambda 関数を呼び出すことができる。或いは、関数 URL を生成した場合は、関数 URL を `curl` コマンドで叩くことでも Lambda 関数を呼び出すこともできる

    - 同期呼び出しする場合<br>
        ```sh
        aws lambda invoke \
            --function-name ${FUNCTION_NAME} \
            --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
            --cli-binary-format raw-in-base64-out response.json
        ```
        - `--cli-binary-format` : `--payload` のフォーマット
            - `raw-in-base64-out` : base64 変換前のフォーマットを base64 に変換

    - 非同期呼び出しする場合<br>
        ```sh
        aws lambda invoke \
            --invocation-type Event \
            --function-name ${FUNCTION_NAME} \
            --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
            --cli-binary-format raw-in-base64-out response.json
        ```

    - 関数 URL を使用する場合<br>
        関数 URL を生成した場合は、関数 URL を `curl` コマンドで叩くことでも Lambda 関数を呼び出すこともできる
        ```sh
        FUNCTION_URL=`aws lambda get-function-url-config --function-name ${FUNCTION_NAME} --query FunctionUrl`
        curl ${FUNCTION_URL}
        ```

        > クエリパラメータなどは、 `curl https://xxx.lambda-url.${REGION}.on.aws/?param1=hoge` のような形式で渡せば良い


## ■ 参考サイト
- https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/services-apigateway.html
- https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/gettingstarted-awscli.html
- https://docs.aws.amazon.com/lambda/latest/dg/urls-tutorial.html
- https://qiita.com/ekzemplaro/items/7dc187885dffe0be6341
- https://qiita.com/hayao_k/items/d091081a692f41226d71