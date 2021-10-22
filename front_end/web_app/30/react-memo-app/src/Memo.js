import React, { Component } from 'react';
import { connect } from 'react-redux';
import Item from './Item';

// メモ画面のコンポーネント
class Memo extends Component {
  constructor(props){
    super(props);
  }

  render() {
    console.log("[Memo] this.props.data_list", this.props.data_list)
    //console.log("this.props.data_list[0]", this.props.data_list[0])
    //console.log("this.props.data_list[0].memo_text", this.props.data_list[0].memo_text)
    //console.log("this.props.data_list[0].created_time", this.props.data_list[0].created_time)
    /*
    return (
      <p>テキスト : {this.props.data_list[0].memo_text}, 保存時間 : {this.props.data_list[0].created_time.getHours() + ':' + this.props.data_list[0].created_time.getMinutes() + ':' + this.props.data_list[0].created_time.getSeconds()}</p>
    );
    */
    // <table> タグ : 表
    return (
      // 保存済みメモ一覧
      <table><tbody>
        <th>No</th>
        <th>テキスト</th>
        <th>保存時間</th>
        {this.props.data_list.map((data,index)=>(
          <Item index={index} memo_text={data.memo_text} created_time={data.created_time} />
        ))}
      </tbody></table>
    );
  }
}

// コンポーネントで使用する state を返すメソッド
function mappingState(state) {
  return state;
}

// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
// 第１引数に state の内容をそのまま返す mappingState() メソッドを設定することで、Memo コンポーネント内の this.props に Store.js 内のレデューサーで定義した state が設定される
Memo = connect(mappingState)(Memo);

// 外部公開する
export default Memo
