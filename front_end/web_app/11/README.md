# 【Vue.js】Vue.js スクリプトの基本的な書き方

## ■ 最もシンプルな構成

1. Vue.js を用いた静的な Web ファイル `index1.html` を作成する
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
		{{ message }}
		</div>
		
		<script>
		const appdata = {
			data() {
				return {
					message: 'Hello Vue!'
				}
			}
		}
		
		Vue.createApp(appdata).mount('#app')
		</script>
	</body>

	</html>
	```

	ポイントは、以下の通り

	- CDN 版（スタンドアロン版）の Vue.js は、`<script src="https://unpkg.com/vue@next"></script>` タグを HTML ファイル内に埋め込むだけで使用できる。

	- `<script></script>` タグで定義している Vue.js スクリプトの挙動<br>
		スクリプト内では初めに `appdata` という定数を定義している。Vue.js では、`const appdata{...}` 内部で定義した値をそのまま return する`data()` メソッドを定義する形式で記述するが、これは以下の一般的な Javascript での書き方と同じ意味になる
		```javascript
		const appdata = {
			message: 'Hello Vue!',
		}
		```

		その後、`Vue.createApp(appdata).mount('#app')` の部分で `appdata` で定義した定数を Vue.js オブジェクト `Vue` にあるメソッド `createApp()` を使って、アプリケーションオブジェクトを生成し、`mount()` メソッドで HTML 中の `<div id="app"></div>` で指定した id に組み込んでいる。

		このとき `<div id="app"></div>` 内で定義していた `{{ message }}` が `appdata` 内で定義した値　`message` の値 `'Hello Vue!'`　に置き換えられる動作になる。

1. 作成した静的な Web ファイルをブラウザで開く
	```sh
	$ open index1.html
	```

## ■ `created()`メソッド, `mounted()` メソッド、`this.` での変数アクセス

1. Vue.js を用いた静的な Web ファイル `index2.html` を作成する
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
		{{ message }}
		</div>
		
		<script>
		const appdata = {
			// data() には、Web ページで表示するためのデータのみ定義する（ここでの例では `timer_count` は対象外）
			data() {
				return {
					message: 'init\n',
				}
			},

			// Vue.createApp() で、アプリケーションオブジェクトが作成された時点で呼び出されるコールバック関数
			// Web ページで表示するためのデータ以外（内部的な変数）はここで定義するのが一般的（ここでの例では `timer_count`）
			created() {
				this.timer_count = 0
				this.message += "call created()" + " timer_count : " + this.timer_count + "\n"
			},

			// Vue.createApp(appdata).mount('#app') で、Vue3 オブジェクトが Web ページに組み込まれたときに呼び出されるコールバック関数
			mounted() {
				this.timer_count += 1
				this.message += "call mounted()" + " timer_count : " + this.timer_count + "\n"
			},
		}
		
		Vue.createApp(appdata).mount('#app')
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

