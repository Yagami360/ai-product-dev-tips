# 認証認可の基礎事項

## 認証
ある個人を特定し認証してよいユーザーか確認すること。具体的には、

- ログイン API での｛ユーザーID・パスワード｝一致でのログイン
    - ログイン API での｛ユーザーID・パスワード｝一致でのログイン後の JWT token の発行
- 二要素認証（2FA）など

## 認可
上記認証プロセスで認証されたユーザーに対して、特定のアクション（API処理）やリソースへのアクセス許可をすること。具体的には、

- JWTトークンによるAPI認可
    - 非ログイン API でのリクエストされた JWT token の正しさ確認後のAPI 処理許可

## Basic 認証
ユーザー名とパスワードでの単純な認証<br>

- リクエスト側<br>
    ユーザー名とパスワードを「`ユーザー名:パスワード`」の形式で結合してリクエスト

    - パターン１<br>
        ユーザー名とパスワードを「`ユーザー名:パスワード`」の形式で結合してリクエスト
        ```python
        curl -u username:password https://example.com/api
        ```

    - パターン２<br>
        ユーザー名とパスワードを「`ユーザー名:パスワード`」の形式で結合して、Base64 エンコード
        エンコードした値をヘッダーに付与してリクエスト
        ```python
        curl -H Authorization: Basic <エンコードされた文字列> https://example.com/api
        ```

- サーバー側<br>
    1. `Authorization` ヘッダーから「`ユーザー名:パスワード`」の形式で Base64 エンコードされた認証情報を抽出
    2. エンコードされた Base64 文字列をデコードして「`ユーザー名:パスワード`」の形式に分割
    3. 分割したユーザー名とパスワードをデータベースで照合
    4. データベース（またはメモリ内）のユーザー情報（ユーザー名＆パスワード）と照合
        - データベース内のパスワードは、ハッシュ化されたパスワードにしているので、パスワードのハッシュ値で照合
    5. 認証処理
        - 成功した場合：リクエストを続行し、API 処理を実行
        - 失敗した場合：`401 Unauthorized` レスポンスを返す

## JWT [JSON Web Token] 認証 

決まった書式の JSON データからエンコードした `ヘッダー.ペイロード.署名` の形式のAPIトークンでの認証

- リクエスト側
    以下のような JSON データをを Base64 でエンコードし、ドット(`.`)で区切られたトークン `ヘッダー.ペイロード.署名（Signature）` として表現する

    - JSON データ
        - ヘッダー<br>
            ```json
            {
                "alg": "HS256",
                "typ": "JWT"
            }
            ```

        - ペイロード<br>
            ```json
            {
                "iss": "io.exact.sample.jwt",     # トークン発行者
                "sub": "sample",                   # トークンの対象者
                "exp": 1670085336,                # トークンの有効期限
                "iat": 1670085336,                # トークンの発行時間
                ...
            }
            ```

        - 署名（Signature）<br>
            以下のコードで生成される部分
            ```bash
            HMACSHA256(
                base64UrlEncode(header) + "." + base64UrlEncode(payload),
                secret
            )
            ```
            - secret: サーバー側の秘密鍵

            署名の目的は、以下のようになる
            - トークンの改ざん防止
                - JWTトークンのヘッダーやペイロード部分が変更されると署名が一致しなくなる
            - トークンの発行者等が正しいか確認
                - トークンの発行者等が正しいか確認することで、トークンが改ざんされていないか確認できる

    - Base64 エンコード値（`ヘッダー.ペイロード.署名` の形式）
        ```bash
        JWT_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        ```

    Token の送信に使うヘッダは、以下の形式（Bearer token）が一般的
    ```bash
    curl -H "Authorization: Bearer ${JWT_TOKEN}" https://example.com/api
    ```

    > Bearer 認証: `Authorization: Bearer ${TOKEN}` の形式の認証。`{TOKEN}` の形式は任意である。`{TOKEN}` の形式として JWT token を使用する場合は、JWT 認証と呼ぶ

- サーバー側
    1. `Authorization` ヘッダーから Base64 デコードされた JWT token をデコード
    2. デコードした JWT トークンの検証を行う
        1. 秘密鍵からデコード
            - 秘密鍵は、サーバー側のみが知っている
            - 秘密鍵は、外部に漏洩しないように管理するGitHub Actions の Secrets などで管理）
            - JWTトークンを直接改ざんされた場合でも、秘密鍵が一致しないとデコードできないようになっている
            - 具体的には、
                1. 改ざん前の正常なトークン
                    ```sh
                    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.ABC123...
                    ```

                2. ペイロード部分を改ざん<br>
                    ```sh
                    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo5OTl9.ABC123...
                    ```

                3. API 内部での JWT トークンのデコード処理
                    以下のような JWT デコード処理の部分で、`401 Unauthorized`（不正なトークンです）となる
                    ```python
                    try:
                        # トークンの検証
                        decoded_token = jwt.decode(
                            token,
                            secret_key,  # 秘密鍵
                            algorithms=['HS256']
                        )
                    except jwt.InvalidSignatureError:
                        # 署名が無効な場合の処理
                        return {'error': '不正なトークンです'}, 401
                    ```

        2. header の alg, typ などが正しいか確認
        3. payload の iss, sub などの値が正しいか確認
        4. payload の exp が有効期限内であるか確認など
    3. 認証処理
        - 成功した場合：リクエストを続行
        - 失敗した場合：`401 Unauthorized` レスポンスを返す


## OAuth 2.0

認可（認証されたユーザーに対して、特定のアクションやリソースへのアクセス許可をすること）のための仕組みで、サードパーティのアプリケーション（自社のアプリケーションなど）に対して、サードパーティのアプリケーション側で保持しているパスワードを共有することなく、認証ユーザーへアプリケーションのリソースへの限定的なアクセス権を付与するための仕組み。

具体的には、Google アカウントでのログインで、自社のアプリケーションの特定のリソース（画像など）にアクセスする場合など


## OpenID Connect (OIDC)

OAuth 2.0 の拡張仕様で、認可だけでなく、認証（ある個人を特定し認証してよいユーザーか確認すること）も行うことができる仕組み。

具体的には、Google アカウントでのログインで、自社のアプリケーションにログインする場合など

- JSON Token を使用して、ユーザーの基本的な情報（名前、メールアドレスなど）を提供
- シングルサインオン（SSO）を可能する

## SSO [Single Sign-On]

1回のログイン認証で複数のアプリケーションやサービスにアクセスできる認証方式

## 参考サイト

- OAuth, OpenID Connect
    - https://www.macnica.co.jp/business/security/manufacturers/okta/blog_20210901.html
