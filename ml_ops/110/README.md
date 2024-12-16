# 構造化データの基礎事項

## セッションとトランザクション

- トランザクション<br>
    複数の SQL 文によるCRUD操作を1つの処理としてまとめてデータベースに反映させる操作。<br>

    トランザクションを使用することで、複数テーブルにまたがる API 処理などにおいて、テーブルレコードの一貫性が保証されるような処理が可能になる。<br>
    例えば、オーガニゼーション＆ユーザーを作成する API において、オーガニゼーションの追加には成功したが、ユーザーの追加には失敗した場合、トランザクションを使用しないと、オーガニゼーションレコードのみが作成されてユーザーが作成されていないという不整合が発生するが、トランザクションを使用することで、オーガニゼーションとユーザーの作成の両方が成功した場合のみオーガニゼーションとユーザーの作成が完了するという処理が可能になる。

    - SQLAlchemy（PostgreSQL）の場合
        ```python
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # データベースへの接続を確立
        engine = create_engine('postgresql://user:password@localhost:5432/dbname')

        # DBセッションを作成
        Session = sessionmaker(bind=engine)
        session = Session()

        # セッションを Begin して、トランザクションを開始する
        session.begin()

        try:
            # CRUD処理
            # この時点では、データベースに対してのCRUD処理は反映されていない
            organization = session.query(Organization).filter_by(id=organization_id).first()
            user = session.query(User).filter_by(id=user_id).first()
            ...

            # セッションを Commit して、トランザクションを終了する
            # この時点で、データベースに対してのCRUD処理が反映される
            session.commit()
        except Exception as e:
            # エラーが発生した場合は、トランザクションをロールバックする（データベースに対してのCRUD処理が反映されない）
            session.rollback()
            raise e
        finally:
            # セッションを Close して、DBセッションを終了する
            session.close()
        ```

    <!-- トランザクションには、以下の制御モードが存在する

    - 自動モード
        - デフォルトのモード
        - トランザクションの開始、コミット、ロールバックは自動的に行われる

    - 手動モード
        - トランザクションの開始、コミット、ロールバックは手動で行われる -->

- セッション<br>
    データベースへの1つの接続を表すオブジェクト。アプリケーションは複数のセッションを持つことが可能であるが、1つのセッションには同時に1つのアクティブなトランザクションしか持てない点に注意。セッションが終了すると、未コミットのトランザクションは自動的にロールバックされる

    <img width="500" alt="image" src="https://github.com/user-attachments/assets/718b2ae5-165b-49d5-a541-a440bcfb645f" />

- Begin<br>
    セッション及びトランザクションを開始する操作。
    例えば SQLAlchemy の場合は、`session.begin()` で行う。

- コミット（Commit）<br>
    トランザクションの結果（各種CRUD処理の結果）をデータベースに「恒久的に」反映させる操作。トランザクションも終了するので、Commit 成功後のロールバックは不可能になっている。（Commit 失敗の場合は、ロールバックは可能）<br>
    例えば SQLAlchemy の場合は、`session.commit()` で行う。内部では、`session.commit()` が呼ばれると、`session.flush()` が自動的に呼ばれている

- フラッシュ（Flush）<br>
    トランザクションの結果（各種CRUD処理の結果）をデータベースに「一時的に」反映させる操作。Flush 後でもロールバックは可能になっている。<br>
    例えば SQLAlchemy の場合は、`session.flush()` で行う。

    あくまで一時的な反映である Flush 後でもロールバックは可能になっているので、テーブル A 作成後に別のテーブル B 作成時にテーブル A の ID が必要になるようなケースなどで利用する

    - SQLAlchemy（PostgreSQL）の場合
        ```python
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # データベースへの接続を確立
        engine = create_engine('postgresql://user:password@localhost:5432/dbname')

        # DBセッションを作成
        Session = sessionmaker(bind=engine)
        session = Session()

        # セッションを Begin して、トランザクションを開始する
        session.begin()

        try:
            # ユーザーを作成
            user = User(email=email)
            session.add(user)
            
            # Flushして、user.idを取得
            # この時点では、一時的な反映であるので、ロールバックは可能
            session.flush()

            # UserSettings では、レコード作成時に user.id が必要であるが、Flush したことで user.id が利用可能になる
            settings = UserSettings(
                user_id=user.id,  # flush したので id が利用可能
                theme='default'
            )
            session.add(settings)

            # セッションを Commit して、トランザクションを終了する
            # この時点で、データベースに対してのCRUD処理が恒久的に反映される
            session.commit()
        except Exception as e:
            # エラーが発生した場合は、トランザクションをロールバックする（データベースに対してのCRUD処理が反映されない）
            session.rollback()
            raise e
        finally:
            # セッションを Close して、DBセッションを終了する
            session.close()
        ```

