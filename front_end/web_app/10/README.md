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

	上記コマンドでプロジェクトを作成すると、以下のようなディレクトリ構造で各種ファイルが出力される。

	```sh
	+ ${PROJECT_NAME} + /public         			# HTML や CSS などの公開ファイル
	|                 +-- index.html    			# 表示される Web サイト。
	|                 + /src            			# .vue などの Vue3 が作成した各種ソースファイル
	|                 +-- main.js       			# プロジェクトを Web アプリケーションとして実行した場合に、最初に実行されるスクリプト。
	|                 +-- App.vue       			# HTML, CSS, Javascropt をまとめた vue ファイル。コンポーネント定義も vue ファイルで行う
	|                 + /components     			# 各種コンポーネントの vue ファイルを保管
	|                 |  +-- HelloWorld.vue  	# App.vue から呼び出されるコンポーネント
	```

	- `index.html`
		```html
		<!DOCTYPE html>
		<html lang="">
			<head>
				<meta charset="utf-8">
				<meta http-equiv="X-UA-Compatible" content="IE=edge">
				<meta name="viewport" content="width=device-width,initial-scale=1.0">
				<link rel="icon" href="<%= BASE_URL %>favicon.ico">
				<title><%= htmlWebpackPlugin.options.title %></title>
			</head>
			<body>
				<noscript>
					<strong>We're sorry but <%= htmlWebpackPlugin.options.title %> doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
				</noscript>
				<div id="app"></div>
				<!-- built files will be auto injected -->
			</body>
		</html>
		```

		> `<div id="app"></div>` で `createApp(App).mount('#app')` の `"app"` を指定している

	- `main.js`
		```js
		import { createApp } from 'vue'
		import App from './App.vue'

		createApp(App).mount('#app')
		```

		> `main.js` 内部では、`App.vue` を呼び出しており、`createApp(App).mount('#app')` で Vue.js アプリケーションオブジェクトを作成している。

	- `App.vue`
		```js
		<template>
			<img alt="Vue logo" src="./assets/logo.png">
			<HelloWorld msg="Welcome to Your Vue.js App"/>
		</template>

		<script>
		import HelloWorld from './components/HelloWorld.vue'

		export default {
			name: 'App',
			components: {
				HelloWorld
			}
		}
		</script>

		<style>
		#app {
			font-family: Avenir, Helvetica, Arial, sans-serif;
			-webkit-font-smoothing: antialiased;
			-moz-osx-font-smoothing: grayscale;
			text-align: center;
			color: #2c3e50;
			margin-top: 60px;
		}
		</style>
		```

		> `components: {HelloWorld}` の部分で、`components/HelloWorld.vue` を呼び出している
	
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

