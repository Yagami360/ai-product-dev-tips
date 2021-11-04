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
  ```js
  ```

  ポイントは、以下の通り

  - xxx

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
