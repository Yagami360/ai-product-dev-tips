# 【Firebase】Cloud Storage for Firebase を使用してウェブアプリ上で使用する画像データを表示する

## ■ 方法

1. Firebase プロジェクトを初期化する
    ```sh
    $ firebase login --project ${PROJECT_ID}
    $ firebase init --project ${PROJECT_ID}
    ```

1. 表示させたい画像データを `public` ディレクトリ以下に配置する<br>
    `index.html` が存在する `public` ディレクトリに HTML 上で表示させたい画像ファイル群を配置する

1. `index.html` を作成する<br>
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
            <img src="sample_n5/000001_0.jpg" id="pose_image_1">
            <img src="sample_n5/000010_0.jpg" id="pose_image_2">
            <img src="sample_n5/000020_0.jpg" id="pose_image_3">
            <img src="sample_n5/000028_0.jpg" id="pose_image_4">
            <img src="sample_n5/000038_0.jpg" id="pose_image_5">  
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
    
    > `<img src="xxx">` の src 属性に上記 `public` ディレクトリに配置した画像ファイルのパスを指定する。後述の `firebase deploy` コマンドで、`public` ディレクトリ以下に配置された画像ファイル群もデプロイされるので、`<img src="xxx">` の src 属性でその画像データへの相対パスを指定すれば HTML 上で画像を表示させることが可能になる

1. Firebase Hosting で作成したウェブサイト `index.html` をデプロイする
    ```sh
    $ firebase deploy --project ${PROJECT_ID}
    ```
    > `public` ディレクトリ以下に配置された画像ファイル群もデプロイされるので、`<img src="xxx">` の src 属性でその画像データへの相対パスを指定すれば HTML 上で画像を表示させることが可能になる

1. Hosting URL を開く
    ```sh
    $ open https://${PROJECT_ID}.web.app
    ```
