import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';

// ステート初期値
const init_state = {
  id:0,
  name: "none"
}

// レデューサー
function reducer(state = init_state, action) {
  switch (action.type) {
    case 'ADD_USER':
      return state;
    default:
      return state;
  }
}

// createStore() で作成した store を返すメソッド。lib/redux-store.js の AppWithRedux コンポーネントで利用しているので外部公開する
export function initStore(state = init_state) {
  // applyMiddleware() でミドルウェアを追加する。ここでいうミドルウェアとは、React の処理に途中に入り込んで、実行する処理の内容をカスタマイズするものである。
  // redux-thunk の thunkMiddleware ミドルウェアを追加することで、Next.js で Redux がうまく動作するようになる
  return createStore(reducer, state, applyMiddleware(thunkMiddleware))
}
