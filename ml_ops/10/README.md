# 【Terraform】Terraform の基礎事項

- インフラのコード化（Infrastructure as Code）<br>
    サーバーなどのインフラを GCP などのクラウドサービスの GUI を用いて構築したり、サーバーに ssh ログインして必要なライブラリをインストール方法では、「別環境を作る際にまた手動で同じ作業を行う必要がある」「現在のインフラやサーバの構成を把握することが難しい」「属人性が発生する」などの問題がある。<br>
    このような問題を解決するためには、インフラの構築もコードで行うという所謂 Infrastructure as Code の方法がある。<br>
    代表的なインフラのコード化ツールとしては、以下のようなものがある。
    - Terraform<br>
    - Deployment Manage r(GCP)<br>
    - CloudFormation (AWS)<br>

- Terraform<br>
    インフラのコード化（Infrastructure as Code）を行うためのツール。<br>
    テンプレートファイル（*.tf形式）に HCL [HashiCorp Configuration Language] という json ライクな言語で記述することで、インフラの環境構築を自動的に行えるようになる。

<!--
## ■ Terraform のテンプレートファイルの構成

### ◎ リソースの設定
- プロバイダーの設定
    ```
    provider "aws" {
    access_key = "ACCESS_KEY_HERE"
    secret_key = "SECRET_KEY_HERE"
    region = "ap-northeast-1"
    ```

### ◎ 他の属性の参照
xxx

### ◎ 変数の使用
xxx

-->

## ■ 参考サイト
- https://qiita.com/Chanmoro/items/55bf0da3aaf37dc26f73
- https://dev.classmethod.jp/articles/terraform-getting-started-with-aws/
