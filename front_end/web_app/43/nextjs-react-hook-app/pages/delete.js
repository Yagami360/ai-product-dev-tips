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
        //console.log("snapshot", snapshot)
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
  const onClickDelete = ((e)=> {
    // イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
    //e.preventDefault();

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
      <form>
        <label>document id : </label>
        <select onChange={updateSelect} defaultValue="-1" style={selectStyle}>
          {documentIdsJsx}
        </select>
      </form>
      <button onClick={onClickDelete} className="btn btn-primary" style={btnStyle}>Delete</button>
      <p>{showMessage}</p>
      <table>
        <th style={indexStyle}>id</th>
        <th style={nameStyle}>name</th>
        <tbody>{documentsJsx}</tbody>
      </table>
    </div>
  );
}
