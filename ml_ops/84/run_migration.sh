#!/bin/sh
set -eu
PROJECT_NAME=migrations
MIGRATION_FILE_NAME="create_table"

#=============================
# PostgreSQL
#=============================
mkdir -p postgresql

# PostgreSQL サーバー起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# PostgreSQL サーバーに接続する
#docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"

#=============================
# alembic
#=============================
# alembic をインストールする
pip install alembic
pip install psycopg2

# alembic プロジェクトを作成する
if [ -e ${PROJECT_NAME} ] ; then
    alembic init ${PROJECT_NAME}
fi
#cd ${PROJECT_NAME}

# make sqlalchemy scripts and edit env.py

# モデルクラスの内容を元にマイグレーションスクリプトファイルを作成する
alembic revision --autogenerate -m ${MIGRATION_FILE_NAME}

# マイグレーションスクリプトを元に DB マイグレーションを行う（PostgreSQL データベースに反映する）
alembic upgrade head

#=============================
# PostgreSQL
#=============================
# PostgreSQL サーバーに接続する
docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"
