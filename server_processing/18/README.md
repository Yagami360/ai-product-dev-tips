# 【Firebase】Firebase Cloud Function を JavaScript(`Node.js`) ではなく Google Cloud Function で登録した Python スクリプトで登録する
Cloud Functions for Firebase では、`firebase deploy` コマンドで Firebase CLI を使って deploy するときに、JavaScript(`Node.js`) か TypeScript しか選択できないが、Firebase 各種機能設定ファイルである `firebase.json` の設定値を変えることで、Google Cloud Function で登録した Python スクリプトを登録することが可能である。

## ■ 手順
1. [Firebase プロジェクトの作成](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/15)
    1. Firebase コンソール画面からプロジェクト作成
    1. Firebase プロジェクトへのログイン
        ```sh
        $ firebase login
        ```
    1. Firebase プロジェクトを初期化
        ```sh
        $ firebase init
        ```
1. Firebase プロジェクトと同じプロジェクトの GCP 画面で Google Cloud Function を作成する
1. `firebase.json` に `rewrites` 設定を追加する
    ```json
    {
        :
    "hosting": {
        :
        "rewrites": [{
            "source": "/エンドポイント名",
            "function": "pythonの関数名"
        }],
        :
    }
        :
    }    
    ```
1. Firebase Cloud Function を deploy
    ```sh
    $ firebase deploy --only functions
    ```
1. Firebase Cloud Function の公開 URL にアクセスする
    ```sh
    $ open https://${独自ドメイン}/${エンドポイント名}
    ```

## ■ 参考サイト
- https://www.marketechlabo.com/google-cloud-functions/