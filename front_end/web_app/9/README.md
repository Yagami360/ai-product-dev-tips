# 【Vue.js】CDN 版（スタンドアロン版）の Vue.js を使用する

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

- ブラウザに Vue.js devtool のアドオンをインストール