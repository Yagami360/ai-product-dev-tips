import React from 'react';
import { useState, useEffect } from 'react'
import firebase from "firebase";
import '../firebase/initFirebase'

// Auth オブジェクトの作成
const auth = firebase.auth()

// 認証プロバイダー（Google）の作成
const provider = new firebase.auth.GoogleAuthProvider();

// ルートページ
export default function Home() {
  // ステートフック
  const [message, setMessage] = useState('wait...')

  // イベントハンドラ
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

  const onClickLogOut = ((e)=> {
    // ログアウトする
    auth.signOut()
    setMessage('logout.')
  })

  // JSX での画面表示
  // auth.currentUser でログインユーザーを取得できる（ログインユーザーがいないときは undefined が入る）
  // 三項演算子 {条件式 ? Trueの場合の処理 : Falseの場合の処理} で auth.currentUser に値が入っているときのみ表示するようにしている
  return (
    <div>
      <h1>Next.js & Firebase Auth Sample App</h1>
      <button onClick={onClickLogIn} className="btn btn-primary">log in</button>
      <button onClick={onClickLogOut} className="btn btn-primary">log out</button>
      <h5>{message}</h5>
      <p className="h6 text-left">
        uid: {auth.currentUser != undefined ? auth.currentUser.uid : ''}<br/>
        displayName: {auth.currentUser != undefined ? auth.currentUser.displayName : ''}<br/>
        email: {auth.currentUser != undefined ? auth.currentUser.email : ''}<br/>
        phoneNumber: {auth.currentUser != undefined ? auth.currentUser.phoneNumber : ''}
      </p>
    </div>
  );
}
