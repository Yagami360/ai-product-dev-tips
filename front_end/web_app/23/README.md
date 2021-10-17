# 【React】JSX で HTML 属性に変数値を設定する

JSX では `{}` の形式で変数値を埋め込むことができる。これを利用して HTML 属性に変数値を埋め込むこともできる。

ここでは、`<タグ名 style=スタイル名></タグ名>` で定義される style 属性に `{}` で値を設定する

このとき、const で定義したオブジェクトリテラルで style を定義すると便利である

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
      const style_h1 = {            // スタイルはオブジェクトリテラル（{..., ..., ...} の形式）で定義すると便利
        fontSize:"20pt",            // スタイルシートの font-size に対応
        color:"red",                // 
        border:"1px solid blue"     //
      }
      const style_h2 = {
        fontSize:"16pt",
        color:"blue",
        border:"1px solid blue"
      }

      let message_h1 = "Hello React!"
      let message_h2 = "react sample app"
      let message_li1 = "list1"
      let message_li2 = "list2"

      let element = (
        <div>
          <h1 style={style_h1}>{message_h1}</h1>
          <h2 style={style_h2}>{message_h2}</h2>
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

  - オブジェクトのリテラルの形式（`{xxx, yyy, zzz}` の形式）で style を定義し、それを `<タグ名 style=スタイル名></タグ名>` で定義される style 属性に `{}` で値を設定している。

  - `fontSize` は、スタイルシートの `font-size` に対応している。このように、スタイルシートでの定義名におけるハイフンをハイフンの後の文字の大文字に変えたものが定義可能な名前となる。
   
1. 静的な Web ファイル `index.html` をブラウザで開き、動作確認する
	```sh
	$ open index.html
	```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137619625-b743d29c-a7ec-40da-b974-689b4ab2be88.png" width="500"><br>

