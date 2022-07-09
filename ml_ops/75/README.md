# Amazon DynamoDB を使用して NoSQL データベースの CRUD 処理を行う（AWS CLI 使用）

Amazon DynamoDBは、AWS が提供するフルマネージド型の NoSQL データベースで、以下のような特徴を持つ

- NoSQL データベース

    > NoSQL [Not only SQL] データベース : リレーショナルデータベースとは異なり、SQL 言語を使わずにデータ操作ができるデータベース

- Key-Value ストアのデータベースとして使用可能

  > Key-Value ストア : 「値」とそれを取得するための「キー」だけでデータを管理する方法

- ドキュメント型データベースとしても使用可能

    > ドキュメント型データベース : JSONやXMLなどの記述書式で書かれた不定形なデータを管理するデータベース

- 処理速度が速い<br>
    システムの規模にかかわらず、一貫して数ミリ秒台の応答時間をサポートしている

- ストレージ容量が無制限<br>
    Amazon DynamoDBのストレージ容量は、事実上無制限に増やすことが可能。また、Amazon DynamoDB のグローバルテーブルを利用した場合、ストレージの利用状況に合わせて自動的に容量をスケーリングできる

- サーバー管理が不要<br>
    Amazon DynamoDBはサーバーレスで動作する。またスケーリングは負荷状況に応じて、AWS側で自動的にスケールアップ・スケールダウンして調整されるのでサービ管理が不要


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

1. テーブルを作成する<br>
    ```sh
    aws dynamodb create-table --table-name ${TABLE_NAME} \
        --attribute-definitions \
            AttributeName=id,AttributeType=N \
            AttributeName=name,AttributeType=S \
        --key-schema \
            AttributeName=id,KeyType=HASH \
            AttributeName=created_at,KeyType=RANGE \
        --provisioned-throughput \
            ReadCapacityUnits=10,WriteCapacityUnits=10 \
        --table-class STANDARD
    ```

    - `--attribute-definitions` : テーブルの要素名と型を `AttributeName=id,AttributeType=S` のような形式で指定
        - `AttributeType` : データの型
            - `S` : 文字列型
            - `N` : 数値型
            - `B` : バイナリー型

    - ` --key-schema` : テーブルの要素名の key を `AttributeName=xxx,KeyType=HASH` のような形式で指定
        - `KeyType` : キーの種類
            - `HASH` : パーティションキー
            - `RANGE` : ソートキー

        > パーティションキーのみの場合、`KeyType` が `HASH` である要素を1つだけ指定する必要がある。複合キー (パーティションキーとソートキー) の場合は、最初の要素の `KeyType` は `HASH` で、 2 番目の要素の `KeyType` は `RANGE` で指定する必要がある。

    - `--provisioned-throughput` : データベースのスループット（単位時間あたりに処理できるデータ量）

    - `--table-class` : 
        - `STANDARD` : 
        - `STANDARD_INFREQUENT_ACCESS` :

    > 作成したデータベースのテーブルは、「[Amazon DynamoDB コンソール画面](https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#tables)」から確認できる

1. 作成したデータベースの CRUD 処理を行う<br>

    - テーブル一覧の確認<br>
        ```sh
        aws dynamodb list-tables
        ```

    - テーブル詳細の確認<br>
        ```sh
        aws dynamodb describe-table --table-name ${TABLE_NAME}
        ```

    - データベースのテーブルを更新<br>
        ```sh
        aws dynamodb update-table --table-name ${TABLE_NAME} \
	        --provisioned-throughput '{"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}'
        ```

    - データベースのテーブルにアイテム（項目）追加<br>
        ```sh
        aws dynamodb put-item --table-name ${TABLE_NAME} \
        	--item '{ "id": { "N": "1" }, "name": { "S": "yagami" } }'
        ```

        > 追加したアイテムは「[[DynamoDB] -> [項目] のコンソール画面](https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#item-explorer?initialTagKey=)」から確認できる

    - データベースのテーブルの item 取得<br>
        ```sh
        aws dynamodb get-item --table-name ${TABLE_NAME} \
	        --key '{ "id": { "N": "1" }, "name": { "S": "yagami" } }'
        ```

    - データベースを削除する<br>
        ```sh
        aws dynamodb delete-table --table-name ${TABLE_NAME}
        ```

## ■ 参考サイト
- https://www.fenet.jp/aws/column/tool/722/
- https://www.wakuwakubank.com/posts/675-aws-cli-dynamodb/
- https://docs.aws.amazon.com/cli/latest/reference/dynamodb/create-table.html