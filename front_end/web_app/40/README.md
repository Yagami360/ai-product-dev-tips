# 【React】React と React Hooks を使用して簡単なウェブアプリを作成する

ここでは、React と React Hooks を使用した簡単なウェブアプリの構成例として、以下のようなメモ帳アプリを作成する

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

1. `src/LocalPersist.js` を作成する<br>
    ローカルストレージにデータを保存する独自フックである `useLocalPersist()` を作成する<br>

    ```js
    import { useState } from 'react'

    // ローカルストレージでのデータの永続化を行う独自フック
    function useLocalPersist(key, initValue) {
      const _key = "hooks:" + key

      // ローカルディスクから key の value を取得する関数
      // 初回の書き込みで key がない場合は、初期値 initValue を返す
      const loadValueFromStorage = () => {
        try {
          const item = window.localStorage.getItem(_key)
          return item ? JSON.parse(item) : initValue
        }
        catch (err) {
          console.log(err)
          return initValue;
        }
      }

      // ローカルストレージから読み込んだ initVal
      const [savedValue, setSavedValue] = useState(loadValueFromStorage)

      // key の value を json 形式に変化してローカルストレージに保存する関数
      // この関数を第２戻り値として return し、state の値を更新する関数とする
      const saveValueToStorage = (value) => {
        try {
          setSavedValue(value)
          window.localStorage.setItem(_key, JSON.stringify(value))
        }
        catch (err) {
          console.log(err)
        }
      }

      // ローカルストレージから読み込んだ value と key の value をローカルストレージに保存する関数を return
      return [savedValue, saveValueToStorage]
    }

    export default useLocalPersist
    ```

    ポイントは、以下の通り

    - ローカルディスクから key の value を読み込む処理は、`window.localStorage.getItem()` メソッドで行っている

    - ローカルディスクから key の value を書き込む処理は、`window.localStorage.setItem()` メソッドで行っている

    - ローカルディスクから key の value を取得する関数 `loadValueFromStorage()` を定義し、これを `useState()` の引数に設定することで、ローカルディスクから key の value を初期値とする state `savedValue` を定義している

    - 更に、key の value を json 形式に変化してローカルストレージに保存する関数 `saveValueToStorage()` を定義している。この関数は return されるので、関数の引数 `value` には、この独自フックを使用する側で設定されたローカルストレージへの書き込み値が設定される。この value を `setSavedValue` で xxx

    - return 値には、ローカルストレージから読み込んだ value である `savedValue` と、key の value をローカルストレージに保存する関数である `saveValueToStorage` を設定している。この２つを return することにより、この独自フックの使用側でローカルストレージからの読み込むと書き込みが行えるようになる

    > この独自フックは使えれば良いので、あんま動作の詳細おっかけなくてよい


1. `src/App.js` を修正する<br>
    `App.js` の `App` コンポーネントは、アプリ全部画面のコンポーネントであり、アプリ全部表示を行う。

    ```js
    import './App.css';
    import React from 'react'
    import Memo from './Memo'
    import AddMemoForm from './AddMemoForm'
    import DeleteMemoForm from './DeleteMemoForm'

    function App() {
      return (
        <div className="App">
          <header className="App-header">
            <h1>React Hook Memo App</h1>
            <AddMemoForm />
            <p></p>
            <DeleteMemoForm />
            <Memo />
          </header>
        </div>
      );
    }

    export default App;
    ```

    ポイントは、以下の通り

    - retrun 内で、後述で作成した各種画面表示を行うコンポーネント `Memo`, `AddMemoForm`, `DeleteMemoForm` を呼び出すことで、アプリ全部画面の表示を行っている

