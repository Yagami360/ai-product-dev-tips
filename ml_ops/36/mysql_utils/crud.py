# coding=utf-8
import os
import argparse
from sqlalchemy import Column, Integer, String, Float, DateTime

from config import MySQLConfig
from setting import engine, session, Base
from models import LogData


def insert(session=session, id=0, data=None):
    """
    MySQL サーバーに指定したテーブルデータを INSERT する（書き込む）
    """
    data = LogData(log_id=id, log=data)
    session.add(data)
    session.commit()
    return

def select_first(session):
    """
    MySQL サーバーに保存されている最初のレコードのテーブルデータを SELECT する（読み込む）
    """
    # LogData の最初のレコードをクラスで返す
    data = session.query(LogData).first()
    return data

def select_all(session):
    """
    MySQL サーバーに保存されている全レコードのテーブルデータを SELECT する（読み込む）
    """
    # LogData の全レコードをクラスが入った配列で返す
    data = session.query(LogData).all()
    return data