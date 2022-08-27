#!/bin/sh
set -eu
PROJECT_NAME="elixir_ecto_postgresql"
ECTO_REPO_NAME="ElixirEctoPostgresql"
MIGRATION_NAME="create_person_migration"
TABLE_NAME="postgresql_table"

#=============================
# OS判定
#=============================
if [ "$(uname)" = 'Darwin' ]; then
	OS='Mac'
	echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
	OS='Linux'
	echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then                                                                                           
	OS='Cygwin'
	echo "Your platform is Cygwin."  
else
	echo "Your platform ($(uname -a)) is not supported."
	exit 1
fi

#=============================
# PostgreSQL
#=============================
mkdir -p postgresql/db
rm -rf postgresql/db

# PostgreSQL サーバー起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
#sleep 5

#=============================
# Elixir
#=============================
#-----------------------------
# Elixir をインストールする
#-----------------------------
elixir --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
  	    brew install elixir
    elif [ ${OS} = "Linux" ] ; then
        # Erlang をインストール
        wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb && sudo dpkg -i erlang-solutions_1.0_all.deb
        sudo apt-get update
        sudo apt-get install esl-erlang

        # elixir をインストール
        sudo apt-get install elixir
    fi
fi
echo "elixir version : `elixir --version`"

#-----------------------------
# node.js をインストールする
#-----------------------------
npm --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
		brew install node
    elif [ ${OS} = "Linux" ] ; then
        sudo apt update
        sudo apt install nodejs
        sudo apt install npm
    fi
fi
echo "npm version : `npm --version`"

#-----------------------------
# Phoenix
#-----------------------------
# Phoenix をインストールする
#mix phx.new -v &> /dev/null
#if [ $? -ne 0 ] ; then
#	mix local.hex --force
#	mix archive.install hex phx_new --force
#fi
#mix phx.new -v

#-----------------------------
# Ecto
#-----------------------------
# Elixir プロジェクトを作成する
mix new ${PROJECT_NAME} --sup
cd ${PROJECT_NAME}

# `mix.exe` を修正する
:

# プロジェクトの各種ライブラリ（Ecto, PostgreSQL）をインストールする
#mix deps.get

# Repo モジュールと config を作成する
#mix ecto.gen.repo -r ${ECTO_REPO_NAME}.Repo

# config.exs を修正する
:

# PostgreSQL データベースを作成する
mix ecto.create

# マイグレーションファイルを作成する
mix ecto.gen.migration ${MIGRATION_NAME}

# マイグレーションファイルを修正する
:

# マイグレーションを実行し、PostgreSQL データベース内にテーブルを作成する
mix ecto.migrate

# PosgreSQL サーバーにログイン
#docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"