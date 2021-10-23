import { createStore } from 'redux';   // ストア機能を import

// ステートの初期値
let init_state = {
  // 各メモをリストで管理
  data_list: [{
    memo_text: "xxx",                // メモのテキスト内容
    created_time: new Date(),       // メモの作成時刻
  }]
}

//-----------------------------------------
// レデューサー
//-----------------------------------------
function reducer(state = init_state, action) {
  console.log("[reducer] state", state)
  console.log("[reducer] action", action)
  // action : レデューサーを呼び出す際の情報をまとめたオブジェクト
  // action.type : action オブジェクトに必ず用意されているプロパティで、レデューサーを呼び出す際の呼び出しの種類を表している。これらの値は、App.js 内の `this.props.dispath({type:"xxx"})` で定義している
  switch (action.type) {
    case 'ADD_MEMO': // 
      // state の新しい値を return する
      return addMemo(state, action);
    case 'DELETE_MEMO':
      // state の新しい値を return する
      return deleteMemo(state, action);
    default:
      return state;
  }
}

//-----------------------------------------
// レデューサー内部から呼び出される各種メソッド
//-----------------------------------------
// メモを追加するメソッド
function addMemo(state, action){
  let new_data = {
    memo_text: action.memo_text,
    created_time: new Date(),
  }

  // リスト.slice() で state 内の変数のリストのコピーインスタンスを作成
  // Redux では state の値を直接変えて setState() で state の更新を行っても、state の更新なしと判断してしまうため、state オブジェクトのコピーを作成して、そのオブジェクトを更新するようにする
  let new_data_list = state.data_list.slice();

  // unshift() でリストの先頭に値を追加
  new_data_list.unshift(new_data)
  console.log("[reducer:addMemo] new_data_list", new_data_list)

  // 新たな state を return
  return {
    data_list: new_data_list,
  }
}

// メモを削除するメソッド
function deleteMemo(state, action){
  // リスト.slice() で state 内の変数のリストのコピーインスタンスを作成
  // Redux では state の値を直接変えて setState() で state の更新を行っても、state の更新なしと判断してしまうため、state オブジェクトのコピーを作成して、そのオブジェクトを更新するようにする
  let new_data_list = state.data_list.slice();

  // splice() でリストの要素を削除
  // action.select_index : メモの番号
  new_data_list.splice(action.select_index, 1);

  // 新たな state を return  
  return {
    data_list: new_data_list,
  }
}

//-----------------------------------------
// アクションクリエイター
// this.props.dispatch({action}) 呼び出し時の action の値を定義するメソッド　
//-----------------------------------------
export function addMemoAction(memo_text){
  return {
    type: 'ADD_MEMO',
    memo_text:memo_text
  }
}

export function deleteMemoAction(select_index){
  return {
    type: 'DELETE_MEMO',
    select_index:select_index
  }
}

//-----------------------------------------
// `ストア変数名 = createStore(レデューサー関数名)` の形式でストアを作成
// export default で外部ファイルに公開
//-----------------------------------------
let store = createStore(reducer);
export default store;
