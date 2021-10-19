# 【React】関数コンポーネントを使用する（CDN 版での構成）

React における関数コンポーネントとは、React スクリプト内で `function コンポーネント名(引数) {...}` の形式で定義した処理を、`<コンポーネント名 />` の形式で組み込むことで再利用可能にしたものである

## ■ 方法

1. HTML ファイルを作成する
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

        // function コンポーネント名(引数) の形式でコンポーネントの定義。コンポーネント名の先頭は大文字である必要がある
        // return 値は JSX の形式で記述
        function HelloReactComponent(props) {
            return <p>Hello React Component! name={props.name}, id={props.id}</p>;
        }

        // JSX を用いた 仮想 DOM のエレメント定義
        // <コンポーネント名 /> の形式でコンポーネントを呼び出し
        let element = (
          <div>
            <h1><HelloReactComponent name="Yagami" id="0" /></h1>
            <h2><HelloReactComponent name="Yagoo" id="1" /></h2>
          </div>
        );

        // ReactDOM.render(エレメント, DOM) : 仮想DOMにレンダリング
        ReactDOM.render(element, dom);
      </script>
    </body>
    </html>
    ```

    ポイントは、以下の通り

    - `function コンポーネント名(引数){...}` の形式でコンポーネントの定義する。ここで、コンポーネント名の先頭は大文字である必要があることに注意。また return 値は JSX の形式で記述する。
    
    - コンポーネントは１つの引数 `props` のみを取り、 この引数 `props` に、コンポーネントの呼び出し側で `<コンポーネント名 属性１ 属性２ ... />` の形式で呼び出されたコンポーネントの属性が設定される。各属性名には、`props.属性名` の形式でアクセスできる

    - JSX を用いた 仮想 DOM のエレメント定義の箇所にて、`<コンポーネント名 属性１ 属性２ ... />` の形式でコンポーネントを呼び出している。引数（＝コンポーネントの属性）を設定しない場合は、`<コンポーネント名 />` でコンポーネントを呼び出す

1. 静的な Web ファイル `index.html` をブラウザで開き動作確認する
	```sh
	$ open index.html
	```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137622084-4232d221-c4a3-4e13-a177-3116c4efa99c.png" width="500"><br>
