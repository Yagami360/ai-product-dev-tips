# 【Firebase】Firebase Authentication を使用してウェブアプリに Authentication 機能を導入する

## 1. ログイン方法の設定

1. [Authenticationコンソール画面](https://console.firebase.google.com/project/sample-app-73cab/authentication/providers?hl=ja) から各種ログイン方法を「有効」にする。<br>
    <img src="https://user-images.githubusercontent.com/25688193/107348240-1caee100-6b0a-11eb-9b61-8a7d3163422d.png" width="500"><br>

1. GitHub を有効にする場合の設定<br>
    GitHub を有効にする場合は、GitHub のクライアントIDとクライアントシークレットが必要になる。<br>
    <image src="https://user-images.githubusercontent.com/25688193/107350003-3d783600-6b0c-11eb-8b29-f4fbfd400164.png" width="500"><br>

    クライアントIDとクライアントシークレットは、GitHub 上の「Settings -> Developer settings -> OAuth Apps」で、「Register a new OAuth application」作成後に取得できる。この際の Homepage URL には、今作成している firebase アプリの URL を指定し、Authorization callback URL には、上記画面で提示されているコールバック URL を貼り付ければよい。<br>
    <image src="https://user-images.githubusercontent.com/25688193/107350167-6e586b00-6b0c-11eb-8a41-a1f61e942b07.png" width="800"><br>

<!--
1. Twitter を有効にする場合の設定<br>
    1. [Twitter ディベロッパーサイト](https://developer.twitter.com/en/apps) へアクセス
    1. 「Create an app」ボタンをクリック
    1. xxx
-->

## 2. Web アプリでの Authentication の利用（クライアント側から Authentication を利用する場合）
Firebase での Authentication は、以下の２つのパターンで利用できる。<br>

1. クライアント側から Authentication を利用<br>
    ウェブページの HTML `<script>` タグを設置するか、ことで、クライアント側から Authentication を利用する方法

1. サーバー側から Authentication を利用<br>
    Node.js で Firebase API を読み込み、サーバー側から Authentication を利用する方法

この内、「クライアント側から Authentication を利用する方法」では、ログインのための GUI などが Firebase によって予め提供されるので、こちらの方法のほうが便利で簡単である。<br>
そのため、以下ではこの方法での手順を記載する。

### 2-1. メールアドレスでのログイン



### 2-2. 電話番号でのログイン

### 2-3. Google アカウントでのログイン

### 2-4. GitHub アカウントでのログイン

### 2-5. GitHub アカウントでのログイン
xxx

## ■ 参考サイト
- xxx
