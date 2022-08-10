# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from .config import MySQLConfig

# engine 作成
engine = create_engine(
    MySQLConfig.database_url,
    encoding = "utf-8",
    echo = True               # True : 実行のたびにSQLが出力される
)

# Session クラス作成
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# sessionmaker インスタンスを内包した scoped_session インスタンスを生成
# sessionmaker との違いは、Session() を何回実行しても同一の Session が返されるという点
session = scoped_session(Session)

# Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）を作成
Base = declarative_base()

# 予め Base クラスに query プロパティを仕込んでおく
Base.query = session.query_property()