- ロールバック（Rollback）<br>
    トランザクションの結果（各種CRUD処理の結果）をデータベースに反映させない操作で、主に各種CRUD処理でエラーが発生したケースで使用する。<br>
    例えば SQLAlchemy の場合は、`session.rollback()` で行う。<br>

- クローズ（Close）<br>
    セッションを終了する操作。例えば SQLAlchemy の場合は、`session.close()` で行う。<br>
    1つのセッションには同時に1つのアクティブなトランザクションしか持てないので、セッションが終了すると未コミットのトランザクションは自動的にロールバックされる。<br>


## コネクションプールとコネクション数

- コネクションプール<br>
    コネクションプールとは、（APIやアプリケーション等から）データベースへの複数接続を効率的に管理するための仕組みで、アプリケーションがデータベースへの接続を必要とする際に、既存の接続を再利用することで、接続の確立と切断のオーバーヘッドを削減し、パフォーマンスを向上させることができる機能になっている。

    より詳細には、アプリケーションからデータベースを操作する際は以下の手順で行われるが、

    1. アプリとデータベースとの接続を確立する
    2. トランザクションを開始する
    3. SQLを実行する
    4. トランザクションを終了する
    5. データベースとの接続を切断する

    この内の１つ目の接続処理は処理負荷が大きく時間がかかり、アプリケーションから複数のデータベースアクセスが行われるようなケースでは、毎回接続処理を行うとパフォーマンスが大きく低下してしまう。そのため、４つ目のトランザクション終了処理のあとに、５つ目の確立した接続の切断処理を行わず、プールと呼ばれる場所にコネクションを保存することで、接続処理のオーバーヘッドを削減することができる。

    <img width="800" alt="image" src="https://github.com/user-attachments/assets/e27dfef2-c4e7-4303-a74c-bb0ad2fe219e" /><br>

    <img width="500" alt="image" src="https://github.com/user-attachments/assets/5abcf5e4-386e-4b23-a71c-665c3d2fed6b" /><br>


- コネクション数<br>
    コネクション数が大きくなりすぎるとデータベースへの負荷が高くなり、各種 CRUD 処理のパフォーマンスが低下する可能性があるので注意が必要。

    コネクション数の適切な数は、データベースの種類やデータベースのパフォーマンス、アプリケーションのニーズによって異なるが、一般的にはデータベースのパフォーマンスに応じて、数百から数千程度のコネクション数が適切な場合が多い。コネクション数を適切に管理することで、データベースへの負荷を最小化し、パフォーマンスを向上させることができる。

    データベースコネクション数の上限は、PostgreSQL の場合 `max_connections` で確認できる。
    ```sh
    postgres=> SHOW max_connections;
    -[ RECORD 1 ]---+-----
    max_connections | 1704
    ```


## リレーション

データベースにおけリレーション（関係）とは、主キー（Primary Key）と外部キー（Foreign Key）を使用して実現する異なるテーブル間の関連付けのこと。リレーションには、以下のパターンが存在する。

