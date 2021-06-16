# Fluentd を使用して Web-API からのログデータを転送する（FastAPI + uvicorn + gunicorn + Fluentd + docker + docker-compose での構成）

Fluentd を使用して Web-API からのログデータを転送する方法を実現するためには、以下のようにいくつかの構成パターンが考えられるが、ここでは、API 構成パターン１（Web-API のコンテナ + fluentd サーバーのコンテナ）での　API を構成する

- API 構成パターン１（Web-API のコンテナ + fluentd サーバーのコンテナ）<br>
	<img src="https://user-images.githubusercontent.com/25688193/122184459-30f35800-cec7-11eb-8656-283946cf359d.png" width="500"><br>

	- Web-API には fluentd をインストールしない
	- fluentd サーバーのコンテナを別途作成
	- Web-API の log ファイルの転送は、fluentd サーバーではなくディレクトリのマウントで行う。詳細には、Web-API の log ファイルを docker-compose の `volumes` タグでローカル環境のディレクトリにマウントし、ローカル環境のディレクトリを更に fluentd サーバーのログディレクトリ `/var/log` にマウントする。
	- fluentd サーバーで `/var/log` 内のログデータを `/fluentd/log` に転送する<br>
	- 【Option】fluentd サーバーで `/fluentd/log` 内のログデータを GCP に転送する<br>

	> k8s で API を構成する場合は、ローカル環境のディレクトリのマウントはできないので、同じような構成で API を構成できなくなる。
	> その場合は、k8s のサイドカーを使って、Web-API サーバーのコンテナと fluentd サーバーのコンテナ間でディスクを共有すればよい

- API 構成パターン２（Web-API のコンテナ に fluentd をインストール）<br>
	- Web-API に fluentd をインストールし、Web-API のコンテナ内で fluentd サーバーを起動する
	- fluentd サーバーのコンテナは別途作成しない
	- Web-API のコンテナ内で fluentd サーバーで Web-API の log ファイルを fluentd サーバーのログディレクトリ `/fluentd/log` に転送する
	- Web-API コンテナ内の fluentd サーバーのログディレクトリ `/fluentd/log` をローカル環境のディレクトリにマウントする
	- 【Option】Web-API コンテナ内の fluentd サーバーで `/fluentd/log` 内のログデータを GCP に転送する
	- 複数の Web-API のコンテナが存在する場合は、それぞれの fluentd サーバーのログディレクトリ `/fluentd/log` を、それぞれ異なるローカル環境のディレクトリにマウントする<br>

	> Web-API の dockerfile にわざわざ fluentd のインストールを追加する必要がある

	> Web-API のログデータを `/fluentd/log` に転送するだけなら、わざわざ fluentd サーバーを用いなくても、cp や mv でも可能

## 方法

