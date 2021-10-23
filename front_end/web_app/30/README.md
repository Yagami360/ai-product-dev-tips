
# 【React】React を使用して簡単なウェブアプリを作成する

ここでは、React を使用した簡単なウェブアプリの構成例として、以下のようなメモ帳アプリを作成する

<img src="https://user-images.githubusercontent.com/25688193/138546011-aff3aeb7-0ed8-4d40-9c56-6cfc074a7321.png" width="500"/>

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

1. `src/index.js` を修正する<br>
    ```js
    import React from 'react';
    import ReactDOM from 'react-dom';
    import { Provider } from 'react-redux';                 // プロバイダー機能を import
    import './index.css';
    import App from './App';
    import Store from './Store'

    // 表示をレンダリング
    ReactDOM.render(
      // プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
      // この例では、App.js で定義されている App コンポーネントにストアの内容が渡される
      <Provider store={Store}>
        <App />
      </Provider>,
      document.getElementById('root')
    );
    ```

	ポイントは、以下の通り

	- `<Provider store={ストアの変数名}>` タグでプロバイダーとその store 属性で定義し、アプリ全部のコンポーネント `<App />`にストアの内容が渡している。

1. `src/App.js` を修正する<br>
  `App.js` の `App` コンポーネントは、アプリ全部画面のコンポーネントであり、アプリ全部表示を行う。

    <img src="https://user-images.githubusercontent.com/25688193/138546011-aff3aeb7-0ed8-4d40-9c56-6cfc074a7321.png" width="500"/>

    ```js
    import React, { Component } from 'react';
    import { connect } from 'react-redux';
    import './App.css';
    import Memo from './Memo';
    import AddMemoForm from './AddMemoForm';
    import DeleteMemoForm from './DeleteMemoForm';

    // アプリ全部のコンポーネント
    class App extends Component {
      constructor(props){
        super(props);
      }

      render() {
        // <hr /> タグ : 区切り線
        return (
          <div>
            <h1>React Memo App</h1>
            <AddMemoForm />
            <hr />
            <DeleteMemoForm />
            <Memo />
          </div>
        );
      }
    }

    // connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
    App = connect()(App);

    // 外部公開する
    export default App
    ```

	  ポイントは、以下の通り

    - `render()` 内で、後述で作成した各種画面表示を行うコンポーネント `Memo`, `AddMemoForm`, `DeleteMemoForm` を呼び出すことで、アプリ全部画面の表示を行っている

	  - `connect(stateを設定する関数)(コンポーネント)` でコンポーネントに対して、ストアの state を接続している。

    - `export default` で `App` コンポーネントを外部公開している

