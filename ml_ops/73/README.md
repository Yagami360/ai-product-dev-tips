# 【AWS】 AWS Batch を使用して EC2 インスタンス上で簡単なバッチ処理を行う（AWS CLI 使用）

AWS Bacth は、フルマネージド型のバッチ処理実行サービスであり、以下のような特徴がある

> バッチ処理 : 予め定義しておいた処理（ジョブ）を定期実行する仕組み

- ECR に docker image を push して、Amazon ECS 内の EC2 インスタンス上で動作するコンテナを動かす形でジョブを実行する

- Amazon ECS 上で動作するので、オートスケールも可能

- 依存関係のあるジョブ実行が可能

- ジョブキューに優先度を持たせ、利用リソースの最適化を図れる

<img width="653" alt="image" src="https://user-images.githubusercontent.com/25688193/177789123-48e0c701-9768-4a2f-8161-5b31cefda4b8.png">

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
    - `job/job.py`
        ```python
        import os
        import sys
        import argparse
        from datetime import datetime
        from time import sleep
        import random
        import logging

        # logger
        if not os.path.isdir("log"):
            os.mkdir("log")
        #if( os.path.exists(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log')) ):
        #    os.remove(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
        logger = logging.getLogger(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
        logger.setLevel(10)
        logger_fh = logging.FileHandler(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
        logger.addHandler(logger_fh)

        #
        if __name__ == "__main__":
            parser = argparse.ArgumentParser()
            parser.add_argument('--ok_or_ng', type=str, default="ok" )
            args = parser.parse_args()

            logger.info('[{}] time {} | 処理開始しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
            sleep(10)
            if( args.ok_or_ng == "ok" ):
                logger.info('[{}] time {} | 正常終了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
                sys.exit(0)
            else:
                logger.info('[{}] time {} | 異常終了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
                sys.exit(1)
        ```

    - `job/Dockerfile`
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
    AWS Batch 用の IAM role を作成する。これらの IAM role は、後述のコンピューティング環境を作成する際に使用する

    - `AWSBatchServiceRole`（ARN 名 : `arn:aws:iam::${AWS_ACCOUNTID}:role/AWSBatchServiceRole`）<br>
        AWS Batch が ECS や EC2 などのリソースを操作するためのロールで AWS Batch 自体に付与する<br>
        IAM policy `AWSBatchServiceRole`（ARN 名 : `arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole`）が付与されている

        ```sh
        IAM_ROLE_NAME_1="AWSBatchServiceRole"
        IAM_POLICY_FILE_PATH_1="aws-batch-service-iam-policy.json"
        
        if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME_1}` ] ; then
            # IAM ロールを作成する
            aws iam create-role \
                --role-name ${IAM_ROLE_NAME_1} \
                --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH_1}"

            sleep 10

            # 作成した IAM ロールに IAM ポリシーを付与する
            aws iam attach-role-policy \
                --role-name ${IAM_ROLE_NAME_1} \
                --policy-arn arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole
        fi
        ```

        - `AWSBatchServiceRole` policy
            ```json
            {
              "Version": "2008-10-17",
              "Statement": [
                {
                  "Sid": "",
                  "Effect": "Allow",
                  "Principal": {
                    "Service": "batch.amazonaws.com"
                  },
                  "Action": "sts:AssumeRole"
                }
              ]
            }
            ```

    - `ecsInstanceRole`（ARN 名 : `arn:aws:iam::${AWS_ACCOUNTID}:role/ecsInstanceRole`）<br>
        AWS Batch を実行すると、バックグラウンドで自動的に ECS クラスターが作成され、EC2 インスタンスが起動するが、その EC2 インスタンスに対して ECS を認識させるために付与する IAM role。
        IAM policy `AmazonEC2ContainerServiceforEC2Role`（ARN名：`arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role`）が付与されている

        ```sh
        IAM_ROLE_NAME_2="ecsInstanceRole"
        IAM_POLICY_FILE_PATH_2="aws-batch-ec2-iam-policy.json"
        
        # ecsInstanceRole
        if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME_2}` ] ; then
            # IAM ロールを作成する
            aws iam create-role \
                --role-name ${IAM_ROLE_NAME_2} \
                --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH_2}"

            sleep 10

            # 作成した IAM ロールに IAM ポリシーを付与する
            aws iam attach-role-policy \
                --role-name ${IAM_ROLE_NAME_2} \
                --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role
        fi
        ```

        - `AmazonEC2ContainerServiceforEC2Role` policy
            ```json
            {
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            ```

