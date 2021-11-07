import React from 'react';
import firebase from "firebase";
import Link from 'next/link'
import '../firebase/initFirebase'

// ルートページ
export default function Home() {
  // スタイル定義
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

  return (
    <div className="App">
      <h1>Next.js & Firebase Sample App</h1>
      <table>
        <th style={indexStyle}>No</th>
        <th style={nameStyle}>操作一覧</th>
        <tbody>
          <tr>
            <td style={indexStyle}>1</td>
            <td style={nameStyle}><Link href="/show"><a>Firestore を表示する</a></Link></td> 
          </tr>
          <tr>
            <td style={indexStyle}>2</td>
            <td style={nameStyle}><Link href="/add"><a>Firestore を追加する</a></Link></td>
          </tr>
          <tr>
            <td style={indexStyle}>3</td>
            <td style={nameStyle}><Link href="/delete"><a>Firestore を削除する</a></Link></td>
          </tr>
          <tr>
            <td style={indexStyle}>4</td>
            <td style={nameStyle}><Link href="/find"><a>Firestore を検索する</a></Link></td>
          </tr>
        </tbody>
      </table>      
    </div>
  );
}
