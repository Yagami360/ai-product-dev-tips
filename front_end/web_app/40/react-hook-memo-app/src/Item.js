import React from 'react'

// メモの各項目のコンポーネント
function Item(props) {
  // スタイル定義
  const indexStyle = {
    fontSize:"14pt",
    backgroundColor:"blue",
    color:"white",
    padding:"5px 10px",
    width:"50px"
  }
  const memoTextStyle = {
    fontSize:"14pt",
    backgroundColor:"white",
    color:"darkblue",
    padding:"5px 10px",
    border:"1px solid lightblue",
    minWidth:"300px"
  }
  const dateStyle = {
    fontSize:"14pt",
    backgroundColor:"white",
    color:"darkblue",
    padding:"5px 10px",
    border:"1px solid lightblue",
    width:"80px"
  }

  console.log("call Item")  
  return (
    <tr>
      <th style={indexStyle}>{props.index}</th>
      <td style={memoTextStyle}>{props.memoText}</td>
      <td style={dateStyle}>{props.createdTime}</td>
    </tr>
  );
}

export default Item;