1. `src/Store.js` を修正する<br>
  `Store.js` では、レデューサーの定義、レデューサーの action を定義するアクションクリエイター、及び、ストアの作成を行う。

    ```js
    import { createStore } from 'redux';   // ストア機能を import

    // ステートの初期値
    let init_state = {
      // 各メモをリストで管理
      data_list: [{
        memo_text: "xxx",                // メモのテキスト内容
        created_time: new Date(),       // メモの作成時刻
      }]
    }

    //-----------------------------------------
    // レデューサー
    //-----------------------------------------
    function reducer(state = init_state, action) {
      // action : レデューサーを呼び出す際の情報をまとめたオブジェクト
      // action.type : action オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。これらの値は、App.js 内の `this.props.dispath({type:"xxx"})` で定義している
      switch (action.type) {
        case 'ADD_MEMO': // 
          // state の新しい値を return する
          return addMemo(state, action);
        case 'DELETE_MEMO':
          // state の新しい値を return する
          return deleteMemo(state, action);
        default:
          return state;
      }
    }

    //-----------------------------------------
    // レデューサー内部から呼び出される各種メソッド
    //-----------------------------------------
    // メモを追加するメソッド
    function addMemo(state, action){
      let new_data = {
        memo_text: action.memo_text,
        created_time: new Date(),
      }

      // リスト.slice() で state 内の変数のリストのコピーインスタンスを作成
      // Redux では state の値を直接変えて setState() で state の更新を行っても、state の更新なしと判断してしまうため、state オブジェクトのコピーを作成して、そのオブジェクトを更新するようにする
      let new_data_list = state.data_list.slice();

      // unshift() でリストの先頭に値を追加
      new_data_list.unshift(new_data)

      // 新たな state を return
      return {
        data_list: new_data_list,
      }
    }

    // メモを削除するメソッド
    function deleteMemo(state, action){
      // リスト.slice() で state 内の変数のリストのコピーインスタンスを作成
      // Redux では state の値を直接変えて setState() で state の更新を行っても、state の更新なしと判断してしまうため、state オブジェクトのコピーを作成して、そのオブジェクトを更新するようにする
      let new_data_list = state.data_list.slice();

      // splice() でリストの要素を削除
      // action.select_index : メモの番号
      new_data_list.splice(action.select_index, 1);

      // 新たな state を return  
      return {
        data_list: new_data_list,
      }
    }

    //-----------------------------------------
    // アクションクリエイター
    // this.props.dispatch({action}) 呼び出し時の action の値を定義するメソッド　
    //-----------------------------------------
    export function addMemoAction(memo_text){
      return {
        type: 'ADD_MEMO',
        memo_text:memo_text
      }
    }

    export function deleteMemoAction(select_index){
      return {
        type: 'DELETE_MEMO',
        select_index:select_index
      }
    }

    //-----------------------------------------
    // `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
    // export default で外部ファイルに公開
    //-----------------------------------------
    let store = createStore(reducer);
    export default store;
    ```

    - `function レデューサーの関数名 (state=stateの初期値, action){...}` の形式でレデューサーを定義している。 ここで、`action` 引数には、レデューサーを呼び出す際の情報をまとめたオブジェクトが設定される。この内、`action.type` は action オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。 そして、レデューサーは、後述の `AddMemoForm.js` や `DeleteMemoForm.js` のコンポーネント内にて、`this.props.dispatch({action})` を呼び出したときに呼び出される。

    - レデューサー内（レデューサーから呼び出されるメソッド内）では、`リスト.slice()` の形式で state 内の変数のリスト `state.data_list` のコピーを作成し、そのコピーインスタンスの値を新たな state として設定している。これは Redux では state の値を直接変えて `setState()` で state の更新を行っても、state の更新なしと判断してしまうためである。そのため state オブジェクトのコピーを作成して、そのオブジェクトを更新するようにしている。

    - `addMemoAction()` メソッドや `deleteMemoAction` メソッドは、アクションクリエイターで、レデューサーの引数に渡される `action` を返す外部公開されたメソッドになっている。このメソッドを用意して外部公開しておくことで、`this.props.dispatch({action})` の呼び出さし元（今の場合 `AddMemoForm.js` や `DeleteMemoForm.js`）が、レデューサーにどのような action を定義すればよいのか知らなくて良くなるので便利

    - レデューサー定義後、`ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成し、`export default ストア名` で外部ファイルに公開している。

