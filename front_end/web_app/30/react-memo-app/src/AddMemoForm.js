import React, { Component } from 'react';
import { connect } from 'react-redux';
import { addMemoAction } from './Store';

// 保存済みメモの各項目のコンポーネント
class AddMemoForm extends Component {
  constructor(props){
    super(props);

    // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
    this.state = {
      memo_text: ""
    };

    // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
    this.updateMemo = this.updateMemo.bind(this);
    this.addMemo = this.addMemo.bind(this);
  }

  // テキスト入力フォーム更新時のイベント処理
  // このイベント処理を定義しないと、テキスト入力フォームにキーボードで入力したテキストが入らない
  updateMemo(e){
    // `state` の値の更新は、`this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。
    // e.target.value に入力テキストが入る
    this.setState(
      (state)=>({
        memo_text: e.target.value,
      })
    );
  }

  // Add ボタンクリック時のイベント処理
  addMemo(e){
    // 
    e.preventDefault();

    // アクションクリエイターで定義した action
    let action = addMemoAction(this.state.memo_text);
    console.log("[addMemo] action", action)
    
    // this.props.dispatch({action}) でレデューサーを呼び出す。
    this.props.dispatch(action);

    // テキスト入力フォームのテキストを空にする
    this.setState({memo_text: ''});
  }

  // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
  // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
  // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
  render() {
    return (
      <div>
        <p>Please type your message</p>
        <form onSubmit={this.addMemo}>
          <input type="text" size="40" onChange={this.updateMemo} value={this.state.memo_text} />
          <input type="submit" value="Add"/>
        </form>
      </div>
    );
  }
}

// コンポーネントで使用する state を返すメソッド
function mappingState(state) {
  return state;
}

// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
AddMemoForm = connect(mappingState)(AddMemoForm);

// 外部公開する
export default AddMemoForm