1. `src/Memo.js` を作成する<br>
    `Memo.js` では、保存済みのメモ画面の表示を行う `Memo` コンポーネントとを定義する<br>
    <img src="https://user-images.githubusercontent.com/25688193/138546222-a696d6de-3d7c-4b40-a689-2b408e9dd722.png" width="500"><br>

    ```js
    import React, { useState } from 'react'
    import useLocalPersist from './LocalPersist';
    import Item from './Item'

    // メモ画面のコンポーネント
    function Memo(props) {
      // 独自フック
      // ローカルディスクから読み込んだメモの各項目のリスト。以下のデータ構造を持つ（初期値は空リスト）
      // savedMemo = [
      //   {
      //     memoText: "xxx",                 // メモのテキスト内容
      //     createdTime: "00:00:00",         // メモの作成時刻
      //   },
      //   {
      //     memoText: "yyy",                 // メモのテキスト内容
      //     createdTime: "00:00:01",         // メモの作成時刻
      //   },
      //   ...        
      // ]
      const [savedMemo, setSavedMemo] = useLocalPersist("memo", [])
      console.log("[Memo] savedMemo :", savedMemo)

      // 配列.map((value,index)=>(配列番号 index の各要素 data に対しての処理)) : map で配列の各要素 data を取り出し、data を引数に、配列の各要素 data に対しての処理を行う
      let items = savedMemo.map((data,index)=>(
        <Item index={index+1} memoText={data.memoText} createdTime={data.createdTime} />
      ))
      console.log("[Memo] items :", items)

      return (
        // 保存済みメモ一覧
        <table><tbody>
          <th>No</th>
          <th>テキスト</th>
          <th>保存時間</th>
          {items}
        </tbody></table>
      );
    }

    export default Memo;
    ```

    ポイントは、以下の通り

    - `useLocalPersist()` を用いて、ローカルディスクからメモの各項目の情報を保持したデータを `savedMemo` に保存する。この時 `savedMemo` のデータ構造は以下のようになっている（初期値は空のリスト）
      ```js
      savedMemo = [
        {
          memoText: "xxx",                 // メモのテキスト内容
          createdTime: "00:00:00",         // メモの作成時刻
        },
        {
          memoText: "yyy",                 // メモのテキスト内容
          createdTime: "00:00:01",         // メモの作成時刻
        },
        ...        
      ]
      ```

    - `配列.map((data,index)=>(配列番号 index の配列の各要素 data に対しての処理))` の形式で、ローカルディスクから読み込んだメモ情報の配列 `savedMemo` を、以下のようなメモの各項目のコンポーネント `<Item />` の配列 `items` に変換している。
      ```js
      items = [
        <Item index="1" memoText="text1" createdTime="00:00:00" />,
        <Item index="2" memoText="text2" createdTime="00:01:00" />,
        ...
      ]
      ```

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
    `Item.js` では、保存済みのメモ画面の各項目の表示を行う `Item` コンポーネントを定義する<br>
    <img src="https://user-images.githubusercontent.com/25688193/138546235-6c03c5d3-5c9d-446e-99c6-cf6a82f3243f.png" width="500"><br>

    ```js
    import React from 'react'

    // メモの各項目のコンポーネント
    function Item(props) {
      // スタイル定義
      const indexStyle = {
        fontSize:"14pt",
        backgroundColor:"blue",
        color:"white",
        padding:"5px 10px",
        width:"50px"
      }
      const memoTextStyle = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        minWidth:"300px"
      }
      const dateStyle = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        width:"80px"
      }

      console.log("call Item")  
      return (
        <tr>
          <th style={indexStyle}>{props.index}</th>
          <td style={memoTextStyle}>{props.memoText}</td>
          <td style={dateStyle}>{props.createdTime}</td>
        </tr>
      );
    }

    export default Item;
    ```

    - メモの各項目の値は、`<Item index=0 memoText="memo1" createdTime=xxx />` の形式で呼び出されてときの関数の引数 `props` を元に `props.属性名` で render する。


