# 【React】React Hooks のステートフックを使用して値の状態管理を行う

> Redux との比較の説明分追加

フックには、以下のような種類がある

- ステートフック<br>
  React における state（値を更新すると即座に画面に反映される変数）に対してのフック。<br>
  ステートフックは、以下の形式で定義する。ステートフックは、state と同じように、値が変化すると即座に画面表示に反映される。
  ```js
  import { useState } from 'react'

  // 変数 A : state の値
  // 変数 B : state の値を変更する関数
  const [変数A, 変数B] = useState(初期値) 
  ```

- 副作用フック<br>
  関数コンポーネント内のステートの値が更新されたときに、実行される関数のフック。
  副作用フックは、以下の形式で定義する。
  ```js
  import { useEffect } from 'react'

  // 関数名 : コンポーネント更新時に実行される関数を指定
  useEffect(関数名) 
  ```

- 独自フック<br>
  xxx

## ■ React Hooks のステートフックを使用して値の状態管理を行う（最もシンプルな構成）

### ◎ 方法

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

1. `src/App.js` を修正する
	```js
  import React, { useState } from 'react'
  import './App.css'

  function App() {
    // ステートフックの宣言
    // 第１戻り値 count には、state の値が入る。
    // 第２戻り値 setCount には、state の値を変更する関数が入る。
    // 引数には、state（今の場合 count）の初期値を設定
    const [countA, setCountA] = useState(0)

    // useState() メソッドを複数個使用すれば、複数のステートを作成することが出来る。
    const [countB, setCountB] = useState(0)

    // ボタンクリック時のイベントハンドラ
    // App コンポーネントは、関数コンポーネントなので、const 関数名 = () => {} で宣言する
    const clickFuncA = () => {
      // useState() で取得したstate の値を変更する関数 setCount() を呼び出す
      // 引数には、state の更新式を設定
      setCountA(countA + 1)
    }
    
    const clickFuncB = () => {
      // useState() で取得したstate の値を変更する関数 setCount() を呼び出す
      // 引数には、state の更新式を設定
      setCountB(countB + 1)
    }

    return (
      <div>
        <h1>React Hook Sample App</h1>
        <div>
          <p>clickA: {countA} times!</p>
          <p>clickB: {countB} times!</p>
          <div>
            <button onClick={clickFuncA}>ClickA</button>
            <button onClick={clickFuncB}>ClickB</button>
          </div>
        </div>
      </div>
    )
  }

  export default App
  ```

  ポイントは、以下の通り

  - Hook を使用する場合は、各コンポーネントをクラスコンポーネントではなく、関数コンポーネントで定義する必要がある

  - `useState()` メソッドで、ステートフックを宣言する。このとき、第１戻り値 `countA` には、state の値が入る。第２戻り値 `setCountA` には、state の値を変更する関数が入る。引数には、state（今の場合 count）の初期値を設定する

  - `useState()` メソッドで取得した第１戻り値（＝state の値）`countA` は、`App` コンポーネントの return 分（JSX形式）の中で `{countA}` とすることで、表示させることが出来る

  - `useState()` メソッドで取得した第２戻り値（=state の値を変更する関数）`setCountA` は、ボタンクリック時のイベントハンドラ `clickFuncA` 内で呼び出している。このとき `setCountA` の引数には、state の更新式を設定する

  - 尚、このイベントハンドラ `clickFuncA` は、`App` コンポーネントがクラスコンポーネントではなく関数コンポーネントなので、`const 関数名 = () => {}` の形式で定義している

  - `useState()` メソッドを複数個使用すれば、複数のステートを作成することが出来る。この例では、`countA` と `countB` が該当する

  - クラスコンポーネントでは、画面表示される値のみを state として定義するようしていた。**一方で、関数コンポーネントでは内部で宣言した変数の値が保持されない（＝関数スコープを抜けるとメモリが開放される）ので、関数コンポーネントを使用する Hook での状態管理では、例え画面表示に関連しない変数であっても、内部で値を保持したい変数に関しては、全て state で定義する必要があることに注意。**

  - Redux を使用した状態管理に比べて、非常にシンプルな構成になっていることに注目。

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


## ■ React Fook 使用時に関数コンポーネントに値を渡す

関数コンポーネントに値を渡すには、クラスコンポーネントのときと同じように `<コンポーネント名 args1="" args2="" ... />` の形式でタグ属性を指定して関数コンポーネントを呼び出し、呼び出された関数コンポーネント側でタグ属性の値を `props` 引数で取得すればよい

