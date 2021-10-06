# 【Vue.js】vue-cli を用いて Vue.js アプリをデプロイする

## ■ 方法

1. npm をインストール
    - MacOS の場合
        ```sh
        # Node.jsをインストール
        $ brew install node
        ```

    > Node.js のパッケージを管理する

1. Vue.js の CLI をインストール
    ```sh
    $ npm install --global vue-cli
    ```

1. Vue.js のプロジェクトを作成し、起動する
    ```sh
    # プロジェクトを作成
    $ vue init webpack ${PROJECT_NAME}

    # 依存関係をインストールして、起動
    $ cd ${PROJECT_NAME}
    $ npm run dev
    ```

1. デプロイしたアプリの Web サイトにアクセスする
    ```sh
    $ open http://localhost:8080
    ```

## ■ 参考サイト
- https://blog.brainpad.co.jp/entry/2018/04/13/160000