1. コンピューティング環境（起動する EC2 インスタンス環境）を作成する<br>
    1. コンピューティング環境（起動する EC2 インスタンス環境）を定義した json ファイルを作成する
        ```sh
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
            "serviceRole": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/AWSBatchServiceRole"
        }
        EOF
        ```

        > `cat << EOF` で、ヒアドキュメント使って json データを指定している
        
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

        - `"computeResources.instanceRole"` : 上記 IAM の作成で作成した `ecsInstanceRole` の IAM role の ARN を設定する

        - `"serviceRole"` : 上記 IAM の作成で作成した `AWSServiceRoleForBatch` の IAM role の ARN を設定する<br>

    1. コンピューティング環境（起動する EC2 インスタンス環境）を作成する<br>
        上記 json ファイルを元に、コンピューティング環境（起動する EC2 インスタンス環境）を作成する
        ```sh
        aws batch create-compute-environment --cli-input-json file://${COMPUTE_ENV_NAME}.spec.json
        ```
        - `--cli-input-json` : コンピューティング環境を定義した json ファイル

        > 作成したコンピューティング環境は、「[AWS Batch -> コンピューティング環境のコンソール画面](https://us-west-2.console.aws.amazon.com/batch/home?region=us-west-2#compute-environments)」から確認できる

        > コンピューティング環境を作成することで、AWS Batch が自動的に ECS クラスターを作成し、そのクラスター上で EC2 インスタンスが起動する動作になる

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

    > 作成したジョブキューは、「[AWS Batch -> ジョブキューのコンソール画面](https://us-west-2.console.aws.amazon.com/batch/home?region=us-west-2#queues)」から確認できる

1. ジョブ定義の作成<br>
    1. ジョブ定義を記述した json ファイルを作成する<br>
        ```sh
        cat << EOF > ${JOB_DEFINITION_NAME}.spec.json
        {
          "image": "${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest",
          "command": ["python", "job.py", "--ok_or_ng", "Ref::ok_or_ng"],
          "vcpus": 1,
          "memory": 500,
        }
        EOF
        ```

        - `"image"` : Amazon ECR 上の docker image 名

        - `"command"` : ジョブ実行時に実行するコマンド<br>
          `"Ref::**"` の形式で、`--parameters` で定義した値を参照できる。

        - `"jobRoleArn"`: ジョブ実行に必要な IAM role の ARN<br>
            例えば、ジョブへ S3 へのアクセス権限を付与するには、`"jobRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/AmazonECSTaskS3FullAccess"` とすればよい（予め `AmazonECSTaskS3FullAccess` の IAM role を作成する必要はあり）。今回のケースでは、ジョブが S3 等の AWS リソースを使用していないので省略している

    1. ジョブ定義を作成する<br>
        ```sh
        # ジョブ定義を作成する
        aws batch register-job-definition \
          --job-definition-name ${JOB_DEFINITION_NAME} \
          --type container \
          --container-properties file://${JOB_DEFINITION_NAME}.spec.json \
          --parameters ok_or_ng="ok" > ${JOB_DEFINITION_NAME}.log

        # ジョブ定義の ARN を取得
        JOB_DEFINITION_ARN=$(jq -r '.jobDefinitionArn' ${JOB_DEFINITION_NAME}.log)
        echo "JOB_DEFINITION_ARN : ${JOB_DEFINITION_ARN}"
        ```
        - `--parameters` : ジョブ実行時のパラメータ（変数）<br>
            変数は、ジョブ定義を記述した json ファイルにおける、ジョブのコンテナプロパティの `command` フィールドで、`"Ref::**"` の形式で使用することができる

1. ジョブの送信<br>
    ```sh
    aws batch submit-job \
      --job-name "${JOB_NAME}" \
      --job-queue "${JOB_QUEUE_ARN}" \
      --job-definition "${JOB_DEFINITION_ARN}" \
      --parameters ok_or_ng="ok"
    ```
    
    > 作成したジョブは、「[AWS Batch -> ジョブ のコンソール画面](https://us-west-2.console.aws.amazon.com/batch/home?region=us-west-2#jobs)」から確認できる

    > AWS Batch を実行すると、ECS クラスターが自動的に作成され、ジョブを実行するための EC2 インスタンスも自動的に作成される。そのため、明示的に EC2 インスタンスを作成する必要がないことに注意

1. 出力ログを確認する<br>
  「[CloudWatch のコンソール画面](https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logsV2:log-groups/log-group/$252Faws$252Fbatch$252Fjob)」からログデータを確認する

## ■ 参照サイト

- https://qiita.com/aokad/items/e08a9355e76a31711149
- https://dev.classmethod.jp/articles/aws-batch-getting-started/
- https://dev.classmethod.jp/articles/relay_looking_back_aws-batch/