### ◎ 方法

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

1. `src/App.js` を修正する
	```js
  import React, { useState } from 'react'
  import './App.css';

  // 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
  function User(props) {
    return (
      <div>
        <p>id:{props.id}, name:{props.name}</p>
      </div>
    )
  }

  function App() {
    // ステートフックの宣言
    // 第１戻り値には、state の値が入る。
    // 第２戻り値には、state の値を変更する関数が入る。
    // 引数には、state の初期値を設定
    const [id, setId] = useState(1)
    const [name, setName] = useState("Yagami")

    // 名前入力ボタンクリック時のイベントハンドラ
    // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
    const onClickId = ()=>{
      let res = window.prompt('type your id')
      setId(res)
    }
    const onClickName = ()=>{
      let res = window.prompt('type your name')
      setName(res)
    }

    // 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
    // useState() メソッドで取得した第１戻り値（＝state の値）を、別の関数コンポーネントのタグ属性に指定して渡す
    return (
      <div className="App">
        <header className="App-header">
          <h1>React Hook Sample App1</h1>
          <User id={id} name={name} />
          <button onClick={onClickId} className="btn btn-primary">input your id</button>
          <button onClick={onClickName} className="btn btn-primary">input your name</button>
        </header>
      </div>
    );
  }

  export default App;
  ```

  ポイントは、以下の通り

  - アプリ全体の表示を行う関数コンポーネント `App` 内で、別の関数コンポーネント `User` を呼び出している

  - 関数コンポーネントでも（クラスコンポーネントのときと同じように）、`<コンポーネント名 args1="" args2="" ... />` の形式でタグ属性を指定して関数コンポーネントを呼び出すことができる。そして、呼び出された関数コンポーネント側では、タグ属性の値を props 引数で取得出来る。（本項目の主題）

  - この例では、関数コンポーネント `App` 内で、`useState()` を使用して `id`, `name` を state として定義し、この state を別の関数コンポーネント `User` のタグ属性の値に `{id}`, `{name}` の形式で設定している。そして関数コンポーネント `User` 内では、設定されたタグ属性を元に `{prob.id}`, `{prob.name}` の形式で表示を行っている。<br>
    これにより、関数コンポーネント `App` 内で、`useState()` で定義した state `id`, `name` の値が変化すると、即座に関数コンポーネント `User` の表示も変化するようになる。実際に、ボタンクリック時のイベントハンドラ `onClickId()`, `onClickName()` を呼び出して、関数コンポーネント `App` 内で state `id`, `name` の値を変化させると、関数コンポーネント `User` の表示も即座に変化する挙動になっている

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


## ■ React Fook 使用時に子関数コンポーネントから親関数コンポーネントに値を渡す

関数コンポーネント（＝親関数コンポーネント）内で呼び出した別の関数コンポーネント（＝子関数コンポーネント）から、親関数コンポーネントに値を渡すには、`useState()` の第２戻り値で取得した state の値設定用関数をタグ属性で子関数コンポーネントに渡して、子関数コンポーネント内でこの関数を用いて state の値を更新すればよい

### ◎ 方法

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

1. `src/App.js` を修正する
	```js
  import React, { useState } from 'react'
  import './App.css';

  // 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
  function User(props) {
    // 名前入力ボタンクリック時のイベントハンドラ
    // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
    // 関数コンポーネントのタグ属性で指定された state の値を変更する関数に対して props.関数名() の形式でアクセスすることで、親関数コンポーネントで定義した state の値を更新する。
    // これにより、子コンポーネントから親関数コンポーネントに値を渡すことが出来る
    const onClickId = ()=>{
      let res = window.prompt('type your id')
      props.setId(res)
    }
    const onClickName = ()=>{
      let res = window.prompt('type your name')
      props.setName(res)
    }

    return (
      <div>
        <p>id:{props.id}, name:{props.name}</p>
        <button onClick={onClickId} className="btn btn-primary">input your id</button>
        <button onClick={onClickName} className="btn btn-primary">input your name</button>
      </div>
    )
  }

  function App() {
    // ステートフックの宣言
    // 第１戻り値には、state の値が入る。
    // 第２戻り値には、state の値を変更する関数が入る。
    // 引数には、state の初期値を設定
    const [id, setId] = useState(1)
    const [name, setName] = useState("Yagami")

    // 関数コンポーネントでも（クラスコンポーネントのときと同じように）<コンポーネント名 args1="" args2="" ... /> の形式ででタグ属性を指定出来る
    // useState() メソッドで取得した第２戻り値（＝state の値を変更する関数）を、別の関数コンポーネントのタグ属性に指定して渡す
    return (
      <div className="App">
        <header className="App-header">
          <h1>React Hook Sample App1</h1>
          <User id={id} name={name} setId={setId} setName={setName} />
        </header>
      </div>
    );
  }

  export default App;
  ```

  ポイントは、以下の通り

  - `useState()` メソッドで取得した第２戻り値（＝state の値を変更する関数）`setId`, `setName` を、子関数コンポーネント `User` のタグ属性に指定して渡している。<br>
    そして子関数コンポーネント側では、ボタンクリック時のイベントハンドラ `onClickId()`, `onClickName()` 内で、`props.setId()`, `props.setName()` の形式でこの関数にアクセスすることで、親関数コンポーネントで定義した state の値を更新している。これにより、子コンポーネントから親関数コンポーネントに値を渡すことが出来ている。

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


