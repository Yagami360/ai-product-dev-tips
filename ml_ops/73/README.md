# 【AWS】 AWS Batch を使用して簡単なバッチ処理を行う（AWS CLI 使用）

AWS Bacth は、フルマネージド型のバッチ処理実行サービスであり、以下のような特徴がある

> バッチ処理 : 予め定義しておいた処理（ジョブ）を定期実行する仕組み

- ECR に docker image を push して、Amazon ECS 上のコンテナを動かす形でジョブを実行する

- Amazon ECS 上で動作するので、オートスケールも可能

- 依存関係のあるジョブ実行が可能

- ジョブキューに優先度を持たせ、利用リソースの最適化を図れる


<img width="566" alt="image" src="https://user-images.githubusercontent.com/25688193/177032203-6e9aeb5e-b65b-4142-8c10-8884fb208dcd.png">


AWS Batch では、以下のようなコンポーネントから構成される

- ジョブ

- ジョブ定義

- ジョブキュー

- ジョブタイプ


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

1. EC2 インスタンス上でバッチ処理させるコードと Dockerfile を作成する<br>
    - `predict-server/app.py`
        ```python
        ```

    - `predict-server/Dockerfile`
        ```Dockerfile
        ```

1. Amazon ECR に docker image を push する<br>
    EC2 インスタンス上でバッチ処理させるコードの docker image を作成し、Amazon ECR に push する
    ```sh
    # Docker image を作成する
    cd api/predict-server
    docker build ./ -t ${IMAGE_NAME}
    cd ../..

    # ECR リポジトリを作成する
    aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --image-scanning-configuration scanOnPush=true

    # ECR にログインする
    aws ecr get-login-password --profile ${AWS_PROFILE} --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

    # ローカルの docker image に ECR リポジトリ名での tag を付ける
    docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest

    # ECR に Docker image を push する
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
    ```

1. AWS Batch 用の IAM role を作成する<br>

1. EC2 インスタンスを作成する<br>
    新たに作成した EC2 インスタンスで AWS Bacth を実行する場合は、EC2 インスタンスを新規作成する
    1. VPC を作成
    1. サブネットを作成
    1. セキュリティーグループを作成
    1. EC2 インスタンスを作成

1. コンピューティング環境（起動する EC2 インスタンス環境）を作成する<br>
    ```sh
    # コンピューティング環境（起動する EC2 インスタンス環境）を定義した json ファイルを作成する
    cat << EOF > ${COMPUTE_ENV_NAME}.spec.json
    {
        "computeEnvironmentName": "${COMPUTE_ENV_NAME}",
        "type": "MANAGED",
        "state": "ENABLED",
        "computeResources": {
            "type": "EC2",
            "minvCpus": 0,
            "maxvCpus": 4,
            "desiredvCpus": 0,
            "instanceTypes": ["optimal"],
            "subnets": ["${SUBNET_ID_1}", "${SUBNET_ID_2}", "${SUBNET_ID_3}", "${SUBNET_ID_4}"],
            "securityGroupIds": ["${SECURITY_GROUP_ID}"],
            "instanceRole": "arn:aws:iam::${AWS_ACCOUNTID}:instance-profile/ecsInstanceRole"
        },
        "serviceRole": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch"
    }
    EOF

    # 上記 json ファイルを元に、コンピューティング環境（起動する EC2 インスタンス環境）を作成する
    aws batch create-compute-environment --cli-input-json file://${COMPUTE_ENV_NAME}.spec.json
    ```

    - `type` : マネージド型 or アンマネージド型<br>
      `"MANAGED"` を指定するとマネージド型になる

    - `computeResources:minvCpus` : <br>
      `minvCpus` が 0 の場合、ジョブがないときは EC2 インスタンスが削除され、ジョブが発生したら再作成される。`minvCpus` が 1 以上の場合、ジョブがないときでも EC2 インスタンスを起動してしまうので、コスト的に 0 を推奨

    - `computeResources:instanceTypes` : <br>
      `["optimal"]` とした場合、起動するインスタンスタイプは AWS Batch で自動的に判断される。

    - `computeResources.subnets` : サブネットIDを指定。<br>
      今回のケースでは、デフォルトで存在している VPC に紐付けれれた４つにサブネット `SUBNET_ID_1="subnet-fd3dd885"`, `SUBNET_ID_2="subnet-d2292f99"`, `SUBNET_ID_3="subnet-b1f601ec"`, `SUBNET_ID_4="subnet-6fa0cf44"` を指定しているが、新たに VPC & サブネットを作成した場合は、そのサブネットの ID を指定すればよい

    - `computeResources.securityGroupIds` : セキュリティーグループID<br>
      今回のケースでは、デフォルトで存在している VPC に紐付けれれたセキュリティーグループID `SECURITY_GROUP_ID="sg-9c562fd9""` を指定しているが、新たに VPC & セキュリティーグループを作成した場合は、そのセキュリティーグループの ID を指定すればよい     

    - `"serviceRole"` : <br>
      `arn:aws:iam::${AWS_ACCOUNT_ID}:role/service-role/AWSBatchServiceRole` の IAM role は存在しなかったので、存在している IAM role `arn:aws:iam::${AWS_ACCOUNT_ID}:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch` に設定した。

    - `--cli-input-json` : コンピューティング環境を定義した json ファイル

    > `cat << EOF` で、ヒアドキュメント使って json データを指定している

    > 作成したコンピューティング環境を削除する際に、コンピューティング環境に関連づけられて IAM role が存在せず、`INVALID - CLIENT_ERROR ...` のメッセージが出ている場合、上記作成したコンピューティング環境を削除できなくなるのことに注意

