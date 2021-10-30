import React, { Component } from 'react';
import './App.css';
import FirebaseDatabase from './FirebaseDatabase';

// App コンポーネント
class App extends Component {
  constructor(props){
    super(props);
  }

  render() {
    return (
      <div>
        <p>Hello React Firebase App!</p>
        <FirebaseDatabase db_name="sample-database" />
      </div>
    );
  }
}

export default App;
