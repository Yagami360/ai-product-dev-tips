# 【React】JSX を用いて階層構造のタグを表示する

```html
<body>
  <div id="root">
    <h1>Hello React!</h1>
    <h2>react sample app</h2>
    <ul>
      <li>list1</li>
      <li>list2</li>
    </ul>
  </div>
</body>
```

のような階層構造を持つタグ `<div id="root">` のエレメントを生成しようとすると、以下のように、`React.createElement(HTMLタグ名, 属性, タグの中身)` における第３引数に、更に `React.createElement()` を呼び出す形式になり、非常に扱いにくくなる問題がある。

```js
let dom = document.querySelector('#root');
let element = React.createElement(
    'div', {}, [
        React.createElement(
            'h1', {}, "Hello React!"
        ),
        React.createElement(
            'h2', {}, "react sample app"
        ),
        React.createElement(
            'ul', {}, [
                React.createElement(
                    'li', {}, "list1"
                ),
                React.createElement(
                    'li', {}, "lsit2"
                ),
            ]
        ),
    ]
);
```

JSX を用いれば、このような階層構造を持つタグも HTML ライクに記述することができる。ただし、JSX を用いた React スクリプトは、HTML ファイル内に組み込む必要があることに注意

## ■ 方法

1. HTML ファイル `index2.html` を作成する

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
        let element = (
          <div>
            <h1>Hello React!</h1>
            <h2>react sample app</h2>
            <ul>
              <li>list1</li>
              <li>list2</li>
            </ul>
          </div>
        );
        // ReactDOM.render(エレメント, DOM) : 仮想DOMにレンダリング
        ReactDOM.render(element, dom);
      </script>
    </body>
    </html>
    ```

    ポイントは、以下の通り。React では元々の HTML タグの値を置き換えることで、表示を行っている点がポイント

    - `<script src="https://unpkg.com/babel-standalone@6.26.0/babel.js"></script>` で JSX の機能を利用するための Babel ライブラリを読み込んでいる

    - `<script></script>` タグではなく、`<script type="text/babel"></script>` タグで React スクリプトを定義している。これにより、タグ内に定義した React スクリプトが、Bable のコンパイラによってコンパイルされ、JSX で記述されたスクリプトが動作するようになる。（このタグで定義しないと文法エラーがでる）

    - `element` 変数に HTML におけるタグ定義と同じ形式で階層構造のタグを定義し、それを `React.createElement()` のときと同じように、`ReactDOM.render()` に渡すことで階層構造のタグをレンダリングできる

2. 静的な Web ファイル `index2.html` をブラウザで開き動作確認する
	```sh
	$ open index2.html
	```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137618707-c9b15e9b-1eed-4b18-9b6c-3b1c43a6e75f.png" width="500"><br>