1. ジョブキューの作成<br>
    ```sh
    # ジョブキューを作成
    aws batch create-job-queue \
      --job-queue-name ${JOB_QUEUE_NAME} \
      --priority 1 \
      --compute-environment-order order=1,computeEnvironment="arn:aws:batch:${REGION}:${AWS_ACCOUNT_ID}:compute-environment/${COMPUTE_ENV_NAME}" /
      > ${JOB_QUEUE_NAME}.log

    # ジョブキューの ARN を取得
    JOB_QUEUE_ARN=$(jq -r '.jobQueueArn' ${JOB_QUEUE_NAME}.log)
    ```

1. ジョブ定義の作成<br>
    ```sh
    # ジョブ定義を記述した json ファイルを作成する
    cat << EOF > ${JOB_DEFINITION_NAME}.spec.json
    {
      "image": "${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest",
      "command": ["gunicorn", "app:app", "--bind", "0.0.0.0:5001", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--reload", "Ref::Input", "Ref::Output"],
      "vcpus": 1,
      "memory": 500,
      "jobRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/AmazonECSTaskS3FullAccess"
    }
    EOF

    # ジョブ定義を作成する
    aws batch register-job-definition \
      --job-definition-name ${JOB_DEFINITION_NAME} \
      --type container \
      --container-properties file://${JOB_DEFINITION_NAME}.spec.json \
      --parameters "" > ${JOB_DEFINITION_NAME}.log

    # ジョブ定義の ARN を取得
    JOB_DEFINITION_ARN=$(jq -r '.jobDefinitionArn' ${JOB_DEFINITION_NAME}.log)
    echo "JOB_DEFINITION_ARN : ${JOB_DEFINITION_ARN}"
    ```

    - `"image"` : Amazon ECR 上の docker image 名

    - `"command"` : ジョブ実行時に実行するコマンド<br>
      `"Ref::**"` の形式で、`--parameters` で定義した値を参照できる

    - `--parameters` : ジョブ実行時のパラメータ（変数）<br>
        変数は、ジョブ定義を記述した json ファイルにおける、ジョブのコンテナプロパティの `command` フィールドで、`"Ref::**"` の形式で使用することができる

1. ジョブの送信

## ■ 参照サイト

- https://dev.classmethod.jp/articles/relay_looking_back_aws-batch/
- https://qiita.com/aokad/items/e08a9355e76a31711149