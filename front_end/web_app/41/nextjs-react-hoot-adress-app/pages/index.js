import 'bootstrap/dist/css/bootstrap.min.css'
import React from 'react';
import firebase from "firebase";
import Link from 'next/link'
import { useState } from 'react'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import Layout from '../components/layout';
import '../firebase/initFirebase'

// ログイン認証の初期化
const auth = firebase.auth()
const provider = new firebase.auth.GoogleAuthProvider();

// ルートページ
export default function Home() {
  // Firestore にアクセスするためのオブジェクト作成
  const db = firebase.firestore()

  // コレクション名
  const collectionName = 'adress-database'

  //------------------------
  // フック
  //------------------------
  // リダイレクトのための独自フック
  const router = useRouter()

  // ドキュメント表示用のステートフック
  const addressesJsx_ = []    // 一時変数
  const [addressesJsx, setAddressesJsx] = useState(addressesJsx_)

  // 読み込み待ち表示のステートフック
  const [message, setMessage] = useState('wait...')

  // コレクション名からコレクション内のデータを取得する副作用フック。
  // [データベース構造]
  // adress-database +- ドキュメントID(ログインユーザーのemailの値) +-- adress-database  + ドキュメントID(ユーザー１のemailの値) +-- name
  //                 |                                        |                    |                                  +-- email
  //                 |                                        |                    |                                  +-- message-database + ドキュメントID(自動割り振り) +-- comment  // メッセージデータベース
  //                 |                                        |                    |                                  |                                               +-- time
  //                 |                                        |                    + ドキュメントID(ユーザー２のemailの値) +-- name
  //                 |                                        |                    |                                  +-- email
  //                 |                                        |                    |                                  +-- message-database + ドキュメントID(自動割り振り) +-- comment
  //                 |                                        |                    |                                  |                                               +-- time
  //                 |-- ドキュメントID(ユーザー１のemailの値)     +-- adress-database  + ドキュメントID(ログインユーザーのemailの値) +- message-database + ドキュメントID(自動割り振り) +-- comment
  //                 |                                        |                    |                                       |                                              +-- time
  useEffect(() => {
    // ログイン済みに場合のみ表示
    if (auth.currentUser != undefined) {
      // db.collection(コレクション名) : コレクションにアクセスするためのオブジェクト取得
      // db.collection(コレクション名).doc(ドキュメントID) : 指定したドキュメントIDのドキュメント取得
      // db.collection(コレクション名).get() : コレクションにアクセスするためのオブジェクトからコレクションを取得。get() は非同期のメソッドで Promise を返す。そのため、非同期処理が完了した後 then() で非同期完了後の処理を定義する
      db.collection(collectionName).doc(auth.currentUser.email).collection(collectionName).get().then(
        // snapshot には、Firestore のコレクションに関連するデータやオブジェクトが入る
        (snapshot)=> {
          // snapshot.forEach((document)=> {..}) : snapshot から順にデータを取り出して処理を行う。無名関数の引数 document には、コレクション内の各ドキュメントが入る
          snapshot.forEach((document)=> {
            //console.log("document", document)
            // document.data() : ドキュメント内のフィールド
            const field = document.data()

            // フィールドの値を表形式のデータに変換して追加
            // ステート addressesJsx に直接 push すると、リストにデータが蓄積され続けるので、一旦一時変数 addressesJsx_ に push してから、setDocumentsJsx() でステートを更新する
            addressesJsx_.push(
              <li className="list-group-item list-group-item-action p-1" onClick={onClickList} id={document.id}>
                {field.name} ({field.email})
              </li>
            )
          })
          
          setAddressesJsx(addressesJsx_)
          setMessage("login user : " + auth.currentUser.displayName)
        }
      )
    }
    else {
      setMessage('Please login')
    }
  }, [message])

  //------------------------
  // イベントハンドラ
  //------------------------
  const onClickLogIn = ((e)=> {
    // auth.signInWithPopup(認証プロバイダー) : 
    // ポップアップ画面で認証を行う。このメソッドは Promise オブジェクトを返すので、then(...) で認証後の処理を定義する。
    // この時、result.user には以下の情報が入る
    // result.user.providerID : 利用している認証プロバイダーのID
    // result.user.uid : ユーザーID
    // result.user.displayName : ユーザーの表示名
    // result.user.email : ユーザーのEmail
    // result.user.phoneNumber : ユーザーの電話番号
    auth.signInWithPopup(provider).then(result=> {
      setMessage('logined: ' + result.user.displayName)
    }).catch((error) => {
      // ログイン失敗時の処理
      setMessage('not logined.')
    })
  })

  // リストクリック時のイベントハンドラ
  const onClickList = (e)=> {
    // e.target.id には、リストタグ <li id={document.id}></li> で指定した ID（今の場合ドキュメントID）が入る
    const documentId = e.target.id

    // パスパラメーターでドキュメントIDを渡し、/info ページにリダイレクトする
    router.push('/info?documentId=' + documentId)
  }

  // 
  const onClickAdd = (e)=> {
    // /add ページへ移動
    router.push('/add')
  }

  //------------------------
  // JSX での表示処理
  //------------------------
  // <ul> : unordered list（順序がないリスト）<ul><li>サンプルテキスト1</li><li>サンプルテキスト2</li></ul> の形式で使用する 
  return (
    <div className="container">
      <Layout header="AdressBook App" title="adress book">
        <div className="alert alert-primary text-center">
          <h5 className="mb-4">{message}</h5>
          {auth.currentUser == undefined ? <button onClick={onClickLogIn} className="btn btn-primary mx-3 mb-3">login</button> : ''}    {/* 未ログインの場合のみボタン表示 */}
          <ul className="list-group">{addressesJsx}</ul>
          {auth.currentUser != undefined ? <button className="btn btn-primary mt-3" onClick={onClickAdd}>Add address</button> : ''}     {/* ログイン中の場合のみボタン表示 */}
        </div>
      </Layout>
    </div>
  );
}

