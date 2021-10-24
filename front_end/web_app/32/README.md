# 【React】Next.js を使用してサーバーサイドレンダリング（SSR）する

- ToDo
  - サーバーサイドレンダリングとクライアントサイドレンダリングの比較についての記載追加
  - `index.js` 以外のページを表示するようなサンプルアプリに変更（React の SPA[Single Page Application] との比較）
  - React のコンポーネントを使用したサンプルアプリに変更

## ■ 方法

1. npm をインストール
    - MacOS の場合
        ```sh
        # Node.jsをインストール
        $ brew install node
        ```
    > npm : Node.js のパッケージを管理するコマンド

1. Next.js プロジェクトのディレクトリを作成する<br>
    ```sh
    $ mkdir -p ${PROJECT_NAME}
    ```

1. `package.json` を作成する<br>
  Next.js プロジェクトのディレクトリ以下に、以下のような `package.json` を作成する

    ```json
    {
      "scripts": {
        "dev": "next",
        "build": "next build",
        "start": "next start",
        "export": "next export"
      }
    }
    ```

1. next.js, react, react-dom をインストールする
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm install --save next
    $ npm install --save react
    $ npm install --save react-dom
    ```


1. `pages/index.js` を作成する
    ```sh
    $ mkdir -p ${PROJECT_NAME}/pages
    $ touch ${PROJECT_NAME}/pages/"index.js"
    ```

    ```js
    // アロー関数 ()=>{...} の return に JSX 形式で表示させる内容を記述し、export default で外部公開
    export default () =>{
      return (
        <div>
          {/* ビルドインcss*/ }
          <style jsx>{`
          h1 {
            font-size:68pt;
            font-weight:bold;
            text-align:left;
            letter-spacing:-8px;
            color:#f0f0f0;
            margin:-32px 0px;
          }
          p {
              margin:0px;
              color:#666;
              font-size:16pt;
          }
          `}</style>

          <h1>Next.js</h1>
          <div>Welcome to next.js!</div>
        </div>
      );
    }
    ```

    ポイントは、以下の通り

    - Next.js でのサーバーサイドレンダリングでアプリ開発をする場合は、全て Jacascript ファイルで開発を行い HTML ファイルは使わない（※Javascript ファイル内部で JSX 形式で HTML タグの出力は行う）。そのため、プログラムの起点となる `index.html` も存在しない。プログラムの起点は、この `index.js` になる。

    - 各種ソースファイルは、`pages` ディレクトリ以下に保存するようにする。

    - アロー関数（無名関数） `()=>{...}` の return に JSX 形式で表示させる内容を記述し、export default で外部公開している

    - Next.js では css ファイルは使えない。JSX 内でスタイル定義したい場合は、ビルドイン css でスタイルを定義するのが一般的である。ビルドイン css は、JSX 記述の内で、`<style jsx>` タグで定義できる。


1. 【オプション】プロジェクトをビルドする
  1. Next.js の設定ファイル `next.config.js` を作成する<br>
      アプリの公開時に、外部公開される静的な HTML ファイルを生成するために、 Next.js の設定ファイル `next.config.js` を作成する
      ```js
      module.exports = {
        exportPathMap: function () {
          return {
            '/': { page: '/' }
          }
        }
      }
      ```
    1. プロジェクトをビルドする
        ```sh
        $ npm run build
        ```

    1. プロジェクトをエクスポートする
        ```sh
        $ npm run export
        ```

        > ビルドしてエクスポートされたプロジェクトは `${PROJECT_NAME}/out` ディレクトリに作成される。この out ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

    1. 【オプション】出力された静的な Web ファイル　`out/index.html` を確認する
        ```html
        ```

        > 出力された静的な Web ファイル　`index.html` では、`index.js` の JSX の内容で書き換わっていることに注目。
        
        > サーバーから送られる静的な Web ファイル　`index.html` に表示内容が生成されてウェブブラウザに送られた後に、ウェブブラウザで表示内容をレンダリングする形式になっているので、サーバーサイドレンダリングできるようになっている

1. 作成した React のプロジェクトのサーバーを起動する
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm run dev
    ```

    コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く
