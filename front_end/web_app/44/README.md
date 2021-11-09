# 【React】Next.js アプリでレイアウトを関数コンポーネントで行う

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

1. React 版 bootstrap をインストールする<br>
    本コンポーネントでは、CSS フレームワークである bootstrap を利用するため、React 版 bootstrap をインストールする
    ```sh
    $ npm install react-bootstrap bootstrap
    ```

1. ページ全体のレイアウトを設定して表示するコンポーネント `components/layout.js` を作成する
    ```js
    import 'bootstrap/dist/css/bootstrap.min.css'
    import Head from 'next/head'
    import Header from './Header'
    import Footer from './Footer'

    //-----------------------------------------------
    // ページ全体のレイアウトを設定するコンポーネント
    // [引数]
    //   props.header : ヘッダー文字列
    //   props.title : タイトル文字列
    //   props.children : コンテンツ部分。 このコンポーネント呼び出し元での <Layout>xxx</Layout> の xxx が props.children になる
    //-----------------------------------------------
    export default function Layout(props) {
      // Bootstrap の className
      // <div className="container"> : コンテンツを配置するときに使用。各コンテンツ間が適度な余白で表示されるようになる
      // my-x : 上下のマージン
      return (
        <div>
          <Head>
            <title>{props.title}</title>
          </Head>
          <Header header={props.header} />
          <div className="container">
            <h3 className="my-3 text-primary text-center">{props.title}</h3>
            {props.children}
          </div>
          <Footer footer="footer" />
        </div>
      )
    }
    ```

    ポイントは、以下の通り

    - `import 'bootstrap/dist/css/bootstrap.min.css'` で bootstrap を import することで、各タグの `className` 属性でスタイルを設定できるようにしている。

      > CDN 版 bootstrap を利用する場合は、`<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" crossorigin="anonymous"></link>` を return 分の JSX 内に追加すればよいが、今回は `npm` でインストールした bootstrap を使用するようにしている

    - xxx

1. ヘッダーのレイアウトを設定して表示するコンポーネント `components/header.js` を作成する
    ```js
    import 'bootstrap/dist/css/bootstrap.min.css'

    //-----------------------------------------------
    // ヘッダーのレイアウトを設定して表示するコンポーネント
    // [引数]
    //   props.header : ヘッダーの文字列
    //-----------------------------------------------
    export default function Header(props) {
      // Bootstrap の className
      // bg-色名 : 背景色。色名には red, blue などの色ではなく、primary, secondary などの役割を表す名前が指定できる
      // text-色名 : テキスト色
      // display-x : 通常のヘッダよりもさらに目立たせたいヘッダがあれば、.display-1～.display-4 を用いてさらに大きな見出しに出来る
      // px-x : 左右のパティング
      return (
        <div>
          <h1 className="bg-primary px-3 text-white display-4 text-right">{props.header}</h1>
        </div>
      )
    }
    ```

    ポイントは、以下の通り

    - xxx

1. フッターのレイアウトを設定して表示するコンポーネント `components/footer.js` を作成する
    ```js
    import 'bootstrap/dist/css/bootstrap.min.css'

    //-----------------------------------------------
    // フッターのレイアウトを設定して表示するコンポーネント
    // [引数]
    //   props.header : フッターの文字列
    //-----------------------------------------------
    export default function Footer(props) {
      return (
        <div className="text-center h6 my-4">
          <div>{props.footer}</div>
        </div>
      )
    }
    ```

    ポイントは、以下の通り

    - xxx

1. 画像のレイアウトを設定して表示するコンポーネント `components/image.js` を作成する
    ```js
    import 'bootstrap/dist/css/bootstrap.min.css'

    //-----------------------------------------------
    // 画面のレイアウトを設定して表示するコンポーネント
    // [引数]
    //   props.fileName : ファイル名（画面ファイルはpulicディレクトリ以下に配置する必要あり）
    //   props.width : 画像の幅
    //-----------------------------------------------
    export default function Image(props) {
      let fileName = './' + props.fileName  // public 以下に配置したファイルは、サーバー直下に置かれるので、ファイルパスは ./ファイル名 になる
      let width = props.width + "px"

      return (
        <div className="container my-3">
          <img width={width} border="1" src={fileName} />
        </div>
      )
    }
    ```

    ポイントは、以下の通り

    - `public` ディレクトリ以下に配置された画像ファイルのファイルパスは、`.public/ファイル名` ではなく、サーバー直下の `./ファイル名` になることに注意

1. `pages/index.js` を作成する
    ルートページである `index.js` を作成する

    ```js
    import 'bootstrap/dist/css/bootstrap.min.css'  // Bootstrap（CSSのフレームワーク）を import。className 属性でスタイルを設定できるようになる
    import Button from 'react-bootstrap/Button'
    import Layout from '../components/layout'
    import Image from '../components/image'

    export default function Home() {
      // Bootstrap の className
      // alert alert-色名 : 強調表示。色名には red, blue などの色ではなく、primary, secondary などの役割を表す名前が指定できる
      // mb-x : 下マージン
      return (
        <div>
          <Layout header="header" title="title">
            <div className="alert alert-primary text-center">
              <h5 className="mb-4">
                <p>contents</p>
                <Button variant="outline-primary">button</Button>
                <Image fileName="panda.jpg" width="200" />
              </h5>
            </div>
          </Layout>
        </div>
      )
    }
    ```

    ポイントは、以下の通り

    - xxx

1. 【オプション】プロジェクトをビルドする<br>
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

		> 出力された静的な Web ファイル　`index.html` では、`index.js` の JSX の内容で書き換わっていることに注目。
		
		> サーバーから送られる静的な Web ファイル　`index.html` に表示内容が生成されてウェブブラウザに送られた後に、ウェブブラウザで表示内容をレンダリングする形式になっているので、サーバーサイドレンダリングできるようになっている

1. 作成した React のプロジェクトのサーバーを起動する
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm run dev
    ```

    コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く
