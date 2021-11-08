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

  /*
  // リダイレクトのための独自フック。遷移元ページからクエリパラメータを取得するために使用
  const router = useRouter()

  // Add ページからリダイレクト時は、クエリパラメータに設定されたコレクション名で初期化
  // 但し、ページ遷移直後は router.query.collectionName = undefined になることに注意
  if( router.query.collectionName != undefined ){
    setCollectionName(router.query.collectionName)
  }
  */

  // コレクション名からコレクション内のデータを取得する副作用フック。コレクション名が更新されると再実行される
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
