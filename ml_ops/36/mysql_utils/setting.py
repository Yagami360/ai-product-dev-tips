# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from mysql_utils.config import MySQLConfig

# engine 作成
engine = create_engine(
    MySQLConfig.database_url,
    encoding="utf-8",
    pool_recycle=3600,
    echo=True,                # True : 実行のたびにSQLが出力される
)

# Session クラス作成
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# sessionmaker インスタンスを内包した scoped_session インスタンスを生成
# sessionmaker との違いは、Session() を何回実行しても同一の Session が返されるという点
global_session = scoped_session(Session)

# Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）を作成
Base = declarative_base()

# 予め Base クラスに query プロパティを仕込んでおく
#Base.query = global_session.query_property()

def get_session():
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def get_context_session():
    """
    with 構文で使う session
    with get_context_session() as session
        ...
    の形式で使用する
    """
    session = Session()
    try:
        yield session
    except:
        session.rollback()      # session.commit() 失敗時は、MySQL のデータをもとに戻す
        raise
    finally:
        session.close()
