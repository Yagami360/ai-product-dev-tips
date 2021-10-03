# 【Firebase】Firebase Hosting と Firebase Cloud Function を使用して GKE 上の http 通信での WebAPI からの出力を返す GUI 付きウェブアプリを作成する（リバースプロキシとしての cloud function 経由で API を呼び出す）

Web アプリ上から外部の API を呼び出す際は、https 通信である必要がある。そのため https 化されていない GKE 上の Web-API を Web アプリ上から呼び出すことができないという問題がある。

GKE 上の Web-API を https 化することでもこの問題は解決できるが、一般的に https 化するは少々面倒な手続きが必要になる。

ここでは、firebase cloud function に https 通信 -> http 通信へのリバースプロキシとして役割をさせることで、GKE 上の Web-API を https 化することなく、手軽に Web アプリ上から外部の http 通信での API を呼び出す方法を記載する


<img src="https://user-images.githubusercontent.com/25688193/135239832-fcb39288-587b-475f-83d9-18753cb937f2.png" width="500"><br>

## ■ 方法

1. WebAPI のコードを作成する
    - `app.py`
        ```python
        ```

1. GKE 上に http 通信での WebAPI をデプロイする
    ```sh
    $ deploy_api_gke.sh
    ```

1. FireBase プロジェクトを作成する
    FireBase のコンソール画面から新規の FireBase プロジェクトを作成する

1. FireBase プロジェクトのデフォルトリージョンを設定する
    FireBase のコンソール画面から新規の FireBase プロジェクトを作成する

1. npm と Firebase CLI をインストールする
    ```sh
    # npm のインストール（MacOSの場合）
    $ brew install npm

    # Firebase CLI のインストール
    $ sudo npm install -g firebase-tools
    ```

1. FireBase を初期化し、静的な Web サイト `index.html` と Cloud Function `index.js` のテンプレートを作成する
    ```sh
    # Firebase へのログイン
    $ firebase login --project ${PROJECT_ID}

    # Firebase プロジェクトを初期化
    $ firebase init --project ${PROJECT_ID}
    ```

    > `Firebase Hosting` と `Cloud Functions for Firebase` の機能を有効にして初期化する

1. `public` ディレクトリ以下に、静的なウェブサイト `index.html` を作成する
    ```html
    ```

