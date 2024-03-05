# Prompt flow をデプロイして、アプリケーションから API として利用できるようにする

Prompt flow では、LLM アプリケーションの処理をコンソール UI 上で定義＆実行＆可視化できるが、このままでは他のアプリケーションから利用できない。
作成したフローをデプロイし、Arure 上の API として利用できるようにすることで、他のアプリケーションから作成したフローを利用できるようになる

## 使用方法

1. 「[Prompt flow の基本的な使い方](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/14)」に従って Prompt flow を作成する

1. 作成したフローをデプロイする<br>
    作成したフローにおいて、画面右上の「デプロイ」ボタンをクリックする。<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/7a85145d-0345-4b6d-9a89-bb5bbff4e7d7"><br>

    「デプロイ」ボタンをクリック後、ウィザード画面が表示されるので必要な設定を行い、「作成」ボタンをクリックする<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/f150a831-457c-4bd1-bdcc-190dd7eeea42"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/1bdff903-89e6-437b-8b94-4e5df5962a52"><br>
    ...<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/19413b91-2cb0-4aca-948a-fd1eefa4bfae">

    > リアルタイムエンドポイントとしてデプロイされるので、サーバーコストが継続的に発生するのとに注意

    > サーバーレスエンドポイントとしてもデプロイ可能？

1. エンドポイントを確認する<br>
    デプロイ完了後 Azure リソース上に API がデプロイされているので、左メニューの「エンドポイント」から確認する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/20255f18-1813-4944-b5a0-29a795ab40b0"><br>

    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/e7f6940e-1536-4729-9ac9-7806d36220b2"><br>

    > デプロイした API のオートスケーリングも行える

1. API にリクエストする<br>
    デプロイした API のエンドポイントにリクエストする<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/c018e4d0-aab6-4063-a888-b431f10c43b5"><br>

    - シェルスクリプトで行う場合
        ```sh
        curl -X POST \
            -H 'Content-Type: application/json' \
            -H 'Authorization: Bearer ${APIキー}' \
            -d '{ "inputs":{ "topic": ["ねこ"]}}' \
            "https://${ワークスペース名}.${リージョン名}.inference.ml.azure.com/score"
        ```

    - Python で行う場合
        ```python
        import urllib.request
        import json
        import os
        import ssl

        def allowSelfSignedHttps(allowed):
            # bypass the server certificate verification on client side
            if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
                ssl._create_default_https_context = ssl._create_unverified_context

        allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

        # Request data goes here
        # The example below assumes JSON formatting which may be updated
        # depending on the format your endpoint expects.
        # More information can be found here:
        # https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
        data = {}

        body = str.encode(json.dumps(data))

        url = 'https://workspace-test-1-dilqs.eastus2.inference.ml.azure.com/score'
        # Replace this with the primary/secondary key or AMLToken for the endpoint
        api_key = ''
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        # The azureml-model-deployment header will force the request to go to a specific deployment.
        # Remove this header to have the request observe the endpoint traffic rules
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'workspace-test-1-dilqs-1' }

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)

            result = response.read()
            print(result)
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
        ```

## 参考サイト

- https://dev.classmethod.jp/articles/azureml-prompt-flow-ktkr/