import React from 'react';
import ReactDOM from 'react-dom';
import firebase from "firebase";                    // for version 8.x
//import { initializeApp } from 'firebase/app';     // for version 9.x
import './index.css';
import App from './App';

console.log("firebase version", firebase.SDK_VERSION )

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


firebase.initializeApp(firebaseConfig);           // for version 8.x
//initializeApp(firebaseConfig);                  // for version 9.x

// 表示をレンダリング
ReactDOM.render(
    <App />,
    document.getElementById('root')
);