1. `src/Memo.js` を作成する<br>
  `Memo.js` では、保存済みのメモ画面の表示を行う `Memo` コンポーネントを定義する

    <img src="https://user-images.githubusercontent.com/25688193/138546222-a696d6de-3d7c-4b40-a689-2b408e9dd722.png" width="500"><br>

    ```js
    import React, { Component } from 'react';
    import { connect } from 'react-redux';
    import Item from './Item';

    // メモ画面のコンポーネント
    class Memo extends Component {
      constructor(props){
        super(props);
      }

      render() {
        // <table> タグ : 表
        // 配列.map((value)=>(配列の各要素 value に対しての処理)) : map で配列の各要素 value を取り出し、value を引数に、配列の各要素 value に対しての処理を行う
        return (
          // 保存済みメモ一覧
          <table><tbody>
            <th>No</th>
            <th>テキスト</th>
            <th>保存時間</th>
            {this.props.data_list.map((data,index)=>(
              <Item index={index} memo_text={data.memo_text} created_time={data.created_time} />
            ))}
          </tbody></table>
        );
      }
    }

    // コンポーネントで使用する state を返すメソッド
    function mappingState(state) {
      return state;
    }

    // connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
    // 第１引数に state の内容をそのまま返す mappingState() メソッドを設定することで、Memo コンポーネント内の this.props に Store.js 内のレデューサーで定義した state が設定される
    Memo = connect(mappingState)(Memo);

    // 外部公開する
    export default Memo
    ```

    - `Memo = connect(mappingState)(Memo);` とすることで、`this.props.state内の変数名` で `Store.js` 内のレデューサー `reducer` で定義したストアの state にアクセス出来るようにしている。
      ```js
      // `Store.js` 内のレデューサー `reducer` で定義したストアの state
      data_list: [{
        memo_text: "xxx",                // メモのテキスト内容
        created_time: new Date(),       // メモの作成時刻
      }]
      ```

    - `配列.map((value)=>(配列の各要素 value に対しての処理))` の形式で、Store の state で定義した配列 `this.props.data_list` の各要素に対して、メモの各項目のコンポーネント `<Item />` を繰り返し呼び出すことで、メモ画面全部を表示するようにしている。

    - 尚、Store の state で定義した配列 `this.props.data_list` への要素の追加や削除は、`AddMemoForm.js`, `DeleteMemoForm.js` で定義するコンポーネント内でのイベント処理で行われる。

    - メモ画面は、`<table>` タグを使って表形式で表示する。`<Item />` で呼び出しているメモの各項目を表示するコンポーネント内で、`<tr>` タグ（テーブルの行）・`<th>` タグ（テーブルの見出し）・`<td>` タグ（テーブルのセル）が render されるので、結果として、以下のような HTML タグ構造になる。
      ```html
      // 保存済みメモ一覧
      <table><tbody>
        <th>No</th>
        <th>テキスト</th>
        <th>保存時間</th>
        <tr>
          <th>0</th>
          <td>"memo text1"</td>
          <td>00:00:00</td>
        </tr>
        <tr>
          <th>1</th>
          <td>"memo text2"</td>
          <td>00:00:10</td>
        </tr>
        ...
      </tbody></table>
      ```

1. `src/Item.js` を作成する<br>
  `Item.js` では、保存済みのメモ画面の各項目の表示を行う `Item` コンポーネントを定義する

    <img src="https://user-images.githubusercontent.com/25688193/138546235-6c03c5d3-5c9d-446e-99c6-cf6a82f3243f.png" width="500"><br>

    ```js
    import React, { Component } from 'react';
    import { connect } from 'react-redux';

    // メモの各項目のコンポーネント
    class Item extends Component {
      //index = 0;
      //memo_text = "xxx";
      //created_time = "00:00:00";

      index_style = {
        fontSize:"14pt",
        backgroundColor:"blue",
        color:"white",
        padding:"5px 10px",
        width:"50px"
      }
      memo_text_style = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        minWidth:"300px"
      }
      date_style = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        width:"80px"
      }

      constructor(props){
        super(props);
        //this.index = props.index
        //this.memo_text = props.memo_text
        //this.created_time = props.created_time
      }

      render() {
        // <table> タグ : 表
        // <tr> タグ : テーブルの行（横方向）
        // <th> タグ : テーブルの見出し
        // <td> タグ : テーブルのセル
        // 自身のプロパティ this.index, this.memo_text, this.created_time で表示するようにすると、表示が即座に反映されなくなるので、コンポーネント呼び出し時の引数で設定される this.props.xxx でアクセスするようにしている。
        return (
          <tr>
            <th style={this.index_style}>{this.props.index}</th>
            <td style={this.memo_text_style}>{this.props.memo_text}</td>
            <td style={this.data_style}>{this.props.created_time.getHours() + ':' + this.props.created_time.getMinutes() + ':' + this.props.created_time.getSeconds()}</td>
          </tr>
        );
      }
    }

    // connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
    Item = connect()(Item);

    // 外部公開する
    export default Item
    ```

    ポイントは、以下の通り。

    - メモの各項目の値は、`<Item index=0 memo_text="memo1" created_time=xxx />` の形式で呼び出されてときのコンストラクタの引数 `props` を元に `this.props.属性名` で render される。ここでの `props` は、コンポーネントのコンストラクタの引数のことであり、Store の state に接続されてアクセス可能になる `this.props.ストアの変数名` ではないことに注意。

    - また、コンストラクタの引数 `props` を元に `this.xxx = this.props.xxx` で設定した自身のプロパティ（メモの番号 :`this.index`）・（メモのテキスト:`this.memo_text_style`）・（メモの日付: `this.data_style`）で render 行うようにすると、ブラウザ画面の更新直後にしか値が反映されず、後述で定義するメモの追加ボタンクリック時に値が反映されなくなるので注意（コンストラクタの呼び出し時にかこれらのプロパティ値が更新されないので、このような動作になる）

