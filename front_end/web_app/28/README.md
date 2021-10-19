# 【React】クラスコンポーネントでコンテキストを使用する（CDN 版での構成）

コンテキストを用いれば、複数のクラスコンポーネント間で共通に使用する変数を使用できる

コンテキストは、クラスコンポーネントの外側で `const コンテキスト変数名 = React.createContext(値)` の形式で定義し、クラスコンポーネントのプロパティで `static contextType = コンテキスト変数名;` の形式で参照する。そして、クラスコンポーネント内にて、`this.context.コンテキスト変数名の要素変数名` の形式でアクセスできる。

コンテキスト変数の値は直接変更できない。コンテキストの値を変更するには、`<コンテキスト名.Provider value={値}}>` を用いる必要がある。<br>

## ■ 方法

<!--
### ◎ 簡単な例

1. HTML ファイル `index1.html` を作成する
    ```html
    ```

    ポイントは、以下の通り。

    - xxx

1. 静的な Web ファイル `index1.html` をブラウザで開き動作確認する
    ```sh
    $ open index1.html
    ```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="" width="300"><br>
-->

### ◎ コンテキストの活用例（テーマを変更する）

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

        // テーマのスタイル
        let theme = {
          light:{
            backgroundColor:"#eef",
            color:"#006",
            padding:"10px",
          },
          dark:{
            backgroundColor:"#006",
            color:"#eef",
            padding:"10px",
          }
        };

        // コンテキストは、クラスコンポーネントの外側で `const コンテキスト変数名 = React.createContext(値)` の形式で定義する
        const ThemeContext = React.createContext(theme.light);
        //const ThemeContext = React.createContext(theme.dark);

        // アプリ全部のクラスコンポーネント
        class AppComponent extends React.Component {
          // コンテキストをクラスコンポーネントのプロパティで `static contextType = コンテキスト変数名;` の形式で参照
          static contextType = ThemeContext;
          name = "none";
          id = -1;

          // コンストラクタ
          constructor(props){
            super(props); // React.Component クラスのコンストラクタ呼び出し
            this.name = props.name;
            this.id = props.id;

            // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
            this.state = {
              theme_type: props.theme_type,
            };

            // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
            this.doLightTheme = this.doLightTheme.bind(this);
            this.doDarkTheme = this.doDarkTheme.bind(this);
          };

          // イベント処理のメソッド
          doLightTheme(e){
            console.log("change light theme")
            // コンテキストの値を直接変更することはできない
            //this.context = theme.light;
            //this.context.backgroundColor = theme.light.backgroundColor;
            //this.context.color = theme.light.color;
            //this.context.padding = theme.light.padding;
            this.setState(
              (state)=>({theme_type: "light"})
            );
          };
          doDarkTheme(e){
            console.log("change dark theme")
            // コンテキストの値を直接変更することはできない
            //this.context = theme.dark;
            //this.context.backgroundColor = theme.light.backgroundColor;
            //this.context.color = theme.light.color;
            //this.context.padding = theme.light.padding;
            this.setState(
              (state)=>({theme_type: "dark"})
            );
          };

          // render() メソッドは、必ず定義する必要がある
          render(){
            if(this.state.theme_type == "light"){
              return (
                <ThemeContext.Provider value={theme.light}>
                  <div style={theme.light}>
                    <p>Hello React Component!</p>
                    <NameComponent name={this.name} />
                    <IdComponent id={this.id} />
                    <button onClick={this.doLightTheme}>light theme</button>
                    <button onClick={this.doDarkTheme}>dark theme</button>
                  </div>
                </ThemeContext.Provider>
              );
            }
            else{
              return (
                <ThemeContext.Provider value={theme.dark}>
                  <div style={theme.dark}>
                    <p>Hello React Component!</p>
                    <NameComponent name={this.name} />
                    <IdComponent id={this.id} />
                    <button onClick={this.doLightTheme}>light theme</button>
                    <button onClick={this.doDarkTheme}>dark theme</button>
                  </div>
                </ThemeContext.Provider>
              );
            }
          };
        };

        // 名前を表示するクラスコンポーネント
        class NameComponent extends React.Component {
          // コンテキストをクラスコンポーネントのプロパティで `static contextType = コンテキスト変数名;` の形式で参照
          static contextType = ThemeContext;
          name = "none";

          // コンストラクタ
          constructor(props){
            super(props); // React.Component クラスのコンストラクタ呼び出し
            this.name = props.name;
          };

          // render() メソッドは、必ず定義する必要がある
          render(){
            // コンテキストは、クラスコンポーネント内にて、`this.context.コンテキスト変数名の要素変数名` の形式でアクセスできる
            return (
              <p style={this.context}>name={this.name}</p>
            );
          };
        };

        // IDを表示するクラスコンポーネント
        class IdComponent extends React.Component {
          // コンテキストをクラスコンポーネントのプロパティで `static contextType = コンテキスト変数名;` の形式で参照
          static contextType = ThemeContext;
          id = -1;

          // コンストラクタ
          constructor(props){
            super(props); // React.Component クラスのコンストラクタ呼び出し
            this.id = props.id;
          };

          // render() メソッドは、必ず定義する必要がある
          render(){
            // コンテキストは、クラスコンポーネント内にて、`this.context.コンテキスト変数名の要素変数名` の形式でアクセスできる
            return (
              <p style={this.context}>id={this.id}</p>
            );
          };
        };

        // JSX を用いた 仮想 DOM のエレメント定義
        // <コンポーネント名 /> の形式でコンポーネントを呼び出し
        let element = (
          <div>
            <h1><AppComponent name="Yagami" id="0" theme_type="light" /></h1>
            <h2><AppComponent name="Yagoo" id="1" theme_type="dark" /></h2>
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

    - テーマのコンテキストをクラスコンポーネントの外側で `const コンテキスト変数名 = React.createContext(値)` の形式で定義している

    - 各クラスコンポーネント内のプロパティにて、`static contextType = コンテキスト変数名;` の形式でコンテキストを参照するための定義をしている

    - `NameComponent` と `IdComponent` のクラスコンポーネントでは、`this.context.コンテキスト変数名の要素変数名` の形式でコンテキストにアクセスし、スタイルを設定している。（※但し `AppComponent` では `<div style={this.context}>` でスタイル設定すると、コードの作り上うまく全体のスタイルが変わらないので、後述の方法でスタイル設定している）

    - `AppComponent` コンポーネントの `doDarkTheme` イベントメソッド内で、`this.context = theme.dark;` のような形式でコンテキストの値を直接変更したいが、コンテキスト変数の値は直接変更できない。コンテキストの値を変更するには、`<コンテキスト名.Provider value={値}}>` を用いる必要がある。<br>
      そのため、この例では、イベントメソッド内で `theme_type` フラグのみ変更するようにし、`render()` メソッド内にて、このフラグ値 `theme_type` に応じて `<コンテキスト名.Provider value={値}}>` を用いて、コンテキスト値を切り替えることで、テーマの切り替えを行っている。このとき `theme_type` を通常のプロパティとして定義すると、ボタンクリックしてもテーマの変更が反映されないので、state で定義するようにする。

1. 静的な Web ファイル `index2.html` をブラウザで開き動作確認する
    ```sh
    $ open index2.html
    ```

    ブラウザ上に以下のような表示が行われる<br>
    <img src="https://user-images.githubusercontent.com/25688193/137866595-7237f4b8-7bc8-44df-bdbb-a1b2bcadd61b.png" width="300"><br>

    > クラスコンポーネント間でテーマのコンテキストの値が共有されるため、ボタンをクリックすると、全てのクラスコンポーネントのテーマが一斉に切り替わっている点に注目
