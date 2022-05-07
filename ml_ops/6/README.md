# 【BigQuery】BigQuery の基礎事項

<img width="475" alt="image" src="https://user-images.githubusercontent.com/25688193/167242282-37c400e6-a6f8-4baa-aa5b-bdd83d8dbcc8.png">

- BigQuery : <br>
    Google が提供しているクラウド環境でのデータベース管理システム（DBMS）。大量のデータを高速にデータ処理でき、比較的安い領域で利用できるのが大きなメリット<br>
    SQL を使用してデータにアクセスできる<br>

    > 保管可能なデータ形式は、主に csv ファイルと json ファイル。バイナリデータも保存可能であるが、一般的にはテーブルデータを保管する用途で使われる。

    > 画像データセット用途で BigQuery を利用する場合は、その画像データに対して json ファイルなどで画像情報のタグ付け（犬の画像、猫の画像などのタグ）して、その json ファイルを元に、特定の画像データを抽出するような機能にするのが良い？

- BigQueryML : <br>
    BigQuery 上で SQL を使用するだけで、そのまま機械学習モデルの実行を可能にした機能。<br>
    但し、サポートされている機械学習モデルは、主に、データサイエンスのための機械学習モデルであり、｛回帰・分類・クラスタリング・レコメンデーション・時系列予測｝のアプリケーション用途での機械学習モデルに限定されている。
    ```
    [BigQueryML でサポートされている機械学習モデル]
    - 回帰
        - Linear regression（線形回帰）
        - Deep Neural Network（DNN、回帰）
        - XGBoost（回帰）
        - AutoML Tables（回帰）
    - 分類
        - Binary logistic regression（２項分類）
        - Multiclass logistic regression（多項分類）
        - Deep Neural Network（DNN、分類）
        - XGBoost（分類）
        - AutoML Tables（分類）
    - クラスタリング
        - K-means clustering（K 平均法クラスタリング）
    - レコメンデーション
        - Matrix Factorization
    - 時系列予測
        - Time series（ARIMA）
    ```
    > サポートされている機械学習モデルが貧弱すぎて、PoC や R&D 用途とかで全く使えなさそう。なんちゃって機能な印象<br>

    > 画像アプリケーションとかのデータサイエンス領域以外の機械学習アプリケーションでは使えなさそう

- データベース管理システム（DBMS） : <br>

- リレーショナル・データベース（RDB）
    行と列によって構成された「表形式のテーブル」と呼ばれるデータの集合を、互いに関連付けて関係モデルを使ったデータベース

- SQL : <br>

### ◎ BigQuery の用語

- データセット<br>
    データの全体。テーブルの集合から構成される。

- テーブル<br>
    構造化されたデータ(行)の集合

- ジョブ<br>
    ｛クエリ実行・データ追加・テーブルのコピー｝等の処理の実行単位

- クエリ<br>
    データベース管理システムに対する処理要求（問い合わせ）<br>

## ■ 参考サイト
- xxx