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

1. xxx

## ■ 参照サイト

- https://dev.classmethod.jp/articles/relay_looking_back_aws-batch/