- 一対一 (One-to-One)<br>
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/6fcde996-3c06-4492-aab8-73ff2d0f0e67" />

    1つのレコードが、別のテーブルの1つのレコードにのみ関連付けられるリレーション<br>
    外部キーを使用して表現するが、外部キーにはUNIQUE制約を設定する必要がある。（UNIQUE制約で1対1の関係性を表現する）

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship, sessionmaker
        from datetime import datetime

        Base = declarative_base()

        class Organization(Base):
            __tablename__ = 'organizations'

            id = Column(Integer, primary_key=True)
            name = Column(String(100), nullable=False)
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 一対一 (One-to-One)のリレーションシップの定義
            # １つのオーガニゼーションに１つのオーナーが存在する
            # relationship(...) は、Python レベルでの関連付けで（organization.owner で参照可能になる）、PosgreSQL のテーブル構造自体に影響を与えるものではないことに注意
            owner = relationship(
                "Owner",
                back_populates="organization",
                uselist=False    # uselist=Falseが重要
            )

        class Owner(Base):
            __tablename__ = 'owners'

            id = Column(Integer, primary_key=True)

            # 親テーブルのプライマリキー（ID）を外部キーとして追加して表現する
            # 外部キーには UNIQUE 制約を設定する必要がある
            organization_id = Column(
                Integer,
                ForeignKey('organizations.id'),
                unique=True,    # unique=Trueが重要
                nullable=False
            )

            name = Column(String(100), nullable=False)
            email = Column(String(255), nullable=False, unique=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 一対一 (One-to-One)のリレーションシップの定義
            # １つのオーガニゼーションに１つのオーナーが存在する
            # relationship(...) は、Python レベルでの関連付けで（owner.organization で参照可能になる）、PosgreSQL のテーブル構造自体に影響を与えるものではないことに注意
            organization = relationship("Organization", back_populates="owner")
        ```

- 一対多 (One-to-Many)<br>
    1つのレコードが、別のテーブルの複数のレコードに関連付けられるリレーションで、親子関係を表現する<br>
    子テーブルに親テーブルのプライマリキーを外部キーとして追加して表現するが、一対一 (One-to-One)のときとは異なり、外部キーにはUNIQUE制約を設定しない。

    <img width="500" alt="image" src="https://github.com/user-attachments/assets/8d21d142-5981-4885-8604-aee9e2218e85" /><br>
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/6f1eae1d-c8e1-4895-8e59-c32fbb82b2ff" /><br>

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship, sessionmaker
        from datetime import datetime

        Base = declarative_base()

        class Organization(Base):
            __tablename__ = 'organizations'

            id = Column(Integer, primary_key=True)
            name = Column(String(100), nullable=False)
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 一対多 (One-to-Many)のリレーションシップの定義
            # １つのオーガニゼーションに複数のユーザーが存在する
            # relationship(...) は、Python レベルでの関連付けで（organization.users で参照可能になる）、PosgreSQL のテーブル構造自体に影響を与えるものではないことに注意
            users = relationship("User", back_populates="organization", cascade="all, delete-orphan")

        class User(Base):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)

            # 子テーブルに親テーブルのプライマリキー（ID）を外部キーでリレーションする
            # 一対多 (One-to-Many)の場合は、外部キーにはUNIQUE制約を設定しない
            organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)

            username = Column(String(100), nullable=False, unique=True)
            email = Column(String(255), nullable=False, unique=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 一対多 (One-to-Many)のリレーションシップの定義
            # １つのオーガニゼーションに複数のユーザーが存在する
            # relationship(...) は、Python レベルでの関連付けで（user.organization で参照可能になる）、PosgreSQL のテーブル構造自体に影響を与えるものではないことに注意
            organization = relationship("Organization", back_populates="users")
        ```

- 多対一 (Many-to-One)<br>
    xxx

- 多対多 (Many-to-Many)<br>
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/26730764-1c6e-42f8-b39a-d9f03e887c08" />

    異なるテーブル間のレコードが、相互に複数のレコードと関連付けられるリレーション（上記例では、1人のユーザーが複数の組織に所属可能で、1つの組織が複数のユーザーを持つことが可能）で、中間テーブルを使用してリレーションを実現する。<br>

    テーブル間の複雑な関係性も表現できて拡張性が高いメリットがある一方で、中間テーブルを使用することで、大規模データレコード数の場合はレコードサイズが大きくなり、またSQLクエリが複雑化してCRUD処理が遅くなる可能性があるデメリットもある。<br>
    そのため、本当に必要な場合のみ多対多 (Many-to-Many)のリレーションにしたほうが良い。

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship, sessionmaker
        from datetime import datetime

        Base = declarative_base()

        # 中間テーブルの定義
        organization_users = Table(
            'organization_users',
            Base.metadata,
            # 中間テーブルで両方のテーブルのプライマリキー（organization_id, user_id）を外部キーとして追加して表現する
            Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
            Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),

            Column('role', String(50), nullable=False, default='member'),
            Column('created_at', DateTime, default=datetime.utcnow),
            Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        )

        class Organization(Base):
            __tablename__ = 'organizations'

            id = Column(Integer, primary_key=True)
            name = Column(String(100), nullable=False)
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 多対多のリレーションシップ定義
            users = relationship(
                "User",
                secondary=organization_users,
                back_populates="organizations"
            )

        class User(Base):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            username = Column(String(100), nullable=False, unique=True)
            email = Column(String(255), nullable=False, unique=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 多対多のリレーションシップ定義
            organizations = relationship(
                "Organization",
                secondary=organization_users,
                back_populates="users"
            )
        ```

- N+1問題<br>
    一つのデータベースクエリが発行され、その結果をもとにN回の追加のクエリが発行されてパフォーマンスが低下する問題。
    一対多 (One-to-Many)、多対一 (Many-to-One)、多対多 (Many-to-Many)のリレーションの場合に、レコード数が多くなるケースなどで問題になる

    以下のような方法で、N+1問題を解決することが可能になる。

    - JOIN句によるテーブルの結合
    - Eager Loading（必要なデータを事前にロード）

- lazy loading<br>
    ORM（SQLAlchemy等）におけるデフォルトのロードモードで、必要なときにレコードを読み込む方式。メモリ効率が良い反面、N+1問題が発生するケースがあるので注意が必要

    - SQLAlchemy（PosgreSQL）での例（lazy loading で N+1問題が発生するコード）<br>
        ```python
        from sqlalchemy import Column, Integer, String, ForeignKey
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm import joinedload

        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            name = Column(String)

            # 多対一 (Many-to-One)のリレーションシップの定義
            # 1人のユーザーが複数の注文を持つ
            orders = relationship('Order', back_populates='user')

        class Order(Base):
            __tablename__ = 'orders'
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey('users.id'))
            amount = Column(Integer)

            # 多対一 (Many-to-One)のリレーションシップの定義
            # 1つの注文は1人のユーザーに属する
            user = relationship('User', back_populates='orders')

        # lazy loading で N+1問題が発生するコード
        # users を for ループで回して、user.orders を参照すると、PosgreSQL 内部で各 user ごとにSQLが実行されるので、パフォーマンスが低下する
        users = session.query(User).all()
        for user in users:
            print(f"{user.name}の注文数: {len(user.orders)}")
        ```

- eager loading<br>
    ORM（SQLAlchemy等）におけるロードモードの１つで、必要なレコードを事前に読み込む方法。
    一対多 (One-to-Many)、多対一 (Many-to-One)、多対多 (Many-to-Many)のリレーションの場合に、レコード数が多くなるほどパフォーマンスが低下する所謂 N+1問題を解決するために使用される。

    N+1問題を解決できる反面で、レコード数が多い場合にJOIN句によるテーブルの結合でメモリ使用量が多くなったり、JOIN処理に時間がかかり逆にパフォーマンスが低下する可能性があるので注意が必要

    - joined loading<br>
        JOIN句によるテーブルの結合を使用して、必要なレコードを事前に読み込む方法

        - SQLAlchemy（PosgreSQL）での実装例<br>
            ```python
            from sqlalchemy import Column, Integer, String, ForeignKey
            from sqlalchemy.orm import relationship
            from sqlalchemy.orm import joinedload

            class User(Base):
                __tablename__ = 'users'
                id = Column(Integer, primary_key=True)
                name = Column(String)

                # 多対一 (Many-to-One)のリレーションシップの定義
                # 1人のユーザーが複数の注文を持つ
                orders = relationship('Order', back_populates='user')

            class Order(Base):
                __tablename__ = 'orders'
                id = Column(Integer, primary_key=True)
                user_id = Column(Integer, ForeignKey('users.id'))
                amount = Column(Integer)

                # 多対一 (Many-to-One)のリレーションシップの定義
                # 1つの注文は1人のユーザーに属する
                user = relationship('User', back_populates='orders')

            # lazy loading で N+1問題が発生するコード
            # users を for ループで回して、user.orders を参照すると、PosgreSQL 内部で各 user ごとにSQLが実行されるので、パフォーマンスが低下する
            users = session.query(User).all()
            for user in users:
                print(f"{user.name}の注文数: {len(user.orders)}")

            # joinedload での JOIN を使用して事前に一度に読み込む
            # users を for ループで回して、user.orders を参照する際にも、追加のSQLは実行されないので、パフォーマンスが低下しない
            # 但し、JOIN を使用することで、メモリ使用量が多くなる可能性があり、JOIN 時に処理時間がかかるので注意が必要
            users = session.query(User)\
                .options(joinedload(User.orders))\
                .all()

            for user in users:
                print(f"{user.name}の注文数: {len(user.orders)}")  # 追加のSQLは実行されない
            ```

    - selectinload<br>
        主クエリ + IN句による副クエリで、必要なレコードを事前に読み込む方法

        - SQLAlchemy（PosgreSQL）での実装例<br>
            ```python
            ```

## インデックス

- インデックス<br>
    インデックスは、データベースのテーブルに対して作成されるデータ構造で、データの検索やフィルタリングを高速化するために使用される。
    インデックスを活用することで、例えば where 句などの SQL クエリ処理の大幅な高速化が可能になる。

    基本的には、以下のようなフィールドにはインデックスを追加したほうが良い
    - ID などのプライマリキー、ユニークキー
    - 外部キーのカラム
    - ORDER BYでソートされるフィールド（created_at, updated_atなど）

    一方で、インデックスを追加することで、以下のようなデメリットも存在する

    - デメリット
        - データ量が多くなる（とはいえ通常のインデックスでは、そこまで増えない）
        - メモリ使用量の増加
            - インデックスはメモリ上にもキャッシュされるため、メモリ使用量が多くなる
        - 書き込み性能の低下
            - INSERT時：インデックスの更新が必要
            - UPDATE時：インデックス列の更新で再編成が発生
            - DELETE時：インデックスの更新が必要

- 複合インデックス<br>
    複数のフィールドにまたがる１つのインデックスで、複数のフィールドを（where句などで）"同時に"検索する際に、効率的に検索できるようになる。

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        from sqlalchemy import create_engine, Column, Integer, String, DateTime, Index
        from sqlalchemy.ext.declarative import declarative_base
        from datetime import datetime

        Base = declarative_base()

        # ユーザーモデル
        class User(Base):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            name = Column(String)
            email = Column(String)
            status = Column(String)
            created_at = Column(DateTime, default=datetime.utcnow)

            # 複合インデックスの定義
            # status と created_at の２つのフィールドの複合インデックスを作成
            __table_args__ = (
                Index('ix_users_status_created', status, created_at),
            )

        # データベース接続と使用例
        # status と created_at の複合インデックスを活用するクエリ
        users = session.query(User)\
            .filter(User.status == 'active')\
            .order_by(User.created_at.desc())\
            .all()
        ```

