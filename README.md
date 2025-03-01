# ai-product-dev-tips
AIプロダクト開発のための Tips 集。<br>
｛機械学習論文調査・前処理/後処理/データセット作成・機械学習モデル開発/機械学習フレームワーク・バックエンド/機械学習基盤（MLOps）・フロントエンド/アプリ開発・特許｝などのAIプロダクト開発に関わる幅広い範囲の Tips 集になってます。

## ■ 基本事項

<details>
<summary>入出力処理</summary>

- [【シェルスクリプト】フォルダ内のファイル数を確認する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/io_processing/2)
- [【Python】フォルダ内のファイル一覧を取得する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/io_processing/1)
- [【Python】２つのフォルダのファイル数＆ファイル名の差分を確認する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/io_processing/3)
- [【シェルスクリプト】ランダムに１００個のファイルをサンプリングする。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/io_processing/4)
- [【Python】独自の Python CLI コマンドを作成する（ローカル環境にあるファイルでインストールする場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/io_processing/5)
- 【Python】独自の Python CLI コマンドを作成する（PyPI に公開したファイルでインストールする場合）
- [【Golang】cobra を使用して独自の Golang CLI コマンドを使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/io_processing/7)

</details>

<details>
<summary>開発環境</summary>

- git<br>
    - [git flow をしてブランチ管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/others_processing/1)
- conda
    - [【シェルスクリプト】シェルスクリプト内で conda 環境を切り替える。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/conda_processing/1)
    - [【シェルスクリプト】conda 環境の自動的に作成する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/conda_processing/2)
