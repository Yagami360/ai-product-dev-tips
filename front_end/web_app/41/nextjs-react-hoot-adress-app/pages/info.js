import 'bootstrap/dist/css/bootstrap.min.css'
import React from 'react';
import { useState } from 'react'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import firebase from "firebase";
import '../firebase/initFirebase'
import Layout from '../components/layout';

// ログイン認証の初期化
const auth = firebase.auth()

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
  const [name, setName] = useState([])

  // 送信メッセージ表示用のステートフック
  const [sendMsg, setSendMsg] = useState([])

  //送信済みメッセージ表示用のステートフック
  const [sendedMsgJsx, setSendedMsgJsx] = useState([])  

  // 読み込み待ち表示のステートフック
  const [message, setMessage] = useState('wait...')

  // リダイレクトのための独自フック。遷移元ページからクエリパラメータを取得するために使用
  const router = useRouter()

  // ログインしてなければトップページに戻る副作用フック
  useEffect(() => {
    if (auth.currentUser == undefined) {
      router.push('/')
    }
  },[])

  // コレクション名からコレクション内のデータを取得する副作用フック。
  // [データベース構造]
  // adress-database +- ドキュメントID(ログインユーザーのemailの値) +-- adress-database  + ドキュメントID(ユーザー１のemailの値) +-- name
  //                 |                                        |                    |                                  +-- email
  //                 |                                        |                    + ドキュメントID(ユーザー２のemailの値) +-- name
  //                 |                                        |                    |                                  +-- email
  //                 |                                        |                    + ドキュメントID(ユーザー１のemailの値) +-- message-database + ドキュメントID(自動割り振り) +-- comment  // メッセージデータベース
  //                 |                                        |                    |                                  |                                               +-- time
  //                 |-- ドキュメントID(ユーザー１のemailの値)     +-- message-database + ドキュメントID(自動割り振り) +-- comment  // メッセージデータベース
  //                 |                                        |                    |                          +-- time
  useEffect(() => {
    // ログイン済みに場合のみ表示
    if (auth.currentUser != undefined) {
      // アドレス帳の各項目の表示
      // db.collection(コレクション名) : コレクションにアクセスするためのオブジェクト取得
      // db.collection(コレクション名).doc(ドキュメントID) : 指定したドキュメントIDのドキュメント取得
      // db.collection(コレクション名).get() : コレクションにアクセスするためのオブジェクトからコレクションを取得。get() は非同期のメソッドで Promise を返す。そのため、非同期処理が完了した後 then() で非同期完了後の処理を定義する
      db.collection(collectionName).doc(auth.currentUser.email).collection(collectionName).get().then(
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
                setName(field.name)
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

      // 送信済みメッセージの取得（＝相手のメッセージデータベースの表示）
      db.collection(collectionName).doc(auth.currentUser.email).collection(collectionName).doc(router.query.documentId).collection('message-database').orderBy('time', 'desc').get().then(
        snapshot=> {
          const sendedMsgJsx_ = []
          snapshot.forEach((document)=> {
            let field = document.data()
            sendedMsgJsx_.push(<li className="list-group-item px-3 py-1">[{field.time}] [{field.direction}] {field.comment}</li>)
          })
          setSendedMsgJsx(sendedMsgJsx_)
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
  // 入力フィールドの処理
  const onChangeSendMsg = ((e)=> {
    setSendMsg(e.target.value)
  })

  // 送信ボタンクリック時のイベントハンドラ
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
  const onClickSend = (e)=> {
    const date = new Date()
    const sendMsgTo = {
      direction : "To : " + name,
      comment: sendMsg,
      time: date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds()
    }
    const sendMsgFrom = {
      direction : "From : " + auth.currentUser.displayName,
      comment: sendMsg,
      time: date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds()
    }

    // 自分のメッセージデータベースにデータ追加
    db.collection(collectionName).doc(auth.currentUser.email).collection(collectionName).doc(router.query.documentId).collection("message-database").add(sendMsgTo).then(ref=> {
      // 相手のメッセージデータベースにデータ追加
      db.collection(collectionName).doc(router.query.documentId).collection(collectionName).doc(auth.currentUser.email).collection("message-database").add(sendMsgFrom).then(ref=> {
        setSendMsg("")
        setMessage('sended message')
      })
    })
  }

  // 戻るボタンクリック時のイベントハンドラ
  const onClickReturn = (e)=> {
    router.push('/')      
  }

  //------------------------
  // JSX での表示処理
  //------------------------
  //console.log("router.query.documentId : ", router.query.documentId)
  //console.log("adressJsx : ", adressJsx)
  console.log("sendedMsgJsx : ", sendedMsgJsx)
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
        <div className="form-group">
          <label>send message :</label>
          <input type="text" onChange={onChangeSendMsg} className="form-control" />
        </div>
        <div className="text-center">
        <button className="btn btn-primary my-3 mx-3" onClick={onClickSend}>送信</button>
          <button className="btn btn-primary my-3" onClick={onClickReturn}>戻る</button>
        </div>
        <ul className="list-group">{sendedMsgJsx}</ul>
      </Layout>
    </div>
  );
}