- GIN インデックス<br>
    配列やJSONBなどの複数の値を含むフィールドに適しているインデックスで、完全一致だけでなく包含検索なども可能になっている。
    利用可能なフィールドは、配列・JSONBデータ・全文検索のフィールドになる

    - デメリット
        - インデックスのサイズが大きくなりやすい
        - メモリ使用量が多くなりやすい

    - SQLAlchemy（PosgreSQL）での実装例<br>

        - JSONB型のフィールドにGINインデックスを作成する場合
            ```python
            from sqlalchemy import create_engine, Column, Integer, Text
            from sqlalchemy.dialects.postgresql import JSONB
            from sqlalchemy.ext.declarative import declarative_base
            from sqlalchemy.schema import Index

            Base = declarative_base()

            class Product(Base):
                __tablename__ = 'products'

                id = Column(Integer, primary_key=True)
                name = Column(Text)

                # JSONB型の列にGINインデックスを作成
                # postgresql_using='gin' は、GINインデックスを使用するためのオプション
                attributes = Column(JSONB)
                __table_args__ = (
                    Index('ix_products_attributes', attributes, postgresql_using='gin'),
                )

            # 使用例
            session.query(Product).filter(
                # 複数の値を含む型に適している
                Product.attributes.contains({
                    'color': 'red',
                    'size': 'M'
                })
            ).all()
            ```

        - 配列型のフィールドにGINインデックスを作成する場合
            ```python
            from sqlalchemy.dialects.postgresql import ARRAY

            class Post(Base):
                __tablename__ = 'posts'

                id = Column(Integer, primary_key=True)
                title = Column(Text)

                # 配列型のフィールドにGINインデックスを作成
                tags = Column(ARRAY(Text))
                __table_args__ = (
                    Index('ix_posts_tags', tags, postgresql_using='gin'),
                )

            # 使用例
            session.query(Post).filter(
                Post.tags.overlap(['tag1', 'tag2'])
            ).all()
            ```


