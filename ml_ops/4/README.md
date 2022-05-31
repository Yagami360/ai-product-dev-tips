# CI/CD の基礎事項

- CI [Continuous Integration]<br>
    継続的インテグレーション。<br>
    ビルドやテストを自動化することで、短期間のサイクルで継続的にソフトウェアの品質管理を行う手法

- CD [Continuous Delivery, Continuous Deployment]<br>
    継続的デリバリー・継続的デプロイメント。<br>
    継続的デリバリーと継続的デプロイメントが同じ意味で使用されることもあるが、一般的には異なるもの
    - 継続的デリバリー<br>
        開発者によるコードの変更（git push）を起点に、バグがないか自動的にテストし、リポジトリにアップロードする。
    - 継続的デプロイメント<br>
        開発者によるコードの変更（git push）を起点に、システムテストやデプロイなどを自動的に行った後、リポジトリから本番環境に自動的にリリースし、製品として使用できるようにするもの。

- CI/CDツール
    一般的な CI/CD ツールでは、リポジトリに対するプッシュ（git push）やプルリクエスト（git pull）といった操作、もしくは指定した時刻になるといったイベントをトリガーとして、あらかじめ定義しておいた処理を実行することで自動的に CI/CD を行えるようになっている。<br>
    有名な CI/CDツールとしては、以下のようなものがある。<br>
    - Jenkins<br>
    - Circle CI<br>
    - **GitHub Actions**<br>
        GitHub だけで CI/CD 的な機能を実現できるのがメリット。利用料金も無料。現状 GitHub Actions を使うのがベストっぽい
    - **Cloud Build**<br>
        Cloud Build　は、GCP で提供されている docker image などのビルドサービスであるが、CI/CD ツールとしても利用できる。<br>
        Cloud Build を利用した CI/CD では、GKE や Cloud Function, Cloud Run などの GCP が提供する各種サービスとの連携が容易であるというメリットがある。

- アジャイル開発<br>
    xxx

- DevOps（デブオプス）
    xxx

- GitOps<br>
    Git コマンド（git push, git pull など）を起点として Kubernetes のリソースの CI/CD を行う仕組み<br>
    GithubActions のような CI/CD ツールを利用して構築することも可能であるが、ArgoCD などの専用 CI/CD ツールで実現することもできる

- MLOps

