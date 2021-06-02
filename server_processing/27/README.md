# 【uWSGI】WSGI / uWSGI の基本事項

<img src="https://user-images.githubusercontent.com/25688193/113583847-1b5ee800-9665-11eb-9a73-3b47c60942ce.png" width="400"><br>

- WSGI [Web Server Gateway Interface]<br>
    Python で記述された Web アプリケーションと Web サーバー間との通信仕様を定めた通信プロトコル。この WSGI に従ったアプリケーションを動作させたサーバーを WSGI サーバーという<br>
    Flask や Django などのほとんどの Python 製 Web フレームワークは、この WSGI という通信プロトコルに則っている。<br>

- ASGI [Asynchronous Server Gateway Interface]<br>
    WSGI の拡張プ通信ロトコルで、非同期処理に対応した通信プロトコル。この ASGI に従ったアプリケーションを動作させたサーバーを ASGI サーバーという。<br>
    FastAPI は、ASGI に準拠した Web フレームワークになっている

- uWSGI<br>
    WSGI サーバーの１種で、アプリケーションサーバー（Flask, Django など）とウェブサーバ（nginxなど）をつなぐサーバ。<br>
    uWSGI は、Web サーバーとアプリケーションサーバーに対して、HTTP 通信と UNIXドメインソケット通信の方法で通信することができる

    - UNIXドメインソケット通信<br>
        高速でアプリケーションサーバーとWebサーバー間の通信を行うことが可能であるが、直接リクエストしたりレスポンスを参照することができないため、トラブルが起きた際のデバッグコストが高い

    - HTTP<br>
        http （非SSL）での通信。ソケット通信より速度面では劣るが、最新のサーバーでは殆ど問題とはならないことが多い。

- Gunicorn<br>
    WSGI サーバーの１種。

## ■ 手順
ここでは、簡単な例として、nginx などの Web サーバーを経由しない場合での、uWSGI + Flask を用いた Web-API の構築方法を示す。<br>
より実践的な方法については、「[【uWSGI】docker + nginx + uWSGI + Flask を用いた Web-API の構築](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/28)」を参照のこと。

1. Flask-API サーバーの構築<br>
    1. Flask のインストール
        ```sh
        $ pip install flask
        $ pip install Flask-Cors
        ```
    1. Flask-API のコード `app.py` を作成する。<br>
        ここでは、簡単な例として `api/app.py` に "Hello Flask-API Server! (host=${ホスト名}, port=${ポート番号})" を表示するような Flask-API を作成する

    1. Flask-API を起動する<br>
        ```sh
        $ cd api/
        $ python app.py
        ```
        > このコマンドでの Flask-API の起動は、後述のリクエスト処理で Flask-API のサーバーに直接リクエスト処理を行った場合の動作確認用に起動しているだけで、後述の `uwsgi` コマンドで uWSGI の起動すれば、uWSGI 経由で Flask-API サーバーが自動的に起動されるので、このコマンドでの Flask-API の起動は必要ないことに注意

