# Spotinst Ocean を使用して AWS の EKS クラスターを低価格＆高安定で運用する

「[Spotinst Elastigroup を使用して AWS Spot インスタンスを低価格＆高安定で運用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/87)」では、Spotinst の Elastigroup 機能を使用して AWS の Spot インスタンスをより低価格＆高安定で運用する方法を記載したが、Spotinst には、EKS クラスターなどの k8s クラスターに対してのマネージドサービスである Ocean も存在する。

この Ocean は、（Elastigroup のときと同じように）EKS クラスターなどの k8s クラスターに対して、より低価格＆高安定で運用可能にな機能になっている

## ■ 方法

1. [Spotinst](https://console.spotinst.com/spt/auth/signUp) の Web ページにアクセスし、ユーザー登録を行う

    > 所属会社（Company）を記載する必要があるが、適当な名前（"Personal Use", "Yagami360" とか）入力しておけば、個人利用できる

1. Spotinst のコンソール画面から各種初回セットアップを行う<br>
    <img width="784" alt="image" src="https://user-images.githubusercontent.com/25688193/184467144-027e9761-4ce3-4487-b6a8-e2a26742bf1a.png"><br>
    <img width="1294" alt="image" src="https://user-images.githubusercontent.com/25688193/184467176-ff2ae7af-f38d-4023-959c-6fa0d94be44a.png"><br>

1. Spotinst Ocean コンソール画面から Ocean Cluster を作成する<br>

## ■ 参考サイト

- https://docs.spot.io/ocean/getting-started/eks/
- https://blog.recruit.co.jp/rmp/infrastructure/post-19364/