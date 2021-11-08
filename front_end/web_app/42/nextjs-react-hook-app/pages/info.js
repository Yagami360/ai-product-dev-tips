import React from 'react';
import { useState } from 'react'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import firebase from "firebase";
import '../firebase/initFirebase'

// アドレスの詳細画面ページのコンポーネント
export default function AdressInfo() {
  // Firestore にアクセスするためのオブジェクト作成
  const db = firebase.firestore()

  // コレクション名
  const collectionName = 'adress-database'
  const documentId = '1'
  
  //------------------------
  // スタイル定義
  //------------------------
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
  // ドキュメント表示用のステートフック
  const documentsJsx_ = []    // 一時変数
  const [documentsJsx, setDocumentsJsx] = useState(documentsJsx_)

  // 読み込み待ち表示のステートフック
  const [message, setMessage] = useState('wait...')

  // リダイレクトのための独自フック。遷移元ページからクエリパラメータを取得するために使用
  const router = useRouter()

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
          // ページ遷移直後は router.query.documentId = undefined になることに注意
          if( router.query.documentId != undefined ){
            documentId = router.query.documentId

            if( document.id == documentId ){
              // document.data() : ドキュメント内のフィールド
              const field = document.data()

              // フィールドの値を表形式のデータに変換して追加
              // ステート documentsJsx に直接 push すると、リストにデータが蓄積され続けるので、一旦一時変数 documentsJsx_ に push してから、setDocumentsJsx() でステートを更新する
              documentsJsx_.push(
                <tr key={document.id}>
                  <td style={nameStyle}>{field.name}</td>
                  <td style={nameStyle}>{field.email}</td>
                  <td style={nameStyle}>{field.tell}</td>
                  <td style={nameStyle}>{field.memo}</td>
                </tr>
              )
            }
            setMessage('adress info')
          }
          else{
            setMessage('not find adress')
          }
        })
        
        setDocumentsJsx(documentsJsx_)
      }
    )
  }, [])

  //------------------------
  // JSX での表示処理
  //------------------------
  return (
    <div>
      <p>{message}</p>
      <table>
        <th style={nameStyle}>name</th>
        <th style={nameStyle}>email</th>
        <th style={nameStyle}>tell</th>
        <th style={nameStyle}>memo</th>
        <tbody>{documentsJsx}</tbody>
      </table>
    </div>
  );
}
