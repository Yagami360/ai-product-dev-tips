# 【Firebase】iOS アプリから Firebase Cloud Functions を利用する

## ■ 手順

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

1. `ViewController.swift` を例えば以下のようなコードに修正し、iOS アプリから Firebase と Firebase Cloud Functions を読むこむ。<br>
    ```swift
    import UIKit
    import Firebase     // @ Firebase での追加箇所

    class ViewController: UIViewController {
        // アウトレット（Swift ソースコード内でのストーリーボード上のオブジェクト（ボタンなど）への参照）
        @IBOutlet weak var firebase_name_label: UILabel!

        // Firebase Cloud Functions インスタンス作成
        lazy var functions = Functions.functions()

        // 起動時のイベントハンドラ（インスタンス化された直後の初回に一度のみ）
        override func viewDidLoad() {
            super.viewDidLoad()
            // firebase_name_label に FirebaseApp の名前を設定
            firebase_name_label.text = FirebaseApp.app()?.name  // @ Firebase での追加箇所
        }

        // ボタンを押したときのイベントハンドラ
        @IBAction func bt_cloud_funtion(_ sender: Any) {
            functions.httpsCallable("helloWorld").call() { (result, error) in
                ...
            }
            ...
    }
    ```


## ■ 参考サイト
- https://firebase.google.com/docs/functions/callable
- xxx