- インデックスを活用できないSQLクエリ<br>
    以下のような SQL クエリは、例えインデックスを追加していてもパフォーマンスが向上しないので、注意が必要

    - OR
    - LIKE
    - NULL値の比較
    - 否定条件など


## 正規化

データベースにおける正規化とは、データの重複をなくし整合的にデータを取り扱えるようにデータベース設計すること。

これにより、データ更新時の異常（片方のテーブルは更新されているが、同じ意味のもう片方のデータが更新されていないケースなど）やデータの重複によるレコードの不要な増加などを防ぐことができる。
一方で、正規化を行うことで、テーブルの結合が増えたり、クエリが複雑になるなどしてパフォーマンスが低下する可能性があるので、アプリケーションの要件に応じて正規化を行うことが必要になってくる。

正規化には、以下のような正規形がある。

- 第一正規形（1NF）
    - 各列がこれ以上分割できない値（原子値）であること
    - 同じような項目を複数列に持たないこと

    - OK例
        ```sql
        CREATE TABLE orders (
            id INT,
            customer_name TEXT
        );

        CREATE TABLE order_phones (
            order_id INT,
            phone_number TEXT
        );

        CREATE TABLE order_products (
            order_id INT,
            product_name TEXT
        );
        ```

    - NG例
        ```sql
        CREATE TABLE orders (
            id INT,
            customer_name TEXT,
            phone_numbers TEXT,  -- "080-1234-5678, 090-8765-4321" のように "," で区切った複数の値を TEXT として持つ
            product_1 TEXT,      -- 複数の商品を列として持つ
            product_2 TEXT
        );
        ```

