# 【Vue.js】CDN 版（スタンドアロン版）の Vue.js を使用する

CDN 版（スタンドアロン版）の Vue.js を使用した場合は、HTML ファイルに `<script src="https://unpkg.com/vue@next"></script>` タグを埋め込むだけで使用できる

ただし、CDN 版の Vue.js は、予め CDN 版に織り込まれているモジュールしか使えない（例えば、npmにあるモジュールは使えない）ので、大規模なアプリケーション開発には向いていない。

この場合は、vue-cli を用いて Vue.js プロジェクトを作成して Vue.js を使用する形になる。詳細は、「[【Vue.js】vue-cli を用いて Vue.js アプリをデプロイする](https://github.com/Yagami360/MachineLearning_Tips/tree/master/front_end/web_app/8)」を参照

## ■ 方法
	
- HTML ファイルを作成する
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
 	
- 静的な Web ファイル `index.html` をブラウザで開き動作確認する
	```sh
	$ open index.html
	```

- ブラウザに Vue.js devtool のアドオンをインストール
	xxx

- Chrome の「デベロッパーツール」で動作確認する
