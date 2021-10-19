# 【React】JSX に変数値を埋め込む（CDN 版での構成）

JSX では `{}` の形式で変数値を埋め込むことができる

## ■ 方法

1. HTML ファイル ``index.html` を作成する

	```html
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="UTF-8" />
		<title>React</title>
		<!-- CDN 版（スタンドアロン版）の React を使用 -->
		<script src="https://unpkg.com/react@16/umd/react.development.js"></script>
		<script src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"></script>
		<!-- JSX の機能を利用するための Babel ライブラリを読み込む  -->
		<script src="https://unpkg.com/babel-standalone@6.26.0/babel.js"></script>
	</head>
	<body>
		<div id="root">wait...</div>
		<!-- React のスクリプト -->
		<script type="text/babel">
		// DOM におけるタグのエレメント取得
		let dom = document.querySelector('#root');
		// JSX を用いた 仮想 DOM のエレメント定義
		let message_h1 = "Hello React!"
		let message_h2 = "react sample app"
		let message_li1 = "list1"
		let message_li2 = "list2"
		let element = (
			<div>
			<h1>{message_h1}</h1>
			<h2>{message_h2}</h2>
			<ul>
				<li>{message_li1}</li>
				<li>{message_li2}</li>
			</ul>
			</div>
		);
		// ReactDOM.render(エレメント, DOM) : 仮想DOMにレンダリング
		ReactDOM.render(element, dom);
		</script>
	</body>
	</html>
	```

	ポイントは、以下の通り

	- `element` 変数に `{}` の形式で変数の値を埋め込んでいる

2. 静的な Web ファイル `index.html` をブラウザで開き、動作確認する

	```sh
	$ open index.html
	```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137618707-c9b15e9b-1eed-4b18-9b6c-3b1c43a6e75f.png" width="500"><br>
