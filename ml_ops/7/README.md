# 【BigQuery】BigQuery を使用したデータ処理（GUI使用時）

## ■ 事前準備（一般公開データセットを使用）
1. BigQuery API を有効化する
1. [BigQuery のウェブ UI ページ](https://console.cloud.google.com/bigquery?hl=ja&project=my-project2-303004) にアクセス<br>
1. Google が一般公開している一般公開データセットをプロジェクトに追加したい場合は、以下のコマンドでサイトにアクセスする<br>
    ```sh
    $ open https://console.cloud.google.com/bigquery?p=bigquery-public-data&page=project
    ```

## ■ データセットを作成する

1. 指定したプロジェクトで、「データセットを作成」ボタンをクリックして、空のデータセットを作成する<br>
    <img src="https://user-images.githubusercontent.com/25688193/106879123-18f01880-671e-11eb-96b3-831667955381.png" width="500"><br>
1. 作成した空のデータセットに対して、「テーブルを作成」ボタンをクリックし、次のテーブルの作成ページに移動する。<br>
    <img src="https://user-images.githubusercontent.com/25688193/106879156-21e0ea00-671e-11eb-85fb-58dcdf4e9aee.png" width="500"><br>
1. テーブルの作成ページにて、以下の操作を行う。<br>
    <img src="https://user-images.githubusercontent.com/25688193/106880922-48078980-6720-11eb-8563-2490bb2a0085.png" width=""><br>
    1. アップロードしたファイルからテーブルを作成する場合は、「テーブルの作成元」を「アップロード」に選択し、対象ファイル（通常 csv ファイルか json ファイル）をアップロードする。
    1. 「テーブル名」を入力する
    1. スキーマ（テーブルの各要素のデータ型指定）を自動的に行う場合は、自動検出チェックボックスをクリックする
    <!--
    1. スキーマ（テーブルの各要素のデータ型指定）を「テキストとして編集ボタン」をクリックし、以下のようなスキーマ定義を入力する。
        ```sql
        POM:integer,Description:string,Length:float
        ```
    -->
1. 作成したテーブルデータは、「プレビュー」タグから閲覧できる。
    <img src="https://user-images.githubusercontent.com/25688193/106881667-2bb81c80-6721-11eb-8bae-5ee9a635e3fe.png" width=""><br>


## ■ クエリ（処理要求）を実行する（一般公開データセット使用）

- クエリ（処理要求）を実行する
    xxx

- クエリ（処理要求）を実行する（一般公開データセット使用）
    例えば、一般公開データセット（PROJECT_ID=`bigquery-public-data`）の `usa_names` データセットの `usa_1910_2013` テーブルに対してクエリを実行する場合は、以下のような処理となる<br>
    1. 「クエリを新規作成」ボタンをクリック<br>
    1. 以下のクエリコード（SQL）を、エディタフィールドに貼り付け<br>
        ```sql
        SELECT
            name, gender,
            SUM(number) AS total
        FROM
            `bigquery-public-data.usa_names.usa_1910_2013`
        GROUP BY
            name, gender
        ORDER BY
            total DESC
        LIMIT
            10
        ```
    1. 「実行」ボタンをクリック<br>
    1. クエリの結果フィールドにクエリの実行結果が表示される<br>
        <img src="https://user-images.githubusercontent.com/25688193/106378265-b2e65700-63e6-11eb-95ee-66164f6fd17f.png" width="800">

## ■ 参考サイト
- https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui?hl=ja&_ga=2.65098990.-1151485257.1612079281
