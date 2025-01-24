# Rancher の基礎事項

<img width="600" alt="image" src="https://github.com/user-attachments/assets/3441b305-504b-42a1-9b07-3952c33ec08d" />

- Rancher<br>
    クラウド環境（AWS の EKS, GCP の GKE など）やオンプレミス環境（自社サーバーなど）において、Kubernetes(K8s)クラスターの管理を容易にするためのサードパーティ製（Runcher社）のオープンソースプラットフォーム。<br>
    複数の Kubernetes クラスターを管理するための GUI ツールや、ユーザー管理・モニタリング・アプリケーションカタログなどの機能なども提供しており、Kubernetes 全体の管理プラットフォームになっている。

    > 特にオンプレミス環境上に Kubernetes クラスターを構築する場合は、Rancher の RKE を使用することが多い。

- RKE [Rancher Kubernetes Engine]<br>
    Rancher の中の１つの機能で、Rancher を使用して Kubernetes クラスターを構築するためのツール。
    クラウド環境やオンプレミス環境の両方に対して、Kubernetes クラスターを構築できる。
