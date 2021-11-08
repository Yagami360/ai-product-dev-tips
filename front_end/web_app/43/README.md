# 【React】Next.js + React Hooks アプリで Firestore Database の基本的なデータベース操作を行う

## ■ 方法

1. npm をインストール
    - MacOS の場合
        ```sh
        # Node.jsをインストール
        $ brew install node
        ```
    > npm : Node.js のパッケージを管理するコマンド

1. Next.js プロジェクトのディレクトリを作成する<br>
    ```sh
    $ mkdir -p ${PROJECT_NAME}
    ```

1. `package.json` を作成する<br>
  Next.js プロジェクトのディレクトリ以下に、以下のような `package.json` を作成する

    ```json
    {
      "scripts": {
        "dev": "next",
        "build": "next build",
        "start": "next start",
        "export": "next export"
      }
    }
    ```

1. next.js, react, react-dom をインストールする
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm install --save next
    $ npm install --save react
    $ npm install --save react-dom
    ```

1. firebase API をインストールする<br>
		```sh
		$ cd ${PROJECT_NAME}
		$ npm install --save firebase@8.10.0
		```

	> バージョン指定なしの `npm install --save firebase` でインストールすると、現時点（21/10/31）では version 9.x の Firebase がインストールされるが、version8 -> version9 へ変更した場合は、firebase の import 方法が、`import firebase from 'firebase/app';` -> `import { initializeApp } from 'firebase/app';` に変更されたりしており、version8 の Firebase コードが動かなくなることに注意

1. Firebase プロジェクトの作成<br>
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
    1. 「プロジェクトを作成」
    1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
        <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>

1. <a id="ウェブアプリをFirebaseに登録する"></a>ウェブアプリを Firebase に登録する<br>
    1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
        <img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>
    1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。このとき、以下の画面のコードをコピーしておく。<br>
        <img src="https://user-images.githubusercontent.com/25688193/138590270-3304ca03-787d-43d2-8c81-e6f65e754b6e.png" width="300"><br>

        ```js
        // Import the functions you need from the SDKs you need
        import { initializeApp } from "firebase/app";
        import { getAnalytics } from "firebase/analytics";
        // TODO: Add SDKs for Firebase products that you want to use
        // https://firebase.google.com/docs/web/setup#available-libraries

        // Your web app's Firebase configuration
        // For Firebase JS SDK v7.20.0 and later, measurementId is optional
        const firebaseConfig = {
          apiKey: " APIキー ",
          authDomain: "プロジェクト.firebaseapp.com",
          databaseURL: "https://プロジェクト.firebaseio.com",
          projectId: "プロジェクト",
          storageBucket: "プロジェクト.appspot.com",
          messagingSenderId: " ID番号 "
          appId: "appid",
          measurementId: "measurementId"
        };

        // Initialize Firebase
        const app = initializeApp(firebaseConfig);
        const analytics = getAnalytics(app);
        ```

1. Firestore Database を有効化する。<br>
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1) の左側画面の「Firestore Database」→「データベースの作成」ボタンをクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601915-46e91203-5664-4d14-9751-8c815dcf66da.png" width="500"><br>
    1. セキュリティモードの選択画面で、「テストモードで開始」を選択し、「次へ」をクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601923-c575d907-a8db-4aab-8f99-66f0da393901.png" width="400"><br>
        - 「ロックモードで開始」：特定のアプリケーションでのみ利用可能<br>
        - 「テストモードで開始」：公開モードでどこからでも自由にアクセスできる<br>
    1. セキュリティモードの選択画面で、「テストモードで開始」を選択し、「次へ」をクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601923-c575d907-a8db-4aab-8f99-66f0da393901.png" width="400"><br>
    1. 「有効」をクリックする<br>
        <img src="https://user-images.githubusercontent.com/25688193/140601942-874ab099-78ef-450e-b390-9da1763b9e55.png" width="400"><br>

1. Firebase プロジェクトの初期化<br>
    1. Firebase CLI をインストールする<br>
        ```sh
        $ cd ${PROJECT_NAME}
        $ sudo npm install -g firebase-tools
        ```
    1. Firebase プロジェクトにログインする<br>
        ```sh
        $ firebase login --project ${PROJECT_ID}
        ```
        - `${PROJECT_ID}` : Firebase プロジェクトのプロジェクトID。作成した Firebase プロジェクトのコンソール画面の「プロジェクトの設定」から確認可能

    1. Firebase プロジェクトを初期化する<br>
        ```sh
        $ firebase init --project ${PROJECT_ID}
        ```
        <img src="https://user-images.githubusercontent.com/25688193/138589325-28e234a6-2c99-4bff-8bc4-34ec47ec5545.png" width="500"><br>

        > "Realtime Database: Configure a security rules file for Realtime Database and (optionally) provision default instance" を選択しスペースキーを押して、Realtime Database の機能を有効化する。

1. `firebase/initFirebase.js` を作成する
    FireBase の初期化処理を行う `initFirebase.js` を作成する

    ```js
    import firebase from "firebase";

    // Firebaseの初期化
    const firebaseConfig = {
      apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
      authDomain: "react-firebase-app-2cc53.firebaseapp.com",
      databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
      projectId: "react-firebase-app-2cc53",
      storageBucket: "react-firebase-app-2cc53.appspot.com",
      messagingSenderId: "686383733508",
      appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
      measurementId: "G-MCWN891SRK"   
    };

    if (firebase.apps.length == 0) {
      firebase.initializeApp(firebaseConfig);
    }
    ```

    ポイントは、以下の通り

	  - `firebase.initializeApp()` で firebase の初期化を行っている。このときの config 引数には、先の「[ウェブアプリをFirebaseに登録する](#ウェブアプリをFirebaseに登録する)」の処理時にコピーしていた値を設定すればよい。そして 一旦 firebase の初期化処理を行えば、どのコンポーネントからも firebase を利用することが出来るようになる。

		  > このコンフィ値には、API キーの情報が含まれており、GitHub に公開することでセキュリティ上のリスクがあるように思えるが、公開前提の値であり隠すようなものではないらしい。<br>
			> 詳細は、https://qiita.com/hoshymo/items/e9c14ed157200b36eaa5 などを参照のこと

  	- Firebase API を version8 -> version9 に変更した場合は、Firebase の処理化部分のコードは以下のようなコードになることに注意<br>
      ```js
      import { initializeApp } from 'firebase/app';     // for version 9.x

      // Firebaseの初期化
      var firebaseConfig = {
          apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
          authDomain: "react-firebase-app-2cc53.firebaseapp.com",
          databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
          projectId: "react-firebase-app-2cc53",
          storageBucket: "react-firebase-app-2cc53.appspot.com",
          messagingSenderId: "686383733508",
          appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
          measurementId: "G-MCWN891SRK"   
      };
      initializeApp(firebaseConfig);                    // for version 9.x
      ```
    
	  - `pages/index.js` 内で Firebase の初期化処理を行うと、他のページのコンポーネント（今回の場合は `pages/show.js` など）で Firebase が使えなくなるので、別の独立したファイルで初期化を行い、Firebase を使用する各ページのコンポーネントで、このファイルを import するようにする。

1. `pages/index.js` を作成する
    ルートページである `index.js` を作成する

    ```js
    import React from 'react';
    import firebase from "firebase";
    import Link from 'next/link'
    import '../firebase/initFirebase'

    // ルートページ
    export default function Home() {
      // スタイル定義
      const indexStyle = {
        fontSize:"14pt",
        backgroundColor:"blue",
        color:"white",
        padding:"5px 10px",
        width:"50px"
      }
      const nameStyle = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        minWidth:"300px"
      }

      return (
        <div className="App">
          <h1>Next.js & Firebase Sample App</h1>
          <table>
            <th style={indexStyle}>No</th>
            <th style={nameStyle}>操作一覧</th>
            <tbody>
              <tr>
                <td style={indexStyle}>1</td>
                <td style={nameStyle}><Link href="/show"><a>Firestore を表示する</a></Link></td> 
              </tr>
              <tr>
                <td style={indexStyle}>2</td>
                <td style={nameStyle}><Link href="/add"><a>Firestore を追加する</a></Link></td>
              </tr>
              <tr>
                <td style={indexStyle}>3</td>
                <td style={nameStyle}><Link href="/delete"><a>Firestore を削除する</a></Link></td>
              </tr>
            </tbody>
          </table>      
        </div>
      );
    }
    ```

    ポイントは、以下の通り

	  - `import Link from 'next/link'` で `Link` コンポーネントを import し、`<Link href="/show"><a>Firestore を表示する</a></Link>` とすることで、クリック時のページ移動を行うようにしている

1. `pages/show.js` を作成する
    Firestore のデータセットの表示ページのコンポーネントである `show.js` を作成する

    ```js
    import React from 'react';
    import { useState } from 'react'
    import { useEffect } from 'react'
    import { useRouter } from 'next/router'
    import firebase from "firebase";
    import '../firebase/initFirebase'

    // Firestore からデータを取り出し、それらを画面表示するコンポーネント
    export default function ShowFirestore() {
      // Firestore にアクセスするためのオブジェクト作成
      const db = firebase.firestore()

      //------------------------
      // スタイル定義
      //------------------------
      const indexStyle = {
        fontSize:"14pt",
        backgroundColor:"blue",
        color:"white",
        padding:"5px 10px",
        width:"50px"
      }
      const nameStyle = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        minWidth:"300px"
      }

      //------------------------
      // フック
      //------------------------
      // コレクション名入力フォームのステートフック
      const [collectionName, setCollectionName] = useState('sample-database')

      // ドキュメント表示用のステートフック
      const documentsJsx_ = []    // 一時変数
      const [documentsJsx, setDocumentsJsx] = useState(documentsJsx_)

      // 読み込み待ち表示のステートフック
      const [message, setMessage] = useState('wait...')

      // コレクション名からコレクション内のデータを取得する副作用フック。コレクション名が更新されると再実行される
      useEffect(() => {
        // db.collection(コレクション名) : コレクションにアクセスするためのオブジェクト取得
        // db.collection(コレクション名).get() : コレクションにアクセスするためのオブジェクトからコレクションを取得。get() は非同期のメソッドで Promise を返す。そのため、非同期処理が完了した後 then() で非同期完了後の処理を定義する
        db.collection(collectionName).get().then(
          // snapshot には、Firestore のコレクションに関連するデータやオブジェクトが入る
          (snapshot)=> {
            // snapshot.forEach((document)=> {..}) : snapshot から順にデータを取り出して処理を行う。無名関数の引数 document には、コレクション内の各ドキュメントが入る
            snapshot.forEach((document)=> {
              // document.data() : ドキュメント内のフィールド
              const field = document.data()

              // フィールドの値を表形式のデータに変換して追加
              // ステート documentsJsx に直接 push すると、リストにデータが蓄積され続けるので、一旦一時変数 documentsJsx_ に push してから、setDocumentsJsx() でステートを更新する
              documentsJsx_.push(
                <tr key={document.id}>
                  <td style={indexStyle}>{field.id}</td>
                  <td style={nameStyle}>{field.name}</td>
                </tr>
              )
            })
            
            setDocumentsJsx(documentsJsx_)
            setMessage('documents')
          }
        )
      }, [collectionName])

      //------------------------
      // イベントハンドラ
      //------------------------
      // テキスト入力フォーム更新時のイベントハンドラ。このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
      // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
      const updateInputText = (e)=>{
        // e.target.value に入力テキストが入る
        setCollectionName(e.target.value)
      }

      //------------------------
      // JSX での表示処理
      //------------------------
      return (
        <div>
          <form>
            <p>Please type your firestore collection name</p>
            collection name : <input type="text" size="40" onChange={updateInputText} value={collectionName} />
          </form>
          <p>{message}</p>
          <table>
            <th style={indexStyle}>id</th>
            <th style={nameStyle}>name</th>
            <tbody>{documentsJsx}</tbody>
          </table>
        </div>
      );
    }
    ```

    ポイントは、以下の通り

    - Firestore からデータベースを取得する一連の処理の大まかな処理は、以下のようになる。
      1. `let db = firebase.database();` で、Firestore にアクセスするためのオブジェクト作成する。
      1. `db.collection(props.collectionName)` で、コレクションにアクセスするためのオブジェクト取得する
      1. `db.collection(props.collectionName).get()` で、コレクションにアクセスするためのオブジェクトからコレクションを取得する。この `get()` は非同期のメソッドで Promise を返す。そのため、非同期処理が完了した後 `db.collection(props.collectionName).get().then(...)` の `then(...)` 内で非同期完了後の処理を定義する
          > Promise : JavaScriptにおいて、非同期処理の操作が完了したときに結果を返すもの
          > https://techplay.jp/column/581
      1. `then((snapshot)=>{...})` 内の無名関数の引数 `snapshot` には、Firestore のコレクションに関連するデータやオブジェクトが入る
      1. `snapshot.forEach((document)=> {..})` で `snapshot` から順にデータを取り出して処理を行う。無名関数の引数 `document` には、コレクション内の各ドキュメントが入る
      1. `document.data()` で、ドキュメント内のフィールドを取得する


    - Firestore には契約内容によってアクセス可能数決まっているが、Firestore からデータベースを取得する `db.collection(props.collectionName).get().then((snapshot)=> {..})` の部分（＝関数）を `useEffect(関数名)` を使って副作用フックにすることで、特定のステート更新時のみ副作用フック内の処理を行うようにすることが出来るので、データベースにアクセスされすぎるのを防止することが出来る。今の場合、`useEffect(関数名, [ステート１，ステート２])` の第２引数の部分を `[collectionName]` で定義しているので、この副作用フックは、初回アクセス時と入力フォームに入力されたコレクション名が更新されたときのみ呼び出される。

    - HTML タグ内の key 属性について<br>
      `<tr key={i}>` の部分指定している key 属性は、HTMLでもともと定義されているタグ属性ではなく、React の機能であり、React が仮想DOM を更新する際に更新対象を識別するための一意の値になっている。<br>
      key を設定しない場合は、データベースの内容が変わらなくても表示させる順が変化するするだけで、仮想DOMを再構成する必要がありパフォーマンスが低下する。一方、key を設定しない場合は、データベースの順番が変化しても、中身の値が変わらなければ、仮想DOMを再構成する必要がないのでパフォーマンスが向上するメリットがある。<br>
      詳細は、以下のサイトを参考のこと<br>
      - https://watablogtravel.com/react-key-props/

	  - ステート `documentsJsx` は、リスト型のステートであるが、このリスト型のステートに直接 `push()` でデータを追加すると、副作用フックが呼びだれる度にリストの要素が増え続けてしまう。そのため、この副作用フック外では空リストになる一時的なリスト変数 `documentsJsx_` に一旦 push してから、この一時変数 `documentsJsx_` で `setDocumentsJsx` でステートを更新するようにしている

1. `pages/add.js` を作成する
    Firestore のデータセットの追加ページのコンポーネントである `add.js` を作成する

    ```js
    import React from 'react';
    import { useState } from 'react'
    import { useEffect } from 'react'
    import { useRouter } from 'next/router'
    import firebase from "firebase";
    import '../firebase/initFirebase'

    // Firestore に追加し、それらを画面表示するコンポーネント
    export default function AddFirestore() {
      // Firestore にアクセスするためのオブジェクト作成
      const db = firebase.firestore()

      //------------------------
      // スタイル定義
      //------------------------
      const indexStyle = {
        fontSize:"14pt",
        backgroundColor:"blue",
        color:"white",
        padding:"5px 10px",
        width:"50px"
      }
      const nameStyle = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        minWidth:"300px"
      }

      //------------------------
      // フック
      //------------------------
      // 入力フォームのステートフック
      const [collectionName, setCollectionName] = useState('sample-database')
      const [id, setId] = useState(0)
      const [name, setName] = useState(0)

      // リダイレクト（ユーザー操作ではないプログラム側での別ページへの移動）のための独自フック
      const router = useRouter()

      //------------------------
      // イベントハンドラ
      //------------------------
      // テキスト入力フォーム更新時のイベントハンドラ。このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
      // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
      const updateInputText = (e)=>{
        // e.target.value に入力テキストが入る
        setCollectionName(e.target.value)
      }

      const onChangeId = ((e)=> {
        setId(e.target.value)
      })

      const onChangeName = ((e)=> {
        setName(e.target.value)
      })

      // Add ボタンクリック時のイベントハンドラ
      const onClickAdd = ((e)=> {
        // 新規に追加するドキュメントデータ
        const document = {
          id:id,      // 入力フォームの値を追加
          name:name,  // 入力フォームの値を追加
        }

        // db.collection(コレクション名).add(ドキュメントデータ) で、コレクションに新たなドキュメントを追加する
        // この時ドキュメントIDは自動的に割り振られる
        // 新規にコレクションを追加する場合も、このメソッドで作成できる
        db.collection(collectionName).add(document).then(ref=> {
          // 別ページにリダイレクト
          //router.push('/show')
          router.push('/show?collectionName=' + collectionName)      
        })
      })

      //------------------------
      // JSX での表示処理
      //------------------------
      return (
        <div>
            <p>Please type your add data and click "Add" bottom</p>
          <form>
          <label>collection name : </label><input type="text" size="40" onChange={updateInputText} value={collectionName} />
          </form>
          <div className="text-left">
            <div className="form-group">
              <label>id : </label>
              <input type="text" onChange={onChangeId} className="form-control" />
            </div>
            <div className="form-group">
              <label>name : </label>
              <input type="text" onChange={onChangeName} className="form-control" />
            </div>
          </div>
        <button onClick={onClickAdd} className="btn btn-primary">Add</button>
        </div>
      );
    }

    ```

    ポイントは、以下の通り

	  - `db.collection(コレクション名).add(ドキュメントデータ)` で、コレクションに新たなドキュメントを追加する（※ この時ドキュメントIDは自動的に割り振られることに注意）。
      この `add()` は Promise を返すので、`then(()=>{...})` で、非同期処理完了後の処理を定義する。ここでは、リダイレクト（＝別ページへの移動）を行う独自フック `const router = useRouter()` の `router.push()` メソッドを使用して、`show.js` で定義した別ページにリダイレクトするようにしている


1. `pages/delete.js` を作成する
    Firestore のデータセットの削除ページのコンポーネントである `delete.js` を作成する

    ```js
    import React from 'react';
    import { useState } from 'react'
    import { useEffect } from 'react'
    import { useRouter } from 'next/router'
    import firebase from "firebase";
    import '../firebase/initFirebase'

    // Firestore に追加し、それらを画面表示するコンポーネント
    export default function DeleteFirestore() {
      // Firestore にアクセスするためのオブジェクト作成
      const db = firebase.firestore()

      //------------------------
      // スタイル定義
      //------------------------
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
      const indexStyle = {
        fontSize:"14pt",
        backgroundColor:"blue",
        color:"white",
        padding:"5px 10px",
        width:"50px"
      }
      const nameStyle = {
        fontSize:"14pt",
        backgroundColor:"white",
        color:"darkblue",
        padding:"5px 10px",
        border:"1px solid lightblue",
        minWidth:"300px"
      }
      
      //------------------------
      // フック
      //------------------------
      // 入力フォームのステートフック
      const [collectionName, setCollectionName] = useState('sample-database')

      // 選択ボックスのステートフック
      const [selectIndex, setSelectIndex] = useState(0)

      // リダイレクト（ユーザー操作ではないプログラム側での別ページへの移動）のための独自フック
      const router = useRouter()

      // ドキュメントID表示用のステートフック
      const documentIds_ = []
      const documentIdsJsx_ = []
      const [documentIds, setDocumentIds] = useState(documentIds_)
      const [documentIdsJsx, setDocumentIdsJsx] = useState(documentIdsJsx_)

      // ドキュメントデータ表示用のステート
      const documentsJsx_ = []
      const [documentsJsx, setDocumentsJsx] = useState(documentsJsx_)
      
      // 読み込み待ち表示のステートフック
      const [showMessage, setShowMessage] = useState('wait...')

      // コレクション名からドキュメントIDを取得する副作用フック。コレクション名が更新されたときに再実行される
      useEffect(() => {
        db.collection(collectionName).get().then((snapshot)=> {
          snapshot.forEach((document)=> {
            // リストの末端にデータ追加
            documentIds_.push(document.id)
            setDocumentIds(documentIds_)
          })
          documentIdsJsx_ = documentIds_.map((data,index)=>(<option key={index} value={index++}>{data.substring(0,20)}</option>));
          setDocumentIdsJsx(documentIdsJsx_)
        });
      }, [collectionName])

      // コレクション名からコレクション内のデータを取得する副作用フック。コレクション名か選択ボックスが更新されると再実行される
      useEffect(() => {
        // db.collection(コレクション名) : コレクションにアクセスするためのオブジェクト取得
        // db.collection(コレクション名).get() : コレクションにアクセスするためのオブジェクトからコレクションを取得。get() は非同期のメソッドで Promise を返す。そのため、非同期処理が完了した後 then() で非同期完了後の処理を定義する
        db.collection(collectionName).get().then(
          // snapshot には、Firestore のコレクションに関連するデータやオブジェクトが入る
          (snapshot)=> {
            // snapshot.forEach((document)=> {..}) : snapshot から順にデータを取り出して処理を行う。無名関数の引数 document には、コレクション内の各ドキュメントが入る
            snapshot.forEach((document)=> {          
              // 選択ボックスで選択したドキュメントID と一致する場合
              if( document.id == documentIds[selectIndex] ) {
                // document.data() : ドキュメント内のフィールド
                const field = document.data()

                // フィールドの値を表形式のデータに変換して追加
                documentsJsx_.push(
                  <tr key={document.id}>
                    <td style={indexStyle}>{field.id}</td>
                    <td style={nameStyle}>{field.name}</td>
                  </tr>
                )
              }
            })
            
            setDocumentsJsx(documentsJsx_)
            setShowMessage('fields')
          }
        )
      }, [collectionName, selectIndex])

      //------------------------
      // イベントハンドラ
      //------------------------
      // テキスト入力フォーム更新時のイベントハンドラ。このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
      // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
      const updateInputText = (e)=>{
        // e.target.value に入力テキストが入る
        setCollectionName(e.target.value)
      }

      // 選択ボックス更新時のイベントハンドラ
      // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
      const updateSelect = (e)=>{
        // e.target.value に選択ボックスの番号が入る
        setSelectIndex(e.target.value)
      }

      // Delete ボタンクリック時のイベントハンドラ
      const onSubmitDelete = ((e)=> {
        // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
        e.preventDefault();    // その処理を入れると、Delete ボタンクリック直後に（画面をリロードするまでは）メモの削除が行われなくなるのことに注意

        // db.collection(コレクション名).doc(ドキュメントID).delete() で、ドキュメントを削除する
        db.collection(collectionName).doc(documentIds[selectIndex]).delete().then(ref=> {
          // ページ再読み込み（e.preventDefault() を追加したため）
          location.reload()

          // 別ページにリダイレクト
          //router.push('/show')
        })
      })

      //------------------------
      // JSX での表示処理
      //------------------------
      return (
        <div>
            <p>Please type your delete data and click "Delete" bottom</p>
          <form>
            collection name : <input type="text" size="40" onChange={updateInputText} value={collectionName} />
          </form>
          <form onSubmit={onSubmitDelete}>
            <label>document id : </label>
            <select onChange={updateSelect} defaultValue="-1" style={selectStyle}>
              {documentIdsJsx}
            </select>
            <input type="submit" style={btnStyle} value="Delete"/>
          </form>
          <p>{showMessage}</p>
          <table>
            <th style={indexStyle}>id</th>
            <th style={nameStyle}>name</th>
            <tbody>{documentsJsx}</tbody>
          </table>
        </div>
      );
    }

    ```

    ポイントは、以下の通り

	  - `db.collection(コレクション名).doc(ドキュメントID).delete()` で、コレクションの中のドキュメントを削除する。この `delete()` は Promise を返すので、`then(()=>{...})` で、非同期処理完了後の処理を定義する。

	  - ステート `documentIds`, `documentIdsJsx`, `documentsJsx` は、それぞれリスト型のステートであるが、このリスト型のステートに直接 `push()` でデータを追加すると、副作用フックが呼びだれる度にリストの要素が増え続けてしまう。そのため、この副作用フック外では空リストになる一時的なリスト変数 `documentIds_`, `documentIdsJsx_`, `documentsJsx_` に一旦 push してから、この一時変数で `setステート名()` でステートを更新するようにしている


1. 【オプション】プロジェクトをビルドする<br>
	1. Next.js の設定ファイル `next.config.js` を作成する<br>
			アプリの公開時に、外部公開される静的な HTML ファイルを生成するために、 Next.js の設定ファイル `next.config.js` を作成する
			```js
			module.exports = {
				exportPathMap: function () {
					return {
						'/': { page: '/' }
					}
				}
			}
			```

	1. プロジェクトをビルドする
		```sh
		$ npm run build
		```

	1. プロジェクトをエクスポートする
			```sh
			$ npm run export
			```

			> ビルドしてエクスポートされたプロジェクトは `${PROJECT_NAME}/out` ディレクトリに作成される。この out ディレクトリのファイルを全部アップロードすることで、アプリケーションを公開できる。

	1. 【オプション】出力された静的な Web ファイル　`out/index.html` を確認する

		> 出力された静的な Web ファイル　`index.html` では、`index.js` の JSX の内容で書き換わっていることに注目。
		
		> サーバーから送られる静的な Web ファイル　`index.html` に表示内容が生成されてウェブブラウザに送られた後に、ウェブブラウザで表示内容をレンダリングする形式になっているので、サーバーサイドレンダリングできるようになっている

1. 作成した React のプロジェクトのサーバーを起動する
    ```sh
    $ cd ${PROJECT_NAME}
    $ npm run dev
    ```

    コマンド実行後、作成した React アプリの Web サイト（デフォルトでは http://localhost:3000）が自動的に開く
