# coding=utf-8
from sqlalchemy import Column, Integer, String, Float, DateTime

from mysql_utils.config import MySQLConfig
from mysql_utils.setting import engine, Base
from mysql_utils.models import JobTable


def init(checkfirst=True):
    """
    MySQL のデータベースにテーブルデータを登録する。
    Base を継承したテーブルデータクラス定義後に、一度実行する必要がる
    """
    # Base を継承したテーブルデータクラス全てが、MySQL のデータベースに登録される
    # create_all() を１度実行済みで、テーブルを再作成する場合は　checkfirst=False を設定
    Base.metadata.create_all(bind=engine, checkfirst=checkfirst)
    return

def delete_all(session, commit=True):
    session.query(JobTable).delete()
    if(commit):
        session.commit()
    return

def insert(session, job_id=0, image_in=None, image_out=None, elapsed_time=None, commit=True):
    """
    MySQL データベースにテーブルデータを INSERT する（書き込む）
    """
    #table = JobTable(job_id=job_id, image_in=image_in, image_out=image_out, elapsed_time=elapsed_time)
    table = JobTable(job_id=job_id, elapsed_time=elapsed_time)
    session.add(table)
    if(commit):
        session.commit()
        session.refresh(table)
    return table

def select_first(session):
    """
    MySQL データベースに保存されている最初のレコードのテーブルデータを SELECT する（読み込む）
    """
    # テーブルデータの最初のレコードのオブジェクトで返す
    table = session.query(JobTable).first()
    return table

def select_all(session):
    """
    MySQL データベースに保存されている全レコードのテーブルデータを SELECT する（読み込む）
    """
    # テーブルデータの全レコードのオブジェクトが入った配列で返す
    table = session.query(JobTable).all()
    return table

def select_job_id(session, job_id):
    """
    指定した Job ID 値に一致する MySQL データベースに保存されているテーブルデータを SELECT する（読み込む）
    """
    return session.query(JobTable).filter(JobTable.job_id == job_id).first()