1. `src/AddMemoForm.js` を作成する。<br>
  `AddMemoForm.js` では、メモの追加画面とそれに関連するイベント処理を行うコンポーネントを定義する。

    <img src="https://user-images.githubusercontent.com/25688193/138546263-b03171d1-68cd-435d-88c5-6d04a09c4505.png" width="500"><br>

    ```js
    import React, { Component } from 'react';
    import { connect } from 'react-redux';
    import { addMemoAction } from './Store';

    // メモの追加画面のコンポーネント
    class AddMemoForm extends Component {
      constructor(props){
        super(props);

        // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
        this.state = {
          memo_text: ""
        };

        // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
        this.updateInputText = this.updateInputText.bind(this);
        this.addMemo = this.addMemo.bind(this);
      }

      // テキスト入力フォーム更新時のイベント処理
      // このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
      updateInputText(e){
        // `state` の値の更新は、`this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。
        // e.target.value に入力テキストが入る
        this.setState(
          (state)=>({
            memo_text: e.target.value,
          })
        );
      }

      // Add ボタンクリック時のイベント処理
      addMemo(e){
        // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
        e.preventDefault();

        // アクションクリエイターで定義した action
        let action = addMemoAction(this.state.memo_text);
        
        // this.props.dispatch({action}) でレデューサーを呼び出す。
        this.props.dispatch(action);

        // テキスト入力フォームのテキストを空にする
        this.setState({memo_text: ''});
      }

      // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
      // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
      // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
      render() {
        return (
          <div>
            <p>Please type your message</p>
            <form onSubmit={this.addMemo}>
              <input type="text" size="40" onChange={this.updateInputText} value={this.state.memo_text} />
              <input type="submit" value="Add"/>
            </form>
          </div>
        );
      }
    }

    // コンポーネントで使用する state を返すメソッド
    function mappingState(state) {
      return state;
    }

    // connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
    AddMemoForm = connect(mappingState)(AddMemoForm);

    // 外部公開する
    export default AddMemoForm
    ```

    ポイントは、以下の通り。

    - `<form>` タグで入力フォームを作成する。このがひとつのフォームとなり、フォームの中に `<input>` タグなどのフォーム部品を配置してフォームを作られる

    - `AddMemoForm = connect(mappingState)(AddMemoForm);` でコンポーネントをストアに接続することで、`this.props.dispatch({action}) ` でレデューサーを呼び出すことが出来るようにする。

    - 入力フォーム内のテキスト `memo_text` は、state として定義し、値の変更が即座に画面表示されるようにする（ここでの state はストアの state ではないことに注意）。`state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う

    - `<input>` タグの onChange 属性で、入力フォームのコントロール部品の値が変更されたとき（＝入力フォームにキーボードでテキストを入力したとき）のイベント処理のメソッド `updateInputText(e)` を指定する。このメソッドは、`this.メソッド名 = this.メソッド名.bind(this);` の形式でイベントをバインド（割り当て）しておく。
      `updateInputText(e)` 内では、`state` の値の更新を `this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。入力フォームに入力されてテキスト情報は、`e.target.value` に入っているので、その値で stete の `memo_text` を更新する。

    - `<form>` タグの onSubmit 属性で、`<form>` タグ内部の `<input type="submit">` で定義したボタンクリック時のイベント処理のメソッド `addMemo(e)` を指定する。このメソッドは、`this.メソッド名 = this.メソッド名.bind(this);` の形式でイベントをバインド（割り当て）しておく。
      `addMemo(e)` 内では、`Store.js` 内で定義したアクションクリエイター `addMemoAction(memo_text)` から、レデューサーに渡す `action` を取得し、その後 `this.props.dispatch({action}) ` でレデューサーを呼び出している。最後に、`state` の値の更新を `this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行い、テキストを空にしておく。