## ■ React Fook 使用時の関数コンポーネントでのフォームの使用

関数コンポーネントでは、フォームに入力された値が関数スコープ内の変数になるので、関数コンポーネント呼び出し後に消えてしまう。そのため React Hook での関数コンポーネントでは、フォームに入力された値を全て state で管理する必要がある

### ◎ 方法

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

1. `src/App.js` を修正する
	```js
  import React, { useState } from 'react'
  import './App.css';

  // 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
  function User(props) {
    const id_style = {
      fontSize:"14pt",
      backgroundColor:"blue",
      color:"white",
      padding:"5px 10px",
      width:"50px"
    }
    const name_style = {
      fontSize:"14pt",
      backgroundColor:"white",
      color:"darkblue",
      padding:"5px 10px",
      border:"1px solid lightblue",
      minWidth:"300px"
    }

    // <tr> タグ（テーブルの行）・<th> タグ（テーブルの見出し）・<td> タグ（テーブルのセル
    return (
      <tr>
        <td style={id_style}>{props.id}</td>
        <td style={name_style}>{props.name}</td>
      </tr>
    )
  }

  function App() {
    // ステートフックの宣言
    // 第１戻り値には、state の値が入る。
    // 第２戻り値には、state の値を変更する関数が入る。
    // 引数には、state の初期値を設定
    const [id, setId] = useState(1)
    const [name, setName] = useState("Yagami")
    const [form, setForm] = useState({id:'-1', name:'no name'})

    // フォーム入力ボタンクリック時のイベントハンドラ
    // 関数コンポーネント内なので、const 関数名 = (event) => {} の形式でイベントハンドラを定義する
    const doSubmit = (event) => {
      setForm({id:id, name:name})
      event.preventDefault()
    }
    
    // 入力フォーム更新時のイベントハンドラ
    const doChangeId = (event) => {
      setId(event.target.value)
    }
    const doChangeName = (event) => {
      setName(event.target.value)
    }

    // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
    // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
    // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
    // 子関数コンポーネント User のタグ属性には、form の state `form["id"]`, `form["name"]` を渡す（）
    return (
      <div className="App">
        <header className="App-header">
          <h1>React Hook Sample App3</h1>
          <form onSubmit={doSubmit}>
            <div className="form-group">          
              <label>id:</label>
              <input type="number" className="form-control" onChange={doChangeId} />
              <label>name:</label>
              <input type="text" className="form-control" onChange={doChangeName} />
              <input type="submit" className="btn btn-primary" value="change user" />
            </div>
          </form>
          <p></p>
          <tabel><tbody>
            <th>id</th>
            <th>name</th>
            <User id={form["id"]} name={form["name"]} />
          </tbody></tabel>
        </header>
      </div>
    );
  }

  export default App;

  ```

  ポイントは、以下の通り

  - `const [form, setForm] = useState({id:'-1', name:'no name'})` の部分で、フォームの値を state で管理している

 - ボタンクリック時のイベントハンドラ `doSubmit()` 内の `setForm()` にて、フォームの内容を `form` ステートに保存するようにして、このフォームのステート `form` を、子関数コンポーネントのタグ属性に、`<User id={form["id"]} name={form["name"]} />` の形式で設定することで、ボタン時クリックに表示が変化するようにしている

   > `<User id={id} name={name} />` のようにして、id と name のステートをそのまま渡すと、入力フォーム更新時に（送信ボタンクリックしてなくとも）画面の表示が変化してしまうことに注意

  - フォームに入力されるデータ `id`, `name`, `form={id:'xxx', name:'xxx'}` を全て state で管理している点に注意

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
