import React, { Component } from 'react';
import { connect } from 'react-redux';

// ユーザーデータ表示のコンポーネント
class User extends Component {
  render(){
    return (
      <p>id={this.props.id}, name={this.props.name}</p>
    );
  }
}

// StateComponent コンポーネントにストアを接続する
// 第１引数に state の内容をそのまま返す mappingState() メソッドを設定することで、StateComponent コンポーネント内の this.props に index.js 内のレデューサーで定義した state が設定される
User = connect((state)=> state)(User);

// App を外部ファイルから利用できるようにする
export default User;
