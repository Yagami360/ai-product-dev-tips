# 【Firebase】iOS アプリ（Xcodeプロジェクト）に Firebase を登録する

## ■ 手順

1. iOS アプリの Xcode プロジェクトを作成する<br>
1. iOS アプリの Firebase プロジェクトを作成する<br>
1. iOS アプリ（Xcodeプロジェクト）を Firebase に追加する<br>
    作成した Firebase プロジェクトの「プロジェクト概要」ページの「iOS」ボタンをクリックし、iOS アプリに Firebase を追加する<br>
    <img src="https://user-images.githubusercontent.com/25688193/108582343-fd1f8000-7375-11eb-9ef4-7b3ebd68cd0a.png" width="500"><br>
    1. iOS ハンドル ID には、XCode プロジェクトに設定したハンドルIDを入力すればよい。<br>
        <img src="https://user-images.githubusercontent.com/25688193/108582378-39eb7700-7376-11eb-80c8-7736be8b7e0e.png" width="300"><br>
        <img src="https://user-images.githubusercontent.com/25688193/108582143-a4031c80-7374-11eb-8779-d066c57c076c.png" width="500"><br>
    1. 次に、`GoogleService-info.plits` という設定ファイルをダウンロードし、iOS アプリの Xcode プロジェクトのルートディレクトリに配置する。
        <img src="https://user-images.githubusercontent.com/25688193/108582484-183ebf80-7377-11eb-8a99-67f231dd4da4.png" width="300"><br>

1. アプリに Firebase SDK を追加する<br>
    1. CocoaPod のインストール<br>
        以下のコマンドで CocoaPod をインストールする<br>
        ```sh
        $ sudo gem update --system      # ruby gemを最新にする
        $ sudo gem install cocoapods    # CocoaPod のインストール
        ```
        上記コマンドでうまく行かない場合は、以下のコマンドで CocoaPod をインストールする<br>
        ```sh
        $ sudo gem update --system
        $ xcode-select --install
        $ sudo gem install compass -n /usr/local/bin
        $ sudo gem install cocoapods -n /usr/local/bin
        ```
    1. Xcode プロジェクトに Pod ファイルを作成<br>
        Xcode プロジェクトに移動して、以下のコマンドで Pod ファイルを作成する
        ```sh
        $ cd ${XCODE_PROJ_DIR}
        $ pod init
        ```
    1. Pod ファイル `Podfile` を修正する。<br>
        ```pod
        # Uncomment the next line to define a global platform for your project
        # platform :ios, '9.0'
        target 'sample-ios-app-project' do
          # Comment the next line if you don't want to use dynamic frameworks
          use_frameworks!

          # Pods for sample-ios-app-project
          pod 'Firebase/Core'       # Firebase のコア部分のライブラリ

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
        $ pod install
        ```

    > - CocoaPod<br>
    > iOS アプリ開発におけるライブラリ管理ツール。<br>
    > 外部ライブラリを Pod という単位でまとめており、この Pod をコマンドでインストールすることで、外部ライブラリを Xcode プロジェクトから使えるようになる


1. 初期化コードを追加する<br>
    iOS アプリのコード（Swift）で、Firebase ライブラリを追加するためのコードの説明が表示される。実際のコード修正はあとのステップで行うので、そのまま「次へ」ボタンをクリックすればよい。<br>
    <img src="https://user-images.githubusercontent.com/25688193/108583344-29d69600-737c-11eb-9a4c-86ca81f78c87.png" width="300"><br>

1. 開いている Xcode プロジェクト `*.xcodeproj` を閉じて、`pod install` コマンド実行後に作成されたプロジェクトファイル `*.xcworkspace` を開く。

1. `AppDelegate.swift` を以下のようなコードに修正し、iOS アプリから Firebase を読むこむ。<br>
    ```swift
    import UIKit
    import Firebase // @ Firebase での追加箇所

    @main
    class AppDelegate: UIResponder, UIApplicationDelegate {
        func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
            // Override point for customization after application launch.
            FirebaseApp.configure()  // @ Firebase での追加箇所
            return true
        }

        // MARK: UISceneSession Lifecycle

        func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
            // Called when a new scene session is being created.
            // Use this method to select a configuration to create the new scene with.
            return UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
        }

        func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
            // Called when the user discards a scene session.
            // If any sessions were discarded while the application was not running, this will be called shortly after application:didFinishLaunchingWithOptions.
            // Use this method to release any resources that were specific to the discarded scenes, as they will not return.
        }
    }
    ```
    > - `AppDelegate.swift` の `AppDelegate` クラスの役割<br>
    > アプリをつくった段階でデフォルトでつくられるファイルのひとつ。アプリ全体のライフタイムイベントを管理するためのクラス。

1. 同様にして、`ViewController.swift` を例えば以下のようなコードに修正し、iOS アプリから Firebase を読むこむ。<br>
    ```swift
    import UIKit
    import Firebase     // @ Firebase での追加箇所

    class ViewController: UIViewController {
        // アウトレット（Swift ソースコード内でのストーリーボード上のオブジェクト（ボタンなど）への参照）
        @IBOutlet weak var firebase_name_label: UILabel!

        // 起動時のイベントハンドラ（インスタンス化された直後の初回に一度のみ）
        override func viewDidLoad() {
            super.viewDidLoad()
            // firebase_name_label に FirebaseApp の名前を設定
            firebase_name_label.text = FirebaseApp.app()?.name  // @ Firebase での追加箇所
        }

    }
    ```

1. Xcode の「▷」ボタンをクリックして、iOS アプリをビルドし iPhone シミュレーターを起動する。<br>
    この際に「再生」ボタンをクリックしても iPhone シミュレーターが起動しない場合は、「Product -> Scheme」を Firebase ではなく Xcode プロジェクト名に切り替えばよい。また、「Product -> Destination」を iPhone に切り替えればよい。

## ■ 参考サイト
- https://firebase.google.com/docs/ios/setup?hl=ja

