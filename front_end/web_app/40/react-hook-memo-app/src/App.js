import './App.css';
import React, { useState } from 'react'
import useLocalPersist from './LocalPersist';
import Memo from './Memo'
import AddMemoForm from './AddMemoForm'
import DeleteMemoForm from './DeleteMemoForm'

function App() {
  const [mode, setMode] = useLocalPersist('mode', 'default')

  return (
    <div className="App">
      <header className="App-header">
        <h1>React Hook Memo App</h1>
        <h5>mode: {mode}</h5>
        <AddMemoForm />
        <p></p>
        <DeleteMemoForm />
        <Memo />
      </header>
    </div>
  );
}

export default App;
