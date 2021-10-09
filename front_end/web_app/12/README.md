# 【Vue.js】Vue.js スクリプトにおけるコンポーネントの基本的な書き方

Vue.js におけるコンポーネントとは、Vue.js スクリプト内で `Vue.createApp(appdata).component(コンポーネント名、{設定情報})` の形式で定義した処理を HTML ファイル内にて `<コンポーネント名/>` の形式で組み込むことで再利用可能にしたものである

## ■ コンポーネントを使用する

1. Vue.js を用いた静的な Web ファイル `index1.html` を作成する
	```html
	<!DOCTYPE html>
	<html>
	<head>
		<title>My first Vue app</title>
		<script src="https://unpkg.com/vue@next"></script>
	</head>

	<body>
		<h1 class="bg-secondary text-white display-4 px-3">Vue3</h1>
		<div id="app" class="container">
			<p>{{ message }}</p>
			<!--<コンポーネント名/> でコンポーネントを使用-->
			<hello/>
		</div>
		
		<script>
		const appdata = {
			data() {
				return {
					message : 'コンポーネントを表示する'
				}
			}
		}
		
		// アプリケーションオブジェクトの変数定義
		let app = Vue.createApp(appdata)
		
		// コンポーネントの作成 : app.component(コンポーネント名、{設定情報})
		// {設定情報} の `template:` 項目に設定した内容がコンポーネントとして表示される
		app.component('hello', {
			template: '<p class="alert alert-primary">Hello!</p>'		// HTML の <p></p> タグで文字列 "Hello!" を表示
		})
		app.mount('#app')
		</script>
	</body>

	</html>
	```

	ポイントは、以下の通り

	- xxx

1. 作成した静的な Web ファイルをブラウザで開く
	```sh
	$ open index1.html
	```

## ■ 変数をコンポーネントに渡す

1. Vue.js を用いた静的な Web ファイル `index2.html` を作成する
	```html
	```
    
	ポイントは、以下の通り

	- xxx

1. 作成した静的な Web ファイルをブラウザで開く
	```sh
	$ open index2.html
	```

## ■ HTML でのタグ属性とコンポーネント

1. Vue.js を用いた静的な Web ファイル `index3.html` を作成する
	```html
	```
    
	ポイントは、以下の通り

	- xxx

1. 作成した静的な Web ファイルをブラウザで開く
	```sh
	$ open index3.html
	```

