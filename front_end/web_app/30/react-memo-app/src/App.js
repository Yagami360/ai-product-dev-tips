import React, { Component } from 'react';
import { connect } from 'react-redux';
import './App.css';
import Memo from './Memo';

// App コンポーネント
class App extends Component {
  constructor(props){
    super(props);
  }

  render() {
    return (
      <div>
        <p>Hello React Component!</p>
        <Memo />
      </div>
    );
  }
}

// connect(stateを設定する関数)(コンポーネント) : コンポーネントにストアを接続する
App = connect()(App);

// 外部公開する
export default App
