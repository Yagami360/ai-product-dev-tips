import React, { useState } from 'react'
import useLocalPersist from './LocalPersist';

function AddMemoForm(props) {
  // ステートフック・独自フック
  const [memoText, setMemoText] = useState('')
  const [savedMemo, setSavedMemo] = useLocalPersist("memo", [])
  const [mode, setMode] = useLocalPersist('mode', 'default')

  // テキスト入力フォーム更新時のイベントハンドラ。このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
  // 関数コンポーネント内なので、const 関数名 = () => {} の形式でイベントハンドラを定義する
  const updateInputText = (e)=>{
    // e.target.value に入力テキストが入る
    setMemoText(e.target.value)
  }

  // Add ボタンクリック時のイベントハンドラ
  const addMemo = (e)=>{
    // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
    e.preventDefault();    

    // 追加データ
    const date = new Date()
    const newData = {
      memoText: memoText,
      createdTime: date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds(),
    }

    // unshift() でリストの先頭に値を追加
    savedMemo.unshift(newData)

    // 値の更新を反映（＝ローカルディスクに書き込み）
    setSavedMemo(savedMemo)

    // 入力フォームのテキストをクリア
    setMemoText("")
    console.log("[AddMemoForm] [addMemo] savedMemo", savedMemo)

    //
    setMode('default')
  }
  
  // ステートフック useState() で定義したステート memoText を {memoText} で表示させることで値の変更が即座に画面上に反映されるようにする
  return (
    <div>
      <p>Please type your message</p>
      <form onSubmit={addMemo}>
        <input type="text" size="40" onChange={updateInputText} value={memoText} />
        <input type="submit" value="Add"/>
      </form>
    </div>
  );
}

export default AddMemoForm;
