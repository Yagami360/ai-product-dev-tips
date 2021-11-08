import React from 'react';
import firebase from "firebase";
import Link from 'next/link'
import { useState } from 'react'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import '../firebase/initFirebase'

// ルートページ
export default function Home() {
  // Firestore にアクセスするためのオブジェクト作成
  const db = firebase.firestore()

  // コレクション名
  const collectionName = 'adress-database'

  // スタイル定義
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
  // リダイレクトのための独自フック
  const router = useRouter()

  // ドキュメント表示用のステートフック
  const addressesJsx_ = []    // 一時変数
  const [addressesJsx, setAddressesJsx] = useState(addressesJsx_)

  // 読み込み待ち表示のステートフック
  const [message, setMessage] = useState('wait...')

  // コレクション名からコレクション内のデータを取得する副作用フック。
  useEffect(() => {
    // db.collection(コレクション名) : コレクションにアクセスするためのオブジェクト取得
    // db.collection(コレクション名).get() : コレクションにアクセスするためのオブジェクトからコレクションを取得。get() は非同期のメソッドで Promise を返す。そのため、非同期処理が完了した後 then() で非同期完了後の処理を定義する
    db.collection(collectionName).get().then(
      // snapshot には、Firestore のコレクションに関連するデータやオブジェクトが入る
      (snapshot)=> {
        //console.log("snapshot", snapshot)
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
        setMessage('documents')
      }
    )
  }, [message])

  //------------------------
  // イベントハンドラ
  //------------------------
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
    <div className="App">
      <h1>AdressBook App</h1>
      <ul>{addressesJsx}</ul>
      <button className="btn btn-primary" onClick={onClickAdd}>Add address</button>
    </div>
  );
}
