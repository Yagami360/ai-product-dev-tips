# 【React】CDN 版（スタンドアロン版）の React を使用する

CDN 版（スタンドアロン版）の React を使用したい場合は、HTML ファイルに `<script src="https://unpkg.com/react@16/umd/react.development.js"></script>` タグを埋め込むだけで使用できる
ただし、CDN 版の React は、予め CDN 版に織り込まれているモジュールしか使えない（例えば、npmにあるモジュールは使えない）ので、大規模なアプリケーション開発には向いていない。

この場合は、Creat React App を用いて React プロジェクトを作成して React を使用する形になる。詳細は、「[【React】Creat React App を用いて React アプリをデプロイする](https://github.com/Yagami360/MachineLearning_Tips/tree/master/front_end/web_app/20)」を参照

## ■ 方法

1. HTML ファイルを作成する<br>

	```html
	<!DOCTYPE html>
	<html>
	<head>
		<meta charset="UTF-8" />
		<title>React</title>
		<!-- CDN 版（スタンドアロン版）の React を使用 -->
		<script src="https://unpkg.com/react@16/umd/react.development.js"></script>
		<script src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"></script>
	</head>
	<body>
		<h1>React</h1>
		<div id="root">wait...</div>
		<!-- React のスクリプト -->
		<script>
			// DOM におけるタグのエレメント取得
			let dom = document.querySelector('#root');
			// React.createElement(HTMLタグ名, 属性, タグの中身) : 仮想DOMのエレメントを生成
			let element = React.createElement(
				'p',            // <p> タグ
				{},             // 特に必要ない場合は、{} を指定する
				'Hello React!'  // <p> タグの中身
			);    
			// ReactDOM.render(エレメント, DOM) : 仮想DOMにレンダリング
			ReactDOM.render(element, dom);
		</script>
	</body>
	</html>
	```

	ポイントは、以下の通り。React では元々の HTML タグの値を置き換えることで、表示を行っている点がポイント
		
	- `<script src="https://unpkg.com/react@16/umd/react.development.js"></script>` で、CDN という Web サイトから React ライブラリを読み込んでいる。同じく `<script src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"></script>` で、CDN という Web サイトから React-DOM ライブラリを読み込んでいる

	- `document.querySelector()` で、DOM におけるタグ `<div id="root">wait...</div>` のエレメントを取得している（※ このメソッドは、React のメソッドではなく JavaScript のメソッド）。

	- `React.createElement(HTMLタグ名, 属性, タグの中身)` で、仮想DOMにおけるエレメント（＝タグのオブジェクト）`<p>'Hello React!'</p>` を生成している（※ DOMのエレメントではなく仮想DOMのエレメントになっている）

	- `ReactDOM.render(エレメント, DOM)` で、React-DOM ライブラリの `ReactDOM` オブジェクトを用いて、仮想DOMにレンダリングしている。これにより、`document.querySelector()`　で取得した HTML 要素 `<div id="root">wait...</div>` の部分が `<div id="root"><p>'Hello React!'</p></div>` に置き換わる。<br>
	
	その後、仮想DOMのレンダリングがDOMのレンダリングに反映され、HTML 上の表示に反映される

	> エレメント : HTML タグを操作するためのオブジェクト（JavaScript における用語）

	> ノード : 各 HTML 要素のオブジェクト。エレメントのノードの１つになる

1. 静的な Web ファイル `index.html` をブラウザで開き動作確認する
	```sh
	$ open index.html
	```

	ブラウザ上に以下のような表示が行われる<br>
	<img src="https://user-images.githubusercontent.com/25688193/137611994-6c3a823c-3572-47e1-a69e-1037f0d8f008.png" width="500"><br>


1. 【オプション】React Developer Tools をインストール<br>
  [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi/related?hl=ja)
