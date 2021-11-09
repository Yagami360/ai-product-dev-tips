import 'bootstrap/dist/css/bootstrap.min.css'
import React from 'react';
import { useState } from 'react'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import firebase from "firebase";
import '../firebase/initFirebase'
import Layout from '../components/layout';

// アドレスの詳細画面ページのコンポーネント
export default function AdressInfo() {
  // Firestore にアクセスするためのオブジェクト作成
  const db = firebase.firestore()

  // コレクション名
  const collectionName = 'adress-database'
  const documentId = '1'
  
  //------------------------
  // フック
  //------------------------
  // アドレス表示用のステートフック
  const adressJsx_ = {   // 一時変数
    name : <li className="list-group-item px-3 py-1"></li>,
    email : <li className="list-group-item px-3 py-1"></li>,
    tell : <li className="list-group-item px-3 py-1"></li>,
    memo : <li className="list-group-item px-3 py-1"></li>,
  }
  const [adressJsx, setAdressJsx] = useState(adressJsx_)

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
        // snapshot.forEach((document)=> {..}) : snapshot から順にデータを取り出して処理を行う。無名関数の引数 document には、コレクション内の各ドキュメントが入る
        snapshot.forEach((document)=> {
          // ページ遷移直後は router.query.documentId = undefined になることに注意
          if( router.query.documentId != undefined ){
            documentId = router.query.documentId

            if( document.id == documentId ){
              // document.data() : ドキュメント内のフィールド
              let field = document.data()
              adressJsx_.name = <li className="list-group-item px-3 py-1">{field.name}</li>
              adressJsx_.email = <li className="list-group-item px-3 py-1">{field.email}</li>
              adressJsx_.tell = <li className="list-group-item px-3 py-1">{field.tell}</li>
              adressJsx_.memo = <li className="list-group-item px-3 py-1">{field.memo}</li>
            }
            setMessage('')
          }
          else{
            setMessage('not find adress')
          }
        })
        
        //console.log("adressJsx_ : ", adressJsx_)
        setAdressJsx(adressJsx_)
      }
    )
  }, [message])

  //------------------------
  // JSX での表示処理
  //------------------------
  //console.log("adressJsx : ", adressJsx)
  return (
    <div className="container">
      <Layout header="AdressBook App" title="adress info">
        <div className="alert alert-primary text-left">
          <p>{message}</p>
          <div>name : {adressJsx.name}</div>
          <div>email : {adressJsx.email}</div>
          <div>tell : {adressJsx.tell}</div>
          <div>memo : {adressJsx.memo}</div>
        </div>
      </Layout>
    </div>
  );
}
