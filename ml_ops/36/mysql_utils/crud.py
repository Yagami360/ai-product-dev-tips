# coding=utf-8
from sqlalchemy import Column, Integer, String, Float, DateTime

from mysql_utils.config import MySQLConfig
from mysql_utils.setting import engine, Base
from mysql_utils.models import LogTable


def init(checkfirst=True):
    """
    MySQL のデータベースにテーブルデータを登録する。
    Base を継承したテーブルデータクラス定義後に、一度実行する必要がる
    """
    # Base を継承したテーブルデータクラス全てが、MySQL のデータベースに登録される
    # create_all() を１度実行済みで、テーブルを再作成する場合は　checkfirst=False を設定
    Base.metadata.create_all(bind=engine, checkfirst=checkfirst)
    return

def insert(session, id=0, data=None, commit=True):
    """
    MySQL データベースにテーブルデータを INSERT する（書き込む）
    """
    data = LogTable(log_id=id, log=data)
    session.add(data)
    if(commit):
        session.commit()
        session.refresh(data)
    return data

def select_first(session):
    """
    MySQL データベースに保存されている最初のレコードのテーブルデータを SELECT する（読み込む）
    """
    # テーブルデータの最初のレコードのオブジェクトで返す
    data = session.query(LogTable).first()
    return data

def select_all(session):
    """
    MySQL データベースに保存されている全レコードのテーブルデータを SELECT する（読み込む）
    """
    # テーブルデータの全レコードのオブジェクトが入った配列で返す
    data = session.query(LogTable).all()
    return data
