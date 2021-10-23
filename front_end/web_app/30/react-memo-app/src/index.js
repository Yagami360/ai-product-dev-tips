import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';                 // プロバイダー機能を import
import './index.css';
import App from './App';
import Store from './Store'

// 表示をレンダリング
ReactDOM.render(
  // プロバイダーは、`<Provider store={ストアの変数名}>xxx</Provider>` タグとその store 属性で定義し、このタグ内の xxx の箇所で定義されているコンポーネントにストアの内容が渡される。
  // この例では、App.js で定義されている App コンポーネントにストアの内容が渡される
  <Provider store={Store}>
    <App />
  </Provider>,
  document.getElementById('root')
);