1. Web API の設定<br>
    1. Web API のコードを作成する<br>
		ここでは、簡単な例として FastAPI を使用した Web-API のコードを作成する。<br>
		`logging` モジュールを使用して Web-API のログデータを `log/app.log` に出力するようにしている点に注目

		- FastAPI での Web-API コード : `app.py`<br>
			```python
			# coding=utf-8
			import os
			import sys
			import argparse
			from datetime import datetime
			import logging
			import uuid

			from fastapi import FastAPI

			# 自作モジュール
			from utils.logger import log_base_decorator

			#--------------------------
			# logger
			#--------------------------
			if( os.path.exists(os.path.join("log", __name__ + '.log')) ):
				os.remove(os.path.join("log", __name__ + '.log'))
			logger = logging.getLogger(__name__)
			logger.setLevel(10)
			logger_fh = logging.FileHandler(os.path.join("log", __name__ + '.log'))
			logger.addHandler(logger_fh)
			logger.info("{} {} start api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", __name__))

			#--------------------------
			# FastAPI
			#--------------------------
			app = FastAPI()

			users_db = {
				"name" : {
					0 : "user1",
					1 : "user2",
					2 : "user3",
				},
				"age" : {
					0 : "24",
					1 : "30",
					2 : "18",
				},
			}

			#======================================
			# GET method
			#======================================
			@app.get("/")
			def root():
				return 'Hello Flask-API Server!\n'

			@log_base_decorator(logger=logger)
			def _health():
				return {"health": "ok"}

			@app.get("/health")
			def health():
				return _health()

			@log_base_decorator(logger=logger)
			def _metadata():
				return users_db

			@app.get("/metadata")
			def metadata():
				return _metadata()

			@app.get("/users_name/{users_id}")
			def get_user_name_by_path_parameter(
				users_id: int,  # パスパラメーター
			):
				return users_db["name"][users_id]

			@app.get("/users_name/")
			def get_user_name_by_query_parameter(
				users_id: int, # クエリパラメーター
			):
				return users_db["name"][users_id]

			@app.get("/users/{attribute}")
			def get_user_by_path_and_query_parameter(
				attribute: str, # パスパラメーター
				users_id: int,  # クエリパラメーター
			):
				return users_db[attribute][users_id]

			#======================================
			# POST method
			#======================================
			from pydantic import BaseModel
			# `pydantic.BaseModel` 継承クラスでリクエストボディを定義
			class UserData(BaseModel):
				id: int
				name: str
				age: str

			@log_base_decorator(logger=logger)
			def _add_user(
				user_data: UserData,
			):
				users_db["name"][user_data.id] = user_data.name
				users_db["age"][user_data.id] = user_data.age
				return users_db

			@app.post("/add_users/")
			def add_user(
				user_data: UserData,     # リクエストボディ
			):
				return _add_user(user_data=user_data)

			```

		- Python デコレーターで使用するロギング処理メソッド : `utils/logger.py`<br>
			```python
			# coding=utf-8
			import os
			import time
			from datetime import datetime
			from logging import getLogger

			def log_base_decorator(logger):
				"""
				メソッド先頭で `@logging` デコレーターを付与することで使用可能になる logger
				"""
				def _logging(func):
					def _wrapper(*args, **kwds):
						start_time = time.time()
						logger.info("{} {} {} {} args={} kwds={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", func.__qualname__, "START", args, kwds))

						# `@logging` デコレーターを付与したメソッドで return されたときに call される
						rtn = func(*args, **kwds)
						elapsed_time = 1000 * (time.time() - start_time)
						logger.info("{} {} {} {} elapsed_time [ms]={:.5f}, return {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", func.__qualname__, "END", elapsed_time, rtn))
						return rtn

					return _wrapper

				return _logging
			```


	1. Web-API の Dockerfile を作成する<br>
		docker-compose で Web-API を起動するための `Dockerfile` を作成する
		```Dockerfile
		#-----------------------------
		# Docker イメージのベースイメージ
		#-----------------------------
		FROM python:3.8-slim
		#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

		#-----------------------------
		# 基本ライブラリのインストール
		#-----------------------------
		# インストール時のキー入力待ちをなくす環境変数
		ENV DEBIAN_FRONTEND noninteractive

		RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
			sudo \
			git \
			curl \
			wget \
			bzip2 \
			ca-certificates \
			libx11-6 \
			python3-pip \
			# imageのサイズを小さくするためにキャッシュ削除
			&& apt-get clean \
			&& rm -rf /var/lib/apt/lists/*

		RUN pip3 install --upgrade pip

		#-----------------------------
		# 環境変数
		#-----------------------------
		ENV LC_ALL=C.UTF-8
		ENV export LANG=C.UTF-8
		ENV PYTHONIOENCODING utf-8

		#-----------------------------
		# 追加ライブラリのインストール
		#-----------------------------
		RUN pip3 install fastapi
		RUN pip3 install uvicorn
		RUN pip3 install Gunicorn
		RUN pip3 install requests

		#-----------------------------
		# ソースコードの書き込み
		#-----------------------------
		#WORKDIR /api
		#COPY *.py /api/

		#-----------------------------
		# ポート開放
		#-----------------------------
		EXPOSE 5000

		#-----------------------------
		# コンテナ起動後に自動的に実行するコマンド
		#-----------------------------
		# docker-compose で起動定義するのでコメントアウト
		#CMD ["gunicorn","app:app","--bind","0.0.0.0:5000","-w","1","-k","uvicorn.workers.UvicornWorker","--reload"]

		#-----------------------------
		# コンテナ起動後の作業ディレクトリ
		#-----------------------------
		WORKDIR /api
		```

