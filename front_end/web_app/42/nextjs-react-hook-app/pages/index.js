import React from 'react';
import firebase from "firebase";
import Firestore from '../components/Firestore';

// Firebaseの初期化
const firebaseConfig = {
  apiKey: "AIzaSyBSKhjSkI0pERNnYhcrl3Uldl47ZyGvNqE",
  authDomain: "react-firebase-app-2cc53.firebaseapp.com",
  databaseURL: "https://react-firebase-app-2cc53-default-rtdb.firebaseio.com",
  projectId: "react-firebase-app-2cc53",
  storageBucket: "react-firebase-app-2cc53.appspot.com",
  messagingSenderId: "686383733508",
  appId: "1:686383733508:web:a1d5c2ec271201d87b4e51",
  measurementId: "G-MCWN891SRK"   
};

if (firebase.apps.length == 0) {
  firebase.initializeApp(firebaseConfig);
}

// ルートページ
export default function Home() {
  return (
    <div className="App">
      <h1>Next.js & Firebase Sample App</h1>
      <Firestore collectionName="sample-database" />
    </div>
  );
}