import React, { Component } from 'react';
import { connect } from 'react-redux';
import './App.css';

// コンポーネントで使用する state を返すメソッド
function mappingState(state) {
  return state;
}

// App コンポーネント
class App extends Component {
  constructor(props){
    super(props);
  }

  render() {
    // <StateComponent /> に部分を <StateComponent id="-1" /> のように属性を指定した呼び出し方をしなくとも、StateComponent コンポーネントで this.props.id でアクセスできる
    return (
      <div>
        <p>Hello React Component!</p>
        <StateComponent />
        <ButtonComponent />
      </div>
    );
  }
}

// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
// let warpWithConnect = connect()  // warpWithConnect は関数オブジェクト
// App = warpWithConnect(warpWithConnect)
App = connect()(App);

// ID 表示のコンポーネント
class StateComponent extends Component {
  render(){
    // このクラスコンポーネントでは、<StateComponent name="Yagami" id="1" /> のように属性を指定して呼び出さられなくても、this.props に index.js のレデューサーで定義した state が設定されている
    return (
      <p>
        name={this.props.name}, id={this.props.id}
      </p>
    );
  }
}

// StateComponent コンポーネントにストアを接続する
// 第１引数に state の内容をそのまま返す mappingState() メソッドを設定することで、StateComponent コンポーネント内の this.props に index.js 内のレデューサーで定義した state が設定される
StateComponent = connect(mappingState)(StateComponent);

// ボタンのコンポーネント
class ButtonComponent extends Component {
  constructor(props){
    super(props);
    // this.メソッド名 = this.メソッド名.bind(this); の形式でイベントをバインド（割り当て）する
    this.doAction = this.doAction.bind(this);
  }

  // ボタンクリックでディスパッチ（レデューサーの呼び出し値を操作するためのもの）を実行
  doAction(e){
    if (e.shiftKey){
      // this.props.dispatch({action}) でレデューサーを呼び出す。このときレデューサーメソッドの action 引数にここで設定した値が設定される
      // type は必ず設定する必要がある
      this.props.dispatch({ type:'DECREMENT_ID' });
    } else {
      this.props.dispatch({ type:'INCREMENT_ID' });
    }
  }

  render(){
    // <button> タグの onClick 属性に、このクラスコンポーネントで定義したイベント処理のメソッドを設定し、onClick 属性に紐付ける
    return (
      <button onClick={this.doAction}>
        click
      </button>
    );
  }
}
// ストアのコネクト
ButtonComponent = connect()(ButtonComponent);

// App を外部ファイルから利用できるようにする
export default App;
