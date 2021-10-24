# 【React】Redux Persist で React アプリのデータを永続化する

データの永続化を行っていないアプリでは、ブラウザでアプリのページをリロードすると、入力したデータなどがすべて消えてしまう。

Redux を利用した React アプリにおいては、Redux Persist を用いることで、データの永続化を行い、アプリを再読み込みしてもデータが消失しないアプリを作成することが出来る。

より詳細には、Redux Persist では、Redux における通常のレデューサー・ストア・プロバイダーに、永続化機能を織り込んだ「パーシストレデューサー」。「パーシスター」・「パーシストゲート」というものを用いて、永続化機能を実現している。その大まかな手順は、以下のようになる。

Redux Persist を使用していない Redux を利用した React アプリから大きな変更を行うことなく、Redux Persist による永続化を組み込むことができる点に注目

1. パーシストレデューサーの作成<br>
    1. Redux Persist の設定情報の作成<br>
        ```js
        import storage from 'redux-persist/lib/storage';
        const 設定情報の定数名 = {
            key: "keyの指定",
            storage,
            blacklist: ["永続化を行わないストアのstateの変数名"],
            whitelist: ["永続化を行うストアのstateの変数名"],
        };
        ```
        - `key` : ブラウザのローカルストレージは、key:value 形式で値を保存しているが、その key を指定する。
        - `storage` : Redux Persist が用意しているストレージを指定する（`redux-persist/lib/storage` で定義されている `storage`）
        - `blacklist` : 永続化を行わないストアのstateの変数名をリスト形式で指定
        - `whitelist` : 永続化を行うストアのstateの変数名をリスト形式で指定

        > `blacklist`, `whitelist` の定義を行わない場合は、ストアの全ての state が永続化される動作になる。

    1. （通常の）レデューサーの作成<br>
        ```js
        // action : レデューサーを呼び出す際の情報をまとめたオブジェクト
        function レデューサーの関数名 (state=stateの初期値, action){
          // state の更新処理を定義
        }
        ```
    1. パーシストレデューサーの作成<br>
        ```js
        import { persistReducer } from 'redux-persist';
        const パーシストレデューサー名 = persistReducer(設定情報の定数名, レデューサーの関数名);
        ```

        `persistReducer()` メソッドを用いて、通常のレデューサーをラッピングすることで、パーシストレデューサーを作成できるので、Redux Persist を使用していない Redux を利用した React アプリから大きな変更を行うことなく、Redux Persist による永続化を組み込むことができる。

1. パーシスターの作成<br>
    1. （通常の）ストアの作成<br>
        ```js
        ストアの変数名 = createStore(パーシストレデューサー)
        ```

        パーシストレデューサーから `createStore()` メソッドを用いて、通常のストアを作成する

    1. パーシスターの作成<br>
        ```js
        import { persistStore } from 'redux-persist';
        パーシスターの変数名 = persistStore(ストアの変数名)
        ```
        
        通常のストアから `persistStore()` メソッドを用いて、パーシスターを作成できるので、Redux Persist を使用していない Redux を利用した React アプリから大きな変更を行うことなく、Redux Persist による永続化を組み込むことができる。

1. パーシストゲートの作成<br>
    ```js
    import { PersistGate } from 'redux-persist/integration/react';

    // 表示をレンダリング
    ReactDOM.render(
        <Provider store={store}>
            <PersistGate loading={<p>loading...</p>} persistor={パーシスターの変数名}>
                <App />
            </PersistGate>
        </Provider>,
        document.getElementById('root')
    );
    ```

    プロバイダーのタグ `<Provider>` 内に、パーシストゲートのタグ `<PersistGate>` を追加するだけなので、Redux Persist を使用していない Redux を利用した React アプリから大きな変更を行うことなく、Redux Persist による永続化を組み込むことができる。

## ■ 方法

1. npm をインストール
    - MacOS の場合
        ```sh
        # Node.jsをインストール
        $ brew install node
        ```
    > npm : Node.js のパッケージを管理するコマンド

