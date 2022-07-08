# Amazon DynamoDB を使用してデータベースの CRUD 処理を行う（AWS CLI 使用）

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
    ```

## ■ 参考サイト
- https://www.fenet.jp/aws/column/tool/722/
- https://www.wakuwakubank.com/posts/675-aws-cli-dynamodb/