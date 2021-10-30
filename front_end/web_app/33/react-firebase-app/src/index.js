import React from 'react';
import ReactDOM from 'react-dom';
import firebase from "firebase";
import './index.css';
import App from './App';

// Firebaseの初期化
var firebaseConfig = {
    apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
    authDomain: "react-firebase-app-2cc53.firebaseapp.com",
    databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
    projectId: "react-firebase-app-2cc53",
    storageBucket: "react-firebase-app-2cc53.appspot.com",
    messagingSenderId: "686383733508",
    appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
    measurementId: "G-MCWN891SRK"   
};

firebase.initializeApp(firebaseConfig);
  
// 表示をレンダリング
ReactDOM.render(
    <App />,
    document.getElementById('root')
);
