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

#================================================================
# "http://host_ip:port_id" リクエスト送信時の処理
#================================================================
@app.route('/')
def hello_world():
    target = os.environ.get('TARGET', 'Flask-API Server')
    #return 'Hello Flask-API Server! (host={}, port={})\n'.format(args.host, args.port)
    return 'Hello Flask-API Server!\n'

if __name__ == "__main__":
    #--------------------------
    # Flask の起動
    #--------------------------
    app.run()
    #app.run( host=args.host, port=args.port, threaded=False )
