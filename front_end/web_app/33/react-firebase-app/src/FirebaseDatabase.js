import React, { Component } from 'react';
import firebase from "firebase";
import "firebase/storage";


// Firebase の Realtime Database からデータを取り出し、それらを表示するコンポーネント
class FirebaseDatabase extends Component {
  style = {
    fontSize:"12pt",
    padding:"5px 10px"
  }

  constructor(props) {
    super(props);

    // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
    this.state = {
      data_list:[]   // Firebase の Realtime Database からデータベースをリストで設定
    }

    this.getDatabaseFromFirebase();
  }

  // Firebase の Realtime Database からデータベースを取得する関数
  getDatabaseFromFirebase(){
    // database にアクセスするためのオブジェクト作成
    let db = firebase.database();

    // ref() メソッドで、取り出すデータの reference オブジェクト作成。
    // 引数には Firebase Realtime Database 上のデータベースのパスを指定（プロジェクト直下の場合は、`${データベース名}/` になる）
    let ref = db.ref(this.props.db_name + "/");

    // ?
    let self = this;

    // orderByKey() : キーをデータを並び替え
    // limitToFirst() : 引数で指定した数だけデータを取り出す
    // on(イベント名, (snapshot)=>{終了後の処理} ) : 
    //   limitToFirst() でアクセスした結果の処理イベントのイベントハンドラで、アクセス後の処理を定義する。ここでは、イベント名に "value"（データベースにアクセスし値を受け取るイベント）を設定している。
    //   snapshot.val() には、イベント時発生時に受け取ったデータが [{"id":1, name:"Yagami"}, {"id":2, name: "Yagoo"}, ...] のような形式で入る
    //   limitToFirst().on(){} とすることで、limitToFirst() の引数で指定した数だけ繰り返し処理が行われる
    ref.orderByKey().limitToFirst(10).on('value', (snapshot)=>{
      console.log("snapshot.val() :", snapshot.val())
      // state の更新は、setState() で行う
      self.setState({
        data_list:snapshot.val()
      });
    });
  }

  // データベースの各項目を表形式でレンダリングする関数
  renderTableColums(){
    console.log("this.state.data_list :", this.state.data_list)
    if (this.state.data_list == null || this.state.data_list.length == 0){
      return [<tr key="0"><th>NO DATA.</th></tr>];
    }

    let result = [];
    for(let i in this.state.data_list){
      // <tr> タグ（テーブルの行）・<th> タグ（テーブルの見出し）・<td> タグ（テーブルのセル）
      // タグ内の key属性 : React が仮想DOMを更新する際に更新対象を識別するための一意の値（※ この key 属性は、HTML　でもともと定義されているタグ属性ではなく、React の仮想DOM の機能であることに注意）
      result.push(
        <tr key={i}>
          <th>{this.state.data_list[i].id}</th>
          <td>{this.state.data_list[i].name}</td>
        </tr>
      );
    }
    return result;
  }

  render(){
    if (this.state.data_list.length == 0){
      this.getDatabaseFromFirebase();
    }
    return (
      <div>
        <p>Realtime Database name : {this.props.db_name}</p>
        <table><tbody>
          <tr>
            <th>id</th>
            <th>name</th>
          </tr>
          {this.renderTableColums()}
        </tbody></table>
      </div>
    )
  }
}

// 外部公開する
export default FirebaseDatabase;