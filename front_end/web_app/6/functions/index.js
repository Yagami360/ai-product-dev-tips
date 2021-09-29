const functions = require("firebase-functions");
const request = require('request');

//var API_ENDPOINT_URL = 'http://0.0.0.0:5000/predict';
var API_ENDPOINT_URL = 'http://35.232.16.150:5000/predict';

// HTTP トリガーでのレスポンス処理
exports.call_api = functions.https.onRequest((req, res) => {
    // リクエストデータ解析
    functions.logger.info("req : ", req);

    // CORS 設定    
    res.set('Access-Control-Allow-Origin', '*');
    if (req.method === 'OPTIONS') {
        // Send response to OPTIONS requests
        res.set('Access-Control-Allow-Methods', 'GET');
        res.set('Access-Control-Allow-Headers', 'Content-Type');
        res.set('Access-Control-Max-Age', '3600');
        res.status(204).send('');
    }

    // API にリクエスト
    request.post({
        uri: API_ENDPOINT_URL,
        headers: { "Content-type": "application/json" },
        json: {
            // JSONをPOSTする場合書く
        }
    }, (err, res, data) => {
        console.log(data);
    });

});