1. fluentd の設定ファイル `fluent.conf` を作成する<br>
	```conf
	# 標準入力 -> fluentd 集約ログファイル（デバッグ用）
	<source>
	type forward
	port 24224
	</source>

	<match debug.**>
	type file
	path /fluentd/log/debug.*.log
	</match>

	# Web-API のログファイル -> fluentd 集約ログファイル
	<source>
	type tail
	format none
	path /var/log/app.log
	tag app.log
	</source>

	<match app.**>
	type file
	path /fluentd/log/app.*.log
	</match>
	```

	ポイントは、以下の通り

	- `<source>` の `type` で `tail` を指定することで、Web-API からローカル環境経由で `/var/log/app.log` にマウントした Web-API のログファイルを入力データそして指定している。
	- 更に `<match app.**>` で、`type file` を指定して `path` として `/fluentd/log/app.*.log` を指定することで、`/var/log/app.log` を `/fluentd/log/app.*.log` ファイルに転送する設定にしている
	- デバッグ用に `echo '{"log_message":"sample"}' | fluent-cat debug` などのコマンドで、標準入力から `/fluentd/log/debug.*.log` ファイルへの書き込みを行うことも可能にしている

1. `docker-compose.yml` を作成する<br>
	Web-API と fluentd サーバー用の `docker-compose.yml` を作成する。
    ```yaml
    version: '2.3'
    services:
	  fast-api-server:
	    container_name: fast-api-container
	    image: fast-api-image
	    build:
  	      context: "api/"
	      dockerfile: Dockerfile
	    volumes:
		  - ${PWD}/api:/api
	    ports:
	      - "5000:5000"
	    tty: true
	    environment:
	      TZ: "Asia/Tokyo"
	      LC_ALL: C.UTF-8
	      LANG: C.UTF-8
		depends_on:
	      - fluentd-server
	    command: bash -c "gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"

	  fluentd-server:
	    container_name: fluentd-container
	    image: fluent/fluentd:latest
	    volumes:
	      - ${PWD}/fluentd/log:/fluentd/log
	      - ${PWD}/api/log:/var/log/
	      - ${PWD}/fluentd/fluent.conf:/fluentd/etc/fluent.conf:ro
	    ports:
	      - "127.0.0.1:24224:24224"
	      - "127.0.0.1:24224:24224/udp"
	    tty: true
	    environment:
	      TZ: "Asia/Tokyo"
	      LC_ALL: C.UTF-8
	      LANG: C.UTF-8
    ```

	ポイントは、以下の通り

    - fluent コンテナに関しては、Dockerfile を作成するのではなく、`fluent/fluentd:latest` の docker image を直接使用している

	- Web-API コンテナ内のログデータ `/api/log/app.log` は、`fast-api-server` の `volumes:` タグの `${PWD}/api:/api` で、ローカル環境のディレクトリ `api/log/app.log` にマンうとされる。更に、このローカル環境での Web-API のログファイル `api/log/app.log` は、`fluentd-server` の `volumes:` タグの `${PWD}/api/log:/var/log/` で、fluent コンテナ内の `/var/log/app.log` にマウントされる。最後に、このディレクトリ内のログファイルは、`fluent.conf` で指定した設定により、fluent サーバーで `/fluentd/log` に転送される

	- fluent コンテナ内でのログデータは、`/fluentd/log` 以下に出力されるので、`volumes:` タグで `${PWD}/fluentd/log:/fluentd/log` として、ローカル環境の `${PWD}/fluentd/log` にマウントされるようにしている。これにより、ローカル環境の `${PWD}/fluentd/log` ディレクトリを確認すれば、全ログデータを確認できるようになる

	- fluent コンテナ内での設定ファイル `fluent.conf` は、`/fluentd/etc/fluent.conf` にあるファイルで実行されるので、`volumes:` タグで `${PWD}/fluentd/fluent.conf:/fluentd/etc/fluent.conf:ro` で、ローカル環境での `fluent.conf` にマウントしている（※ `ro` は ReadOnly 属性）。<br>
	これにより、ローカル環境での `fluent.conf` を編集すれば、fluent コンテナのもローカル環境で編集された `fluent.conf` で動作するようになる

	- fluent サーバーは、デフォルトでは `127.0.0.1:24224` で実行されるので、`ports:` タグで `"127.0.0.1:24224:24224"` でローカル環境とコンテナ環境のポートを同期している

    - `fluent/fluentd:latest` の docker image では、自動的に `/bin/entrypoint.sh` が実行され、fluentd サーバーが起動する構成になっている。<br>
	そのため、`command: bash -c "fluentd -c /fluentd/etc/fluent.conf"` などで再度 fluentd サーバーが起動する必要はないことに注意


