# Spotinst Elastigroup を使用して AWS Spot インスタンスを低価格＆高安定で運用する

AWS の Spot インスタンスや GCP の Preemptible VM では、通常のインスタンスの 70-80% 程度低い価格でインスタンスを使用できる一方で、予期せぬタイミングでサーバーが落ちるデメリットが存在する。またその価格も使用状況によって変動する

> より詳細には、AWS の Spot インスタンスの場合は、スポットインスタンスの価格は、使用中のインスタンスが少ないときは安くなり使用中のインスタンスが多いときは高くなるといった具合で、Spot インスタンス在庫の状況によって決定される。そして、使用中のインスタンスの在庫が不足してきてスポットインスタンスに回せる分の在庫が無くなった時点で、Spot インスタンスはシャットダウンされる

Spotinst は、このような AWS の Spot インスタンスや GCP の Preemptible VM（最近 Spot インスタンスも出た）をうまく管理することで、より低価格（最大で通常のインスタンスの90%程度のコストダウン）で、より安定的に使用できるようにした、サードパーティ製のマネージドサービスである。

Spotinst には、以下のような機能がある

- Elastigroup<br>
    以下のような処理を行うことで、Spot インスタンスをより低価格でより安定的に使用できるようにする機能
    - 独自の予測アルゴリズムを使用して、AWS などのクラウドプロバイダーによって「中断されようとしている」Spot インスタンスを特定して排除する。
    - 排除前に、Elastigroup はアプリケーションを自動的に最も安価な「利用可能な」Spot インスタンスまたはオンデマンドインスタンスに移行させ、ダウンタイムは発生させなくしてくれる。

- Ocean<br>
    Elastigroup は、Spot インスタンスに対してのサービスであるが、Ocean は AWS EKS クラスターなどの k8s クラスターに対してのサービスになっている<br>
    但し、k8s の Node 管理（Spotインスタンス）には、Elastigroup を利用している

なお、Spotinst 導入で、コスト削減できた分の20％が Spotinst の使用料として支払う必要がある

> 「オンデマンドの価格からスポットインスタンスによって割引された価格"の20%」なので、通常の AWS の Spot インスタンスより、多少割高になる？

## ■ 方法

1. [Spotinst](https://console.spotinst.com/spt/auth/signUp) の Web ページにアクセスし、ユーザー登録を行う

    > 所属会社（Company）を記載する必要があるが、適当な名前（"Personal Use", "Yagami360" とか）入力しておけば、個人利用できる

1. Spotinst のコンソール画面から各種初回セットアップを行う<br>
    <img width="784" alt="image" src="https://user-images.githubusercontent.com/25688193/184467144-027e9761-4ce3-4487-b6a8-e2a26742bf1a.png"><br>
    <img width="1294" alt="image" src="https://user-images.githubusercontent.com/25688193/184467176-ff2ae7af-f38d-4023-959c-6fa0d94be44a.png"><br>


1. Spotinst コンソール画面から Elastigroup を作成する<br>
    「[Spotinst の Elastigroup コンソール画面](https://console.spotinst.com/spt/aws/ec2/elastigroup/list)」から「Create Elastigroup」ボタンをクリックする。その後、コンソール画面に従って各種設定値を入力し、Elastigroup を作成する<br>

    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184471469-1a6e17a4-2e7b-44ce-8a9b-f10c8f203337.png"><br>
    <img width="804" alt="image" src="https://user-images.githubusercontent.com/25688193/184471637-c4020d03-87d5-451f-a901-05c857d6babe.png"><br>

    > Spotinst の CLI コマンドで作成する方法も存在する？

1. Elastigroup と Spot インスタンスが作成されていることを確認する<br>
    Elastigroup 作成後、AWS の EC2 インスタンス（Spot インスタンス）も自動的に作成される<br>
    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184471795-ba8acd6e-722d-48ff-9b47-f3939e245f09.png">

1. 【オプション】Spot インスタンスに ssh 接続する<br>
    - Amazon Libux の image で作成した場合
        ```sh
        ssh ec2-user@${IP_ADDRESS}
        ```

## ■ 参考サイト

- https://buildersbox.corp-sansan.com/entry/2019/12/16/110000
- https://tech-blog.abeja.asia/entry/lets-use-spotinst
- https://docs.spot.io/elastigroup/tutorials/elastigroup-tasks/create-an-elastigroup-from-scratch
