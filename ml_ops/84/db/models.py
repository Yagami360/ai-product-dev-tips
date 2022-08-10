# coding=utf-8
from sqlalchemy import Column, Integer, String, Float, DateTime
from .setting import engine, session, Base

class UserData(Base):
    """
    MySQL でテーブルデータを定義したモデルクラス
    """
    __tablename__ = "userdata"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', String(200))
    age = Column('age', Integer)
    