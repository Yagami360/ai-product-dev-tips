# Web サーバーの基礎事項

- WebSocket 通信<br>
    双方向のHTTPプロトコルで、クライアントとサーバー間でリアルタイム通信を行うための技術。<br>
    
    - HTTPとは異なり、`ws://` あるいは `wss://` から始まる。<br>
    - クライアントとサーバ間の接続はどちらか一方が切断されると終了する<br>
    - リアルタイムで更新が必要なアプリケーション（チャットアプリ等）で有用になる

    <!--
    - ヘッダー
        - Upgradeヘッダ : HTTPからWebSocketへのプロトコルのアップグレード
        - Connectionヘッダが存在する事で、この二つでHTTPからWebSocketへのプロトコルのアップグレードを表現している。アップグレードって言われると良く分からないけど、ただのHTTPでないんだって事をサーバーに伝えたいんだなーくらいに思っておけばOK。

    - フレーム<br>

    -->

- HTTP クッキー（Cookie）<br>
    <img width="577" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/54f3d0b5-12d0-4c31-b09b-67912ebe3173"><br>
    サーバーがユーザーのウェブブラウザーに送信する小さなデータであり、ブラウザーに保存され、その後のリクエストと共に同じサーバーへ返送される。


## 参考サイト
- WebSocket
    https://qiita.com/south37/items/6f92d4268fe676347160