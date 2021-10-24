import React from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux';   // ストア機能を import
import { Provider } from 'react-redux';                 // プロバイダー機能を import
import storage from 'redux-persist/lib/storage';
import { persistStore, persistReducer } from 'redux-persist';   // redux-persist のパーシストレデューサーとパーシスター
import { PersistGate } from 'redux-persist/integration/react';  // redux-persist のパーシストゲート
import './index.css';
import App from './App';
import { reducer } from './Store'

// Redux Persist の設定情報の作成
const persist_config = {
  key: "react-memo-app",
  storage,
};

// パーシストレデューサーの作成
const persist_reducer = persistReducer(persist_config, reducer);

// `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
let store = createStore(persist_reducer);

// パーシスターの作成
let persist_store = persistStore(store);

// 表示をレンダリング
ReactDOM.render(
  // プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
  // この例では、App.js で定義されている App コンポーネントにストアの内容が渡される
  // プロバイダーのタグ `<Provider>` 内に、パーシストゲートのタグ `<PersistGate>` を追加することで、パーシストゲートをコンポーネントに適用する
  <Provider store={store}>
    <PersistGate loading={<p>loading...</p>} persistor={persist_store}>
      <App />
    </PersistGate>
  </Provider>,
  document.getElementById('root')
);
