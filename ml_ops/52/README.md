# 【Datadog】GCE の各種メトリクスとログデータを Datadog で表示する 

## ■ 方法

1. [Datadog サイト](https://www.datadoghq.com/ja/) から「無料トライアルを開始」ボタンをクリックして、ユーザー登録を行う<br>

  > 無料トライアルの場合でも、会社名の記載が必要であることに注意

1. Datadog　から各種 GCP サービスにアクセスするためのサービスアカウントを作成する。<br>
    サービスアカウントには、「Compute 閲覧者」、「モニタリング閲覧者」、「クラウドアセット閲覧者」の権限を付与する
    ```sh
    ```

1. DataDog の Welcome ページにて、作成したサービスアカウントの json 鍵をアップロードする<br>

  > これらの作業を CLI で自動化できないのか？ Datadog の CLI は存在しないのか？

1. Datadog 左メニューの「Logs」→「Getting Started」→「Cloud」→「Google Cloud Platform」をクリックして選択すると、下記画像のページが出るので、記載された内容を実施していく<br>
  1. GCE のメトリクスやログデータを Datadog に転送するための Cloud Pub/Sub の作成を行う<br>


1. Datadog Dashboard から GCP の各種メトリクスを確認する<br>

1. Datadog Logs から GCP の各種ログデータを確認する<br>


> これらの操作を teraform で自動化することは可能？

## ■ 参考サイト

- https://qiita.com/suzuyui/items/b18a7e686bab69d9ecd2
- https://docs.datadoghq.com/ja/integrations/google_cloud_platform/?tab=datadogussite
