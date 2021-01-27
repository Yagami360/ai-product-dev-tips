# 【Kubeflow】Google AI Platform Pipelines を利用して Kubeflow Pipelines を構築する
「[【Kubeflow】GKE クラスタに Kubeflow を構築する](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ml_ops/2) 」記載の方法でも Kubeflow Pipelines を構築することができるが、Google AI Platform Pipelines を利用することで、より手軽に Kubeflow Pipelines を構築することができる。

## ■ AI Platform Pipelines を使用した kubeflow をデプロイした GKE クラスタの構築
1. AI Platform Pipelines の [GUI 画面](https://console.cloud.google.com/kubernetes/application?project=my-project2-303004) に移動する
1. 「新しいインスタンス」ボタンを選択し、kubeflow をデプロイした GKE クラスタを新規作成する
    <img src="https://user-images.githubusercontent.com/25688193/105569886-fa3a6b00-5d88-11eb-9553-923c7be219ba.png" width="800"><br>
    1. [次の Cloud API へのアクセスを許可する] をオンにし、GKE クラスタ上で実行されるアプリケーションに Google Cloud リソースへのアクセス権を付与する。
    1. [新しいクラスタの作成] のリンクが表示されたら、[新しいクラスタの作成] をクリック。<br>
        <img src="https://user-images.githubusercontent.com/25688193/105569915-484f6e80-5d89-11eb-87f4-560a553f4c8d.png" width="400">
    1. 作成した Pipiline と GKE クラスタは、それぞれ [Pipelines の GUI 画面](https://console.cloud.google.com/ai-platform/pipelines/clusters?folder=&organizationId=&project=my-project2-303004) と [GKE の GUI 画面](https://console.cloud.google.com/kubernetes/list?hl=ja&organizationId=0&project=my-project2-303004) から確認できる。<br>
        ※ Pipiline を削除する際は、Pipeline だけでなく GKE クラスタも削除する必要があることに注意<br>
        <img src="https://user-images.githubusercontent.com/25688193/105570220-18a16600-5d8b-11eb-8bed-ea1dbe7a1b13.png" width="500"><br>
        <img src="https://user-images.githubusercontent.com/25688193/105570145-adf02a80-5d8a-11eb-8381-fbceccc16e57.png" width="500"><br>
1. 作成した GKE クラスタの「パイプライン ダッシュボードを開く」ボタンを選択し、kubeflow の Central Dashboard 画面に移動する。<br>
    <img src="https://user-images.githubusercontent.com/25688193/105570231-44245080-5d8b-11eb-9166-9e6911c39ff9.png" width="800"><br>
    <img src="https://user-images.githubusercontent.com/25688193/105570262-85b4fb80-5d8b-11eb-8d2e-a5fcf1d583cb.png" width="800"><br>

## ■ AI Platform Pipelines を使用した機械学習のワークフローの構築

ここでの例では、以下の一連の機械学習ワークフローを AI Platform Pipelines で構築してみる。

```
1. GCS から学習用データセットをダウンロード
2. ダウンロードした学習用データセットを前処理でクレンジング
3. クレンジングした学習用データセットで機械学習モデル（Light-Weight GAN）を学習
4. 学習済みモデルでの推論
```

### ◎ Kubeflow Pipelines SDK での Python コードを新規作成して、Pipelines を構築する。

1. Kubeflow Pipelines SDK である `kfp` をインストールする。
    ```sh
    $ pip install kfp
    ```
1. Pipeline の Python スクリプトを作成＆コンパイルし、Pipeline の yaml ファイルを作成する<br>
    Pipeline を定義するための Python スクリプトを記載し、それを Kubeflow Pipelines SDK を用いてコンパイルすることで Pipeline の実体である yaml ファイルを作成する<br>
    ```sh
    $ cd pipelines
    # 処理完了後、yaml ファイル download_dataset_from_gcs.py.yaml が同ディレクトリ上に作成される
    $ python download_dataset_from_gcs.py
    ```
1. 作成した Pipeline の yaml ファイルをアップロードし、Pipeline を作成する<br>
    <img src="https://user-images.githubusercontent.com/25688193/105571445-31157e80-5d93-11eb-90e1-910b59dc6b02.png" width="500"><br>
    <img src="https://user-images.githubusercontent.com/25688193/105571713-9e2a1380-5d95-11eb-9fb7-9d3517a36d86.png" width="500"><br>
1. 作成した Pipeline に対して、Run を作成＆実行し、Pipeline に定義した処理フローを動かす。（必要があれば先に Experiment も作成）<br>
    <img src="https://user-images.githubusercontent.com/25688193/105571867-ba7a8000-5d96-11eb-81ac-5d28a168b70d.png" width="500"><br>

### ◎ 既存の Python コードを docker image 化して、Pipelines を構築する。
xxx

<img src="" width=""><br>

## ■ 参考文献
- 公式 : https://cloud.google.com/ai-platform/pipelines/docs?hl=ja
- https://ymym3412.hatenablog.com/entry/2020/01/07/051653
- https://techblog.zozo.com/entry/aip-pipelines-impl
- https://qiita.com/oguogura/items/32fcaaa7ece2ab868e81