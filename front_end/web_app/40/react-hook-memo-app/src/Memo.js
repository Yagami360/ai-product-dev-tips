import React, { useState } from 'react'
import useLocalPersist from './LocalPersist';
import Item from './Item'

// メモ画面のコンポーネント
function Memo(props) {
  // 独自フック
  // ローカルディスクから読み込んだメモの各項目のリスト。以下のデータ構造を持つ（初期値は空リスト）
  // savedMemo = [
  //   {
  //     memoText: "xxx",                 // メモのテキスト内容
  //     createdTime: "00:00:00",         // メモの作成時刻
  //   },
  //   {
  //     memoText: "yyy",                 // メモのテキスト内容
  //     createdTime: "00:00:01",         // メモの作成時刻
  //   },
  //   ...        
  // ]
  const [savedMemo, setSavedMemo] = useLocalPersist("memo", [])
  const [mode, setMode] = useLocalPersist('mode', 'default')
  console.log("[Memo] savedMemo :", savedMemo)

  // mode によって表示を変える
  let items = []
  switch (mode){
    case 'default':
      items = savedMemo.map((data,index)=>(
        <Item index={index+1} memoText={data.memoText} createdTime={data.createdTime} />
      ))
      break
    case 'find':
      break
    default:
      items = savedMemo.map((data,index)=>(
        <Item index={index+1} memoText={data.memoText} createdTime={data.createdTime} />
      ))
  }
  console.log("[Memo] items :", items)

  // // 配列.map((value,index)=>(配列番号 index の各要素 data に対しての処理)) : map で配列の各要素 data を取り出し、data を引数に、配列の各要素 data に対しての処理を行う
  return (
    // 保存済みメモ一覧
    <table><tbody>
      <th>No</th>
      <th>テキスト</th>
      <th>保存時間</th>
      {items}
    </tbody></table>
  );
}

export default Memo;
