# Kubernetes (k8s) の基本事項

## ■ Kubernetes (k8s) の基本事項

Kubernetes（クーベネティス）は、コンテナの運用管理と自動化（＝コンテナオーケストレーション）を行うシステム。<br>
具体的には、以下のような機能を持つ

- 複数のDockerホストの管理
- コンテナのスケジューリング
- オートスケーリング、ロードバランシング
- ロードバランシング
- コンテナの死活監視
- 障害時のセルフヒーリング
- ログの管理

多数のコンテナから構成され、それらを適切にスケーリングする必要があるシステムにおいて、Kubernetes を導入することで、システムの管理が用意になるというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/103282973-a99a5100-4a1a-11eb-8c1b-9a3511616e58.png" width=915>

上図は Kubernetes のアーキテクチャを示した図である。<br>
Kubernetes は、以下のようなコンポーネントから構成される

- Node : Dockerが動くマシンのこと。
- Pod（クラスター？） : コンテナを配置する入れ物で１つ以上のコンテナを持つ。この単位でスケーリングされる。Pod の設定は yaml で記述
- Proxy : コンテナとの通信を経由するプロキシ。
- Deployments : Pod（コンテナ）を複数集めて管理するもの。
- Service : Deployment に対して外部からアクセス可能な IP アドレスを付与し、外部からアクセスできるようにしたもの。Pod群（Deployment）へのロードバランシングやサービスディスカバリを行う


### ◎ 参考サイト
- https://www.kagoya.jp/howto/rentalserver/kubernetes/

## ■ Kubernetes のインストール

## ■ Kubernetes の構築手順

