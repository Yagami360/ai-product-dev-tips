# 【AWS】 AWS Step Functions を使用して複数の AWS Lambda を順次実行する

AWS Step Functions は、Lambda / DynamoDB / SNS / SQS などの各種 AWS リソースと連携して、それらの AWS リソース実行を一連のステップとして順次実行するためのサーバーレスのワークフローであり、このワークフローを状態遷移図（ステートマシン）で可視化することもできる<br>

<img width="300" alt="image" src="https://user-images.githubusercontent.com/25688193/183925557-868e207f-6ca8-4630-99e4-ea2a6517e85b.png"><br>

状態遷移図（ステートマシン）のどのステップでエラーが起きたかも分かるので、例えばデプロイした API の自動テストなどでも使用できる。

ステートマシンは、ASL [Amazon States Language] と呼ばれる json 形式での独自言語を用いて定義する

## ■ ToDo

- [ ] CLI でステートマシンを構築した際に、IAM 権限関連で lambda 関数の呼び出しに失敗するエラーの解決

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

1. lambda 関数のコードを作成する<br>
    lambda 関数のコードを作成する。今回は、Step Funtions で２つの lambda 関数を使うので、２つの lambda 関数を作成する

    - `lambda_function_1.py`<br>
        ```python
        import json

        def lambda_handler(event, context):
            # TODO implement
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda!')
            }
        ```

    - `lambda_function_2.py`<br>
        ```python
        import json

        def lambda_handler(event, context):
            # TODO implement
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from Lambda!')
            }
        ```

1. lambda 関数のコードを zip ファイルにする<br>
    ```sh
    zip -r lambda_function_1.zip lambda_function_1.py
    zip -r lambda_function_2.zip lambda_function_2.py
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

1. 【オプション】Lambda 関数を呼び出す<br>
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


1. AWS Step Functions を作成する<br>
    - コンソール画面から行う場合<br>
        1. 「[AWS Step Functions コンソール画面](https://us-west-2.console.aws.amazon.com/states/home?region=us-west-2#/statemachines)」にブラウザアクセスし、「ステートマシンの作成」ボタンをクリックする

        1. 「ワークフローを視覚的に作成」を選択し、「」ボタンをクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/183927696-e5950b43-fa6d-4b5a-9bad-48aeff3a9eb5.png"><br>

        1. 左側の各種 AWS リソースから Lambda 関数をドラック＆ドロップし、Funtion name から先で作成した lambda 関数を選択する。<br>
            <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/183928058-c5391426-f616-40e1-a46b-54c089602413.png"><br>
            <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184059901-1ecc4d09-bb18-4d1d-898b-cc889dba3174.png"><br>

        1. ステートマシンを構築したら、「次へ」ボタンをクリックする<br>

        1. 「ステートマシン設定を指定」画面にて、「新しいロールの作成」を選択し、「ステートマシンを作成」ボタンをクリックする<br>
            <img width="850" alt="image" src="https://user-images.githubusercontent.com/25688193/184060250-4b27aed2-a957-4e14-b6e5-6390b49cf88d.png"><br>

    - CLI から行う場合<br>
        1. AWS Step Functions 用の IAM ポリシーの内容を定義した json ファイルを作成<br>
            IAM ロールに割り当てるための IAM ポリシーの内容を定義した json ファイルを作成する
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "states.us-west-2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            ```

        1. AWS Step Functions 用の IAM ロールを作成<br>
            `aws iam create-role` コマンドを使用して、Lambda 関数実行のための IAM ロールを作成する
            ```sh
            aws iam create-role \
                --role-name ${STEPFUNTIONS_IAM_ROLE_NAME} \
                --assume-role-policy-document "file://${STEPFUNTIONS_IAM_POLICY_FILE_PATH}"
            ```
            - `--assume-role-policy-document` : IAM ポリシーの内容を定義した json ファイルを指定。

        1. 作成した IAM ロールにアクセス権限を付与する<br>
            作成した IAM ロールに、lambda 関数にアクセスできるようにするための IAM ポリシーを付与する
            ```sh
            aws iam attach-role-policy \
                --role-name ${STEPFUNTIONS_IAM_ROLE_NAME} \
                --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
            ```
            
        1. ステートマシンを定義した json ファイルを作成する<br>
            ```json
            {
                "Comment": "A description of my state machine",
                "StartAt": "hellow-lambda",
                "States": {
                "hellow-lambda": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                    "Payload.$": "$",
                    "FunctionName": "arn:aws:lambda:us-west-2:735015535886:function:lambda-function-1:$LATEST"
                    },
                    "Retry": [
                    {
                        "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException"
                        ],
                        "IntervalSeconds": 2,
                        "MaxAttempts": 6,
                        "BackoffRate": 2
                    }
                    ],
                    "Next": "world-lambda"
                },
                "world-lambda": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                    "Payload.$": "$",
                    "FunctionName": "arn:aws:lambda:us-west-2:735015535886:function:lambda-function-2:$LATEST"
                    },
                    "Retry": [
                    {
                        "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException"
                        ],
                        "IntervalSeconds": 2,
                        "MaxAttempts": 6,
                        "BackoffRate": 2
                    }
                    ],
                    "End": true
                }
                }
            }
            ```

            > CLI で行う場合でも、この json ファイルの作成部分のみ、AWS Step Functions のコンソール画面から行う方法のほうが便利

        1. ステートマシンを作成する<br>
            ```sh
            aws stepfunctions create-state-machine \
                --name ${STATEMACHINE_NAME} \
                --definition file://${STATEMACHINE_DEFINITION_FILE_PATH} \
                --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/${STEPFUNTIONS_IAM_ROLE_NAME}
            ```

