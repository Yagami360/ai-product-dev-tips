import React, { Component } from 'react';
import { connect } from 'react-redux';
import { deleteMemoAction } from './Store';

// メモの削除画面のコンポーネント
class DeleteMemoForm extends Component {
  select_style = {
    fontSize:"12pt",
    color:"#006",
    padding:"1px",
    margin:"5px 0px"
  }
  btn_style = {
    fontSize:"10pt",
    color:"#006",
    padding:"2px 10px"
  }

  constructor(props){
    super(props);

    // `state` の値の初期化は、コンストラクタで `this.state = {変数名1:値1, 変数名2:値2, ...};` の形式で行う
    // select_index : 選択ボックスの番号
    this.state = {
      select_index: -1
    };

    // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
    this.updateSelect = this.updateSelect.bind(this);
    this.deleteMemo = this.deleteMemo.bind(this);
  }

  // 選択ボックス更新時のイベント処理
  updateSelect(e){
    // `state` の値の更新は、`this.setState((state)=>({変数名1:値1, 変数名2:値2, ...}))` の形式で行う。
    // e.target.value に選択ボックスの番号が入る
    this.setState(
      (state)=>({
        select_index: e.target.value,
      })
    );
  }

  // Delete ボタンクリック時のイベント処理
  deleteMemo(e){
    // submit イベント e の発生元であるフォームが持つデフォルトのイベント処理をキャンセル
    e.preventDefault();

    // アクションクリエイターで定義した action
    let action = deleteMemoAction(this.state.select_index);
    console.log("[deleteMemo] action", action)

    // this.props.dispatch({action}) でレデューサーを呼び出す。
    this.props.dispatch(action);

    // テキスト入力フォームのテキストを空にする
    this.setState({memo_text: ''});
  }

  render() {
    let n = 0;
    // <option> タグ : <select>タグ内で使用し、メニューの選択肢を作成する要素
    let memo_texts = this.props.data_list.map((data)=>(<option key={n} value={n++}>{data.memo_text.substring(0,10)}</option>));

    // <form> タグがひとつのフォームとなり、フォームの中に <input> タグ、<select> タグ、<textarea> タグなどのフォーム部品を配置してフォームを作る
    // <select> タグ : 選択ボックス
    // <input> タグの onChange 属性 : フォームのコントロール部品（input要素, select要素, textarea要素）の属性値が変更されたときのイベント
    // <form> タグの onSubmit 属性 : <form> タグ内部の <input type="submit"> で定義したボタンクリック時のイベント
    return (
      <div>
        <form onSubmit={this.deleteMemo}>
          <select onChange={this.updateSelect} defaultValue="-1" style={this.select_style}>
            {memo_texts}
          </select>
          <input type="submit" style={this.btn_style} value="Delete"/>
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
DeleteMemoForm = connect(mappingState)(DeleteMemoForm);

// 外部公開する
export default DeleteMemoForm
