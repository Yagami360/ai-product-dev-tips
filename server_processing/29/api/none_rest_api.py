import os
import sys
import json

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
args = None

#================================================================
# "http://host_ip:port_id" リクエスト送信時の処理
#================================================================
@app.route('/add_user')
def add_user():
    # ユーザーの登録処理
    return "ユーザーの登録処理"

@app.route('/get_user')
def get_user():
    # ユーザーの取得処理
    return "ユーザーの取得処理"

@app.route('/update_user')
def update_user():
    # ユーザーの更新処理
    return "ユーザーの更新処理"

@app.route('/delete_user')
def delete_user():
    # ユーザーの削除処理
    return "ユーザーの削除処理"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="80", help="ポート番号")
    parser.add_argument('--enable_threaded', action='store_true', help="並列処理有効化")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    args = args
    #--------------------------
    # Flask の起動
    #--------------------------
    app.debug = args.debug
    if( args.enable_threaded ):
        app.run( host=args.host, port=args.port, threaded=False )
    else:
        app.run( host=args.host, port=args.port, threaded=True )
