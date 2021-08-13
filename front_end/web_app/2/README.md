# 【Firebase】Cloud Storage for Firebase を使用してウェブアプリ上で使用する画像データを表示する

## 方法

1. Firebase プロジェクトを初期化する
    ```sh
    $ firebase login --project ${PROJECT_ID}
    $ firebase init --project ${PROJECT_ID}
    ```

1. Cloud Storage for Firebase にウェブサイト上で表示させたい画像をデータをアップロードする<br>
    1. GUI で行う場合<br>
        左側のタブの「Storage」をクリックして「スタートガイド」ボタンをクリックするとダイアログが表示される。ダイアログに従って Cloud Storage 利用手続きを行うと、以降は Cloud Stogage の設定画面が表示されるので、「ファイルをアップロード」ボタンをクリックし、画像データをアップロードする<br>
        <img src="https://user-images.githubusercontent.com/25688193/128618408-1cf69ef6-d3d6-4ce3-962e-a81d0c61f0d6.png" width="500"><br>
        <img src="https://user-images.githubusercontent.com/25688193/128618449-ee7c2cd4-3e83-4b71-a1e2-ed6b962d483c.png" width="300"><br>

    1. CLI で行う場合<br>
        ```sh
        ```

1. セキュリティールールを設定する<br>
    Web アプリ上で認証なしに画像データのアップロードやダウンロードを行えるように、以下のようにセキュリティールールを変更する

    > 今回はテスト環境用として、誰でも認証なしに画像データにアクセスできるようにしているが、本番環境では適切なセキュリティールールになるように留意する必要があることに注意

    1. GUI で行う場合<br>
        <img src="https://user-images.githubusercontent.com/25688193/128670221-05bb0598-2fda-4c20-87f1-71165803f9b2.png" width="600"><br>

        - 変更前
            ```js
            rules_version = '2';
            service firebase.storage {
                match /b/{bucket}/o {
                    match /{allPaths=**} {
                        allow read, write: if request.auth!=null;
                    }
                }
            }
            ```

        - 変更後
            ```js
            rules_version = '2';
            service firebase.storage {
                match /b/{bucket}/o {
                    match /{allPaths=**} {
                        allow read, write;
                    }
                }
            }
            ```

    1. CLI で行う場合<br>
        ```sh
        ```

1. CORS [Cross-Origin Resource Sharing] の設定を行う。<br>
    デフォルトでは、設定されているドメイン以外からのアクセスが制限されているので、CORS [Cross-Origin Resource Sharing] の設定を行い、Web サーバー側に外部からのアクセスを許可するように変更する。

    1. CORS 設定ファイル `cors.json` （ファイル名は任意）を作成する
        ```json
        [
            {
                "origin": ["https://${PROJECT_ID}.firebaseapp.com", "http://localhost:5000"],
                "responseHeader": ["*"],
                "method": ["GET", "PUT", "POST", "DELETE"],
                "maxAgeSeconds": 3600
            }
        ]
        ```
        - `tps://xxxx.firebaseapp.com` : Web アプリの公開 URL

    1. CORS 設定ファイル `cors.json` を Web アプリにデプロイする
        ```sh
        $ gsutil cors set cors.json gs://${PROJECT_ID}.appspot.com
        ```
        - `gs://${PROJECT_ID}.appspot.com` : Cloud Storage のパケット URL

        正しくデプロイできたかは、以下のコマンドで確認できる。
        ```sh
        $ gsutil cors get gs://${PROJECT_ID}.appspot.com 
        ```

