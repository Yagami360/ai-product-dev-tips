import React, { Component } from 'react';
import { connect } from 'react-redux';

// メモの各項目のコンポーネント
class Item extends Component {
  //index = 0;
  //memo_text = "xxx";
  //created_time = "00:00:00";

  index_style = {
    fontSize:"14pt",
    backgroundColor:"blue",
    color:"white",
    padding:"5px 10px",
    width:"50px"
  }
  memo_text_style = {
    fontSize:"14pt",
    backgroundColor:"white",
    color:"darkblue",
    padding:"5px 10px",
    border:"1px solid lightblue",
    minWidth:"300px"
  }
  date_style = {
    fontSize:"14pt",
    backgroundColor:"white",
    color:"darkblue",
    padding:"5px 10px",
    border:"1px solid lightblue",
    width:"80px"
  }

  constructor(props){
    super(props);
    //this.index = props.index
    //this.memo_text = props.memo_text
    //this.created_time = props.created_time
  }

  render() {
    // <table> タグ : 表
    // <tr> タグ : テーブルの行（横方向）
    // <th> タグ : テーブルの見出し
    // <td> タグ : テーブルのセル
    // 自身のプロパティ this.index, this.memo_text, this.created_time で表示するようにすると、表示が即座に反映されなくなるので、コンポーネント呼び出し時の引数で設定される this.props.xxx でアクセスするようにしている。
    return (
      <tr>
        <th style={this.index_style}>{this.props.index}</th>
        <td style={this.memo_text_style}>{this.props.memo_text}</td>
        <td style={this.data_style}>{this.props.created_time.getHours() + ':' + this.props.created_time.getMinutes() + ':' + this.props.created_time.getSeconds()}</td>
      </tr>
    );
  }
}

// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
Item = connect()(Item);

// 外部公開する
export default Item