1. Cloud Function `index.js` にリクエスト処理を行う javascript を作成する<br>
    `index.js` で定義した firebase cloud function を利用して、API にリクエスト処理を行う javascript `js/request.js` を作成する。このスクリプトは、静的なウェブサイト `index.html` から呼び出される

    - `js/request.js`
        ```js
        // HTML の読み込みが全て完了した後に request.js が実行されるようにすうｒために $(function(){} で宣言
        $(function(){
            console.log("load page");

            // ${".xxx"} : `<body>` タグ内の class 名が `pose_panel_select` の要素にアクセス
            var $pose_selectPanel = $('.pose_panel_select');

            //-------------------------------------------------
            // 変数 $pose_selectPanel の要素をクリックしたとき
            //-------------------------------------------------
            $pose_selectPanel.on('click', function(e) {
                // その他の CSS の枠色をクリア
                $pose_selectPanel.css('border', '4px rgba(0,0,0,0) solid');
                $("#selected_file_pose_image_canvas").css('border', '4px rgba(0,0,0,0) solid')

                // クリックした要素のCSSを変更
                $(this).css('border', '4px blue solid');

                // Radio ボタンの選択を消す 
                document.getElementById('pose_select_0').checked = false;
                document.getElementById('pose_select_1').checked = false;
                document.getElementById('pose_select_2').checked = false;
                document.getElementById('pose_select_3').checked = false;
                document.getElementById('pose_select_4').checked = false;
                document.getElementById('pose_select_5').checked = false;

                console.log( this );
                console.log( this.children );
                console.log( this.children[0] );
                console.log( this.children[0].id );
                document.getElementById(this.children[0].id).checked = true;
            });

            //-------------------------------------------------
            // 読み込み人物画像ファイル選択時に呼び出される関数（jQuery 使用）
            //-------------------------------------------------
            jQuery('#selected_file_pose_image').on('change', function(e) {
                // FileReader オブジェクトの作成
                var reader = new FileReader();
                reader.readAsDataURL(e.target.files[0]);    // ファイルが複数読み込まれた際に、1つ目を選択
                reader.onload = function (e) {  // 読み込みが成功時の処理
                    img_src = e.target.result;
                    drawToCanvas( img_src, "selected_file_pose_image_canvas" );
                }

                // 要素のCSSを変更
                $pose_selectPanel.css('border', '4px rgba(0,0,0,0) solid');
                $("#selected_file_pose_image_canvas").css('border', '4px blue solid');
            });
        });

        //============================================
        // 出力画像生成ボタンクリック時に呼び出される関数
        //============================================
        function generateOutputImage() {
            console.log( "背景除去画像の生成開始" );

            // API の URL 取得
            var api_url = document.getElementById("api_url").value;
            var cloud_function_url = document.getElementById("cloud_function_url").value;

            //---------------------------------------
            // 選択されている人物画像を取得
            //---------------------------------------
            radio_btn_pose0 = document.getElementById("pose_select_0");
            radio_btn_pose1 = document.getElementById("pose_select_1");
            radio_btn_pose2 = document.getElementById("pose_select_2");
            radio_btn_pose3 = document.getElementById("pose_select_3");
            radio_btn_pose4 = document.getElementById("pose_select_4");
            radio_btn_pose5 = document.getElementById("pose_select_5");
            console.log( "radio_btn_pose0.checked : ", radio_btn_pose0.checked );
            console.log( "radio_btn_pose1.checked : ", radio_btn_pose1.checked );
            console.log( "radio_btn_pose2.checked : ", radio_btn_pose2.checked );
            console.log( "radio_btn_pose3.checked : ", radio_btn_pose3.checked );
            console.log( "radio_btn_pose4.checked : ", radio_btn_pose4.checked );
            console.log( "radio_btn_pose5.checked : ", radio_btn_pose5.checked );

            var pose_img_base64
            if( radio_btn_pose0.checked == true ) {
                // Canvas から画像データを取得
                var pose_img_canvas = document.getElementById("selected_file_pose_image_canvas");
                pose_img_base64 = pose_img_canvas.toDataURL('image/png').replace(/^.*,/, '');
                //console.log( "pose_img_base64 : ", pose_img_base64 );
            }
            else if( radio_btn_pose1.checked == true ) {
                var pose_img = document.getElementById('pose_image_1');
                pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
            }
            else if( radio_btn_pose2.checked == true ) {
                var pose_img = document.getElementById('pose_image_2');
                pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
            }
            else if( radio_btn_pose3.checked == true ) {
                var pose_img = document.getElementById('pose_image_3');
                pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
            }
            else if( radio_btn_pose4.checked == true ) {
                var pose_img = document.getElementById('pose_image_4');
                pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
            }
            else if( radio_btn_pose5.checked == true ) {
                var pose_img = document.getElementById('pose_image_5');
                pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
            }
            else{
                var pose_img = document.getElementById('pose_image_1');
                pose_img_base64 = convImageToBase64( pose_img, 'image/png' ).replace(/^.*,/, '');
            }

            //--------------------------------------------------------
            // GKE 上の WebAPI に https 送信（リバースプロキシとしての firebase cloud function 経由で API を呼び出す）
            //--------------------------------------------------------
            try {
                $.ajax({
                    url: cloud_function_url,            
                    type: 'POST',
                    dataType: "json",
                    data: JSON.stringify({
                        "api_url" : api_url,
                        "pose_img_base64": pose_img_base64,
                    }),
                    contentType: 'application/json',
                    crossDomain: true,  // API サーバーとリクエスト処理を異なるアプリケーションでデバッグするために必要
                    timeout: 60000,
                })
                .done(function(data, textStatus, jqXHR) {
                    // 通信成功時の処理を記述
                    console.log( "Cloud Function との通信成功" );
                    console.log( data );
                    //console.log( data.img_none_bg_base64 );
                    console.log( textStatus );
                    console.log( jqXHR );
                    
                    if (data.status == "ok" ) {
                        dataURL = `data:image/png;base64,${data.img_none_bg_base64}`
                        drawToCanvas( dataURL, "output_image_canvas" )
                    }
                    else{
                        console.log( "Web-API の推論処理失敗" );                
                        alert("Web-API の推論処理に失敗しました")
                    }
                })
                .fail(function(jqXHR, textStatus, errorThrown) {
                    // 通信失敗時の処理を記述
                    console.log( "Cloud Function との通信失敗" );
                    //console.log( textStatus );
                    console.log( jqXHR );
                    //console.log( errorThrown );
                    alert("Cloud Function との通信に失敗しました\n" + cloud_function_url )
                });
            } catch (e) {
                console.error(e)
                alert(e);
            }
        }
        ```

        > WebAPI の URL `http:${HOST}:5000/predict` ではなく、Cloud Function `index.js` の URL `https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}` に対してリクエスト処理を行っている点に注意。これにより、リバースプロキシとしての cloud function 経由で WebAPI を呼び出す事ができ、http -> https での通信が可能となる。

    - `js/utils.js`
        ```python
        ```

1. `public` ディレクトリ以下に、静的なウェブサイト `index.html` で利用する各種リソースのファイルを保管する<br>
    `public` ディレクトリ以下 に `index.html` で利用する各種リソースのファイル（javascript, css, 画像データ等）を保管する