1. Cloud Storage の画像ファイルを表示するための HTML ファイル `index.html` を作成する<br>    
    1. firebase storage のコンソール画面から取得可能な ダウンロード URL を直接指定する場合<br>
        firebase storage のコンソール画面から取得可能な ダウンロード URL を、`<img src="ダウンロードURL" id="xxx">` の src 属性に直接指定することで、firebase storage 上の画像を HTML で表示できる<br>
        <img src="https://user-images.githubusercontent.com/25688193/129292031-026560d6-fe88-480c-a3f8-f9117a13829e.png" width="500"><br>

        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <title>Cloud Storage の画像を表示</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- Firebase -->
            <!-- update the version number as needed -->
            <script defer src="/__/firebase/8.2.6/firebase-app.js"></script>
            <!-- include only the Firebase features as you need -->
            <script defer src="/__/firebase/8.2.6/firebase-auth.js"></script>
            <script defer src="/__/firebase/8.2.6/firebase-storage.js"></script>
            <!-- 
            initialize the SDK after all desired features are loaded, set useEmulator to false
            to avoid connecting the SDK to running emulators.
            -->
            <script defer src="/__/firebase/init.js?useEmulator=true"></script>
            
        </head>
        <body>
            <h1>Cloud Storage の画像を表示</h1>
            <div class="box_pose">
                <img src="https://firebasestorage.googleapis.com/v0/b/sample-app-73cab.appspot.com/o/000001_0.jpg?alt=media&token=d0666316-78ba-4041-bb9c-0d28ebbb5beb" id="pose_image_1">
                <img src="https://firebasestorage.googleapis.com/v0/b/sample-app-73cab.appspot.com/o/000010_0.jpg?alt=media&token=e5ba1a81-a05a-4188-ad85-e53a0d58a518" id="pose_image_2">
                <img src="https://firebasestorage.googleapis.com/v0/b/sample-app-73cab.appspot.com/o/000020_0.jpg?alt=media&token=4edb38a0-1c84-48d7-ba61-65fbe2cc915f" id="pose_image_3">
                <img src="https://firebasestorage.googleapis.com/v0/b/sample-app-73cab.appspot.com/o/000028_0.jpg?alt=media&token=c91ad187-2af4-47d6-b73c-a30fb8bfca56" id="pose_image_4">
                <img src="https://firebasestorage.googleapis.com/v0/b/sample-app-73cab.appspot.com/o/000038_0.jpg?alt=media&token=c17aca9d-2f59-485a-b703-227015c1aabe" id="pose_image_5">
            </div>  

            <!-- Firebase -->
            <p id="load">Firebase SDK Loading&hellip;</p>
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                const loadEl = document.querySelector('#load');
                // // 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
                // // The Firebase SDK is initialized and available here!
                //
                // firebase.auth().onAuthStateChanged(user => { });
                // firebase.database().ref('/path/to/ref').on('value', snapshot => { });
                // firebase.firestore().doc('/foo/bar').get().then(() => { });
                // firebase.functions().httpsCallable('yourFunction')().then(() => { });
                // firebase.messaging().requestPermission().then(() => { });
                // firebase.storage().ref('/path/to/ref').getDownloadURL().then(() => { });
                // firebase.analytics(); // call to activate
                // firebase.analytics().logEvent('tutorial_completed');
                // firebase.performance(); // call to activate
                //
                // // 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

                try {
                    let app = firebase.app();
                    let features = [
                        'auth', 
                        'database', 
                        'firestore',
                        'functions',
                        'messaging', 
                        'storage', 
                        'analytics', 
                        'remoteConfig',
                        'performance',
                    ].filter(feature => typeof app[feature] === 'function');
                    loadEl.textContent = `Firebase SDK loaded with ${features.join(', ')}`;
                } catch (e) {
                    console.error(e);
                    loadEl.textContent = 'Error loading the Firebase SDK, check the console.';
                }
            });
            </script>
        </body>
        </html>
        ```

        > `<script defer src="/__/firebase/8.2.6/firebase-app.js"></script>` と `<script defer src="/__/firebase/8.2.6/firebase-storage.js"></script>` で、firebase のコアライブラリと Cloud Storage 機能を有効化している

    1. `getDownloadURL()` で取得した画像のダウンロード URL を使用する場合<br>

        > [ToDo] : 現状のコードではうまく画像表示されないので、修正すること

        `index.html` に以下の `<script>` タグを追加し、`getDownloadURL()` で取得した画像の URL を、`<img>` タグの src 属性 `<img src="getDownloadURL()で取得した画像のURL" id="xxx">` に設定することでも画像を表示できる

        ```html
        <script>
        function loaded(file_name){
            var storage = firebase.storage();
            var imgRef = storage.ref(file_name);
            imgRef.getDownloadURL().then((url)=> {
                document.querySelector('#msg').textContent = url;
                var xhr = new XMLHttpRequest();
                xhr.responseType = 'blob';
                xhr.onload = (event)=> {
                    var blob = xhr.response;
                    let im = document.querySelector('#img');
                    im.src = URL.createObjectURL(blob);
                };
                xhr.open('GET', url);
                xhr.send();
            }).catch(function(error) {
            // Handle any errors
            });
        }      
        </script>
        ```

        > `let im = document.querySelector('#img');` と `im.src = URL.createObjectURL(blob);` の部分で、`getDownloadURL()` で取得した画像のURLを `<img>` タグの src 属性に設定している。これを使用するには `<body onload="loaded(xxx);">` 内で `<img id="xxx">` のように src を指定せずに宣言すれば良い


1. Firebase Hosting で作成したウェブサイト `index.html` をデプロイする
    ```sh
    $ firebase deploy --project ${PROJECT_ID}
    ```

1. Hosting URL を開く
    ```sh
    $ open https://${PROJECT_ID}.web.app
    ```
