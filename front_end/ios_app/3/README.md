# 【Firebase】iOS アプリから Firebase Cloud Functions を利用する

## ■ 手順

1. Firebase Cloud Functions をデプロイする。<br>
    > 参考記事 : 「[【Firebase】Firebase Cloud Function を使用して動的なウェブアプリをデプロイする](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/15)」
    1. firebase にログインする<br>
        ```sh
        $ firebase login
        ```
    1.  Firebase プロジェクトを初期化<br>
        初期化する機能は、Firebase Cloud Functions のみで良い
        ```sh
        $ firebase init
        ```
    1. Firebase Cloud Functions `functions/index.js` を修正する。<br>
        `index.js` 内のコードを、例えば以下のように修正する。<br>
        > レスポンス値は json フォーマットでの dict 型に設定する必要があることに注意
        ```js
        const functions = require('firebase-functions');

        exports.helloWorld = functions.https.onRequest(
            (request, response) => {
                response.send({
                    data: "Hello from Firebase Cloud Functions!"
                })
            }
        );
        ```
    1.  動的なウェブアプリをデプロイする<br>
        以下のコマンドで動的なウェブアプリ（`functions/index.js`）を Hosting にデプロイして、公開する
        ```sh
        $ firebase deploy --only functions
        ```

1. 「[iOS アプリ（Xcodeプロジェクト）に Firebase を登録する](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ios_app/2)」記載の処理を行う。
1. Pod ファイル `Podfile` がない場合は、Xcode プロジェクトに Pod ファイルを作成する<br>
    Xcode プロジェクトに移動して、以下のコマンドで Pod ファイルを作成する
    ```sh
    $ cd ${XCODE_PROJ_DIR}
    $ pod init
    ```
1. Pod ファイル `Podfile` を以下のように修正する。<br>
    ```pod
    # Uncomment the next line to define a global platform for your project
    # platform :ios, '9.0'
    target 'sample-ios-app-project' do
        # Comment the next line if you don't want to use dynamic frameworks
        use_frameworks!

        # Pods for sample-ios-app-project
        pod 'Firebase/Core'         # Firebase のコア部分のライブラリ
        pod 'Firebase/Functions'    # Firebase Cloud Functions のライブラリ

        target 'sample-ios-app-projectTests' do
        inherit! :search_paths
        # Pods for testing
        end

        target 'sample-ios-app-projectUITests' do
        # Pods for testing
        end
    end
    ```
1. Pod ファイルに追加定義した Pod をインストールする。<br>
    ```sh
    $ cd ${XCODE_PROJ_DIR}
    $ pod install
    ```
1. `pod install` コマンド実行後に作成されたプロジェクトファイル `*.xcworkspace` を開く。

1. `ViewController.swift` を例えば以下のようなコードに修正し、iOS アプリから Firebase を読み込み、Firebase Cloud Functions のコールバック関数を定義する。<br>
    `functions.httpsCallable("helloWorld").call()` で `functions/index.js` 内にある `helloWorld` の Firebase Cloud Functions を呼び出し、`call()` 後の `{ (result, error) in ... }` 内で、Firebase Cloud Functions 呼び出し後のコールバック関数を定義している点がポイント。
    ```swift
    import UIKit
    import Firebase

    class ViewController: UIViewController {
        // アウトレット（Swift ソースコード内でのストーリーボード上のオブジェクト（ボタンなど）への参照）
        @IBOutlet weak var firebase_name_label: UILabel!
        @IBOutlet weak var cloud_function_label: UILabel!

        // Firebase Cloud Functions インスタンス作成
        lazy var functions = Functions.functions()

        // 起動時のイベントハンドラ（インスタンス化された直後の初回に一度のみ）
        override func viewDidLoad() {
            super.viewDidLoad()
            // firebase_name_label に FirebaseApp の名前を設定
            firebase_name_label.text = FirebaseApp.app()?.name
        }

        // ボタンを押したときのイベントハンドラ
        @IBAction func bt_cloud_funtion(_ sender: Any) {
            // Firebase Cloud Functions の呼び出し
            // call() 後の { (result, error) in ... } 内が Firebase Cloud Functions 呼び出し後のコールバック関数（Closure、無名関数）
            // result : Firebase Cloud Functions 内で問題なく値を取得した場合の情報。result.data に実際の値が格納される
            // error : Firebase Cloud Functions 内で例外が発生した場合のエラー（エラークラス NSError のオブジェクト）
            functions.httpsCallable("helloWorld").call() { (result, error) in
                // Firebase Cloud Functions 内でエラー発生時の処理
                if let error = error {
                    print( "error : ", error )
                }
                // Firebase Cloud Functions 成功時の処理
                else {
                    if let data = result?.data as? String {
                        print( "data : ", data )
                        self.cloud_function_label.text = data
                    }
                }
            }
    }
    ```


## ■ 参考サイト
- https://firebase.google.com/docs/functions/callable
- https://qiita.com/ICTFractal/items/753e5824806fde8a0d10