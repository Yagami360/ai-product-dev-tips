# 【React】React と React Hooks を使用して簡単なウェブアプリを作成する

ここでは、React と React Hooks を使用した簡単なウェブアプリの構成例として、以下のようなメモ帳アプリを作成する

<img src="https://user-images.githubusercontent.com/25688193/138546011-aff3aeb7-0ed8-4d40-9c56-6cfc074a7321.png" width="500"/>


- ToDo : Add ボタンや Delete クリック時に、保存済みメモの内容に即座に反映されない問題の修正（ページ再読み込み時には反映される）

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
    ```js
    ```

    ポイントは、以下の通り

    - xxx

1. `src/Memo.js` を作成する<br>
    `Memo.js` では、保存済みのメモ画面の表示を行う `Memo` コンポーネントとを定義する<br>
    <img src="https://user-images.githubusercontent.com/25688193/138546222-a696d6de-3d7c-4b40-a689-2b408e9dd722.png" width="500"><br>

    ```js
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

    - `配列.map((data,index)=>(配列番号 index の配列の各要素 data に対しての処理))` の形式で、ローカルディスクから読み込んだメモ情報の配列 `savedMemo` を、以下のようなメモの各項目のコンポーネント `<Item />` の配列に変換している。
      ```js
      [
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
    ```

    - メモの各項目の値は、`<Item index=0 memoText="memo1" createdTime=xxx />` の形式で呼び出されてときの関数の引数 `props` を元に `props.属性名` で render する。


1. `src/AddMemoForm.js` を作成する。<br>
    `AddMemoForm.js` では、メモの追加画面とそれに関連するイベント処理を行うコンポーネントを定義する。<br>
    <img src="https://user-images.githubusercontent.com/25688193/138546263-b03171d1-68cd-435d-88c5-6d04a09c4505.png" width="500"><br>

    ```js
    ```

1. `src/DeleteMemoForm.js` を作成する。<br>
    `DeleteMemoForm.js` では、メモの追加画面とそれに関連するイベント処理を行うコンポーネントを定義する。<br>
      <img src="https://user-images.githubusercontent.com/25688193/138546274-0e5989e7-2ce0-4a9b-8126-024bc74bc093.png" width="500"><br>

      ```js
      ```


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
