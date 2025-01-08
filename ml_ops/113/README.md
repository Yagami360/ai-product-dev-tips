# SLURM を使用して学習ジョブの予約＆実行を行う

## 方法（Ubuntu や Debian の場合）

1. SLURM をインストールする<br>
    [SLURM をインストールする](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/112)　の手順を実行してください

1. （オプション）`slurmctld` と `slurmd` が正常に起動していることを確認する<br>
    ```bash
    sudo systemctl status slurmctld slurmd
    ```

    - 例<br>
        ```bash
        ● slurmctld.service - Slurm controller daemon
            Loaded: loaded (/etc/systemd/system/slurmctld.service; enabled; vendor preset: enabled)
            Active: active (running) since Wed 2025-01-08 06:06:59 UTC; 48min ago
        Main PID: 351903 (slurmctld)
            Tasks: 11
            Memory: 10.3M
                CPU: 1.590s
            CGroup: /system.slice/slurmctld.service
                    ├─351903 /usr/local/sbin/slurmctld -D -s
                    └─351904 slurmctld: slurmscriptd

        ● slurmd.service - Slurm node daemon
            Loaded: loaded (/etc/systemd/system/slurmd.service; enabled; vendor preset: enabled)
            Active: active (running) since Wed 2025-01-08 06:07:02 UTC; 48min ago
        Main PID: 351924 (slurmd)
            Tasks: 1
            Memory: 2.0M
                CPU: 149ms
            CGroup: /system.slice/slurmd.service
                    └─351924 /usr/local/sbin/slurmd -D -s
        ```

1. 学習用ジョブのスクリプトを作成する<br>
    [jobs](./jobs) ディレクトリ以下に作成しています

1. Slurm のジョブを実行する<br>

    - ジョブを実行する場合（`srun` コマンド）<br>
        `srun` は、ジョブ実行コマンドでプログラムの実行が終わるまでターミナルがブロックされる

        ```bash
        # Slurm 経由でのスクリプトの実行権限を付与する（初回のみ）
        chmod +x train.sh

        # ジョブを実行する
        srun --nodes=1 --ntasks=1 train.sh
        ```

    - ジョブを予約する場合（`sbatch` コマンド）<br>
        `sbatch` は、バッチジョブ（ジョブ予約）としてジョブを投入する

        ```bash
        # Slurm 経由でのスクリプトの実行権限を付与する（初回のみ）
        chmod +x train.sh

        # ジョブを予約する
        sbatch train.sh
        ```

        - `train.sh` の例<br>
            ```bash
            #!/bin/bash
            #SBATCH --job-name=test_job
            #SBATCH --nodes=1
            #SBATCH --ntasks=1
            #SBATCH --time=01:00:00

            python train.py
            ```


1. （オプション）ジョブの実行状況を確認する<br>
    ```bash
    squeue
    ```
    ```bash
    # ジョブ名の長さを調整したい場合
    squeue --format="%.18i %.9P %.30j %.8u %.8T %.9M %.4D %R"
    ```

    - 例<br>
        ```bash
        JOBID PARTITION                           NAME     USER    STATE      TIME NODE NODELIST(REASON)
        36     debug             train-job-resnet18    sakai  PENDING      0:00    1 (Resources)
        35     debug             train-job-resnet18    sakai  RUNNING      1:30    1 sakai-dev
        ```

1. （オプション）ジョブの実行結果を確認する<br>
    ```bash
    scontrol show job <job_id>
    ```

    - 例<br>
        ```bash
        JobId=35 JobName=train-job-resnet18
        UserId=sakai(1004) GroupId=sakai(1005) MCS_label=N/A
        Priority=4294901744 Nice=0 Account=(null) QOS=(null)
        JobState=COMPLETED Reason=None Dependency=(null)
        Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
        RunTime=00:02:03 TimeLimit=UNLIMITED TimeMin=N/A
        SubmitTime=2025-01-08T06:36:58 EligibleTime=2025-01-08T06:36:58
        AccrueTime=2025-01-08T06:36:58
        StartTime=2025-01-08T06:36:59 EndTime=2025-01-08T06:39:02 Deadline=N/A
        SuspendTime=None SecsPreSuspend=0 LastSchedEval=2025-01-08T06:36:59 Scheduler=Main
        Partition=debug AllocNode:Sid=sakai-dev:321366
        ReqNodeList=(null) ExcNodeList=(null)
        NodeList=sakai-dev
        BatchHost=sakai-dev
        NumNodes=1 NumCPUs=1 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
        ReqTRES=cpu=1,mem=1M,node=1,billing=1
        AllocTRES=cpu=1,mem=1M,node=1,billing=1
        Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
        MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0
        Features=(null) DelayBoot=00:00:00
        OverSubscribe=OK Contiguous=0 Licenses=(null) Network=(null)
        Command=/home/sakai/abeja-platform-onpremise/slurm-exercises/jobs/train.sh
        WorkDir=/home/sakai/abeja-platform-onpremise/slurm-exercises/jobs
        StdErr=/home/sakai/abeja-platform-onpremise/slurm-exercises/jobs/slurm-35.out
        StdIn=/dev/null
        StdOut=/home/sakai/abeja-platform-onpremise/slurm-exercises/jobs/slurm-35.out
        Power=
        ```
