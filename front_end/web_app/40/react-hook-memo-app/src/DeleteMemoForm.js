import React, { useState } from 'react'
import useLocalPersist from './LocalPersist';

function DeleteMemoForm(props) {
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

  // ステートフック・独自フック
  const [selectIndex, setSelectIndex] = useState(0)
  const [savedMemo, setSavedMemo] = useLocalPersist("memo", [])
  const [mode, setMode] = useLocalPersist('mode', 'default')

  // 選択ボックス更新時のイベントハンドラ
  // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
  const updateSelect = (e)=>{
    // e.target.value に選択ボックスの番号が入る
    setSelectIndex(e.target.value)
  }

  // Delete ボタンクリック時のイベントハンドラ
  const deleteMemo = (e)=>{
    // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
    e.preventDefault();    

     // splice() でリストの要素を削除
     // 削除番号には、選択ボックス更新時のイベントハンドラで設定したステート selectIndex の値を使用
    savedMemo.splice(selectIndex, 1)

    // 値の更新を反映（＝ローカルディスクに書き込み）
    setSavedMemo(savedMemo)

    // 選択ボックスの選択インデックスをクリア
    setSelectIndex(0)
    console.log("[DeleteMemoForm] [deleteMemo] savedMemo", savedMemo)

    //
    setMode('default')
  }
  
  // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
  // <select> タグ : 選択ボックス
  // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
  // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
  let memoTexts = savedMemo.map((data,index)=>(<option key={index} value={index++}>{data.memoText.substring(0,10)}</option>));
  return (
    <div>
      <form onSubmit={deleteMemo}>
        <select onChange={updateSelect} defaultValue="-1" style={selectStyle}>
          {memoTexts}
        </select>
        <input type="submit" style={btnStyle} value="Delete"/>
      </form>
    </div>
  );
}

export default DeleteMemoForm;
