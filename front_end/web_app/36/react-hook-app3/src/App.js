import React, { useState } from 'react'
import './App.css';

// 関数コンポーネントにおいても、コンポーネントの呼び出し側で <コンポーネント名 args1="" args2="" ... /> で指定されたタグ属性の値は、props 引数で取得出来る
function User(props) {
  const id_style = {
    fontSize:"14pt",
    backgroundColor:"blue",
    color:"white",
    padding:"5px 10px",
    width:"50px"
  }
  const name_style = {
    fontSize:"14pt",
    backgroundColor:"white",
    color:"darkblue",
    padding:"5px 10px",
    border:"1px solid lightblue",
    minWidth:"300px"
  }

  // <tr> タグ（テーブルの行）・<th> タグ（テーブルの見出し）・<td> タグ（テーブルのセル
  return (
    <tr>
      <td style={id_style}>{props.id}</td>
      <td style={name_style}>{props.name}</td>
    </tr>
  )
}

function App() {
  // ステートフックの宣言
  // 第１戻り値には、state の値が入る。
  // 第２戻り値には、state の値を変更する関数が入る。
  // 引数には、state の初期値を設定
  const [id, setId] = useState(1)
  const [name, setName] = useState("Yagami")
  const [form, setForm] = useState({id:'-1', name:'no name'})

  // フォーム入力ボタンクリック時のイベントハンドラ
  // 関数コンポーネント内なので、const 関数名 = (event) => {} の形式でイベントハンドラを定義する
  const doSubmit = (event) => {
    setForm({id:id, name:name})
    event.preventDefault()
  }
  
  // 入力フォーム更新時のイベントハンドラ
  const doChangeId = (event) => {
    setId(event.target.value)
  }
  const doChangeName = (event) => {
    setName(event.target.value)
  }

  // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
  // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
  // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
  // 子関数コンポーネント User のタグ属性には、form の state `form["id"]`, `form["name"]` を渡す（）
  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hook Sample App3</h1>
        <form onSubmit={doSubmit}>
          <div className="form-group">          
            <label>id:</label>
            <input type="number" className="form-control" onChange={doChangeId} />
            <label>name:</label>
            <input type="text" className="form-control" onChange={doChangeName} />
            <input type="submit" className="btn btn-primary" value="change user" />
          </div>
        </form>
        <p></p>
        <tabel><tbody>
          <th>id</th>
          <th>name</th>
          <User id={form["id"]} name={form["name"]} />
        </tbody></tabel>
      </header>
    </div>
  );
}

export default App;