1. Web-API と fluentd サーバーを起動する<br>
	```sh
	$ docker-compose -f docker-compose.yml stop
	$ docker-compose -f docker-compose.yml up -d
	```

1. Web-API にリクエスト処理する<br>
	```sh
	# health check
	echo "[GET method] ヘルスチェック\n"
	curl http://${HOST}:${PORT}/health
	echo "\n"

	# metadata 取得
	echo "[GET method] metadata 取得\n"
	curl http://${HOST}:${PORT}/metadata
	echo "\n"

	# POST method でのリクエスト処理
	echo "[POST method] ユーザー追加\n"
	curl -X POST -H "Content-Type: application/json" \
		-d '{"id":4, "name":"user4", "age":"100"}' \
		http://${HOST}:${PORT}/add_users/
	```

	これらのリクエスト処理により、ローカル環境の `api/log/app.log` には、以下のようなログデータが書き込まれる
	```sh
	2021-06-16 16:54:49 INFO start api server
	2021-06-16 16:54:54 INFO _health START args=() kwds={}
	2021-06-16 16:54:54 INFO _health END elapsed_time [ms]=0.81348, return {'health': 'ok'}
	2021-06-16 16:54:54 INFO _metadata START args=() kwds={}
	2021-06-16 16:54:54 INFO _metadata END elapsed_time [ms]=0.74697, return {'name': {0: 'user1', 1: 'user2', 2: 'user3'}, 'age': {0: '24', 1: '30', 2: '18'}}
	2021-06-16 16:54:54 INFO _add_user START args=() kwds={'user_data': UserData(id=4, name='user4', age='100')}
	2021-06-16 16:54:54 INFO _add_user END elapsed_time [ms]=0.81968, return {'name': {0: 'user1', 1: 'user2', 2: 'user3', 4: 'user4'}, 'age': {0: '24', 1: '30', 2: '18', 4: '100'}}
	```

1. fluentd サーバー経由で Web-API のログデータが転送されていることを確認する<br>
	上記のローカル環境での `api/log/app.log` は、fluentd コンテナの `var/log/app.log` にマウントされる。<br>
	その後、fluentd サーバーにより fluentd コンテナの `/fluentd/log` に転送される。<br>
	fluentd コンテナの `/fluentd/log` は、ローカル環境の `fluentd/log` にマウントされているので、ローカル環境の `fluentd/log/app.log` には、以下のようなログデータが書き込まれる

	```sh
	2021-06-16T07:54:54+00:00	app.log	{"message":"2021-06-16 16:54:54 INFO _health START args=() kwds={}"}
	2021-06-16T07:54:54+00:00	app.log	{"message":"2021-06-16 16:54:54 INFO _health END elapsed_time [ms]=0.81348, return {'health': 'ok'}"}
	2021-06-16T07:54:54+00:00	app.log	{"message":"2021-06-16 16:54:54 INFO _metadata START args=() kwds={}"}
	2021-06-16T07:54:54+00:00	app.log	{"message":"2021-06-16 16:54:54 INFO _metadata END elapsed_time [ms]=0.74697, return {'name': {0: 'user1', 1: 'user2', 2: 'user3'}, 'age': {0: '24', 1: '30', 2: '18'}}"}
	2021-06-16T07:54:54+00:00	app.log	{"message":"2021-06-16 16:54:54 INFO _add_user START args=() kwds={'user_data': UserData(id=4, name='user4', age='100')}"}
	2021-06-16T07:54:54+00:00	app.log	{"message":"2021-06-16 16:54:54 INFO _add_user END elapsed_time [ms]=0.81968, return {'name': {0: 'user1', 1: 'user2', 2: 'user3', 4: 'user4'}, 'age': {0: '24', 1: '30', 2: '18', 4: '100'}}"}
	```