1. `src/DeleteMemoForm.js` を作成する。<br>
  `DeleteMemoForm.js` では、メモの追加画面とそれに関連するイベント処理を行うコンポーネントを定義する。

    <img src="https://user-images.githubusercontent.com/25688193/138546274-0e5989e7-2ce0-4a9b-8126-024bc74bc093.png" width="500"><br>

    ```js
    import React, { Component } from 'react';
    import { connect } from 'react-redux';
    import { deleteMemoAction } from './Store';

    // メモの削除画面のコンポーネント
    class DeleteMemoForm extends Component {
      select_style = {
        fontSize:"12pt",
        color:"#006",
        padding:"1px",
        margin:"5px 0px"
      }
      btn_style = {
        fontSize:"10pt",
        color:"#006",
        padding:"2px 10px"
      }

      constructor(props){
        super(props);

        // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
        // select_index : 選択ボックスの番号
        this.state = {
          select_index: -1
        };

        // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
        this.updateSelect = this.updateSelect.bind(this);
        this.deleteMemo = this.deleteMemo.bind(this);
      }

      // 選択ボックス更新時のイベント処理
      updateSelect(e){
        // `state` の値の更新は、`this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。
        // e.target.value に選択ボックスの番号が入る
        this.setState(
          (state)=>({
            select_index: e.target.value,
          })
        );
      }

      // Delete ボタンクリック時のイベント処理
      deleteMemo(e){
        // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
        e.preventDefault();

        // アクションクリエイターで定義した action
        let action = deleteMemoAction(this.state.select_index);
        console.log("[deleteMemo] action", action)

        // this.props.dispatch({action}) でレデューサーを呼び出す。
        this.props.dispatch(action);

        // テキスト入力フォームのテキストを空にする
        this.setState({memo_text: ''});
      }

      // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
      // <select> タグ : 選択ボックス
      // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
      // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
      render() {
        let n = 0;
        let memo_texts = this.props.data_list.map((data)=>(<option key={n} value={n++}>{data.memo_text.substring(0,10)}</option>));

        return (
          <div>
            <form onSubmit={this.deleteMemo}>
              <select onChange={this.updateSelect} defaultValue="-1" style={this.select_style}>
                {memo_texts}
              </select>
              <input type="submit" style={this.btn_style} value="Delete"/>
            </form>
          </div>
        );
      }
    }

    // コンポーネントで使用する state を返すメソッド
    function mappingState(state) {
      return state;
    }

    // connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
    DeleteMemoForm = connect(mappingState)(DeleteMemoForm);

    // 外部公開する
    export default DeleteMemoForm

    ```

    ポイントは、以下の通り。

    - `this.props.data_list.map((data)=>(<option key={n} value={n++}>{data.memo_text.substring(0,10)}</option>));` で、メモの各項目のテキストを取得している。

    - `<form>` タグ内の `<select>` タグで、選択ボックスを表示している。

    - その他は、`AddMemoForm.js` と同じような構成

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

<!--
1. デプロイしたアプリの Web サイトにアクセスする
	```sh
	$ open http://localhost:3000
	```
-->
