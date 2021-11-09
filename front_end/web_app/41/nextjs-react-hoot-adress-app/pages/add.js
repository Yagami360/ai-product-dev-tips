import 'bootstrap/dist/css/bootstrap.min.css'
import React from 'react';
import { useState } from 'react'
import { useEffect } from 'react'
import { useRouter } from 'next/router'
import firebase from "firebase";
import '../firebase/initFirebase'
import Layout from '../components/layout';

// アドレスの詳細画面ページのコンポーネント
export default function AddAdress() {
  // Firestore にアクセスするためのオブジェクト作成
  const db = firebase.firestore()

  // コレクション名
  const collectionName = 'adress-database'
  const documentId = '1'
  
  //------------------------
  // フック
  //------------------------
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [tell, setTell] = useState('')
  const [memo, setMemo] = useState('')

  // リダイレクトのための独自フック。遷移元ページからクエリパラメータを取得するために使用
  const router = useRouter()

  //------------------------
  // イベントハンドラ
  //------------------------
  // 入力フォーム更新時のイベントハンドラ
  const onChangeName = (e)=> {
    setName(e.target.value)
  }
  const onChangeEmail = (e)=> {
    setEmail(e.target.value)
  }
  const onChangeTell = (e)=> {
    setTell(e.target.value)
  }
  const onChangeMemo = (e)=> {
    setMemo(e.target.value)
  }

  // Add ボタンクリック時のイベントハンドラ
  const onClickAdd = (e)=> {
    // 新規に追加するドキュメントデータ
    const document = {
      name : name,  // 入力フォームの値を追加
      email : email,
      tell : tell,
      memo : memo,
    }

    // db.collection(コレクション名).add(ドキュメントデータ) で、コレクションに新たなドキュメントを追加する
    // この時ドキュメントIDは自動的に割り振られる
    // 新規にコレクションを追加する場合も、このメソッドで作成できる
    db.collection(collectionName).add(document).then(ref=> {
      // 別ページにリダイレクト
      router.push('/')      
    })
  }

  //------------------------
  // JSX での表示処理
  //------------------------
  //console.log("adressJsx : ", adressJsx)
  return (
    <div className="container">
      <Layout header="AdressBook App" title="adress info">
        <div className="alert alert-primary text-left">
          <div className="form-group">
            <label>name : </label>
            <input type="text" onChange={onChangeName} className="form-control" />            
          </div>
          <div className="form-group">
            <label>email : </label>
            <input type="text" onChange={onChangeEmail} className="form-control" />            
          </div>
          <div className="form-group">
            <label>tell : </label>
            <input type="text" onChange={onChangeTell} className="form-control" />            
          </div>
          <div className="form-group">
            <label>memo : </label>
            <input type="text" onChange={onChangeMemo} className="form-control" />            
          </div>
          <button className="btn btn-primary mt-3" onClick={onClickAdd}>Add</button>
        </div>
      </Layout>
    </div>
  );
}