1. `functions` ディレクトリ以下に、firebase cloud functionhttps 通信 -> http 通信へのリバースプロキシとして役割を行う `index.js` を作成する。<br>
    `functions` ディレクトリ以下に、https 通信 -> http 通信へのリバースプロキシとして役割を行う firebase cloud function `index.js` を作成する。
    ```js
    const functions = require("firebase-functions");
    const request = require('request');

    // HTTP トリガーでのレスポンス処理
    exports.call_api = functions.https.onRequest((req, res) => {
        // リクエストデータ解析
        //functions.logger.info("req : ", req);
        //functions.logger.info("req.body['pose_img_base64'] : ", req.body["pose_img_base64"]);
        functions.logger.info("req.body['api_url] : ", req.body["api_url"]);

        // CORS 設定    
        res.set('Access-Control-Allow-Origin', '*');
        if (req.method === 'OPTIONS') {
            // Send response to OPTIONS requests
            res.set('Access-Control-Allow-Methods', 'GET');
            res.set('Access-Control-Allow-Headers', 'Content-Type');
            res.set('Access-Control-Max-Age', '3600');
            res.status(204).send('');
        }

        // API のヘルスチェック
        request.get({
            uri: req.body["api_url"] + "/health",
            headers: { "Content-type": "application/json" },
        }, function(error_api, res_api, body_api) {
            if ( !error_api && res_api.statusCode == 200 ) {
                functions.logger.info("[health check] API との通信に成功しました");
                functions.logger.info("[health check] error_api : ", error_api);
                //functions.logger.info("[health check] res_api : ", res_api);
                functions.logger.info("[health check] body_api : ", body_api);
            }
            else {
                functions.logger.info("[health check] API との通信に失敗しました");
                functions.logger.info("[health check] error_api : ", error_api);
                //functions.logger.info("[health check] res_api : ", res_api);
                functions.logger.info("[health check] body_api : ", body_api);
            }
        });

        // API の推論処理
        request.post({
            uri: req.body["api_url"] + "/predict",
            headers: { "Content-type": "application/json" },
            json: {"image": req.body["pose_img_base64"]},       // JSON.stringify({"image": req.body["pose_img_base64"]}),
        }, function(error_api, res_api, body_api) {
            if ( !error_api && res_api.statusCode == 200 ) {
                functions.logger.info("[predict] API との通信に成功しました");
                functions.logger.info("[predict] error_api : ", error_api);
                //functions.logger.info("[predict] res_api : ", res_api);
                //functions.logger.info("[predict] body_api : ", body_api);

                // レスポンス処理
                res.send(
                    JSON.stringify({
                        "status": "ok",
                        "img_none_bg_base64" : body_api["img_none_bg_base64"],                
                    })
                );
            }
            else {
                functions.logger.info("[predict] API との通信に失敗しました");
                functions.logger.info("[predict] error_api : ", error_api);
                //functions.logger.info("[predict] res_api : ", res_api);
                //functions.logger.info("[predict] body_api : ", body_api);

                // レスポンス処理
                res.send(
                    JSON.stringify({
                        "status": "ng",
                        "img_none_bg_base64" : null,                
                    })
                );
            }
        });

    });
    ```

    > Node.js において、定義した関数を外部から使用可能にするためには、`exports.${関数名} = functions` の形式で定義する必要がある。

    > Node.js の `request` モジュールを用いてリクエスト処理を行っている

    > この cloud function `index.js` へのリクエスト処理は、静的な Web サイト `index.html` から呼び出される `js/request.js` 内にて、cloud function の URL `https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}` から行う

    
1. firebase cloud function `index.js` で追加使用する各種モジュールをインストールする
    ```sh
    $ cd functions
    $ npm install --save request request-promise
    $ ..
    ```

1. Firebase Hosting を利用して、作成した静的な Web サイト `index.html` と firebase cloud function `index.js` をデプロイする
    ```sh
    $ firebase deploy --project ${PROJECT_ID}
    ```

    > 「Firebase のプラン」を Blaze（従量制）にしておく必要があることに注意

1. Web サイトを表示する
    ```sh
    # Hosting URL を開く
    $ open https://${PROJECT_ID}.web.app
    ```

1. Web サイトの GUI を利用して出力画像を生成する
    1. 「GraphCut API サーバーの URL を指定」に、GKE 上の Web-API の URL `http://${HOST}:5000` を設定する
    1. 「Firebase Cloud Function の URL を指定」に、Cloud Function の URL `https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}` を設定する
    1. 人物画像を指定する
    1. 「背景除去画像を生成」ボタンをクリックし、出力画像を生成する

1. 【オプション】Cloud Function のログデータを確認する
    - CLI を使用する場合
        ```sh
        $ firebase functions:log --only ${FUNCTION_NAME}
        ```

    - GUI を使用する場合
        ```sh
        $ open https://console.firebase.google.com/project/${PROJECT_ID}/functions/logs?hl=ja&functionFilter=${FUNCTION_NAME}(${ZONE})&search=&severity=DEBUG
        ```

1. 【オプション】WebAPI のログデータを確認する
    - コンテナログの確認
        ```sh
        $ kubectl logs `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` graph-cut-api-container
        ```

    - API ログファイルの確認
        ```sh
        $ kubectl exec -it `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` /bin/bash
        $ cat log/app.log
        ```