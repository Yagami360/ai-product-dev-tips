# 【Vue.js】v-bind 属性を使用して HTML タグの属性に値を設定する

HTML 要素を Vue.js スクリプト側から利用するには、`{{}}` を用いた方法が最も一般的であるが、他にも v 属性（HTML ファイル内で `v-v属性名=値` の形式で利用）を使用して、様々な形式の HTML 要素を Vue.js スクリプト側から利用することもできる。

ここでは、v-bind 属性（`v-bind:属性名="設定する値"` の構文）を使用して HTML タグの属性に値を設定する方法を記載する

## ■ 方法

### ◎ v-bind 属性を使用して HTML の style 属性の値を設定する

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
			<!-- v-bind:属性名="設定する値" の形式で利用 -->
			<!-- ここでは、HTML の style 属性（<body style=""></body> のようにタグ内で使用される）に値 "style" を適用している-->
			<p v-bind:style="style">{{ message }}</p>
		</div>
		
		<script>
		const appdata = {
			data() {
				return {
					message : null,
					style:'font-size:32pt; color:red;'	// この値が <p v-bind:style="style"> で定義した　style 属性の値 "style" に置き換えられる
				}
			},
			
			// Vue.createApp(appdata).mount('#app') で、Vue3 オブジェクトが Web ページに組み込まれたときに呼び出されるコールバック関数
			mounted() {
				this.message = 'This is sample page.'
			},
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
	$ open index1.html
	```

### ◎ v-bind 属性を使用して HTML の class 属性の値を設定する

1. Vue.js を用いた静的な Web ファイル `index2.html` を作成する
	```html
	<!DOCTYPE html>
	<html>
	<head>
		<title>My first Vue app</title>
		<script src="https://unpkg.com/vue@next"></script>
	</head>

	<body>
		<style>
		.red {
				font-size:32pt;
				font-weight:plain;
				font-style:normal;
				color:red;
		}
		.blue {
				font-size:24pt;
				font-weight:bold;
				font-style: italic;
				color:blue;
		}
		</style>
		<h1 class="bg-secondary text-white display-4 px-3">Vue3</h1>
		<div id="app" class="container">
			<!-- v-bind:属性名="設定する値" の形式で利用 -->
			<!-- ここでは、HTML の class 属性に値 "class_var" を適用している-->
			<!-- class 属性の値として "class" は使えないことに注意 -->
			<p v-bind:class="class_var">
				{{ message }}
			</p>
		</div>
		
		<script>
		const appdata = {
			data() {
				return {
					message : 'This is sample page.',
					class_var : {   // この値 class_var が <p v-bind:class="class_var"> で定義した　class 属性の値 "class_var" に置き換えられる
						red: true,    // <style> タグ内の .red に対応。値を true, flase で設定することで、対象 style の ON/OFF ができる
						blue: false   // <style> タグ内の .blue に対応。値を true, flase で設定することで、対象 style の ON/OFF ができる
					},
				}
			},

			// Vue.createApp(appdata).mount('#app') で、Vue3 オブジェクトが Web ページに組み込まれたときに呼び出されるコールバック関数
			mounted() {
				this.class_var.red = false
				this.class_var.blue = true
			},
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
	$ open index2.html
	```

