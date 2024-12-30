# SLURM の基礎事項

HPC環境でよく利用されるジョブ環境ツールで、特に機械学習モデルの場合では、V100, A100, H100 などの高性能GPUを搭載した複数のオンプレミス環境において、大規模機械学習モデルの学習や推論を行うジョブを管理するためによく利用される。

<img width="500" alt="image" src="https://github.com/user-attachments/assets/f29c3880-9d17-4db6-bc41-05f6361a9b7b" />

- slurmctld<br>
    Slurm の管理用デーモンで、後述するSlurmデーモンとリソースの監視を担う。マスターノードなどのユーザーがジョブを投入するサーバーに配置する必要がある。（計算ノードには不要）

- slurmd<br>
    各計算ノード（サーバー）におけるジョブの実行管理や監視を担うデーモンで、クラスタを構成するすべてのノード（サーバー）に配置する必要がある。

- MUNGE<br>
    HPC [High Performance Computing] 環境でよく使用されるライブラリで、Slurm などでのノード間通信を安全に行うための認証を提供している。<br>
    Slurm でのデフォルトの認証システムは MUNGE になっている

    MUNGE では、共有鍵暗号方式（MUNGE key）を使用してメッセージの認証と暗号化を行う。具体的には、以下のような流れになる
    1. システム全体で共有される鍵（MUNGE key）を使用
    2. この共有鍵（MUNGE key）を使って認証用のトークンを生成
    3. 各ノードは同じMUNGE keyを持っていることで、トークンの検証が可能

- 主要コマンド例<br>

    - `srun`<br>
        ジョブ実行コマンドで、プログラムの実行が終わるまでターミナルがブロックされる
        ```bash
        # srun <オプション> <実行したいプログラム>
        srun --nodes=1 --ntasks=4 --time=01:00:00 python train.py
        ```

    - `sbatch`<br>
        バッチジョブとしてジョブを投入するコマンド（ジョブ予約）<br>
        ```bash
        sbatch train.sh
        ```

        - `train.sh`
            ```bash
            #!/bin/bash
            #SBATCH --job-name=test_job
            #SBATCH --nodes=1
            #SBATCH --ntasks=4
            #SBATCH --time=01:00:00
            python train.py
            ```
            - `—nodes` : ノード数（２以上でマルチノード分散学習にも対応可能）

    - `squeue`<br>
        ジョブの状態を確認するコマンド<br>
        ```bash
        squeue
        ```
        ```bash
        JOBID PARTITION     NAME     USER    STATE       TIME   NODES NODELIST(REASON)
        12345     debug   python    alice  RUNNING       5:32       1 node01
        12346    normal   mytest      bob  RUNNING      12:04       2 node[02-03]
        12347    normal   calc01    carol  PENDING       0:00       1 (Resources)
        12348      gpu8   train1    david  RUNNING      15:04       4 gpu[01-04]
        ```
