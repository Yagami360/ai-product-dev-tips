import React, { Component } from 'react';
import { connect } from 'react-redux';
import './App.css';
import Memo from './Memo';
import AddMemoForm from './AddMemoForm';
import DeleteMemoForm from './DeleteMemoForm';

// アプリ全部のコンポーネント
class App extends Component {
  constructor(props){
    super(props);
  }

  render() {
    // <hr /> タグ : 区切り線
    return (
      <div>
        <h1>React Memo App</h1>
        <AddMemoForm />
        <hr />
        <DeleteMemoForm />
        <Memo />
      </div>
    );
  }
}

// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
App = connect()(App);

// 外部公開する
export default App
