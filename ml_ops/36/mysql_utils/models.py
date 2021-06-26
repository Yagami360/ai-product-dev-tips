# coding=utf-8
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.types import JSON

from mysql_utils.setting import Base

class LogTable(Base):
    """
    MySQL のデータベースに保存するテーブルデータを定義したモデルクラス
    """
    # クラス変数
    __tablename__ = "log_table"
    log_id = Column( String(255), primary_key=True)     # ログデータの識別 ID
    log = Column( JSON, nullable=False)                 # ログデータ（json）
    datetime = Column( DateTime(timezone=True), server_default=current_timestamp(), nullable=False)     # タイムスタンプ
