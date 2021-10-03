const functions = require("firebase-functions");
const request = require('request');

//var API_URL = 'http://0.0.0.0:5000';
//var API_URL = 'http://35.232.16.150:5000';

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
