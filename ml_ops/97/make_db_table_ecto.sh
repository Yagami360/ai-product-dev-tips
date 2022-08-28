#!/bin/sh
set -eu
PROJECT_NAME="elixir_phoenix_ecto"
MIGRATION_NAME="create_person_tabel_migration"

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

#-----------------------------
# Ecto
#-----------------------------
cd ${PROJECT_NAME}

# PostgreSQL データベースを削除する
mix ecto.drop

# PostgreSQL データベースを作成する
mix ecto.create

# マイグレーションファイルを作成する
set +eu
mix ecto.gen.migration ${MIGRATION_NAME}
set -eu

# マイグレーションファイルを修正する
:

# マイグレーションを実行し、PostgreSQL データベース内にテーブルを作成する
mix ecto.migrate

# Elixir アプリケーションを実行する
iex -S mix