1. `src/AddMemoForm.js` を作成する。<br>
    `AddMemoForm.js` では、メモの追加画面とそれに関連するイベント処理を行うコンポーネントを定義する。<br>
    <img src="https://user-images.githubusercontent.com/25688193/138546263-b03171d1-68cd-435d-88c5-6d04a09c4505.png" width="500"><br>

    ```js
    import React, { useState } from 'react'
    import useLocalPersist from './LocalPersist';

    function AddMemoForm(props) {
      // ステートフック・独自フック
      const [memoText, setMemoText] = useState('')
      const [savedMemo, setSavedMemo] = useLocalPersist("memo", [])

      // テキスト入力フォーム更新時のイベントハンドラ。このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
      // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
      const updateInputText = (e)=>{
        // e.target.value に入力テキストが入る
        setMemoText(e.target.value)
      }

      // Add ボタンクリック時のイベントハンドラ
      const addMemo = (e)=>{
        // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
        //e.preventDefault();    // その処理を入れると、Add ボタンクリック直後に（画面をリロードするまでは）メモの追加が行われなくなるので削除

        // 追加データ
        const date = new Date()
        const newData = {
          memoText: memoText,
          createdTime: date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds(),
        }

        // unshift() でリストの先頭に値を追加
        savedMemo.unshift(newData)

        // 値の更新を反映（＝ローカルディスクに書き込み）
        setSavedMemo(savedMemo)

        // 入力フォームのテキストをクリア
        setMemoText("")
        console.log("[AddMemoForm] [addMemo] savedMemo", savedMemo)
      }
      
      // ステートフック useState() で定義したステート memoText を {memoText} で表示させることで値の変更が即座に画面上に反映されるようにする
      return (
        <div>
          <p>Please type your message</p>
          <form onSubmit={addMemo}>
            <input type="text" size="40" onChange={updateInputText} value={memoText} />
            <input type="submit" value="Add"/>
          </form>
        </div>
      );
    }

    export default AddMemoForm;
    ```

    ポイントは、以下の通り

    - `<form>` タグで入力フォームを作成する。このがひとつのフォームとなり、フォームの中に `<input>` タグなどのフォーム部品を配置してフォームを作られる

    - `<input>` タグの onChange 属性で、入力フォームのコントロール部品の値が変更されたとき（＝入力フォームにキーボードでテキストを入力したとき）のイベント処理のメソッド `updateInputText(e)` を指定する。

    - `<form>` タグの onSubmit 属性で、`<form>` タグ内部の `<input type="submit">` で定義したボタンクリック時のイベント処理のメソッド `addMemo(e)` を指定する。

    - 入力フォームのテキストを `useState` で作成したステート `memoText` で管理する。そして、入力フォーム更新時のイベントハンドラ `updateInputText` 内にて、ステート更新用の関数 `setMemoText()` でステートの状態を変更する。これにより、入力フォームに入力されたテキストが即座に画面上に変更されるようになる。

    - Add ボタンクリック時のイベントハンドラ `addMemo` 内では、まず `unshift()` でローカルディスクから読み込んだメモ情報リスト `savedMemo` の先頭に新たしい値を追加し、これを `setSavedMemo()` に渡し、ローカルディスクに保存する。この時、このリスト `savedMemo` はステートでもあるので、`setSavedMemo()` が呼び出されると、即座に画面上の変更され保存済みメモ画面にメモが追加される動作になる

    - Add ボタンクリック時のイベントハンドラ `addMemo` 内で、`e.preventDefault()` として、submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセルすると、Add ボタンクリック直後に（画面をリロードするまでは）メモの追加が行われなくなることに注意

1. `src/DeleteMemoForm.js` を作成する。<br>
    `DeleteMemoForm.js` では、メモの追加画面とそれに関連するイベント処理を行うコンポーネントを定義する。<br>
      <img src="https://user-images.githubusercontent.com/25688193/138546274-0e5989e7-2ce0-4a9b-8126-024bc74bc093.png" width="500"><br>

      ```js
      import React, { useState } from 'react'
      import useLocalPersist from './LocalPersist';

      function DeleteMemoForm(props) {
        // スタイル定義
        const selectStyle = {
          fontSize:"12pt",
          color:"#006",
          padding:"1px",
          margin:"5px 0px"
        }
        const btnStyle = {
          fontSize:"10pt",
          color:"#006",
          padding:"2px 10px"
        }

        // ステートフック・独自フック
        const [selectIndex, setSelectIndex] = useState(0)
        const [savedMemo, setSavedMemo] = useLocalPersist("memo", [])

        // 選択ボックス更新時のイベントハンドラ
        // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
        const updateSelect = (e)=>{
          // e.target.value に選択ボックスの番号が入る
          setSelectIndex(e.target.value)
        }

        // Delete ボタンクリック時のイベントハンドラ
        const deleteMemo = (e)=>{
          // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
          //e.preventDefault();    // その処理を入れると、Delete ボタンクリック直後に（画面をリロードするまでは）メモの削除が行われなくなるので削除

          // splice() でリストの要素を削除
          // 削除番号には、選択ボックス更新時のイベントハンドラで設定したステート selectIndex の値を使用
          savedMemo.splice(selectIndex, 1)

          // 値の更新を反映（＝ローカルディスクに書き込み）
          setSavedMemo(savedMemo)

          // 選択ボックスの選択インデックスをクリア
          setSelectIndex(0)
          console.log("[DeleteMemoForm] [deleteMemo] savedMemo", savedMemo)
        }
        
        // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
        // <select> タグ : 選択ボックス
        // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
        // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
        let memoTexts = savedMemo.map((data,index)=>(<option key={index} value={index++}>{data.memoText.substring(0,10)}</option>));
        return (
          <div>
            <form onSubmit={deleteMemo}>
              <select onChange={updateSelect} defaultValue="-1" style={selectStyle}>
                {memoTexts}
              </select>
              <input type="submit" style={btnStyle} value="Delete"/>
            </form>
          </div>
        );
      }

      export default DeleteMemoForm;
      ```

    ポイントは、以下の通り

    - `let memoTexts = savedMemo.map((data,index)=>(<option key={index} value={index++}>{data.memoText.substring(0,10)}</option>));` で、メモの各項目のテキストを取得している。

    - `<form>` タグ内の `<select>` タグで、選択ボックスを表示している。

    - その他は、AddMemoForm.js と同じような構成


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
