# 【React】Next.js で Redux を使用して値の状態管理を行う

React で Redux を使用する場合は、以下のような形式で App コンポーネントを `<Provider></Provider>` で囲むことにより、各コンポーネントが store の state を管理出来るようにしていた。
```js
ReactDOM.render(
	<Provider store={store}>
		<App />
	</Provider>,
	document.getElementById('root')
);
```

一方 Next.js には App コンポーネントは存在しないので、xxx


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

1. 各種 Redux モジュールをインストールする<br>
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm install --save redux
    $ npm install --save react-redux
    $ npm install --save redux-thunk
    ```

    > `react-thunk` は、Redux におけるアクションの非同期実行に関する機能を提供するミドルウェア。尚、ここでいうミドルウェアとは、Redux の処理の途中に入り込んで、実行する処理の内容をカスタマイズするものである。


1. Next.js で Redux を利用するためのスクリプトを作成する<br>
    1. `lib/redux-store.js` に `AppWithRedux` コンポーネントを作成する<br>
			`lib/redux-store.js` に `AppWithRedux` コンポーネントを作成する。このコンポーネントでは、Redux の store を初期化し、それに属性を指定して、App コンポーネントを生成する・
			```js
			import { Component } from 'react';
			import {initStore} from '../store';

			const isServer = typeof window === 'undefined'
			const _NRS_ = '__NEXT_REDUX_STORE__'

			function getOrCreateStore (initialState) {
				if (isServer) {
					return initStore(initialState)
				}
				if (!window[_NRS_]) {
					window[_NRS_] = initStore(initialState)
				}
				return window[_NRS_]
			}

			export default (App) => {
				// AppWithRedux コンポーネントでは、Redux の store を初期化し、それに属性を指定して App コンポーネントを生成する
				return class AppWithRedux extends Component {
					static async getInitialProps (appContext) {
						const reduxStore = getOrCreateStore()
						appContext.ctx.reduxStore = reduxStore
						let appProps = {}
						if (typeof App.getInitialProps === 'function') {
							appProps = await App.getInitialProps(appContext)
						}
						return {
							...appProps,
							initialReduxState: reduxStore.getState()
						}
					}

					constructor (props) {
						super(props)

						// getOrCreateStore() 内部で、initStore() でストアを初期化している
						this.reduxStore = getOrCreateStore(props.initialReduxState)
					}

					render () {
						return <App {...this.props}
							reduxStore={this.reduxStore} />
					}
				}
			}
			```

 		1. `pages/_app.js` に `_App` コンポーネントを作成する<br>
			`pages/_app.js` に `_App` コンポーネントを作成する。このコンポーネントは、Next.js の App コンポーネントを継承し、Next.js でも React のときと同じようにして Redux を使用出来るようにたコンポーネントになっている。
			```js
			import App, {Container} from 'next/app';
			import React from 'react';
			import withReduxStore from '../lib/redux-store';
			import { Provider } from 'react-redux';

			// Next.js の App コンポーネントを形式したコンポーネント
			class _App extends App {
				render () {
					const {Component, pageProps, reduxStore} = this.props
					return (
						<Container>
							<Provider store={reduxStore}>
								<Component {...pageProps} />
							</Provider>
						</Container>
					)
				}
			}

			export default withReduxStore(_App)
			```

	  > この２つのコンポーネントの中身のコードを詳細に把握する必要はない。Next.js で React の時と同じようにして Redux を利用するためのスクリプトであって、Next.js で Redux を使用する場合は、毎回同じコードを作成するようにすればよい

1. `store.js` を作成する<br>
		Redux における ストアやレデューサーの作成を行う `store.js` を作成する

		```js
		import { createStore, applyMiddleware } from 'redux';
		import thunkMiddleware from 'redux-thunk';

		// ステート初期値
		const init_state = {
			key:'value',
		}

		// レデューサー
		function reducer(state = init_state, action) {
			switch (action.type) {
				case 'TYPE1':
					return state;
				case 'TYPE2':
					return state;
				default:
					return state;
			}
		}

		// createStore() で作成した store を返すメソッド。lib/redux-store.js の AppWithRedux コンポーネントで利用しているので外部公開する
		export function initStore(state = init_state) {
			// applyMiddleware() でミドルウェアを追加する。ここでいうミドルウェアとは、React の処理に途中に入り込んで、実行する処理の内容をカスタマイズするものである。
			// redux-thunk の thunkMiddleware ミドルウェアを追加することで、Next.js で Redux がうまく動作するようになる
			return createStore(reducer, state, applyMiddleware(thunkMiddleware))
		}
		```

		ポイントは、以下の通り

		- `initStore()` は、単に `createStore()` で作成した store を返すメソッドであるが、このメソッドを `lib/redux-store.js` の `AppWithRedux` コンポーネントで利用するので、外部公開している。

		- `createStore()` の引数に、`applyMiddleware()` でミドルウェアを追加している。ここでいうミドルウェアとは、React の処理に途中に入り込んで、実行する処理の内容をカスタマイズするものであるが、redux-thunk の `thunkMiddleware` ミドルウェアを追加することで、Next.js で Redux がうまく動作するようになる


1. 各種コンポーネントを作成する<br>

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
