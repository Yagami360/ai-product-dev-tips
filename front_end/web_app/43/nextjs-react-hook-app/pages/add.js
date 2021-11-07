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
