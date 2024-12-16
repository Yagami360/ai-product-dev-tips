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

    <img width="500" alt="image" src="https://github.com/user-attachments/assets/e27dfef2-c4e7-4303-a74c-bb0ad2fe219e" /><br>
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

- eager loading (joined loading)

- lazy loading


## インデックス

- インデックス<br>

- 複合インデックス<br>

- GIN インデックス<br>

- インデックスを活用できないSQL<br>
    - OR
    - LIKE
    - xxx


## テーブル操作（CRUD）

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

- INNER JOIN

- LEFT JOIN

- RIGHT JOIN

- FULL JOIN


## 正規化

- 正規化

- 非正規化


## DBパフォーマンス指標

### Amazon RDS のパフォーマンス指標

RDSのデータベースに関するパフォーマンス指標（メトリクス）には、様々なものがあるが、そのうち特に重要なパフォーマンス指標には、以下のようなものがある

- CPUUtilization<br>
    データベースインスタンスのCPU使用率（%）。高い値はDBインスタンスの処理負荷が高いことを示す。<br>
    高い場合は、DBインスタンスのスケーリング（インスタンスタイプの変更）や、API側でのデータベースのCRUD処理のチューニングを行うことでパフォーマンスを改善できる。

- DatabaseConnections<br>
    データベースへの現在のコネクション数。急激な増加は異常なアクセスを示す可能性がある。<br>

    データベースコネクション数の上限は、PostgreSQL の場合 `max_connections` で確認できる。
    ```sh
    postgres=> SHOW max_connections;
    -[ RECORD 1 ]---+-----
    max_connections | 1704
    ```

    xxx

- ReadLatency / WriteLatency<br>
    ディスクI/O操作の平均所要時間（秒）。高い値はディスクの遅延を示す。<br>
    高い場合は、DBインスタンスのスケーリング（インスタンスタイプの変更）や、API側でのデータベースのCRUD処理のチューニングを行うことでパフォーマンスを改善できる。


## その他

- パーティション
