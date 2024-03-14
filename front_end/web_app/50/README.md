# Netlify を使用して簡単なウェブサイトをホスティングする（CLI で行う場合）

## 使用方法

1. Netlify アカウント作成を行う<br>
    「[Netlify の Web ページ](https://www.netlify.com/)」からアカウント作成を行う。

1. Netlify CLI をインストールする<br>
    ```sh
    yarn add --dev netlify-cli 
    ```
    > npm でインストール（`npm install -g netlify-cli`）することもできるが、本ページでは yarn でインストールした場合の手順を記載する

1. yarn 経由での netlify コマンドを実行できるようにする<br>
    `package.json` に以下の項目を追加し、yarn 経由での netlify コマンドを実行できるようにする
    ```json
    "scripts": {
        "netlify": "netlify"
    }
    ```

1. Netlify にログインする<br>
    ```sh
    yarn netlify login
    ```

    上記コマンド実行後、認証を求められるので「Authrize」ボタンをクリックする<br>
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/12eeb145-11fa-4872-bc5c-f0860c641552">

    ログインしているユーザーを確認したい場合は、以下のコマンドを実行する
    ```sh
    yarn netlify status
    ```

    上記 CLI コマンドでログインしない場合は、[Netlify コンソール UI のユーザー設定](https://app.netlify.com/user/settings)から認証キーを取得し、`Personal access tokens` を生成し、その値を Netlify CLI コマンド実行時の `--auth` 引数に指定すればよい。
    <img width="500" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/fcb4fa28-4364-438f-b271-0c9ab448f6bc"><br>

1. Netlify CLI を使用してウェブアプリのサイト（ホスティング）を作成する<br>
    ```sh
    yarn netlify sites:create
    ```
    
    上記コマンド実行後、以下のようなコンソールが表示されるので、`Site name` を入力する。入力完了後に生成されたサイトID `Site ID` をコピーしておく
    ```sh
    yusukesakai@YusukenoMacBook-Pro 50 % yarn netlify sites:create
    yarn run v1.22.21
    warning package.json: No license field
    $ netlify sites:create
    ? Team: Yagami360’s team
    ? Site name (leave blank for a random name; you can change it later): netlify-app-exercise-cli-v1

    Site Created

    Admin URL: https://app.netlify.com/sites/netlify-app-exercise-cli-v1
    URL:       https://netlify-app-exercise-cli-v1.netlify.app
    Site ID:   xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxx


    Adding local .netlify folder to .gitignore file...
    Linked to netlify-app-exercise-cli-v1
    ✨  Done in 26.25s.
    ```

1. Web アプリのコードを作成する<br>
    今回は 簡単のため `netlify-app-exercise-cli-v1` ディレクトリ以下に、以下のような HTML ファイル `index.html` を直接作成する
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>netlify-app-exercise-cli-v2</title>
    </head>
    <body>
        <p>Hello World</p>
    </body>
    </html>
    ```

1. Netlify CLI を使用してデプロイ（ホスティング）する<br>
    ```sh
    yarn netlify deploy --dir=${DEPLOY_FLODER} --prod --auth ${NETLIFY_AUTH_TOKEN} --site ${NETLIFY_SITE_ID}
    ```
    - `--dir`: デプロイするウェブアプリのコードのあるディレクトリを指定。今回の例では、`netlify-app-exercise-cli-v1` を設定する
    - `--prod`: 本番環境にデプロイ。これを記載しないと、下書きサイトとして別のURLで公開される。
    - `--auth`: デプロイに利用する認証トークン（Netlify で管理している）。今回はログイン済みなので不要
    - `--site`: サイトID（Netlify で管理している）

1. デプロイ（ホスティング）されたウェブアプリのサイトを確認する<br>
    ```sh
    yarn netlify open:site
    ```

## 参考サイト

- https://blog.cloud-acct.com/posts/myblog-v2-netlify-create-site
- https://qiita.com/ub0t0/items/7a31369692e03a9428f0