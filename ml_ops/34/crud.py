# coding=utf-8
import os
import argparse
from sqlalchemy import Column, Integer, String, Float, DateTime
from setting import engine, session, Base

class UserData(Base):
    """
    MySQL でテーブルデータを定義したモデルクラス
    """
    __tablename__ = "userdata"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', String(200))
    age = Column('age', Integer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # テーブルデータをデータベースに作成する
    Base.metadata.create_all(bind=engine)

    # テーブルデータへの INSERT 処理
    user_data = UserData(id=0, name="Tom", age=28)
    session.add(user_data)  
    session.commit()

    # SELECT 処理
    user_data = session.query(UserData).first()      # userテーブルの最初のレコードをクラスで返す
    users_data = session.query(UserData).all()       # userテーブルの全レコードをクラスが入った配列で返す
    print( "[user_data] __tablename__={}, id={}, name={}, age={}".format(user_data.__tablename__, user_data.id, user_data.name, user_data.age) )
    for i, user_data in enumerate(users_data):
        print( "[users_data {}] __tablename__={}, id={}, name={}, age={}".format(i, user_data.__tablename__, user_data.id, user_data.name, user_data.age) )
        