import './App.css';
import React from 'react'
import Memo from './Memo'
import AddMemoForm from './AddMemoForm'
import DeleteMemoForm from './DeleteMemoForm'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hook Memo App</h1>
        <AddMemoForm />
        <p></p>
        <DeleteMemoForm />
        <Memo />
      </header>
    </div>
  );
}

export default App;
