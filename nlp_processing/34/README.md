# NVIDIA NIM を使用してオンプレミス環境にLLM APIをデプロイする


## 使用方法

1. NVIDIA AI Enterpriseライセンスを取得する

1. API キー（NGC_API_KEY）を発行する

1. GPU マシンを用意する

1. NVIDIA NGC認証の設定する
    ```sh
    mkdir -p ~/.docker
    cat > ~/.docker/config.json << EOF
    {
    "auths": {
        "nvcr.io": {
        "username": "$oauthtoken",
        "password": "NGC_API_KEY"
        }
    }
    }
    EOF
    ```

1. NVIDIA NIM のコンテナを pull する<br>
    - 基本コンテナの場合<br>
        ```sh
        docker pull nvcr.io/nvidia/nim:23.10-runtime
        ```

    - 特定LLMモデル用のコンテナの場合<br>
        ```sh
        docker pull nvcr.io/nvidia/nim:llama-2-70b
        ```

1. LLMモデルの設定をカスタマイズする<br>
    ```sh
    mkdir -p nim-config
    cat > nim-config/config.json << EOF
    {
    "model_config": {
        "tensor_parallel_size": 4,
        "max_batch_size": 32,
        "max_tokens_in_batch": 8192,
        "max_input_tokens": 2048,
        "max_output_tokens": 1024,
        "quantize": "int8"
    }
    }
    EOF
    ```

1. NVIDIA NIM のコンテナを起動する<br>

    - 特定LLMモデル用のコンテナの場合<br>
        ```sh
        docker run --gpus all -d --name llama-nim-custom \
        --shm-size=1g \
        -p 8000:8000 \
        -v $(pwd)/nim-config:/config \
        -v /path/to/model/data:/models \
        --env NIM_CONFIG_PATH=/config/config.json \
        nvcr.io/nvidia/nim:llama-2-70b
        ```

    - （オプション）Kubernetes でデプロイする場合（スケーラビリティ向上）<br>

        ```sh
        cat > llm-nim-deployment.yaml << EOF
        apiVersion: apps/v1
        kind: Deployment
        metadata:
        name: llama-nim
        spec:
        replicas: 1
        selector:
            matchLabels:
            app: llama-nim
        template:
            metadata:
            labels:
                app: llama-nim
            spec:
            containers:
            - name: llama-nim
                image: nvcr.io/nvidia/nim:llama-2-70b
                resources:
                limits:
                    nvidia.com/gpu: 8
                ports:
                - containerPort: 8000
                volumeMounts:
                - name: nim-config
                mountPath: /config
                - name: model-data
                mountPath: /models
                env:
                - name: NIM_CONFIG_PATH
                value: "/config/config.json"
            volumes:
            - name: nim-config
                configMap:
                name: nim-config
            - name: model-data
                persistentVolumeClaim:
                claimName: model-data-pvc
        ---
        apiVersion: v1
        kind: Service
        metadata:
        name: llama-nim-service
        spec:
        selector:
            app: llama-nim
        ports:
        - port: 8000
            targetPort: 8000
        type: ClusterIP
        EOF
        ```

        ```sh
        # マニフェストの適用
        kubectl apply -f llm-nim-deployment.yaml
        ```

1. LLMモデルのAPIをテストする<br>
    ```sh
    curl -X POST http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama-2-70b",
        "prompt": "AIとは何ですか？",
        "max_tokens": 100,
        "temperature": 0.7
    }'
    ```


## 参考サイト

- https://cn.teldevice.co.jp/blog/p54562/