# Rancher の RKE を使用して、オンプレミス環境上に Kubernetes クラスターを構築する

今回の例では、簡単のため１台のオンプレミス環境上に、Rancher の RKE を使用して Kubernetes クラスターを構築する方法を記載する

## 方法

1. オンプレミス環境を準備する

1. パッケージを更新する
    ```bash
    sudo apt update
    ```

1. Docker をインストールする
    ```bash
    sudo apt install docker.io
    ```

1. RKE をインストールする<br>
    ```bash
    wget https://github.com/rancher/rke/releases/latest/download/rke_linux-amd64
    mv rke_linux-amd64 rke
    chmod +x rke
    ```

1. RKE クラスターの設定ファイル `cluster.yml` を作成する

    - `rke config` で作成する場合<br>
        `rke config` コマンド実行後、`cluster.yml` が自動的に作成される
        ```bash
        ./rke config
        ```
    
    - 手動で作成する場合
        ```bash
        cat > cluster.yml <<EOL
        nodes:
        - address: [サーバー外部IP（同じサーバー上の場合は内部IP）]
          internal_address: [サーバー内部IP]
          user: [SSHユーザー名]
          role: [controlplane,etcd,worker]
          ssh_key_path: ~/.ssh/id_rsa
        EOL
        ```

1. SSH 公開鍵をサーバーにコピーする<br>
    ```bash
    ssh-copy-id -i ~/.ssh/id_rsa.pub ${SSH_USER}@${SERVER_EXTERNAL_IP}
    ```

    GCP の VM インスタンスの場合は、Compute Engine > メタデータ > SSHキー から、SSH公開鍵を追加する

1. RKE クラスターをデプロイする<br>
    ```bash
    ./rke up
    ```
    ```bash
    INFO[0000] Running RKE version: v1.7.2                  
    INFO[0000] Initiating Kubernetes cluster                
    INFO[0000] [dialer] Setup tunnel for host [xx.xx.xx.xx] 
    ...
    ```

    デプロイ正常完了後、`kube_config_cluster.yml` が自動的に作成される。

1. kubeconfig 設定を更新する<br>
    `rke up` コマンド実行後、`kube_config_cluster.yml` が自動的に作成されるので、`~/.kube/config` の YAMLファイルに追加する

    - `~/.kube/config`
        ```yaml
        # 既存のクラスター設定
        apiVersion: v1
        clusters:
        - cluster:
          certificate-authority-data: xxx
          server: https://xxx.xxx.xxx.xxx
          name: arn:aws:eks:us-west-2:xxxx:cluster/xxxx
        ...
        # RKE Cluster
        clusters:
        - cluster:
            api-version: v1
            certificate-authority-data: xxx
            server: "https://xxx.xxx.xxx.xxx:6443"
            name: "local"
        contexts:
        - context:
            cluster: "local"
            user: "kube-admin-local"
            name: "local"
        current-context: "local"
        users:
        - name: "kube-admin-local"
        user:
            client-certificate-data: xxx
            client-key-data: xxx
        ```

1. クラスターの状態を確認する<br>
    ```bash
    kubectl --kubeconfig=kube_config_cluster.yml get nodes
    ```
    ```bash
    NAME            STATUS   ROLES                      AGE   VERSION
    xx.xxx.xx.xxx   Ready    controlplane,etcd,worker   80s   v1.31.4
    ```

1. k8s マニフェストを作成する
    今回の例では、簡単な例として、nginx の Pod の k8s マニフェストを作成する

    - `k8s/nginx.yaml`
        ```yaml
        apiVersion: v1
        kind: Pod
        metadata:
        name: nginx-pod
        labels:
            app: nginx
        spec:
        containers:
        - name: nginx
            image: nginx:latest
            ports:
            - containerPort: 80
        ```

1. Pod をデプロイする<br>
    ```bash
    kubectl --kubeconfig=kube_config_cluster.yml apply -f k8s/nginx.yaml
    ```

1. Pod の状態を確認する<br>
    ```bash
    kubectl --kubeconfig=kube_config_cluster.yml get pods
    ```
    ```bash
    NAME        READY   STATUS    RESTARTS   AGE
    nginx-pod   1/1     Running   0          2m37s
    ```

1. RKE クラスターを削除する<br>
    ```bash
    kubectl delete pods --all --all-namespaces
    ./rke remove
    ```

## 参考サイト

- https://tech.virtualtech.jp/entry/2019/09/03/142114