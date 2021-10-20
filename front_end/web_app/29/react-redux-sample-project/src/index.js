import React from 'react';
import ReactDOM from 'react-dom';
import { createStore, combineReducers } from 'redux';   // ストア機能を import
import { Provider } from 'react-redux';                 // プロバイダー機能を import
import './index.css';
import AppComponent from './App';
import reportWebVitals from './reportWebVitals';

// ステートの初期値
let state_value = {
  name: "Yagami",
  id:-1,
}

// function レデューサーの関数名 (state=stateの初期値, action){} の形式でレデューサーを定義
function reducer(state = state_value, action) {
  // action : レデューサーを呼び出す際の情報をまとめたオブジェクト
  // action.type : action オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。これらの値は、App.js 内の `this.props.dispath({type:"xxx"})` で定義している
  switch (action.type) {
    case 'INCREMENT_ID': // 
      // state の新しい値を return する
      return {
          name:state.name,
          id:state.id + 1,
      };
    case 'DECREMENT_ID':
      return {
        name:state.name,
        id:state.id - 1,
      };
    default:
      return state;
  }
}

// `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
let store = createStore(reducer);

// 表示をレンダリング
ReactDOM.render(
  // プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
  // この例では、App.js で定義されている App コンポーネントにストアの内容が渡される
  <Provider store={store}>
    <AppComponent />
  </Provider>,
  document.getElementById('root')
);
