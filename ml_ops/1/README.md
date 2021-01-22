# 【Kubeflow】 Kubeflow の基礎事項
Kubeflow は、学習用データセットの前処理、機械学習モデルの学習、機械学習モデルの推論API化といった機械学習における一連のワークフローを k8s 上で実行するためのツールである。

Kubeflow は、以下のコンポーネントで構成されている。<br>
<img src="https://user-images.githubusercontent.com/25688193/105124219-07ebb880-5b1d-11eb-99d6-69a4968b1499.png" width="550">

- Central Dashboard<br>
    各種機能を GUI 画面で表示＆作成するための機能

- Pipelines<br>
    Kubeflow 上で機械学習ワークフロー（前処理→モデルの構築→モデルの学習→モデルの推論→モデルのモニタリングなど）の構成を行うための機能

- Frameworks for Training (TensorFlow Training, PyTorch Training など）<br>
    Kubeflow 上で機械フレームワークを用いて機械学習モデルの学習を行うための機能

- Jupyter Notebooks<br>
    Kubeflow 上で Jupyter Notebooks を使用して、機械学習モデルの構築・実験などを行うための機能。

- Katib<br>
    Kubeflow 上でハイパーチューニングを行うための機能

- Feature Store (Feast)<br>
    Kubeflow 上で特徴量管理を行うための機能

- Metadata<br>
    xxx

- Fairing<br>
    xxx

- Tools for Serving<br>
    xxx

## ■ KubeFlow Pipelines の構成
xxx

## ■ 参考文献
- https://ymym3412.hatenablog.com/entry/2020/01/07/051653
