# 【React】クラスコンポーネントを使用する（CDN 版での構成）

React におけるコンポーネントは、以下の形式で定義することで、オブジェクト指向におけるクラスに対しても定義することができる

```js
// React.Component はコンポーネントの基本機能を定義したクラス。これを継承することでコンポーネントクラスを定義する
class コンポーネント名 extends React.Component {
    ...

    // コンストラクタ
    constructor(props){
      super(props); // React.Component クラスのコンストラクタ呼び出し
    }

    // render() メソッドは、必ず定義する必要がある
    render(){
        return JSX形式;
    }
};
```

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

        // React.Component はコンポーネントの基本機能を定義したクラス。これを継承することでコンポーネントクラスを定義する
        class HelloReactComponent extends React.Component {
          name = "none";
          id = 0;

          // コンストラクタ
          constructor(props){
            super(props); // React.Component クラスのコンストラクタ呼び出し
            this.name = props.name;
            this.id = props.id;        
          }

          // render() メソッドは、必ず定義する必要がある
          render(){
            return <p>Hello React Component! name={this.name}, id={this.id}</p>;
          }
        };

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

1. 静的な Web ファイル `index.html` をブラウザで開き動作確認する
	```sh
	$ open index.html
	```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137622084-4232d221-c4a3-4e13-a177-3116c4efa99c.png" width="500"><br>
