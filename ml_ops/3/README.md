# 【Kubeflow】Google AI Platform Pipelines を利用して Kubeflow Pipelines の構築する
「[【Kubeflow】GKE クラスタに Kubeflow を構築する](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/ml_ops/2) 」記載の方法でも Kubeflow Pipelines を構築することができるが、Google AI Platform Pipelines を利用することで、より手軽に Kubeflow Pipelines を構築することができる。

1. AI Platform Pipelines の [GUI 画面](https://console.cloud.google.com/kubernetes/application?project=myproject-292103) に移動する
1. 「新しいインスタンス」ボタンを選択し、kubeflow をデプロイした GKE クラスタを新規作成する
    1. [新しいクラスタの作成] のリンクが表示されたら、[新しいクラスタの作成] をクリック。
    1. [次の Cloud API へのアクセスを許可する] をオンにし、GKE クラスタ上で実行されるアプリケーションに Google Cloud リソースへのアクセス権を付与します。

<!--
    1. kubeflow をデプロイした GKE クラスタ作成後、
    <img src="https://user-images.githubusercontent.com/25688193/105480513-31593f80-5ce9-11eb-8f35-60f075bd126f.png" width="500">
    <img src="https://user-images.githubusercontent.com/25688193/105480552-3fa75b80-5ce9-11eb-8e29-0ebb941248d8.png" width="500">
-->
1. 作成した GKE クラスタの「パイプライン ダッシュボードを開く」ボタンを選択し、kubeflow の Central Dashboard 画面に移動する。
    <img src="" width="">

<img src="" width="">

## ■ 参考文献
- 公式 : https://cloud.google.com/ai-platform/pipelines/docs/getting-started
- https://techblog.zozo.com/entry/aip-pipelines-impl