- [Docker](#Docker)
</details>

<details>
<summary>サーバー処理一般</summary>

- 【シェルスクリプト】ssh 切れ対策のために `nohup` コマンドで実行する。
- 【シェルスクリプト】サーバー間でデータを転送・コピーする。
- 【シェルスクリプト】`curl` コマンドで WebAPI を直接たたく
- [【UNIX】サーバー上の画像ファイルをブラウザ上で確認する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/2)
- [【シェルスクリプト】GCP or AWS インスタンスをシェルスクリプト上から停止する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/1)
- 【Python】サーバー上での Python スクリプトをデバッグするときに、ブレークポイントを有効にする。（`import pdb; pdb.set_trace()`）
- [【シェルスクリプト】シェルスクリプトで、GoogleDrive から大容量データをコピーする。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/3)
- 【Python】スクリプトで GoogleDrive へデータを自動的に転送する。
- [【シェルスクリプト】ポートフォワーディングを使用した tensorboard 接続](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/21)
- VPN 接続

</details>

## ■ 機械学習論文調査

<details>
<summary>機械学習論文サーベイ記事</summary>

- [深層学習モデルの論文サーベイ記事](https://github.com/Yagami360/MachineLearning-Papers_Survey)

</details>

## ■ 前処理・後処理・データセット作成

<details>
<summary>テーブルデータ処理</summary>

- 【Python】pandas_profiling でテーブルデータの統計情報を確認する。
- 【Python】pandas データ型に基づき、欠損値の埋め合わせとカテゴリデータのエンコードを一括して行う。
- 【Python】モデルの `feature_importances_` で重要特徴量を確認する。

</details>

<details>
<summary>画像処理</summary>

- [【シェルスクリプト】画像ファイルの解像度を確認する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/1)
- [【Python】OpenCV ↔ Pillow ↔ numpy の変換対応](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/4)
- [【Python】画像の滑らかさを落とさないように拡張子を変更する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/3)
- [【Python】画像やセマンティックセグメンテーション画像の滑らかさを落とさないようにリサイズする。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/2)
- [【Python】画像の対象物のアスペクト比を変えないまま adjust する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/11)
- [【Python】画像の対象物全体を膨張・収縮させる。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/14)
- [【Python】人物画像の特定の対象物のみを膨張・収縮させる。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/16)
- [【Python】データオーギュメンションや品質評価のための画像の拡大縮小＆平行移動＆回転](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/13)
- [【Python】セマンティックセグメンテーション画像からラベル値を取得する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/5)
- [【Python】セマンティックセグメンテーション画像の特定のラベル値の部分を抜き取る。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/6)
- [【Python】画像のバイナリマスク画像を生成する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/9)
- [【Python】画像の境界輪郭線を滑らかにしたマスク画像を生成する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/17)
- [【Python】画像の背景部分をくり抜く。（グラフ カット）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/10)
- remove bg を使用して、画像の背景部分をくり抜く。（グラフ カット）
- [【Python】画像の上下 or 左右対称性を検出する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/8)
- [【Python】品質評価のためのグリッド画像を生成する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/7)
- [【Python】元画像とセグメンテーション画像をアルファブレンディングで重ねて表示する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/12)
- 【Python】画像の特定の対象物が画面端で途切れているかを検出する。
- 【Python】人物パース画像から上着を着ているような人物画像を検出する。
- OpenPose による姿勢推定
    - OpenPose のインストール
    - 【Python】OpenPose の json ファイルを読み込む。
    - 【Python】OpenPose の json ファイルを書き込む。
    - [【Python】OpenPose の json ファイルの関節点を画像表示する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/openpose/1)
    - [【Python】OpenPose の関節点情報に基づき、人物画像を上半身部分でクロップする。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/openpose/3)
    - [【Python】OpenPose の関節点情報に基づき、人物画像が正面を向いているか後ろを向いているか判定する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/openpose/2)
    - [【Python】OpenPose の関節点情報と人物パース画像に基づき、人物画像が半袖を着ているかを検出する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/openpose/4)
    - [【Python】OpenPose の関節点情報に基づき、人物セグメンテーション画像に、他の人体部位のラベルを追加する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/openpose/5)
- DensePose による姿勢推定
    - [DensePose の推論 API](https://github.com/Yagami360/densepose_wrapper)
    - [DensePose の IUV 画像から人物パース画像を取得する](https://github.com/Yagami360/densepose_wrapper/blob/master/visualization.py)
    - [DensePose の IUV 画像から UV 値の等高線画像を取得する](https://github.com/Yagami360/densepose_wrapper/blob/master/visualization.py)
    - [DensePose と人物パースモデルを用いて、人物画像における手領域の画像を取得する](https://github.com/Yagami360/hand-image-extractor-api)
- dlib による顔の landmark 検出
    - [【Python】dlib で顔の landmark 検出を検出し、画像上に表示する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/image_processing/15)

</details>

<details>
<summary>動画処理</summary>

- ffmpeg を使用して動画ファイル（mp4）をクロップする
- [【Python】ffmpeg を使用して画像ファイルと音声ファイル（mp3）から動画ファイル（mp4）を作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/video_processing/1)

</details>

<details>
<summary>音声処理</summary>

- [pydub と ffmpeg を用いて音声ファイルの無音部分をクレンジングする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/audio_processing/1)

</details>

<details>
<summary>自然言語処理</summary>

- [LLM アプリケーション開発に移動](https://github.com/Yagami360/ai-product-dev-tips?tab=readme-ov-file#-llm-%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E9%96%8B%E7%99%BA)

</details>

<details>
<summary>Web スクレイピング</summary>

- [【Python】WEB 上の画像データを収集する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/web_scraping/1)
- 【Python】Selenium を用いてログインが必要な Web ページにログインし、スクレイピングを行う

</details>

<details>
<summary>高速化処理</summary>

- [【Python】for ループ内の処理を複数 CPU の並列処理で高速化する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/acceleration_processing/2)
- [【Python】複数 GPU での並列化のために、フォルダ内のファイルを分割し別フォルダに保存し、その後１つのフォルダに再統合する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/acceleration_processing/1)
- 【Python】for ではなく行列処理で画像処理を高速化する。
- Cuda
- cupy
- OpenCV (GPU版)
- [【Golang】goroutine と Channel を使用してマルチスレッド処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/100)

</details>

## ■ 機械学習モデル開発・機械学習フレームワーク

<details>
<summary>PyTorch</summary>

- 学習＆推論処理
    - 【PyTorch】学習用データセットと検証用データセットの分割
    - 【PyTorch】学習済みチェックポイント読み込み時に epoch 数や step 数も読み込めるようにする。
    - 【PyTorch】k-fold CV での学習処理
        - scikit-learn の `KFold` と PyTorch の `Subset` の使用
- ネットワーク定義
    - `add_module()` or `nn.ModuleList` or `nn.ModuleDict` でネットワークの段数を柔軟に可変出来るようにする
    - 【PyTorch】特定の層のみ学習を行うようにする : `param.requires_grad = False` と optimizer の `params` 引数の設定
- 高速化
    - [【PyTorch】DP [DataParallel] を使用した単一プロセス + 複数 GPU での高速化](https://github.com/Yagami360/ai-product-dev-tips/tree/master/pytorch_tips/2)
    - [【PyTorch】AMP [Automatic Mixed Precision] を使用した学習と推論の高速化](https://github.com/Yagami360/ai-product-dev-tips/tree/master/pytorch_tips/5)
    - [【PyTorch】DDP [DistributedDataParallel] を使用した複数プロセス + 複数GPU での高速化](https://github.com/Yagami360/ai-product-dev-tips/tree/master/pytorch_tips/3)
    - [【PyTorch】DDP + AMP を使用した高速化](https://github.com/Yagami360/ai-product-dev-tips/tree/master/pytorch_tips/4)
    - [【PyTorch】データローダーでの前処理を GPU 動作させて高速化する（PyTorch 1.7, torchvison 0.8 以降）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/pytorch_tips/6)
- 表示処理
    - 【PyTorch】tensorboard の画像出力を横軸縦軸に並べて表示する
    - 【PyTorch】TensorBoard のヒストグラムにネットワークの重みを表示する。
- データローダー
    - 【PyTorch】独自データセットでの DataLoader 
    - 【PyTorch】複数種類の DA を args 引数でカスタマイズ可能にする
    - [【PyTorch】ネットワークへの入力画像が複数存在する場合に入力画像毎に異なる seed 値での DA を適用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/pytorch_tips/1)
    - 【PyTorch】Random Erasing での DA
    - 【PyTorch】CutMix での DA
    - 【PyTorch】TPS 変換での DA
- その他
    - 【PyTorch】OpenCV ↔ Pillow ↔ numpy ↔ Tensor [PyTorch] の変換対応
    - 【PyTorch】再現性確保のためのシード値固定処理
    - 【PyTorch】GPU での処理時間を計測する : `torch.cuda.Event()` 使用する方法
- [【PyTorch】PyTorch を使用した深層学習モデルの実装コード集](https://github.com/Yagami360/MachineLearning_Exercises_Python_PyTorch)
- [【PyTorch】PyTorch を使用した強化学習モデルの実装コード集](https://github.com/Yagami360/ReinforcementLearning_Exercises)
- [【PyTorch】PyTorch を使用した 3D Reconstruction モデルの実装コード集](https://github.com/Yagami360/3d-reconstruction_exercises_pytorch)

</details>

<details>
<summary>Tensorflow</summary>

- 【Tensorflow】Dataset API を使用したデータローダー（tensorflow 1.4以降, tensoflow 2.x）
- 【Tensorflow】tensor 値の確認方法（tensorflow 1.x, tensoflow 2.x <EagerMode>, tensoflow 2.x<GraphMode>）
- 【Tensorflow】tf_debug CLI でのデバッグ処理
- 【Tensorflow】tf_debug GUI でのデバッグ処理
- 【Tensorflow】複数 GPU での学習
- 【Tensorflow】AMP（混合精度）を使用した高速化
- [【Tensorflow】Tensorflow を使用した深層学習モデルの実装コード集](https://github.com/Yagami360/machine-learning_exercises_tensorflow)

</details>

<details>
<summary>Keras</summary>

- 【Keras】独自データセットの DataLoader
- 【Keras】継承クラスで独自のネットワークを定義する 
- 【Keras】FineTuning
- 【Keras】複数 GPU での学習
- 【Keras】AMP（混合精度）を使用した高速化
- [【Keras】Keras を使用した Kaggle コンペでの実装コード集](https://github.com/Yagami360/kaggle_exercises)

</details>

<details>
<summary>scikit-learn</summary>

- [【scikit-learn】scikit-learn を使用した 非DNN の機械学習モデルの実装コード集](https://github.com/Yagami360/MachineLearning_Exercises_Python_scikit-learn)

</details>

## ■ 機械学習基盤（MLOps）・バックエンド

<details>
<summary>クラウド環境一般</summary>

- AWS
    - 【AWS】EC インスタンスのディスク容量を後から増設する。
- GCP
    - [【シェルスクリプト】GCP に DeepLearning 環境を自動的に構築する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/6)
    - 【GCP】GCP ディスクを `gcsfuse` コマンドでマウントする。
    - [【GCP】サーバー起動後に自動的に実行するスクリプトを設定する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/5)
    - 【GCP】インスタンスグループを利用したオートスケーリング、ロードバランサーの導入
</details>

<details>
<summary>仮想サーバー</summary>

- 【AWS】EC2 インスタンス
    - [Spotinst Elastigroup を使用して AWS の Spot インスタンスを低価格＆高安定で運用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/87)
- 【GCP】VM インスタンス

</details>

<details>
<summary>コンテナ基盤</summary>

- <a id="Docker"></a>Docker
    - [【Docker】Docker の基本事項・基本コマンド](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/1)
    - [【Docker】docker コンテナ内で機械学習モデルの処理を実行中に tensorboard で実行結果を確認する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/2)
    - [【Docker】コンテナの起動とコンテナ内での python スクリプト実行を一括して行う。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/3)
    - [【Docker】docker-compose を用いず Docker イメージの作成＆コンテナ起動を一括して実行する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/4)
    - [【Docker】ホスト環境とコンテナ環境で同期したファイルの所有権を指定する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/5)
    - [【Docker】docker exec を nohup で実行する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/6)
    - [【Docker】本番環境用の Docker イメージと開発環境用の Docker イメージの構成](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/7)
    - 【Docker】dockerfile でユーザー追加後に git clone する際の、permission denied エラー対策
    - [【Docker】dockerfile の WORKDIR 変更前のデフォルトパス](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/9)
    - [【Docker】requests モジュールを用いてコンテナ間通信するときの、IP アドレス指定方式（コンテナ名で指定）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/docker_processing/8)
    - 【Docker】Docker コンテナ内から別の Docker コンテナを認識する
- Kubernetes (k8s)
    - 【GCP】GKE [Google Kubernetes Engine]
        - [【GCP】Kubernetes (k8s) と GKE [Google Kubernetes Engine] の基本事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/9)
        - [【GCP】GKE クラスタのノードで GPU を使用可能にする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/10)
        - [【GCP】GKE を用いた機械学習モデルの推論 API の構築](https://github.com/Yagami360/graphonomy_api-server_gke)
        - [[In-progress]【GCP】GKE でのオートスケールの基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/31)
        - [【GCP】Cloud Monitoring でのカスタム指標を k8s の外部メトリックとしてオートスケールする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/50)
        - 【GCP】Workload Identity を用いた GKE クラスタから GCP リソースへのアクセス
        - 【GCP】GKE の外部公開サービスの IP アドレスを固定する
        - 【GCP】Pod 間で通信する
        - 【GCP】Pod 内のコンテナ間で通信する
        - 【GCP】Pod でのコンテナの起動順を設定する
        - 【GCP】Pod 内のコンテナ内から別の Pod を認識する
        - 【GCP】GKE クラスタをマルチゾーンクラスタにして安定性を向上させる
        - 【GCP】GKE クラスタをマルチリージョン＆マルチゾーンクラスタにして安定性を向上させる
        - 【k8s】Istio の基礎事項
        - [【GCP】GKE で構成した Web API に Istio を使用したサーキットブレーカーを導入する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/27)
        - [【GCP】Istio の VirtualSevice を使用してリクエストデータのヘッダーに応じて異なる Web-API で推論する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/40)
        - [[In-progress]【GCP】GoogleマネージドSSL証明書を用いて、GKE 上の Web-API を https 化する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/45)
        - [【GCP】k8s の Job を使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/51)
        - 【GCP】k8s の CronJob を使用する
        - 【GCP】同期 REST API へのリクエストを k8s のジョブで管理する
        - 【GCP】非同期 REST API へのリクエストを k8s のジョブを管理する
        - 【GCP】サイドカーで異なるコンテナ間のボリュームを共有する
        - 【GCP】k8s の PersistentVolume と hostpath を使用してコンテナ間のボリュームを永続的に共有する
        - [【GCP】GKE 上の Web-API に対して Google Cloud Armor の WAF 機能を使用してクライアントIP単位での RateLimit 制限を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/55)
        - [【GCP】 Kustomize を使用して GKE 上の　Web-API の k8s のリソース管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/71)
        - 【GCP】GKE で Spot インスタンスを使用しコスト削減を行う
    - 【AWS】Amazon EKS [Amazon Elastic Kubernetes Service]
        - [[In-progress]【AWS】`eksctl` コマンドを使用して Amazon EKS 上の Web API を構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/60)
        - [【AWS】Spotinst Ocean を使用して AWS の EKS クラスターを低価格＆高安定で運用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/88)
        - 【AWS】Spotinst Ocean を使用して AWS の EKS クラスターを低価格＆高安定で運用する（terraform 使用）
    - Rancher / RKE [Rancher Kubernetes Engine]
        - [Rancher の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/118)
        - [Rancher の RKE を使用して、オンプレミス環境上に Kubernetes クラスターを構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/119)

</details>

<details>
<summary>認証基盤</summary>

- 認証認可の基礎事項
    - [認証（Authentication）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#%E8%AA%8D%E8%A8%BCauthentication)
    - [認可（Authorization）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#%E8%AA%8D%E5%8F%AFauthorization)
    - [Basic認証](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#basic-%E8%AA%8D%E8%A8%BC)
    - [JWT認証](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#jwt-json-web-token-%E8%AA%8D%E8%A8%BC)
    - [OAuth](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#oauth-20)
    - [OIDC [OpenID Connect]](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#openid-connect-oidc)
    - SAML (Security Assertion Markup Language)
    - [SSO [Single Sign-On]](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#sso-single-sign-on)
    - [CORS [Cross-Origin Resource Sharing]](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/109#cors-cross-origin-resource-sharing)
- [【GCP】GCP の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/11)
- [【AWS】AWS の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/59)

</details>

<details>
<summary>Web サーバー / WSGI サーバー / ロードバランサー / API Gateway</summary>

- Web サーバー / WSGI サーバー
    - [Web サーバーの基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/38)
        - SSL/TLS 通信
        - HTTP クッキー（Cookie）
        - WebSocket 通信
    - nginx
        - [【nginx】nginx の基本事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/22)
        - [【nginx】nginx での Webサーバーを https 化する（自己署名SSL認証書を使用する場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/23)
        - [【nginx】nginx をリバースプロキシとして利用する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/24)
        - [【nginx】リバースプロキシとしての nginx をロードバランサーとして利用する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/25)
        - [【nginx】docker + nginx + Flask を用いた Web-API の構築](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/26)
    - WSGI/ uWSGI
        - [【uWSGI】WSGI / uWSGI の基本事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/27)
        - [【uWSGI】docker + nginx + uWSGI + Flask を用いた Web-API の構築](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/28)
    - Gunicorn
- ロードバランサー
    - 【AWS】ALB [Application Load Balancer]
        - [[In-progress]【AWS】ALB [Application Load Balancer] を使用して複数の EC2 インスタンスに対しての HTTP 接続の L7 ロードバランシングを行う（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/89)
    - 【AWS】AWS Load Balancer Controller / AWS ALB Ingress Controller
        - [[In-progress]【AWS】AWS Load Balancer Controller（旧 AWS ALB Ingress Controller）を使用して EKS 上の Web-API に ALB での L7 ロードバランシングを行う（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/91)
- API Gateway
    - 【AWS】Amazon API Gateway
        - [【AWS】Amazon API Gateway を使用して Lambda 関数での REST API を構築する（Amazon CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/82)
        - 【AWS】Amazon API Gateway を使用して EC2 インスタンス上の REST API を構築する（Amazon CLI 使用）
    - Ambassador
        - [[In-progress] Ambassador を使用して EKS クラスター上の Web-API の API Gateway を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/90)
- DNS サーバー
    - [DNS サーバーの基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/37)
    - 【AWS】Route53
    - 【GCP】Cloud DNS

</details>

<details>
<summary>Web フレームワーク</summary>

- REST API / RESTful API
    - [REST API / RESTful API の基本事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/29)
- 【Python】Flask
    - 【Python】GCP インスタンス + docker + Flask を用いた Web-API の構築
    - [【Python】Flask での Web-API を https 化する（自己署名SSL認証を使用する場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/20)
    - 【Python】Flask での Web-API を https 化（SSL）する（認証局[CA]を使用する場合）
- 【Python】Django
- 【Python】FastAPI
    - [FastAPI の基本事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/30)
    - [FastAPI + uvicorn での構成](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/31)
    - [FastAPI + uvicorn + gunicorn での構成（本番環境想定時）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/32)
    - [FastAPI + uvicorn + gunicorn + docker を用いた Web-API の構築](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/33)
    - [FastAPI での GET / POST 処理（FastAPI + uvicorn + gunicorn + docker での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/34)
    - [FastAPI を使用した Web-API にファイルをアップロードする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/46)
    - [FastAPI を使用した Web-API に複数ファイルを同時にアップロードする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/47)
    - FastAPI を使用した Web-API からファイルをダウンロードする
    - [FastAPI での非同期処理（FastAPI + uvicorn + gunicorn + docker での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/35)
    - [FastAPI を使用した非同期処理での Web-API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成で画像データを扱うケース）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/36)
    - [FastAPI を使用した非同期処理での Web-API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成で動画データを扱うケース）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/48)
    - FastAPI を使用した非同期処理での機械学習モデル推論 API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成）
    - [FastAPI を使用した複数の同期処理での Web-API を並列処理する（FastAPI + uvicorn + gunicorn + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/38)
    - [推論時間が異なる複数の API から構成される Web-API において、推論結果を複数段階に分けてレスポンスする（FastAPI + uvicorn + gunicorn + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/43)
    - FastAPI を使用した非同期処理での Web-API の出力結果を GSC に転送する
    - FastAPI を使用した非同期処理での Web-API の出力結果を GoogleDrive に転送する
    - FastAPI を使用した非同期処理での Web-API の出力完了結果を Slack に通知する
- 【Python】httpx を用いて複数の　Web-API に並列実行でリクエストする
- 【Golang】net/http（標準ライブラリ）
    - [【Golang】net/http を使用して GET リクエストに対しての簡単な REST API を作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/72)
    - net/http を使用して POST リクエストに対しての簡単な REST API を作成する
- 【Golang】Gin
    - [【Golang】Gin を使用して簡単な REST API を作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/69)
- 【Elixir】Phoenix
    - [【Elixir】Phoenix を使用して簡単な REST API を作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/86)
    - [[In-progress]【Elixir】Phoenix を使用して簡単な REST API を作成する（docker 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/83)
    - [[In-progress]【Elixir】Phoenix + PlugCowboy + WebSockex を使用して Websocket 通信のプロキシーサーバーを構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/39)

</details>

<details>
<summary>サーバレス / FaaS [Function as a Service]</summary>

- 【GCP】Cloud Functions
    - [【GCP】Cloud Functions を利用したサーバーレス Web-API の構築](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/7)
    - 【GCP】Cloud Functions の単体テスト＆結合テスト   
    - 【GCP】Cloud Functions で GPU を使用可能にする
    - 【GCP】Cloud Functions を用いた機械学習モデルの推論 API の構築
- 【GCP】Cloud Run
    - [【GCP】Cloud Run を利用したサーバーレス Web-API の構築](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/8)
    - 【GCP】Cloud Run で GPU を使用可能にする
    - 【GCP】Cloud Run を用いた機械学習モデルの推論 API の構築
- 【AWS】AWS Lambda
    - [【AWS】AWS Lambda を使用してサーバレス Web-API を構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/58)
- 【AWS】AWS Step Functions
    - [[In-progress]【AWS】AWS Step Functions を使用して複数の AWS Lambda を順次実行する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/85)

</details>

<details>
<summary>データ基盤 / データ分析基盤</summary>

- 非構造化データ
    - 【GCP】GCS [Google Cloud Storage]
    - 【AWS】Amazon S3
- 構造化データとSQL
    - [構造化データの基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110)
        - [セッションとトランザクション](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110#%E3%82%BB%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%A8%E3%83%88%E3%83%A9%E3%83%B3%E3%82%B6%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3)
        - [コネクションプールとコネクション数](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110#%E3%82%B3%E3%83%8D%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3%E3%83%97%E3%83%BC%E3%83%AB%E3%81%A8%E3%82%B3%E3%83%8D%E3%82%AF%E3%82%B7%E3%83%A7%E3%83%B3%E6%95%B0)
        - [リレーション](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110#%E3%83%AA%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3)
        - [インデックス](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110#%E3%82%A4%E3%83%B3%E3%83%87%E3%83%83%E3%82%AF%E3%82%B9)
        - [正規化](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110#%E6%AD%A3%E8%A6%8F%E5%8C%96)
        - CRUD操作
        - マイグレーション
        - [パフォーマンス指標](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/110#db%E3%83%91%E3%83%95%E3%82%A9%E3%83%BC%E3%83%9E%E3%83%B3%E3%82%B9%E6%8C%87%E6%A8%99)
    - MySQL
        - [【MySQL】SQLAlchemy を使用して Python スクリプトから MySQL に接続する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/34)
        - [【MySQL】SQLAlchemy を使用して Python スクリプトから MySQL に接続する（docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/35)
        - [【MySQL】MySQL に Web-API のログデータを書き込む（FastAPI + uvicorn + gunicorn + MySQL + SQLAlchemy + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/36)
        - 【MySQL】MySQL に書き込んだ Web-API のログデータを監視する（FastAPI + uvicorn + gunicorn + MySQL + SQLAlchemy + docker + docker-compose での構成）
        - [[In-progress]【MySQL】MySQL に保存したジョブデータをバッチ単位で処理する Web-API（FastAPI + uvicorn + gunicorn + MySQL + SQLAlchemy + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/37)
    - PostgreSQL
        - [PostgreSQL CLI を使用して PostgreSQL データベースの CRUD 処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/80)
        - [PostgreSQL CLI を使用して PostgreSQL データベースの CRUD 処理を行う（docker 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/81)
        - [alembic を使用して PostgreSQL データベースの DB マイグレーションを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/84)
        - [[In-progress]【Elixir】Ecto の Ecto.Repo を使用して PostgreSQL データベースの CRUD 処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/92)
        - [[In-progress]【Elixir】Ecto の Ecto.Schema で定義したテーブルデータの内容を PostgreSQL データベースのテーブルに追加する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/93)
        - [【Elixir】Phoenix 版 Ecto の Ecto.Repo を使用して PostgreSQL データベースの CRUD 処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/94)
        - [【Elixir】Phoenix 版 Ecto の Ecto.Schema で定義したテーブルデータの内容を PostgreSQL データベースのテーブルに追加する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/95)
        - [【Elixir】Phoenix 版 Ecto の Ecto.Changeset を使用して PosgreSQL DB のテーブルデータの一部の列のみを変更する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/96)
        - [【Elixir】Phoenix 版 Ecto の Ecto.Query を使用して PosgreSQL DB のテーブルデータを取り出す](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/97)
        - [【Elixir】Phoenix 版 Ecto の Ecto.Multi を使用して PosgreSQL DB に対しての複数のデータベース処理を１つのトランザクションで行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/98)
    - 【GCP】Google Cloud SQL
        - [【GCP】Google Cloud SQL の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/56)
        - [【GCP】Google Cloud SQL を使用して SQL インスタンス上の MySQL データベースの CRUD 処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/57)
        - 【GCP】Google Cloud SQL を使用して MySQL に Web-API のログデータを書き込む（FastAPI + uvicorn + gunicorn + MySQL + docker + docker-compose での構成）
    - 【GCP】BigQuery
        - [【GCP】BigQuery の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/6)
        - [【GCP】BigQuery を使用したデータ処理（GUI使用時）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/7)
        - [【GCP】BigQuery を使用したデータ処理（CLI使用時）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/8)
        - 【GCP】BigQuery を使用したデータ処理（Python 用 BigQuery Storage API ライブラリ使用時）
    - 【AWS】Amazon Aurora
        - [【AWS】Amazon Aurora を使用して MySQL データベースの CRUD 処理を行う（Amazon CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/78)
- 構造化データ（NoSQL）
    - 【AWS】Amazon DynamoDB
        - [【AWS】Amazon DynamoDB を使用して NoSQL データベースの CRUD 処理を行う（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/75)
- NAS [Network Attached Storage] / NFS [Network File System]
    - 【AWS】Amazon EFS
        - [【AWS】Amazon EFS を使用して EC2 インスタンスに共有ストレージ（NAS）を追加する（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/77)
- DVC [Data Version Control]
    - [DVC を使用して機械学習モデルの学習用データセットのバージョン管理を行う（リモートストレージとしてS3を使用する場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/117)
    - DVC を使用して機械学習モデルの学習用データセットのバージョン管理を行う（リモートストレージとしてNASを使用する場合）


</details>

<details>
<summary>メッセージングサービス / キューサービス / キャッシュサービス</summary>

- [メッセージングサービス・キューサービスの基本事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/17)
- Redis
    - Redis の基礎事項
    - [Redis を Python スクリプトで使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/22)
    - [docker + Redis + Python での Redis の構成](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/23)
    - docker + Flask での Web-API を Redis を利用して非同期実行する
    - [推論結果を Redis にキャッシュし、同じ入力データでの Web-API の推論処理を高速化する（FastAPI + uvicorn + gunicorn + redis + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/39)
    - [入力データや前処理データを Redis にキャッシュし、同じ入力データでの Web-API の推論処理を高速化する（FastAPI + uvicorn + gunicorn + redis + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/44)
- 【GCP】Google Cloud Pub/Sub
    - [【GCP】Google Cloud Pub/Sub の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/18)
    - [【GCP】Google Cloud Pub/Sub を Python スクリプト上で利用する（PULL 方式）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/19)
    - 【GCP】Google Cloud Pub/Sub を Python スクリプト上で利用する（PUSH 方式）
    - [【GCP】Cloud Scheduler と Google Pub/Sub を用いて、サーバーを一定の時間間隔で起動・停止する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/4)
    - [[In-progress] docker + Flask での Web-API を Cloud Pub/Sub を利用して非同期実行する（PULL方式）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/20)
    - 機械学習モデルの推論 API を Cloud Pub/Sub を利用して非同期実行する（PULL方式）
- 【AWS】Amazon SQS
    - [【AWS】Amazon SQS を使用して標準キューの簡単なキューイングを行う（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/74)
- 【AWS】Amazon ElastiCache
    - [[In-progress]【AWS】Amazon ElastiCache for Redis を使用してメモリのキャッシングを行う（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/76)

</details>

<details>
<summary>ロギング / モニタリング</summary>

- 【Python】デコレーターを用いてロギング処理を共通化する
- サーバーのロギング / モニタリング
    - 【GCP】Cloud logging（旧 Stackdriver）
    - [【GCP】Cloud Monitoring（旧 Stackdriver Monitoring）にカスタム指標を書き込む（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + モニタリングサーバー + docker での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/49)
    - Datadog
        - 【Datadog】Datadog の基礎事項
        - [【Datadog】GCE の各種メトリクスとログデータを Datadog で表示する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/52)
        - 【Datadog】GCE 上の Web-API の各種ログを Datadog で表示する 
        - 【Datadog】GKE 上の Web-API の各種ログを Datadog で表示する 
        - 【Datadog】アプリの各種ログを Datadog で表示する 
    - Sentry
        - [【Sentry】Sentry を使用して FastAPI を使用した Web-API のエラーを監視する（FastAPI + uvicorn + gunicorn + docker + docker-compose + Sentry での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/53)
    - Grafana
        - Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、単一ノードのオンプレミス環境における GPU の駆動状況や Slurm での学習ジョブの予約＆実行状況を可視化する
        - [Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、マルチノードのオンプレミス環境における GPU の駆動状況や Slurm での学習ジョブの予約＆実行状況を可視化する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/116)
    - OpsGenie
        - [[In-progress] Opsgenie を使用して EC2 インスタンスに導入している Datadog で検知したアラートを管理・通知する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/63)
- ログフォワーダ
    - [Fluentd (td-​agent) を使用してログデータを転送する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/29)
    - [Fluentd を使用して Web-API からのログデータを転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/30)
    - Fluentd を使用して GCE 上の Web-API でのログデータを Cloud logging に転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + GKE での構成）
    - [Fluentd を使用して GKE 上の Web-API でのログデータを Cloud logging に転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + GKE での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/32)
    - [[In-progress] Fluentd を使用して機械学習 API のログデータを転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + docker-compose での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/28)
    - Fluentd を使用して Python スクリプトからログ集約する

</details>

<details>
<summary>品質テスト / 負荷テスト</summary>

- 単体テスト
    - [[In-progress]【Golang】go test と go mock を使用してコードの単体テストを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/101)
- 負荷テスト
    - 機械学習 API サーバーの負荷テストの基礎事項
    - [GKE で構成した Web API に vegeta atteck を使用して負荷テストする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/25)
    - GKE で構成した機械学習 API に vegeta atteck を使用して負荷テストする
- [Istio の VirtualSevice のトラフィックミラーリング機能を使用して Web-API のシャドウA/Bテストを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/41)
- [Istio の VirtualSevice のトラフィック分割機能を使用して、Web-API のオンラインA/Bテストを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/42)

</details>

<details>
<summary>ジョブ管理 / バッチ処理</summary>

- SLURM
    - [SLURM の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/111)
    - [SLURM をインストールする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/112)
    - [SLURM を使用して学習ジョブの予約＆実行を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/113)
    - [[In-progress] SLURM を使用して複数サーバーでの分散学習を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/114)
- 【AWS】AWS Batch
    - [【AWS】 AWS Batch を使用して EC2 インスタンス上で簡単なバッチ処理を行う（AWS CLI 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/73)
    - 【AWS】 AWS Batch を使用して EC2 インスタンス上で簡単なバッチ処理を行う（terraform 使用）

</details>

<details>
<summary>機械学習ワークフロー / 機械学習パイプライン</summary>

- 【Apahe】Apahe Airflow
- 【GCP】CloudComposer
    - [【GCP】CloudComposer の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/61)
    - [【GCP】CloudComposer v1 を使用して簡単なワークフローを構成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/62)
    - 【GCP】CloudComposer v2 を使用して簡単なワークフローを構成する
- Luigi / gokart
    - Luigi を使用して複雑な処理を行う API のパイプラインを管理する
- Kedro
    - [Kedro を使用して簡単なワークフローを構成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/65)
- MLflow
- 【AWS】Amazon SageMaker
- 【GCP】Kubeflow
    - [【Kubeflow】Kubeflow の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/1)
    - [[In-progress]【Kubeflow】GKE クラスタに Kubeflow を構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/2)
    - [【Kubeflow】Google AI Platform Pipelines を利用して Kubeflow Pipelines の機械学習パイプラインを構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/3)
- 【GCP】Vertex AI
    - [【GCP】Vertex AI の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/105)
    - [【GCP】Vertex Pipelines を使用して機械学習パイプラインを構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/54)
    - 【GCP】Vertex Pipelines を使用して独自のパイプラインコンポーネントでの機械学習パイプラインを構築する

</details>

<details>
<summary>インフラのコード化 / Infrastructure as Code</summary>

- Terraform
    - [Terraform の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/10)
    - Terraform を利用して Amazon IAM を構築する
    - [Terraform を利用して AWS インスタンスを構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/11)
    - [Terraform を利用して AWS インスタンスを構築する（docker 使用時）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/67)
    - [Terraform を利用して Amazon EKS クラスターを構築する（docker 使用時）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/70)
    - Terraform を利用して Amazon EKS クラスターを構築する（定義済み module + docker 使用時）
    - Terraform を利用して GCP インスタンスを構築する。
    - Terraform を利用して機械学習環境の GCP インスタンスを自動的に構築する。
- 【GCP】DeploymentManager
    - 【GCP】DeploymentManager の基礎事項
- 【AWS】CloudFormation

</details>

<details>
<summary>CI/CD</summary>

- [CI/CD の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/4)
- GitHub Actions
    - [GitHub Actions を用いた CI/CD](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/5)
    - GitHub Actions を用いて機械学習の推論APIの CI/CD を行う
    - [[In-progress] GitHub Actions と Terraform を使用して EC2 インスタンスの CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/66)
    - [GitHub Actions, Terraform, ArgoCD を使用して GKE 上の Web-API の CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/68)
- CircleCI
    - [CircleCI と Terraform を使用して EC2 インスタンスの CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/79)
- 【GCP】Cloud Build
    - [【GCP】Cloud Build を用いてローカルPC 上で CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/12)
    - 【GCP】Cloud Build を用いて GCE 上で CI/CD を行う
    - [【GCP】Cloud Build を用いて Cloud Run 上で CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/13)
    - [【GCP】Cloud Build を用いて Cloud Function 上で CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/14)
    - [【GCP】Cloud Build を用いて GKE（CPU動作）上で CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/15)
    - [【GCP】Cloud Build を用いて GKE（GPU動作）上で CI/CD を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/16)
- ArgoCD
    - [ArgoCD を使用して Web-API を Kubernetes（Amazon EKS）上に継続的にデプロイ（CD）する](https://github.com/Yagami360/argocd-exercises)

</details>

<details>
<summary>外部APIサービス・外部プラットフォームサービス</summary>

</details>

## ■ アプリ開発・フロントエンド

<details>
<summary>Web アプリ開発</summary>

- HTML
    - Google タグマネージャー（GMT）
- CSS
- JavaScript / TypeScript
- UI フレームワーク
    - jQuery
    - Vue.js / Nuxt.js
        - [[In-progress]【Vue.js】Vue.js の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/7)
        - [【Vue.js】CDN 版（スタンドアロン版）の Vue.js を使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/9)
        - [【Vue.js】Vue.js スクリプトの基本的な書き方（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/11)
        - [【Vue.js】vue-cli を用いて Vue.js アプリをデプロイする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/10)
        - [【Vue.js】v-html 属性を使用して `{{}}` を HTML の要素（タグ）として認識させる（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/13)
        - [【Vue.js】v-bind 属性を使用して HTML タグの属性に値を設定する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/14)
        - 【Vue.js】v-if 属性を使用して条件付きでレンダリングする（CDN 版での構成）
        - 【Vue.js】v-for 属性を使用してオブジェクトのプロパティを順にレンダリングする（CDN 版での構成）
        - [【Vue.js】コンポーネントの基本的な書き方（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/12)
        - [[In-progress]【Vue.js】コンポーネントで v 属性を利用する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/15)
        - [【Vue.js】コンポーネントでイベント処理する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/16)
        - 【Vue.js】Bootstrap（CSSのフレームワーク）を Vue.js アプリケーション内で使用する（CDN 版での構成）
    - <a id="React"></a>React / Next.js
        - [[In-progress]【React】React の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/18)
        - [【React】CDN 版（スタンドアロン版）の React を使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/19)
        - [【React】Creat React App を用いて React アプリをデプロイする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/20)
        - [【React】JSX を用いて階層構造のタグを表示する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/21)
        - [【React】JSX に変数値を埋め込む（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/22)
        - [【React】JSX で HTML 属性に変数値を設定する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/23)
        - [【React】関数コンポーネントを使用する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/24)
        - [【React】クラスコンポーネントを使用する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/25)
        - [【React】クラスコンポーネントでステートを使用する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/26)
        - [【React】クラスコンポーネントでイベントを割り当てる（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/27)
        - [【React】クラスコンポーネントでコンテキストを使用する（CDN 版での構成）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/28)
        - [[In-progress]【React】React で Material-UI のコンポーネントを使用する（TypeScript 使用）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/46)
        - 【React】React で Material-UI のテンプレートを使用する（TypeScript 使用）
        - 【React】React でレスポンシブデザインを行う
        - [【React】Redux を使用して値の状態管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/29)
        - [【React】Redux Persist で React アプリのデータを永続化する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/31)
        - [【React】React Hooks のステートフックを使用して値の状態管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/36)
        - 【React】React Hooks のステートフックを使用して配列の状態管理を行う
        - [【React】React Hooks で副作用フックを使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/37)
        - [【React】React Hooks で独自フックを使用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/38)
        - [【React】React Hooks でステートフックを永続化する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/39)
        - 【React】useRef を使用して DOM 要素を設定する
        - 【React】useRef を使用して自動スクロールを行う
        - 【React】useRef を再描画を行わないコンポーネント内変数として利用する
        - 【React】forwardRef を使用して子コンポーネントの DOM 要素に useRef で作成した ref オブジェクトを渡す
        - 【React】useImperativeHandle を使用して親コンポーネントから子コンポーネントで定義したメソッドを呼び出す
        - [【React】React Router で複数ページの React アプリを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/47)
        - [[In-progress]【React】Next.js を使用してサーバーサイドレンダリング（SSR）する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/32)
        - [[In-progress]【React】Next.js で Redux を使用して値の状態管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/35)
        - [[In-progress]【React】Next.js アプリでレイアウトを関数コンポーネントで行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/44)
        - [【React】React + Redux アプリで Firebase の Realtime Database を利用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/33)
        - [【React】Next.js + React Hooks アプリで Firebase の Firestore Database を利用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/42)
        - [【React】Next.js + React Hooks アプリで Firestore Database の基本的なデータベース操作を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/43)
        - [[In-progress]【React】Next.js + React Hooks アプリで Firebase Authentication でのユーザー認証を利用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/45)
        - 【React】react-beautiful-dnd を使用してドラック＆ドロップ処理を行う
        - 【React】react-infinite-scroller を使用して無限スクロールを行う
        - 【React】html2canvas を使用して React アプリでスクリーンショット画像を出力する
        - 【React】window.requestAnimationFrame を使用してアニメーションを行う
        - 【React】GSAP を使用して React アプリで CSS アニメーションを行う
        - 【React】Sentry を使用して React アプリのエラーを監視する
        - [【React】React と Redux を使用して簡単なウェブアプリを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/30)
        - [【React】React と React Hooks を使用して簡単なウェブアプリを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/40)
        - [【React】Next.js と React Hooks と Firebase を使用して簡単なウェブアプリを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/41)
        - 【React】React を使用して http 通信での WebAPI からの出力を返す GUI 付きウェブアプリを作成する
        - 【React】React アプリから Twitter API を使用する
        - 【React】React アプリから Youtube Data API / YouTube Live Streaming API を使用する
        - 【React】React アプリから IFrame Player API を使用する
        - [【React】React を使用した Web アプリの実装コード集](https://github.com/Yagami360/react-app-exercise)        
- Firebase
    - [【Firebase】Firebase Hosting を使用して静的なウェブサイトをデプロイする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/14)
    - [【Firebase】Firebase Cloud Function を使用して動的なウェブアプリをデプロイする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/15)
    - [【Firebase】Firebase Authentication を使用してウェブアプリに Authentication 機能を導入する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/16)
    - [[In-progress]【Firebase】Cloud Storage for Firebase を使用してウェブアプリ上で使用する画像データを表示する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/2)
    - [[In-progress]【Firebase】Firebase Hosting を使用して GKE 上の https 通信での WebAPI からの出力を返す GUI 付きウェブアプリを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/5)
    - [【Firebase】Firebase Hosting と Firebase Cloud Function を使用して GKE 上の http 通信での WebAPI からの出力を返す GUI 付きウェブアプリを作成する（リバースプロキシとしての firebase cloud function 経由で API を呼び出す）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/6)
    - 【Firebase】Firestore Security Rules の設定
- Netlify
    - [Netlify を使用して簡単なウェブサイトをホスティングする（GitHub レポジトリの連携で行う場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/49)
    - [Netlify を使用して簡単なウェブサイトをホスティングする（CLI で行う場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/50)
- Streamlit
    - [Streamlit を使用して簡単なウェブサイトを作成する（GitHub レポジトリの連携で行う場合）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/48)
    - [stlite を使用して Streamlit アプリをローカルマシンのブラウザ上で実行（サーバレス）させる](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/web_app/51)

</details>

<details>
<summary>iOS アプリ開発</summary>

- iOS アプリ開発の基本事項
- Swift
- Firebase
    - [【Firebase】iOS アプリ（Xcodeプロジェクト）に Firebase を登録する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/ios_app/2)
    - [【Firebase】iOS アプリから Firebase Cloud Functions を利用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/ios_app/3)
    - 【Firebase】Firebase Authentication を使用して iOS アプリに Authentication 機能を導入する
    - 【Firebase】Firebase Hosting と Firebase Cloud Function を使用して GKE 上の http 通信での WebAPI からの出力を返す iOS アプリを作成する（リバースプロキシとしての firebase cloud function 経由で API を呼び出す）

</details>

<details>
<summary>アンドロイドアプリ開発</summary>

- Kotlin

</details>

<details>
<summary>クロスプラットホームアプリ開発</summary>

- Dart 言語
- UI フレームワーク
    - Flutter
        - [【Flutter】Flutter を使用して Web アプリの Hello World を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/1)
        - [【Flutter】`pubspec.yml` でパッケージ管理（ライブラリ管理）を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/2)
        - [【Flutter（外部サイト）】StatefulWidget のライフサイクル](https://zenn.dev/kazutxt/books/flutter_practice_introduction/viewer/intermediate_lifecycle)
        - 【Flutter】StatefulWidget を使用して値の状態管理を行う
        - [【Flutter】Provider を使用して値の状態管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/16)
        - [【Flutter】ChangeNotifierProvider を使用して値の状態管理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/17)
        - 【Flutter】Stream, StreamBuilder, BLoCデザインパターンを使用して動的に Widget を更新する
        - [【Flutter】Container を使用して HTML での div 要素のようにアプリ画面の領域を指定する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/4)
        - [【Flutter】ListView の `ListView(...)` を使用して固定リスト長のリストレイアウトを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/8)
        - [【Flutter】ListView の `ListView.builder(...)` を使用して可変リスト長のリストレイアウトを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/9)
        - [【Flutter】GridView の `GridView.builder(...)` を使用して可変グリッド数のグリッドレイアウトを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/5)
        - 【Flutter】BottomNavigationBar を使用してフッターを作成する        
        - [【Flutter】ポートレートモード（縦向き）でのレスポンシブデザインを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/12)
        - 【Flutter】ポートレートモード（縦向き）とランドスケープモード（横向き）双方でのレスポンシブデザインを行う
        - [【Flutter】Navigator の `pop()`, `push()` メソッドを使用して画面のページ遷移を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/3)
        - 【Flutter】Navigator の `popNamed()`, `pushNamed()` メソッドを使用して画面のページ遷移を行う
        - [【Flutter】ScrollController を使用してスクロール位置を指定した位置に動かす](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/6)
        - 【Flutter】Google Font を使用する
        - 【Flutter】Animated 系 Widget を使用してアニメーションを行う
        - [【Flutter】AnimationController を使用してアニメーションを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/13)
        - [【Flutter】Tween を使用してアニメーションを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/14)
        - 【Flutter】Transition 系 Widget を使用してアニメーションを行う
        - 【Flutter】Transition 系 Widget を使用して画面のページ遷移時のアニメーションを行う
        - [【Flutter】SliverAppBar を使用してスクロール時に大きさが変わるヘッダーを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/7)
        - [【Flutter】独自のフッターを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/10)
        - [【Flutter】スクロール時に大きさが変わる独自のフッターを作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/11)
        - [【Flutter】Flutter アプリから Firebase Authentication でのユーザー認証を利用する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/18)
        - [【Flutter】Flutter アプリから Firestore Database を使用する。](https://github.com/Yagami360/ai-product-dev-tips/tree/master/front_end/cross_platform_app/15)
        - 【Flutter】Flutter アプリから Firebase Cloud Storage を使用する。
        - 【Flutter】Flutter アプリから Firebase Cloud Function を使用する。
        - 【Flutter】Flutter Web アプリから Firebase Hosting を使用する。
        - 【Flutter】Sentry を使用して Flutter アプリのエラーを監視する
        - 【Flutter】Flutter アプリから非同期 API を使用する
        - 【Flutter】Flutter アプリから Twitter API を使用する
        - 【Flutter】Flutter アプリから Youtube Data API / YouTube Live Streaming API を使用する
        - 【Flutter】Flutter アプリから IFrame Player API を使用する
    - React Native

</details>

<details>
<summary>サーバサイド</summary>

- Node.js

</details>

<details>
<summary>サーバレス / FaaS [Function as a Service]</summary>

- Firebase
    - [【Firebase】Firebase の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/server_processing/12)
    - 【Firebase】Firebase Cloud Function を JavaScript(`Node.js`) ではなく Google Cloud Function で登録した Python スクリプトで登録する
    - https 通信での Web サイトからリバースプロキシとしての Firebase Cloud Function 経由で http 通信での Web-API を呼び出す

</details>

<details>
<summary>ロギング / モニタリング</summary>

- Google Analytics
- Sentry

</details>

<details>
<summary>UI デザイン / UX デザイン</summary>

- UI デザイン / UX デザイン
    - UI デザインの基礎事項
    - Figma
        - 【Figma】Figma で Material-UI の UI を使用する

</details>

## ■ LLM アプリケーション開発

<details>
<summary>LLM アプリケーション開発</summary>

- LLM 基礎事項
    - [[In-progress] LLM学習方法の基礎事項](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/31)

- OpenAI の LLM 系サービス
    - [【CLI/Python】OpenAI API の使用方法](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/102)
    - [[In-progress]【Python】ChatGPT plugins を利用＆作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/108)
    - [Function calling を使用して、入力文に応じて適切な外部関数の呼び出し、外部関数の戻り値に基づく出力文を生成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/12)
    - OpenAI API を使用して、OpenAI LLM（GPT-3.5, GPT-4系）のファインチューニングを行う

- Microsoft (Azure) の LLM 系サービス
    - Azure OpenAI Service
        - [[In-progress] Azure OpenAI Service の使用方法](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/4)
    - Prompt flow（旧 Azure Machine Learning Prompt flow）
        - [Prompt flow の概要](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/16)
        - [Prompt flow の基本的な使い方](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/14)
        - [Prompt flow を使用してプロンプトチューニングを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/15)
        - [Prompt flow をデプロイして、アプリケーションから API として利用できるようにする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/17)
        - Prompt flow CLI/SDK を使用して Prompt flow の実行を行う
        - Prompt flow CLI/SDK を使用して Prompt flow の CI/CD を行う

- Anthropic の LLM 系サービス
    - [[In-progress] Claude の概要](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/25)
    - [Claude 3.5 Sonnet の Artifacts を使用してアプリのコードとデモを自動生成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/26)

- LangChain
    - [LangChain の概要](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/1)
    - LangChain Model I/O
        - [【Python】LangChain Language models を使用して OpenAI API の LLM モデルから応答文を得る](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/2)
        - [【Python】LangChain Prompt の Prompt templates 使用してプロンプトを生成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/6)
    - LangChain Data connection
        - [【Python】LangChain Retrievers を使用して LLM が学習に使用していない独自ドメインでの外部データに対しての LLM の応答文を得る](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/3)
    - LangChain Memory
        - [[In-progress]【Python】LangChain Memory を使用して LLM へのプロンプトや応答文の履歴を保持し、過去の応答履歴を反映した出力を得る](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/8)
    - LangChain Agents
        - [[In-progress]【Python】LangChain Agents を使用してプロンプトの内容に応じた外部ツールを実行する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/7)
        - [[In-progress] LangChain Agents の OpenAI Functions Agent を使用して Function calling を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/13)
    - LangChain Evaluation
        - LangChain Evaluation を使用して LLM からの回答の品質評価を行う
    - LangSmith
        - 実行トレース管理機能
            - [[In-progress]【Python】LangSmith を使用して UI コンソール上から LLM アプリケーションの実行トレースと実行ログを確認する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/5)
            - [[In-progress]【Python】LangSmith を使用して人間によるフィードバックを実行トレースに付与する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/11)
        - データセット管理機能
            - [[In-progress]【Python】LangSmith の Evaluation 機能を使用して、データセット化した入出力履歴の評価スコアを表示する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/9)

<!--
        - [[In-progress]【Python】LangSmith を使用してデータセットから LLM モデルのファインチューニングを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/10)
-->

- Hugging Face
    - [Hugging Face の概要](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/103)
    - [【CLI/Python】Hugging Face Hub の基本的な使用方法](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/104)
    - [【Python】Hugging Face Transformers を使用して NLP モデルの推論処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/106)
    - [【Python】Hugging Face Spaces を利用して簡単な機械学習デモアプリを構築する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/107)
    - 【Python】Hugging Face の LLM モデルを LangChain で使用する
    - [[In-progress] HuggingFace Transformers を使用して LLM のファインチューニングを行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/29)
    - HuggingFace Transformers を使用して Llama での推論を行う
    - HuggingFace Transformers を使用して Mistral での推論を行う
    - [[In-progress] HuggingFace Transformers を使用して Qwen での推論を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/30)

- NVIDIA AI Enterprise
    - [[In-progress] NVIDIA AI Enterprise & NVIDIA NeMo の概要](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/33)
    - NVIDIA NeMo
        - [[In-progress] NVIDIA NeMo を使用して LLM の推論処理を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/32)
        - NVIDIA NeMo を使用して LLM のファインチューニングを行う
        - NeMo Curator
        - NeMo Customizer
        - NeMo Evaluator
    - NVIDIA NIM
        - [[In-progress] NVIDIA NIM を使用してオンプレミス環境にLLM APIをデプロイする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/34)

- Dify
    - [Dify の概要](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/18)
    - Dify の基本的な使い方（テンプレートを使用した LLM アプリケーションを作成する）
    - [Dify の基本的な使い方（ワークフローを使用した LLM アプリケーションを作成する）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/20)
    - Dify を使用して RAG を使用した LLM アプリケーションを作成する
    - [Dify を使用した LLM アプリケーションを Web アプリとして外部公開する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/21)
    - [Dify を使用した LLM アプリケーションを API として外部公開する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/22)
    - [[In-progress] Dify を使用した LLM アプリケーションを Web サイトへの埋め込みとして外部公開する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/24)
    - [ Dify をローカル環境（オンプレ環境）で起動する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/23)

<!--
    - [[In-progress] Dify の基本的な使い方（チャットボット用ワークフローを構築する）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/19)
-->

- DeepEval
    - [DeepEval を使用して LLM からの回答の品質評価を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/27)
    - [DeepEval を使用してデータセットの品質評価を行う](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/28)
    - DeepEval のローカル評価モードを使用して LLM からの回答の品質評価を非API経由で行う


</details>

## ■ 特許

<details>
<summary>xxx</summary>

- xxx

</details>

## ■ その他

<details>
<summary>xxx</summary>

- xxx

</details>
