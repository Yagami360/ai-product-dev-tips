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
    $ npm install -g @vue/cli
    ```

1. Vue.js のプロジェクトを作成する
    ```sh
    # プロジェクトを作成
    $ vue create ${PROJECT_NAME}
    ```

    > 「Default (Vue 3) ([Vue 3] babel, eslint) 」を選択

    > 

    ```sh
    + ${PROJECT_NAME} + /public     # HTML や CSS などの公開ファイル
    |                 + /src        # .vue などの Vue3 が作成した各種ファイル


1. 作成した Vue.js のプロジェクトのサーバーを起動する
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm run serve
    ```

1. デプロイしたアプリの Web サイトにアクセスする
    ```sh
    $ open http://localhost:8080
    ```
    
1. 【オプション】プロジェクトをビルドする
    Vue.js を用いたアプリケーションを公開時には、以下のコマンドでプロジェクトをビルドして公開する
    ```sh
    $ npm run build
    ```

    > ビルドしたプロジェクトは `${PROJECT_NAME}/dist` ディレクトリに作成される。この dist ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