- 第二正規形（2NF）
    - 第一正規形であること
    - かつ、主キーの一部ではないすべての列が、主キーに完全に依存していること

    - OK例
        ```sql
        ```

    - NG例
        ```sql
        ```

- 第三正規形（3NF）
    - 第二正規形であること
    - かつ、主キーではないすべての列が、主キーに完全に依存していること

    - OK例
        ```sql
        ```

    - NG例
        ```sql
        ```


## CRUD操作

### バルグ処理（一括操作）関連

バルグ処理での一括 CRUD 操作は、レコード数が多い場合にパフォーマンスが飛躍的に向上する。

- バルグインサート<br>
    xxx

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        ```

- バルグアップデート<br>
    xxx

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        ```

- バルグデリート<br>
    xxx

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        ```

- バルグロック<br>
    xxx

    - SQLAlchemy（PosgreSQL）での実装例<br>
        ```python
        ```

### 削除関連

- カスケードデリート

### JOIN関連

- CROSS JOIN
    xxx

- INNER JOIN
    xxx

- LEFT JOIN
    xxx

- RIGHT JOIN
    xxx

- FULL JOIN
    xxx


## マイグレーション


## DBパフォーマンス指標

### Amazon RDS のパフォーマンス指標

RDSのデータベースに関するパフォーマンス指標（メトリクス）には、様々なものがあるが、そのうち特に重要なパフォーマンス指標には、以下のようなものがある

- CPUUtilization<br>
    データベースインスタンスのCPU使用率（%）。高い値はDBインスタンスの処理負荷が高いことを示す。<br>
    高い場合は、DBインスタンスのスケーリング（インスタンスタイプの変更）や、API側でのデータベースのCRUD処理のチューニングを行うことでパフォーマンスを改善できる。

- DatabaseConnections<br>
    データベースへの現在のコネクション数。急激な増加は異常なアクセスを示す可能性がある。<br>
    コネクション数が大きくなりすぎるとデータベースへの負荷が高くなり、各種 CRUD 処理のパフォーマンスが低下する可能性があるので注意が必要。

    コネクション数の適切な数は、データベースの種類やデータベースのパフォーマンス、アプリケーションのニーズによって異なるが、一般的にはデータベースのパフォーマンスに応じて、数百から数千程度のコネクション数が適切な場合が多い。コネクション数を適切に管理することで、データベースへの負荷を最小化し、パフォーマンスを向上させることができる。

    データベースコネクション数の上限は、PostgreSQL の場合 `max_connections` で確認できる。
    ```sh
    postgres=> SHOW max_connections;
    -[ RECORD 1 ]---+-----
    max_connections | 1704
    ```

- ReadLatency / WriteLatency<br>
    ディスクI/O操作の平均所要時間（秒）。高い値はディスクの遅延を示す。<br>
    高い場合は、DBインスタンスのスケーリング（インスタンスタイプの変更）や、API側でのデータベースのCRUD処理のチューニングを行うことでパフォーマンスを改善できる。


## その他

- パーティション
    xxx

- データベースのバックアップ
    xxx
