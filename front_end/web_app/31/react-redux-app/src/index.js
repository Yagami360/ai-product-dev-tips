import React from 'react';
import ReactDOM from 'react-dom';
import storage from 'redux-persist/lib/storage';
import { createStore } from 'redux';           // ストア機能を import
import { Provider } from 'react-redux';                         // プロバイダー機能を import
import { persistStore, persistReducer } from 'redux-persist';   // redux-persist のパーシストレデューサーとパーシスター
import { PersistGate } from 'redux-persist/integration/react';  // redux-persist のパーシストゲート
import './index.css';
import App from './App';

// Redux Persist の設定情報の作成
const persist_config = {
  key: "root",
  storage,
};

// function レデューサーの関数名 (state=stateの初期値, action){} の形式でレデューサーを定義
function reducer(state = {name: "Yagami",id:-1}, action) {
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

// パーシストレデューサーの作成
const persist_reducer = persistReducer(persist_config, reducer);

// `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
let store = createStore(persist_reducer);

// パーシスターの作成
let persist_store = persistStore(store);

// 表示をレンダリング
ReactDOM.render(
  // プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
  // プロバイダーのタグ `<Provider>` 内に、パーシストゲートのタグ `<PersistGate>` を追加することで、パーシストゲートをコンポーネントに適用する
  <Provider store={store}>
    <PersistGate loading={<p>loading...</p>} persistor={persist_store}>
      <App />
    </PersistGate>
  </Provider>,
  document.getElementById('root')
);
