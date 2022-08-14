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
    「[Spotinst の Ocean コンソール画面](https://console.spotinst.com/spt/aws/ec2/elastigroup/list)」から「Create Cluster」ボタンをクリックする。その後、コンソール画面に従って各種設定値を入力し、Ocean Cluster を作成する<br>
    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184518691-db2392c4-9b84-4640-b4bd-e316b0a44475.png"><br>
    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184518697-d8b65cb5-8a1c-4ef4-925c-db4a0ce7f9e9.png"><br>

    - Step1 & Step2<br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184520522-843ec1d8-65ce-4f02-9bec-0b2ac7cc8fc1.png"><br>
        「Generate Token」ボタンをクリックし、Spotinst の API にアクセスするためのアクセストークンを作成する。後に使用するので値を保存しておく

    - Step3<br>
        <img width="892" alt="image" src="https://user-images.githubusercontent.com/25688193/184520596-33fee59f-406c-48ee-bdbe-cbc4960422e8.png"><br>
        「Launch Cloud Formation」ボタンをクリックし、Cloud Formation で EKS クラスターを作成する

        > eks cluster version をデフォルトの `1.18` で作成すると、Cloud Formation が`ROLLBACK_COMPLETE` で終了し、EKS クラスターの作成に失敗した。内部のエラーを確認すると、以下のような EKS クラスターのバージョンが対応してないエラーが発生していた。
        > ```sh
        > Resource handler returned message: "unsupported Kubernetes version (Service: Eks, Status Code: 400, Request ID: a2154148-7618-4db0-abee-0396d20cb889)" (RequestToken: f12bf652-f7f1-e5dd-e40b-fcddcdb2e04d, HandlerErrorCode: InvalidRequest)
        > ```
        > そのため、eks cluster version をデフォルトの `1.18` から `1.19` に変更して、Cloud Formation を実行した


    - Step4 & Step5<br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184519857-dbc33674-0850-4e91-b2b5-a39842b739e6.png"><br>

        コンソール画面の指示に従って、各種コマンドを実行し、最後に「Done」ボタンをクリックする。<br>
        コンソール画面の指示の意味は以下の通り。
        ```sh
        # .kube/config を更新し、作成した EKS クラスターに切り替える
        aws eks update-kubeconfig --name ${CLUSTER_NAME}
        cat ~/.kube/config

        # Service を確認
        kubectl get svc

        # spotinst-kubernetes-cluster-controller という名前の Pod をデプロイ
        curl -fsSL http://spotinst-public.s3.amazonaws.com/integrations/kubernetes/cluster-controller/scripts/init.sh | \
            SPOTINST_TOKEN=${SPOTINST_TOKEN} \
            SPOTINST_ACCOUNT=${SPOTINST_ACCOUNT} \
            SPOTINST_CLUSTER_IDENTIFIER=${CLUSTER_NAME} \
            ENABLE_OCEAN_METRIC_EXPORTER=false \
            bash

        # AWS 認証用 k8s の ConfigMap をダウンロード
        curl -O https://amazon-eks.s3-us-west-2.amazonaws.com/1.10.3/2018-06-05/aws-auth-cm.yaml

        # In the aws-auth-cm.yaml file, replace the <ARN of instance role (not instance profile)> snippet with the NodeInstanceRole value from the outputs tab of the EKS cluster CloudFormation Stack 

        # AWS 認証用 k8s の ConfigMap をデプロイ
        kubectl apply -f aws-auth-cm.yaml 
        ```

        `aws-auth-cm.yaml` の `data.mapRoles.rolearn` の値は、以下のように CloudFormation の「出力タブ」にある `NodeInstanceRole` の値にすればよい

        <img width="754" alt="image" src="https://user-images.githubusercontent.com/25688193/184520799-110edc56-c95e-480e-9f28-d292d4e1c5f3.png">


1. AWS コンソール画面から作成した EKS クラスターを確認する<br>
    「[EKS クラスターのコンソール画面](https://us-west-2.console.aws.amazon.com/eks/home?region=us-west-2#/clusters)」から作成した EKS クラスターを確認する<br>

    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184520923-8d1d5870-ef52-4b41-b359-49707ca551c5.png"><br>
    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/184520929-36a12f46-cce5-44fa-a02d-99decb719e71.png"><br>

1. Spotinst コンソール画面から作成した Ocean クラスターを確認する<br>
    「[Ocean クラスターのコンソール画面](https://console.spotinst.com/spt/ocean/aws/kubernetes/list)」から作成した Ocean クラスターを確認する<br>
    <img width="922" alt="image" src="https://user-images.githubusercontent.com/25688193/184521056-5965b34c-ecde-4e85-94b8-f6775740ec0b.png">
    
## ■ 参考サイト

- https://docs.spot.io/ocean/getting-started/eks/
- https://blog.recruit.co.jp/rmp/infrastructure/post-19364/