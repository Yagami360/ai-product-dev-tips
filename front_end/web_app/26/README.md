# 【React】クラスコンポーネントでステートを使用する

クラスコンポーネントのプロパティ（インスタンス変数）の値の変更を画面上に反映させようとすると、都度 `ReactDOM.render(elemnt, dom)` を呼び出さす必要がある。<br>

クラスコンポーネントにおける「state」プロパティの機能を利用すると、都度 `ReactDOM.render(elemnt, dom)` を呼び出さなくとも、画面上の値の変更を反映させることができる。

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

            // setInterval(()=>{処理}, インターバル時間msec) : 一定時間度に {} で定義した処理を行うタイマー
            let timer = setInterval( ()=>{
              // this.setState((state)=>({})) : state の
              this.setState(
                // 現在の state を引数とするアロー関数の形式で新しい新しい値を設定
                (state)=>({
                  name: props.name,
                  id: parseInt(state.id) + 1,
                })
              );
            }, 1000 );
          }

          // render() メソッドは、必ず定義する必要がある
          render(){
            // `state` の各要素変数へのアクセスは、`this.state.要素変数名` の形式で行う
            return <p>Hello React Component! name={this.state.name}, id={this.state.id}</p>;
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

    - プロパティ `state` は、継承元の `React.Component` クラスで定義されているので、継承先クラスのプロパティで定義する必要はない

    - `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う

    - `state` の各要素変数へのアクセスは、`this.state.要素変数名` の形式で行う

    - `state` の値の更新は、`this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。この関数では、現在の state の値を引数とするアロー関数（無名関数） `(state)=>({変数名1:値1, 変数名2:値2, ...})` の形式で新しい state の値 `{変数名1:値1, 変数名2:値2, ...}` を設定しいている。<br>
      ここでの例では、`setInterval(()=>{処理}, インターバル時間msec)` 内にて、`this.setState((state)=>({}))` を用いて `state` の `id` 値の値をインクリメントしているので、1sec 度に id 値がインクリメントされて画面上に反映させる動作になる。このとき、`ReactDOM.render(element, dom);` は、Web ページ読み込み時に一度呼ばれているだけだが、`state` で定義した値の変化が都度表示されている動作になっている点に注目。
    
    - この例での処理にはないが、`state` 値の更新ではなく、新たな `state` の各要素変数の追加を行う場合は、`thi.setState({変数名1:値1, 変数名2:値2, ...})` の形式で行う。

1. 静的な Web ファイル `index.html` をブラウザで開き動作確認する
    ```sh
    $ open index.html
    ```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137848614-b437e6f3-db6e-4229-9894-0099a8c56bc2.png" width="300"><br>
    <img src="https://user-images.githubusercontent.com/25688193/137848631-7dc3528e-d092-4582-97f4-cbb501ab169e.png" width="300"><br>

    > `ReactDOM.render(element, dom);` は、Web ページ読み込み時に一度呼ばれているだけだが、`state` で定義した id 値が 1sec 度にインクリメントされて画面表示されている点に注目
