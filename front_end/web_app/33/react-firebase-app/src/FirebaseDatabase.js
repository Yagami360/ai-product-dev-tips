import React, { Component } from 'react';
import firebase from "firebase";
import "firebase/storage";


// Firebase の Realtime Database からデータを取り出し、それらを表示するコンポーネント
class FirebaseDatabase extends Component {
  db_name = "sample-database";   // データベース名
  style = {
    fontSize:"12pt",
    padding:"5px 10px"
  }

  constructor(props) {
    super(props);
    this.db_name = props.db_name

    // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
    this.state = {
      data:[]
    }

    // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
    this.getDatabaseFromFirebase();
  }

  // Firebase の Realtime Database からデータベースを取得するイベントハンドラ
  getDatabaseFromFirebase(){
    // database にアクセスするためのオブジェクト作成
    let db = firebase.database();

    // ref() メソッドで、取り出すデータの reference オブジェクト作成。
    // 引数には Firebase Realtime Database 上のデータベースのパスを指定（プロジェクト直下の場合は、`${データベース名}/` になる）
    let ref = db.ref(this.db_name + "/");

    // ?
    let self = this;

    // orderByKey() : キーをデータを並び替え
    // limitToFirst() : 引数で指定した数だけデータを取り出す
    // on(イベント名, (snapshot)=>{終了後の処理} ) : 
    //   limitToFirst() でアクセスした結果の処理イベントのイベントハンドラで、アクセス後の処理を定義する。ここでは、イベント名に "value"（データベースにアクセスし値を受け取るイベント）を設定している。
    //   snapshot には、イベント時発生時に受け取ったデータが入る
    ref.orderByKey().limitToFirst(10).on('value', (snapshot)=>{
      self.setState({
        data:snapshot.val()
      });
    });
  }

  // データ表示の生成するイベントハンドラ
  getTableData(){
    let result = [];
    if (this.state.data == null || this.state.data.length == 0){
      return [<tr key="0"><th>NO DATA.</th></tr>];
    }
    for(let i in this.state.data){
      result.push(<tr key={i}>
        <th>{this.state.data[i].ID}</th>
        <td>{this.state.data[i].name}</td>
        <td>{this.state.data[i].message}</td>
      </tr>);
    }
    return result;
  }

  render(){
    if (this.state.data.length == 0){
      this.getFireData();
    }
    return (
      <table><tbody>
        {this.getTableData()}
      </tbody></table>
    )
  }
}

// 外部公開する
export default FirebaseDatabase;