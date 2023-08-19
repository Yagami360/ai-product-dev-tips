import argparse
import io
import json

import flask
from flask_cors import CORS
from PIL import Image

app = flask.Flask(__name__)

# OPTIONS を受け取らないようにする（Access-Control-Allow-Origin エラー対策）
CORS(
    app,
    resources={r"*": {"origins": "https://chat.openai.com"}},
    methods=["POST", "GET", "DELETE"],
)
# 日本語文字化け対策
app.config["JSON_AS_ASCII"] = False
# ソートをそのまま
app.config["JSON_SORT_KEYS"] = False

# TODO List（API 起動時は空）
_TODOS = {}

# ---------------------------------------
# ChatGPT Plugin API で共通に必要な API
# ---------------------------------------


@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        json_text = f.read()

    resp = flask.Response(response=json_text, status=200, mimetype="application/json")
    return resp


@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    with open("openapi.yaml") as f:
        yaml_text = f.read()

    resp = flask.Response(response=yaml_text, status=200, mimetype="text/yaml")
    return resp


@app.route("/logo.png", methods=["GET"])
def plugin_logo():
    img_pillow = Image.open("logo.png")
    img_io = io.BytesIO()
    img_pillow.save(img_io, "PNG")
    img_io.seek(0)

    resp = flask.Response(response=img_io, status=200, mimetype="image/png")
    return resp


# ---------------------------------------
# TODO API
# ---------------------------------------

# TODO 追加 API
@app.route("/todos/<username>", methods=["POST"])
def add_todo(username):
    print(f"[add_todo] username={username}")
    if flask.request.headers["Content-Type"] != "application/json":
        resp = flask.Response(response="NG", status=400, mimetype="application/json")
        return resp

    # リクエスト body の todo 内容を取得
    json_body = flask.request.get_json()
    print(f"[add_todo] json_body={json_body}")
    todo = json_body["todo"]

    # _TODOS の配列に {"username": ["todo1", "todo2", ...]} の形式で追加
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(todo)

    resp = flask.Response(response="OK", status=200)
    return resp


# TODO 取得 API
@app.route("/todos/<username>", methods=["GET"])
def get_todos(username):
    resp = flask.Response(response=json.dumps(_TODOS.get(username, [])), status=200)
    return resp


# TODO 削除 API
@app.route("/todos/<username>", methods=["DELETE"])
def delete_todo(username):
    if flask.request.headers["Content-Type"] != "application/json":
        resp = flask.Response(response="NG", status=400, mimetype="application/json")
        return resp

    # リクエスト body の todo 内容を取得
    json_body = flask.request.get_json()
    todo_idx = json_body["todo_idx"]

    # delete todo
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)

    resp = flask.Response(response="OK", status=200)
    return resp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）"
    )
    parser.add_argument("--port", type=str, default="5000", help="ポート番号")
    args = parser.parse_args()

    # API サーバー起動
    app.run(host=args.host, port=args.port, debug=True)
