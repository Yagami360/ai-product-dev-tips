import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Link } from "react-router-dom";
import HomePage from './pages/HomePage'
import AboutPage from './pages/AboutPage'

const App: React.FC = () => {
  //------------------------
  // JSX での表示処理
  //------------------------
  return (
    <BrowserRouter>
      {/* ルーティング設定 */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
      { /* リスト */}
      <ul>
        <li>
          <Link to="/">Home</Link>          {/* 別ページへのリンク */}
        </li>
        <li>
          <Link to="/about">About</Link>    {/* 別ページへのリンク */}
        </li>
      </ul>
    </BrowserRouter>
    );
}

export default App;
