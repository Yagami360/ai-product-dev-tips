import React, { Component } from 'react';
import './App.css';

// App コンポーネント
class App extends Component {
  constructor(props){
    super(props);
  }

  render() {
    return (
      <div>
        <p>Hello React Firebase App!</p>
        <p><Id id="1" /> : <Name name="Yagami" /></p>
      </div>
    );
  }
}

// ID 表示のコンポーネント
class Id extends Component {
  render(){
    return (
      <div>
        id={this.props.id}
      </div>
    );
  }
}

// ID 表示のコンポーネント
class Name extends Component {
  render(){
    return (
      <div>
        name={this.props.name}
      </div>
    );
  }
}

export default App;
