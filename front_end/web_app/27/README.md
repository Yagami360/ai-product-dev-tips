# 【React】クラスコンポーネントでイベントを割り当てる（CDN 版での構成）

JavaScript のイベント処理（`onClick` など）を React で行いたい場合は、クラスコンポーネントで定義したイベント処理メソッドをJavaScript のイベント処理（`onClick` など）にバインド（割り当て）すればよい。

<!--
この割り当て処理を行うには、以下の２つの処理が必要になる。

1. 例えば、`<button>` タグの `onClick` 属性に割り当てる場合は、クラスコンポーネントの `render()` メソッド内の retrun 値を `<button onClick={this.イベントメソッド名}></button>` の形式で記述し、JavaScript のイベント処理（`onClick` など）とクラスコンポーネントで定義したイベント処理メソッドを紐付ける。
1. `this.イベントメソッド名 = this.イベントメソッド名.bind(this);` の形式で、クラスコンポーネントで定義したイベント処理メソッドをイベントとしてバインド（割り当て）する
-->

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
          // コンストラクタ
          constructor(props){
            super(props); // React.Component クラスのコンストラクタ呼び出し

            // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
            this.state = {
              name: props.name,
              id: props.id,
            };

            // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
            this.incrementId = this.incrementId.bind(this);
          }

          // イベント処理のメソッド
          incrementId(e){
            // `state` の値の更新は、`this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。
            this.setState(
              (state)=>({
                id: parseInt(state.id) + 1,
              })
            );
          };

          // render() メソッドは、必ず定義する必要がある
          render(){
            // `state` の各要素変数へのアクセスは、`this.state.要素変数名` の形式で行う
            // <button> タグの onClick 属性に、このクラスコンポーネントで定義したイベント処理のメソッドを設定し、両者を紐付ける
            return <div>
              <p>Hello React Component! name={this.state.name}, id={this.state.id}</p>
              <button onClick={this.incrementId}>increment id</button>
            </div>;
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
        // Web ページ読み込み時に一度行われるのみ
        ReactDOM.render(element, dom);
      </script>
    </body>
    </html>
    ```

    ポイントは、以下の通り。

    - クラスコンポーネントの `render()` メソッド内の retrun 値に、`<button>` タグの `onClick` 属性に `<button onClick={this.incrementId}>increment id</button>` を追加し、JavaScript のイベント処理 `onClick` とクラスコンポーネントで定義したイベント処理メソッド `incrementId(e)` を紐付けている。

    - `this.incrementId = this.incrementId.bind(this);` の形式で、クラスコンポーネントで定義したイベント処理メソッド `incrementId(e)` をイベントとしてバインド（割り当て）している

    - イベント処理メソッド `incrementId(e)` 内では、`state` の値の更新を `this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行っている。具体的には、`state` の `id` 値の値をインクリメントしているので、ボタンクリックのイベントが発生する度に id 値がインクリメントされて画面上に反映させる動作になる。このとき、`ReactDOM.render(element, dom);` は、Web ページ読み込み時に一度呼ばれているだけだが、`state` で定義した値の変化が都度表示されている動作になっている点に注目。

1. 静的な Web ファイル `index.html` をブラウザで開き動作確認する
    ```sh
    $ open index.html
    ```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137854197-267180ef-1ea8-43cc-9ad0-f8a5967367ec.png" width="300"><br>

    > `ReactDOM.render(element, dom);` は、Web ページ読み込み時に一度呼ばれているだけだが、ボタンクリックする度に、id 値がインクリメントされて画面表示されている点に注目
