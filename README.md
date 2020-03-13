# MachineLearning_PreProcessing_Exercises
機械学習のための前処理の練習用コード

## ■ 動作環境

- Python : 3.6
- Anaconda : 5.0.1
- IO関係
    - xxx
- 画像処理系
    - OpenCV : 
    - Pillow :

## ■ 項目

1. 開発環境
    - 【シェルスクリプト】シェルスクリプト内で conda 環境を切り替える。
    - Docker
        - [【Docker】Docker の基本事項・基本コマンド](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/1)
        - [【Docker】docker コンテナ内で機械学習モデルの処理を実行中に tensorboard で実行結果を確認する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/2)
        - [【Docker】コンテナの起動とコンテナ内での python スクリプト実行を一括して行う。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/3)
        - [【Docker】docker-compose を用いず Docker イメージの作成＆コンテナ起動を一括して実行する](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/4)
        - [【Docker】ホスト環境とコンテナ環境で同期したファイルの所有権を指定する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/5)
        - [【Docker】docker exec を nohup で実行する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/6)
        - [【Docker】本番環境用の Docker イメージと開発環境用の Docker イメージの構成](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/docker_processing/7)
        - 【Docker】Docker イメージに sudo 権限ユーザーを追加することで、ホストとコンテナ間の permission 問題を解消する。
        - 【Docker】dockerfile でユーザー追加後に git clone する際の、permission denied エラー対策
        - 【Docker】dockerfile の work_dir 変更前のデフォルトパス
        - 【Docker】Flask & requests を用いてコンテナ間通信するときの、IP アドレス指定方式（コンテナ名で指定）
1. 入出力処理
    - [【シェルスクリプト】フォルダ内のファイル数を確認する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/io_processing/2)
    - [【Python】フォルダ内のファイル一覧を取得する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/io_processing/1)
    - [【Python】２つのフォルダのファイル数＆ファイル名の差分を確認する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/io_processing/3)
    - [【シェルスクリプト】ランダムに１００個のファイルをサンプリングする。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/io_processing/4)
1. サーバー＆クラウド処理
    - 【シェルスクリプト】ssh 切れ対策のために `nohup` コマンドで実行する。
    - 【シェルスクリプト】サーバー間でデータを転送・コピーする。
    - [【UNIX】サーバー上の画像ファイルをブラウザ上で確認する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/server_processing/2)
    - [【シェルスクリプト】GCP or AWS インスタンスをシェルスクリプト上から停止する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/server_processing/1)
    - 【GCP】GCP ディスクを `gcsfuse` コマンドでマウントする。
    - [【GCP】Cloud Scheduler 機能を用いて、サーバーを一定の時間間隔で起動・停止する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/server_processing/4)
    - [【GCP】サーバー起動後に自動的に実行するスクリプトを設定する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/server_processing/5)
    - 【AWS】EC インスタンスのディスク容量を後から増設する。
    - `import pdb; pdb.set_trace()`: 【Python】サーバー上での Python スクリプトをデバッグするときに、ブレークポイントを有効にする。
    - [【シェルスクリプト】シェルスクリプトで、GoogleDrive から大容量データをコピーする。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/server_processing/3)
    - 【Python】スクリプトで GoogleDrive へデータを自動的に転送する。
1. 画像処理
    - [【シェルスクリプト】画像ファイルの解像度を確認する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/1)
    - [【Python】OpenCV ↔ Pillow ↔ numpy の変換対応](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/4)
    - [【Python】画像の滑らかさを落とさないように拡張子を変更する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/3)
    - [【Python】画像やセマンティックセグメンテーション画像の滑らかさを落とさないようにリサイズする。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/2)
    - [【Python】画像の対象物のアスペクト比を変えないまま adjust する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/11)
    - [【Python】画像の対象物全体を膨張・収縮させる。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/14)
    - [【Python】人物画像の特定の対象物のみを膨張・収縮させる。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/16)
    - [【Python】データオーギュメンションや品質評価のための画像の拡大縮小＆平行移動＆回転](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/13)
    - [【Python】セマンティックセグメンテーション画像からラベル値を取得する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/5)
    - [【Python】セマンティックセグメンテーション画像の特定のラベル値の部分を抜き取る。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/6)
    - [【Python】画像のバイナリマスク画像を生成する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/9)
    - [【Python】画像の背景部分をくり抜く。（グラフ カット）](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/10)
    - remove bg を使用して、画像の背景部分をくり抜く。（グラフ カット）
    - [【Python】画像の上下 or 左右対称性を検出する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/8)
    - [【Python】品質評価のためのグリッド画像を生成する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/7)
    - [【Python】元画像とセグメンテーション画像をアルファブレンディングで重ねて表示する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/12)
    - 【Python】画像の特定の対象物が画面端で途切れているかを検出する。
    - 【Python】人物パース画像から上着を着ているような人物画像を検出する。
    1. OpenPose による姿勢推定
        - OpenPose のインストール
        - 【Python】OpenPose の json ファイルを読み込む。
        - 【Python】OpenPose の json ファイルを書き込む。
        - [【Python】OpenPose の json ファイルの関節点を画像表示する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/openpose/1)
        - [【Python】OpenPose の関節点情報に基づき、人物画像を上半身部分でクロップする。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/openpose/3)
        - [【Python】OpenPose の関節点情報に基づき、人物画像が正面を向いているか後ろを向いているか判定する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/openpose/2)
        - [【Python】OpenPose の関節点情報と人物パース画像に基づき、人物画像が半袖を着ているかを検出する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/openpose/4)
        - [【Python】OpenPose の関節点情報に基づき、人物セグメンテーション画像に、他の人体部位のラベルを追加する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/openpose/5)
    1. waifu2x による画像の超解像度
        - waifu2x のインストール
        - waifu2x による画像の超解像度
    1. dlib による顔の landmark 検出
        - [【Python】dlib で顔の landmark 検出を検出し、画像上に表示する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/image_processing/15)
1. 高速化処理
    - 【シェルスクリプト】別プロセスで起動する。
    - [【Python】for ループ内の処理を複数 CPU の並列処理で高速化する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/acceleration_processing/2)
    - [【Python】複数 GPU での並列化のために、フォルダ内のファイルを分割し別フォルダに保存し、その後１つのフォルダに再統合する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/acceleration_processing/1)
    - 【Python】for ではなく行列処理で画像処理を高速化する。
    - 【PyTorch】AMP [Automatic Mixed Precision] を使用した学習と推論の高速化
1. WEB スクレイピング
    - [【Python】WEB 上の画像データを収集する。](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/web_scraping/1)
1. 自然言語処理
1. 音声処理
1. 機械学習フレームワーク
    1. PyTorch
        - 【PyTorch】OpenCV ↔ Pillow ↔ numpy ↔ Tensor [PyTorch] の変換対応
        - 【PyTorch】独自データセットの DataLoader 
        - 【PyTorch】TensorBoard のヒストグラムにネットワークの重みを表示する。
        - 【PyTorch】再現性確保のためのシード値固定処理
1. その他処理
    - 【シェルスクリプト】`curl` コマンドで WebAPI を直接たたく


## ■ 参考文献＆サイト
