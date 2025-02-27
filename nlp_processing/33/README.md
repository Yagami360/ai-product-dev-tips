# NVIDIA AI Enterprise & NVIDIA NeMo の概要

- NVIDIA AI Enterprise<br>
    NVIDIAが提供しているクラウドやオンプレミス環境におけるAIアプリケーションの開発や運用を支援するプラットフォームで、データの準備から機械学習モデルの学習、推論、デプロイまでをサポートしている

    以下のサービス群から構成される

    - NVIDIA NeMo フレームワーク<br>
        <img width="500" alt="Image" src="https://github.com/user-attachments/assets/2f7f7ff5-7740-45ff-aef7-e9730167dae8" />

        NLPや音声系の生成AIなどのマルチモーダルAIアプリケーションの開発を支援するフレームワーク。
        以下のようなサービス群から構成される

        - NeMo Curator

        - NeMo Customizer

        - NeMo Evaluator

        - NeMo Guardrails

        - xxx

    - NVIDIA NIM [NVIDIA Inference Microservices]
        NVIDIAが提供するLLMモデルなどの生成AIモデルを、クラウド環境やオンプレミス環境にデプロイして、推論APIとして容易に利用できるようになるサービス。NVIDIA NIM の docker iamge を pull & run して、クラウド環境やオンプレミス環境にデプロイすることができる

    - xxx


## 参考サイト

- 公式ユーザーガイド: https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html

- https://developer.nvidia.com/ja-jp/blog/simplify-custom-generative-ai-development-with-nvidia-nemo-microservices/

- https://github.com/NVIDIA/NeMo