1. uWSGI の構築<br>
    1. `uwsgi` コマンドのインストール<br>
        ```sh
        $ pip install uWSGI
        ```
    1. uWSGI の起動<br>
        `uwsgi` コマンドを用いて、Flask-API のコード `app.py` を uWSGI 経由で起動する。<br>
        1. uWSGI の設定ファイル（`*.ini`形式）を用いない場合
            ```sh
            # http 通信で uWSGI を起動
            $ cd api
            $ uwsgi --http=localhost:5001 --wsgi-file=app.py --callable=app
            ```
            - `--wsgi-file` : wsgi で動作するファイル（＝Flask API コード `app.py`）
            - `--callable` : Flask アプリケーション名（＝`app.py` で定義した `app = Flask(__name__)` の名前のこと）

            コマンド実行後、以下のような出力が確認されれば、uWSGI が正しく起動された状態になっている。（Ctrl+C で起動状態を停止可能）
            ```sh
            *** Starting uWSGI 2.0.18 (64bit) on [Sat Apr 10 13:45:09 2021] ***
            compiled with version: 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final) on 22 July 2019 16:37:28
            os: Darwin-20.3.0 Darwin Kernel Version 20.3.0: Thu Jan 21 00:07:06 PST 2021; root:xnu-7195.81.3~1/RELEASE_X86_64
            nodename: sakaiyuusukenoMacBook-Pro.local
            machine: x86_64
            clock source: unix
            pcre jit disabled
            detected number of CPU cores: 8
            current working directory: /Users/sakai/GitHub/MachineLearning_Tips/server_processing/27/api
            detected binary path: /Users/sakai/.pyenv/versions/anaconda3-5.3.1/bin/uwsgi
            *** WARNING: you are running uWSGI without its master process manager ***
            your processes number limit is 2784
            your memory page size is 4096 bytes
            detected max file descriptor number: 10496
            lock engine: OSX spinlocks
            thunder lock: disabled (you can enable it with --thunder-lock)
            uWSGI http bound on 0.0.0.0:5001 fd 4
            spawned uWSGI http 1 (pid: 55529)
            uwsgi socket 0 bound to TCP address 127.0.0.1:50650 (port auto-assigned) fd 3
            Python version: 3.7.3 | packaged by conda-forge | (default, Jul  1 2019, 14:38:56)  [Clang 4.0.1 (tags/RELEASE_401/final)]
            *** Python threads support is disabled. You can enable it with --enable-threads ***
            Python main interpreter initialized at 0x7fdf76d09d10
            your server socket listen backlog is limited to 100 connections
            your mercy for graceful operations on workers is 60 seconds
            mapped 72904 bytes (71 KB) for 1 cores
            *** Operational MODE: single process ***
            WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0x7fdf76d09d10 pid: 55528 (default app)
            *** uWSGI is running in multiple interpreter mode ***
            spawned uWSGI worker 1 (and the only) (pid: 55528, cores: 1)
            ```
            
        1. uWSGI の設定ファイル（`*.ini`形式）を用いる場合
            ```sh
            $ cd api
            $ uwsgi --ini uwsgi.ini
            ```

            uWSGI の設定ファイル（`*.ini`形式）には、例えば、以下のような設定を記載できる。<br>
            ※ より細かな設定に関しては、「[uWSGI の設定ファイル（`*.ini`形式）](#uWSGI設定ファイル)」に記載
            ```ini
            [uwsgi]
            
            # wsgiファイル
            wsgi-file=app.py
            callable=app
            
            # アクセス許可ホスト:ポート
            http=localhost:5001
            ```

        > `uwsgi` コマンドを用いて `app.py` を実行する場合は、`app.py` で `import argparse` して定義しているコマンドライン引数は使えないことに注意。<br>
        > `app.py` でコマンドライン引数を使いたい場合は、Python の `sys.argv` を使用し、uWSGI の設定ファイル（`*.ini`形式）内で、`pyargv "args1 args2"` という形式のオプションを追加する方法がある。<br>

        > `uwsgi` コマンドで `app.py` を実行する際に、以下のような import エラーが発生する場合は、conda などの仮想環境と uwsgi & flask のインストール環境のズレが原因である可能性が高い。<br>
        > その場合は、一旦 `pip uninstall` と `conda uninstall` で flask と uwsgi をアンイストールして、再度インストール処理を行えば良い可能性が高い。
        > ```sh
        > Traceback (most recent call last):
        >   File "app.py", line 2, in <module>
        >     import flask
        >   ...
        > ImportError: dlopen(/Users/sakai/.pyenv/versions/anaconda3-5.3.1/> lib/python3.7/lib-dynload/math.cpython-37m-darwin.so, 2): Symbol > not found: _PyExc_MemoryError
        > ```
        > ```sh
        > Traceback (most recent call last):
        > File "app.py", line 2, in <module>
        >     import flask
        > ModuleNotFoundError: No module named 'flask'
        > ```
        
1. リクエスト処理<br>
    1. Flask-API サーバーに直接アクセスする場合<br>
        ```sh
        $ curl http://localhost:5000
        ```
    1. uWSGI 経由で Flask-API にアクセスする場合<br>
        ```sh
        $ curl http://localhost:5001
        ```


- Todo : uwsgi コマンドで Flask-API を実行する際に、app,py で以下のような import エラーが発生する問題の解消
    ```sh
    Traceback (most recent call last):
    File "app.py", line 3, in <module>
        import argparse
    File "/Users/sakai/.pyenv/versions/anaconda3-5.3.1/envs/py36/lib/python3.6/argparse.py", line 93, in <module>
        from gettext import gettext as _, ngettext
    File "/Users/sakai/.pyenv/versions/anaconda3-5.3.1/envs/py36/lib/python3.6/gettext.py", line 49, in <module>
        import locale, copy, io, os, re, struct, sys
    File "/Users/sakai/.pyenv/versions/anaconda3-5.3.1/envs/py36/lib/python3.6/struct.py", line 13, in <module>
        from _struct import *
    ImportError: dlopen(/Users/sakai/.pyenv/versions/anaconda3-5.3.1/envs/py36/lib/python3.6/lib-dynload/_struct.cpython-36m-darwin.so, 2): Symbol not found: _PyByteArray_Type
    Referenced from: /Users/sakai/.pyenv/versions/anaconda3-5.3.1/envs/py36/lib/python3.6/lib-dynload/_struct.cpython-36m-darwin.so
    Expected in: flat namespace
    in /Users/sakai/.pyenv/versions/anaconda3-5.3.1/envs/py36/lib/python3.6/lib-dynload/_struct.cpython-36m-darwin.so
    unable to load app 0 (mountpoint='') (callable not found or import error)
    *** no app loaded. going in full dynamic mode ***
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI worker 1 (and the only) (pid: 97932, cores: 1)
    ```

<a id="uWSGI設定ファイル"></a>

### ◎ uWSGI の設定ファイル（`*.ini`形式）

- デーモン化（バックグラウンド実行）する場合
    ```ini
    [uwsgi]
    ```

- xxx
    ```ini
    [uwsgi]
    ```

## ■ 参考サイト
- https://www.python.ambitious-engineer.com/archives/1959
- https://qiita.com/morinokami/items/e0efb2ae2aa04a1b148b
- https://serip39.hatenablog.com/entry/2020/07/06/070000
