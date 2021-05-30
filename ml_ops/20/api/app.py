import os
import sys
import argparse
import json
import time, datetime

# Clloud Pub/Sub
from google.cloud import pubsub_v1

# flask
import flask
from flask_cors import CORS

#======================
# グローバル変数
#======================
#-------------------
# flask 関連
#-------------------
app = flask.Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}}, methods=['POST', 'GET'])  # OPTIONS を受け取らないようにする（Access-Control-Allow-Origin エラー対策）
app.config['JSON_AS_ASCII'] = False     # 日本語文字化け対策
app.config["JSON_SORT_KEYS"] = False    # ソートをそのまま

#================================================================
# "http://host_ip:port_id" リクエスト送信時の処理
#================================================================
@app.route('/')
def hello_world():
    target = os.environ.get('TARGET', 'World')
    return 'Hello {}!\n'.format(target)

#================================================================
# "http://host_ip:port_id/api_server" にリクエスト送信時の処理
#================================================================
@app.route('/api_server', methods=['POST'])
def responce():
    print( "リクエスト受け取り" )
    if( app.debug ):
        print( "flask.request.method : ", flask.request.method )
        print( "flask.request.headers \n: ", flask.request.headers )

    # ブラウザから送信された json データの取得
    if( flask.request.headers["User-Agent"].split("/")[0] in "python-requests" ):
        json_data = json.loads(flask.request.json)
    else:
        json_data = flask.request.get_json()

    #------------------------------------------
    # json 形式のレスポンスメッセージを作成
    #------------------------------------------
    http_status_code = 200
    response = flask.jsonify(
        {
            'status':'OK',
            'json_data': json_data,
        }
    )
    
    # レスポンスメッセージにヘッダーを付与（Access-Control-Allow-Origin エラー対策）
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    #response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response, http_status_code

def callback(message):
    """
    トピックにメッセージが届いたときに呼び出されるコールバック関数
    """
    # ACK メッセージを送信（受信メッセージの処理が完全に完了したことを通知）
    message.ack()
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="80", help="ポート番号")
    parser.add_argument('--enable_threaded', action='store_true', help="並列処理有効化")
    parser.add_argument("--project_id", default="my-project2-303004", help="GCP のプロジェクトID")
    parser.add_argument("--sub_name", type=str, default="sub-sample", help="サブスクリプション名")
    parser.add_argument("--credentials_file_path", type=str, default="", help="Pub/Sub のjson鍵のファイルパス")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # subscriber のインスタンス作成
    subscriber = pubsub_v1.subscriber.Client.from_service_account_file(args.credentials_file_path)
    subpath = subscriber.subscription_path(args.project_id, args.sub_name)
    flow_control = pubsub_v1.types.FlowControl(max_messages=2)

    # トピックのメッセージを subscribe (pop) する
    #subscriber.subscribe(subpath, callback=callback, flow_control = flow_control)

    #--------------------------
    # Flask の起動
    #--------------------------
    app.debug = args.debug
    if( args.enable_threaded ):
        app.run( host=args.host, port=args.port, threaded=False )
    else:
        app.run( host=args.host, port=args.port, threaded=True )
    