1. React プロジェクトを作成する<br>
    Node.js に組み込まれている `npx` コマンドを用いて、Create React App で React プロジェクトを作成する

    ```sh
    $ npx create-react-app ${PROJECT_NAME}
    ```
    ```sh
    # 強制 yes にする場合
    $ npx -y create-react-app ${PROJECT_NAME}
    ```

1. Redux, React Redux, React DevTools をインストールする<br>
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm install --save redux
    $ npm install --save react-redux
    $ npm install --save-dev redux-devtools
    ```

1. Redux Persist をインストールする<br>
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm install --save redux-persist
    ```

1. `src.index.js` を修正する<br>
    ```js
    import React from 'react';
    import ReactDOM from 'react-dom';
    import storage from 'redux-persist/lib/storage';
    import { createStore } from 'redux';           // ストア機能を import
    import { Provider } from 'react-redux';                         // プロバイダー機能を import
    import { persistStore, persistReducer } from 'redux-persist';   // redux-persist のパーシストレデューサーとパーシスター
    import { PersistGate } from 'redux-persist/integration/react';  // redux-persist のパーシストゲート
    import './index.css';
    import App from './App';

    // Redux Persist の設定情報の作成
    const persist_config = {
      key: "root",
      storage,
      blacklist: ["name"],
      whitelist: ["id"],
    };

    // function レデューサーの関数名 (state=stateの初期値, action){} の形式でレデューサーを定義
    function reducer(state = {name: "Yagami",id:-1}, action) {
      // action : レデューサーを呼び出す際の情報をまとめたオブジェクト
      // action.type : action オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。これらの値は、App.js 内の `this.props.dispath({type:"xxx"})` で定義している
      switch (action.type) {
        case 'INCREMENT_ID': // 
          // state の新しい値を return する
          return {
              name:state.name,
              id:state.id + 1,
          };
        case 'DECREMENT_ID':
          return {
            name:state.name,
            id:state.id - 1,
          };
        default:
          return state;
      }
    }

    // パーシストレデューサーの作成
    const persist_reducer = persistReducer(persist_config, reducer);

    // `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
    let store = createStore(persist_reducer);

    // パーシスターの作成
    let persist_store = persistStore(store);

    // 表示をレンダリング
    ReactDOM.render(
      // プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
      // プロバイダーのタグ `<Provider>` 内に、パーシストゲートのタグ `<PersistGate>` を追加することで、パーシストゲートをコンポーネントに適用する
      <Provider store={store}>
        <PersistGate loading={<p>loading...</p>} persistor={persist_store}>
          <App />
        </PersistGate>
      </Provider>,
      document.getElementById('root')
    );
    ```

    ポイントは、以下の通り。

    - `const persist_config = {key: "root", storage,};` の部分で、redux-persist の設定情報を定義している。`key` には `"root"` を指定している。この値は `index.html` の `root` に対応していたものではなく、ブラウザのローカルストレージの key の値であることに注意（ブラウザのローカルストレージは key:value 形式でデータを保管している）。ブラウザのローカルストレージの key は、ディベロッパーツールから確認できる。<br>
      また　`blacklist` に `"name"`, `whitelist` に `"id"` を指定することで、ストアの state のうち `id` の値のみデータの永続化を行うようにしている。

    - `const persist_reducer = persistReducer(persist_config, reducer);` の部分で、通常のレデューサーからパーシストレデューサーを作成している。

    - `let store = createStore(persist_reducer);` の部分で、パーシストレデューサーから通常のストアを作成している。

    - `let persist_store = persistStore(store);` の部分で、通常のストアからパーシスターを作成している。

    - `ReactDOM.render()` の JSX 定義にて、プロバイダーのタグ `<Provider>` 内に、パーシストゲートのタグ `<PersistGate>` を追加することで、パーシストゲートを `App` コンポーネントに適用している

    - 全体的に、Redux Persist を使用していない Redux を利用した React アプリから大きな変更を行うことなく、Redux Persist による永続化を組み込むことができる点に注目

1. `src/App.js` を修正する<br>

    ```js
    import React, { Component } from 'react';
    import { connect } from 'react-redux';
    import './App.css';

    // コンポーネントで使用する state を返すメソッド
    function mappingState(state) {
      return state;
    }

    // App コンポーネント
    class App extends Component {
      constructor(props){
        super(props);
      }

      render() {
        // <StateComponent /> に部分を <StateComponent id="-1" /> のように属性を指定した呼び出し方をしなくとも、StateComponent コンポーネントで this.props.id でアクセスできる
        return (
          <div>
            <p>Hello React Component!</p>
            <StateComponent />
            <ButtonComponent />
          </div>
        );
      }
    }

    // connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
    // let warpWithConnect = connect()  // warpWithConnect は関数オブジェクト
    // App = warpWithConnect(warpWithConnect)
    App = connect()(App);

    // ID 表示のコンポーネント
    class StateComponent extends Component {
      render(){
        // このクラスコンポーネントでは、<StateComponent name="Yagami" id="1" /> のように属性を指定して呼び出さられなくても、this.props に index.js のレデューサーで定義した state が設定されている
        return (
          <p>
            name={this.props.name}, id={this.props.id}
          </p>
        );
      }
    }

    // StateComponent コンポーネントにストアを接続する
    // 第１引数に state の内容をそのまま返す mappingState() メソッドを設定することで、StateComponent コンポーネント内の this.props に index.js 内のレデューサーで定義した state が設定される
    StateComponent = connect(mappingState)(StateComponent);

    // ボタンのコンポーネント
    class ButtonComponent extends Component {
      constructor(props){
        super(props);
        // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
        this.doAction = this.doAction.bind(this);
      }

      // ボタンクリックでディスパッチ（レデューサーの呼び出し値を操作するためのもの）を実行
      doAction(e){
        if (e.shiftKey){
          // this.props.dispatch({action}) でレデューサーを呼び出す。このときレデューサーメソッドの action 引数にここで設定した値が設定される
          // type は必ず設定する必要がある
          this.props.dispatch({ type:'DECREMENT_ID' });
        } else {
          this.props.dispatch({ type:'INCREMENT_ID' });
        }
      }

      render(){
        // <button> タグの onClick 属性に、このクラスコンポーネントで定義したイベント処理のメソッドを設定し、onClick 属性に紐付ける
        return (
          <button onClick={this.doAction}>
            click
          </button>
        );
      }
    }
    // ストアのコネクト
    ButtonComponent = connect()(ButtonComponent);

    // App を外部ファイルから利用できるようにする
    export default App;

    ```

    Redux Persist を使用していない Redux を利用した React アプリから変更なしになっている点に注目


1. 【オプション】プロジェクトをビルドする
	React を用いたアプリケーションを公開したい場合は、以下のコマンドでプロジェクトをビルドして公開する
	```sh
	$ npm run build
	```

	> ビルドしたプロジェクトは `${PROJECT_NAME}/build` ディレクトリに作成される。この build ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

1. 作成した React のプロジェクトのサーバーを起動する
	```sh
	$ cd ${PROJECT_NAME}
	$ npm start
	```

  コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く

  > ブラウザをリロードしても id の値が変わらなくなっている点に注目

1. 【オプション】ブラウザのディベロッパーツールでブラウザのローカルディスクに保存されているデータを確認する<br>
    「アプリケーション」→「ストレージ」→「ローカルストレージ」→「http://localhost:${PORT}」→「persist:root」から確認できる。

    <img src="https://user-images.githubusercontent.com/25688193/138579809-b3eb3a13-ae29-4608-827f-cffd4b93bf2c.png" width="500"><br>

    > この `persist:root` が、ブラウザのローカルストレージに格納されている key の値になる

    > key の value において、ストアの state のうち、`whitelist` に追加した `"id"` のみが保存されて、`blacklist` に追加した `"name"` の値は保存されていない点に注目