1. AWS Step Functions を実行する<br>
    - コンソール画面から行う場合<br>
        1. 作成したステートマシンを選択し、「実行の開始」ボタンをクリックする<br>
        1. 実行後、以下のような状態遷移図と共に実行結果を確認できる。<br>
            <img width="850" alt="image" src="https://user-images.githubusercontent.com/25688193/184060650-4ffb3852-15dc-470f-b921-1c4e209b845f.png">

            > 実行に失敗した場合は、ステートマシンのステップが赤枠になるので、失敗した箇所を視覚的に確認できる

    - CLI から行う場合<br>
        1. 実行用入力データを定義した json ファイルを作成する<br>
            例えば、以下のような json ファイルを作成する
            ```json
            {
                "Comment": "Insert your JSON here"
            }
            ```

        1. ステートマシンを実行する<br>
            ```sh
            aws stepfunctions start-execution \
                --name ${EXECUTION_NAME} \
                --state-machine-arn arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${STATEMACHINE_NAME} \
                --input file://${STATEMACHINE_INPUT_JSON_PATH}
            ```
            > `--name` を省略すると、自動的に実行名が割り当てられる

        1. ステートマシンの実行結果を確認する<br>
            ```sh
            aws stepfunctions describe-execution \
                --execution-arn arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${STATEMACHINE_NAME}:${EXECUTION_NAME}
            ```

        1. 実行後、AWS Step Functions のコンソール画面から実行結果を確認する<br>
            <img width="850" alt="image" src="https://user-images.githubusercontent.com/25688193/184060650-4ffb3852-15dc-470f-b921-1c4e209b845f.png">

            > 実行に失敗した場合は、ステートマシンのステップが赤枠になるので、失敗した箇所を視覚的に確認できる

## ■ 参照サイト

- https://docs.aws.amazon.com/ja_jp/step-functions/latest/dg/getting-started.html
- https://dev.classmethod.jp/articles/aws-step-functions-for-beginner/
- https://dev.classmethod.jp/articles/aws-step-functions-with-aws-cli/
