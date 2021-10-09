# 【Vue.js】v-html 属性を使用して `{{}}` を HTML の要素（タグ）として認識させる

HTML 要素を Vue.js スクリプト側から利用するには、`{{}}` を用いた方法が最も一般的であるが、他にも v 属性（HTML ファイル内で `v-v属性名=値` の形式で利用）を使用して、様々な形式の HTML 要素を Vue.js スクリプト側から利用することもできる。ここでは、v 属性の一種である v-html 属性を使用して `{{}}` を HTML の要素（タグ）として認識させる。

## ■ 方法

HTML ファイル内で Vue.js のスクリプト出力を `{{xxx}}` で埋め込んだ場合、HTML ファイル側がテキストデータとして認識する。そのため、Vue.js のスクリプト出力に HTML タグを含めた場合でも、それらのタグはテキストデータとして認識され、タグの文字列が表示されるだけになる。

Vue.js のスクリプト出力に対して HTML 側でタグ情報を認識させるには、 v-html 属性のタグ `<div v-html="変数名"></div>` を使用すればよい

1. Vue.js を用いた静的な Web ファイル `index.html` を作成する
	```html
	<!DOCTYPE html>
	<html>
	<head>
		<title>My first Vue app</title>
		<script src="https://unpkg.com/vue@next"></script>
	</head>

	<body>
		<h1>Vue3</h1>
		<div id="app">
			<!-- v-html 属性のタグ `<div v-html="変数名"></div>` を使用することで HTML 側はタグを認識-->
			<div v-html="message"></div>
		</div>
		
		<script>
		const list = ['One', 'Two', 'Three']
		const appdata = {
			data() {
				return {
					// `xxx` : テンプレートリテラル。テキストを改行して記述できる（※javascriptの構文）。このケースでは <li></li> と <li></li> の間に <br> を挟まなくとも、各リストが改行されて表示される
					// <ul> タグ : unordered list（順序がないリスト）
					// <li> タグ : list の各項目
					// ${変数名} : プレースホルダー。テンプレートリテラルの中 `xxx` で定義でき、定義済みの変数の値を埋め込んむことができる（※javascriptの構文）
					message: `<ul>
					<li>${list[0]}</li>
					<li>${list[1]}</li>
					<li>${list[2]}</li>
					</ul>`
				}
			}
		}
		
		let app = Vue.createApp(appdata)
		app.mount('#app')
		</script>
	</body>

	</html>
	```

	ポイントは、以下の通り

	- xxx

1. 作成した静的な Web ファイルをブラウザで開く
	```sh
	$ open index.html
	```
