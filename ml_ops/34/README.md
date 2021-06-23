# 【MySQL】SQLAlchemy を使用して Python スクリプトから MySQL に接続する

SQLAlchemy は、Python から MySQL に接続するための ORM 指向の Python 製ライブラリである

> - ORM [Object Relational Mapper]
>     テーブルデータとクラスを1対1に対応させて，そのクラスのメソッド経由でデータを取得したり，変更したりできるようにしてオブジェクト指向ライクに操作できるようにしたもの

## ■ 方法

1. MySQL をインストールする<br>
    - MacOS の場合
        ```sh
        $ MySQL をインストールする
        ```

1. PyMySQL をインストールする<br>
    ```sh
    $ pip install PyMySQL
    ```

1. SQLAlchemy をインストールする<br>
    ```sh
    $ pip install sqlalchemy
    ```

1. SQLAlchemy の Python コードを作成する<br>
    - `config.py`<br>
        ```python
        # coding=utf-8
        class MySQLConfig:
            # クラス変数
            username="root"
            password="tShH78;g"
            host="localhost"
            port="3306"
            db_name="test_db"
            database_url = f"mysql+pymysql://{username}:{password}@{host}/{db_name}?charset=utf8"
        ```

    - `setting.py`<br>
        ```python
        # coding=utf-8
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from sqlalchemy.ext.declarative import declarative_base

        from config import MySQLConfig

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
        ```

    - `main.py`
        ```python
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
        ```

    ポイントは、以下の通り

    1. データベースエンジンを作成する<br>
        ```python
        # engine 作成
        engine = create_engine(
            MySQLConfig.database_url,
            encoding = "utf-8",
            echo = True               # True : 実行のたびにSQLが出力される
        )
        ```

    1. モデルクラスの基底クラスを作成する<br>
        ```python
        # Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）を作成
        Base = declarative_base()

        # 予め Base クラスに query プロパティを仕込んでおく
        Base.query = session.query_property()
        ```

    1. モデルクラスを作成する<br>
        ```python
        class UserData(Base):
            """
            MySQL でテーブルデータを定義したモデルクラス
            """
            __tablename__ = "userdata"
            id = Column('id', Integer, primary_key = True)
            name = Column('name', String(200))
            age = Column('age', Integer)
        ```

    1. Session を作成する<br>
        ```python
        # Session クラス作成
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # sessionmaker インスタンスを内包した scoped_session インスタンスを生成
        # sessionmaker との違いは、Session() を何回実行しても同一の Session が返されるという点
        session = scoped_session(Session)
        ```

    1. モデルクラスのオブジェクトを作成し、INSERT + SELECT + UPDATE + DELETE 処理を行う<br>
        ```python
        # テーブルデータでの INSERT 処理
        user_data = UserData(id=0, name="Tom", age=28)
        session.add(user_data)  
        session.commit()
        ```

1. MySQL サーバーの root ユーザーを作成する<br>
    ```sh
    $ mysql_secure_installation
    ```

1. MySQL サーバーを起動する<br>
    ```sh
    $ mysql.server start
    ```

1. MySQL サーバーに root ユーザーでログインして、データベースを作成する<br>
    ```sh
    $ mysql -u root -p
    ```
    ```sh
    $ mysql> CREATE DATABASE test_db;
    ```

1. SQLAlchemy の Python スクリプトを実行する<br>
    ```sh
    $ python main.py
    ```

## ■ 参考サイト
- https://qiita.com/ariku/items/75799665acd09520bed2
- https://qiita.com/tomo0/items/a762b1bc0f192a55eae8
