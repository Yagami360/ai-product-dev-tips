# 認証認可の基礎事項

## 認証（Authentication）
ある個人を特定し認証してよいユーザーか確認すること。具体的には、

- ログイン API での｛ユーザーID・パスワード｝一致でのログイン
    - ログイン API での｛ユーザーID・パスワード｝一致でのログイン後の JWT token の発行
- 二要素認証（2FA）など

## 認可（Authorization）
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
        ユーザー名とパスワードを「`ユーザー名:パスワード`」の形式で結合して、Base64 エンコードした値を `Authorization` ヘッダーに付与してリクエスト
        ```python
        curl -H Authorization: Basic <エンコードされた文字列> https://example.com/api
        ```

- サーバー側<br>
    1. `Authorization` ヘッダーから「`ユーザー名:パスワード`」の形式で Base64 エンコードされた認証情報を抽出
    2. エンコードされた Base64 文字列をデコードして「`ユーザー名:パスワード`」の形式に分割
    3. 分割したユーザー名とパスワードをデータベース（またはメモリ内）のユーザー情報（ユーザー名＆パスワード）と照合
        - データベース内のパスワードは、ハッシュ化されたパスワードにしているので、パスワードのハッシュ値で照合
    4. 認証処理
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

異なるアプリケーション間での認可（認証されたユーザーに対して、特定のアクションやリソースへのアクセス許可をすること）のための仕組みで、あるアプリケーション（自社のアプリケーションなど）に対して、別のアプリケーション（Googleなど）側で保持しているパスワードを共有することなく、認証ユーザーへアプリケーションのリソースへの限定的なアクセス権を付与するための仕組み。

具体的には、Google アカウントでのログインで、自社のアプリケーションの特定のリソース（画像など）にアクセスする場合など

以下のような特徴がある

- アクセストークンを使用してリソースへのアクセスを制御
    - OAuth 2.0の仕様ではトークン形式を特定していないので、アクセストークンは、JWT トークンであるとは限らない
    - 但し、一般的には JWTトークンを使用するケースが多い
- ユーザーの機密情報（パスワードなど）をアプリケーション間で共有せずに、クライアントアプリケーションのリソースへの限定的なアクセス権を付与できる

具体的な処理の流れは、以下のようになる

<img width="800" alt="image" src="https://github.com/user-attachments/assets/d9292c75-82fc-4965-b3d9-c01c3dcf419e" />

1. クライアントアプリ（自社アプリケーションなど）内にて、ユーザーが「Googleでログイン」をクリック
2. Googleの認証画面に遷移
3. ユーザーが Google の認証情報（メールアドレス・パスワードなど）を入力
4. OAuth 2.0により、クライアントアプリ（自社アプリケーションなど）のリソース（画像など）への限定的なアクセス権が付与される

## OpenID Connect (OIDC)

OAuth 2.0 の拡張仕様で、認可だけでなく、異なるアプリケーション間での認証（ある個人を特定し認証してよいユーザーか確認すること）も行うことができる仕組み。

具体的には、Google アカウントでのログインで、自社のアプリケーションにログインする場合など

以下のような特徴がある

- IDトークン・アクセストークン・リフレッシュトークンの3種類のトークンを使用し、これらトークンで認証ユーザーの情報やリソースへのアクセス権限を提供する<br>
    - ID トークン<br>
        - JWT 形式のトークン
        - ユーザー認証情報を含むトークンで、このトークンでユーザー認証情報を取得できる
    - アクセストークン<br>
        - 任意のトークン形式（多くの場合は JWT トークン）
        - リソースアクセスのための認可情報を含むトークン、このトークンでリソースアクセスのための認可情報を取得できる
    - リフレッシュトークン<br>
        - 任意のトークン形式（多くの場合は JWT トークン）
        - アクセストークンの有効期限が切れた場合に、新しいアクセストークンを取得するために使用

- ユーザーの機密情報（パスワードなど）をアプリケーション間で共有せずに、クライアントアプリケーションへのログインやリソースアクセスを行うことができる<br>

- シングルサインオン（SSO）を可能する<br>

    > シングルサインオン（SSO）: 1回のログイン認証で複数のアプリケーションやサービスにアクセスできる認証方式

具体的な処理の流れは、以下のようになる

<img width="800" alt="image" src="https://github.com/user-attachments/assets/3ecedde4-b66e-47bc-8794-bc927ae57002" />

1. クライアントアプリ（自社アプリケーションなど）内にて、ユーザーが「Googleでログイン」をクリック
2. Googleの認証画面に遷移
3. ユーザーが Google の認証情報（メールアドレス・パスワードなど）を入力
4. OpenID Connect により、クライアントアプリ（自社アプリケーションなど）に｛IDトークン・アクセストークン・リフレッシュトークン｝が返される
5. IDトークンでユーザー認証情報を取得し、クライアントアプリ（自社アプリケーションなど）にログインする
6. （オプション）アクセストークンでリソースアクセスのための認可情報を取得
7. （オプション）トークンの有効期限が切れた場合は、リフレッシュトークンで新しいアクセストークンを取得


その他補足事項

- Firebase の Google ログインは OpenID Connect を活用している


## SAML 2.0 [Security Assertion Markup Language]


## SSO [Single Sign-On]

1回のログイン認証で複数のアプリケーションやサービスにアクセスできる認証方式。

SSOを可能にするには、以下の方式で実現方法がある

- SAML (Security Assertion Markup Language)<br>
    - 標準的なSSO方式
    - ユーザー認証情報をXML形式でやり取りする
    - AWS SSO で使用されている

- OpenID Connect<br>
    - OAuth 2.0 の拡張仕様で、認証と認可を同時に行うことができるので、SSOにも活用可能
    - モバイルアプリやウェブアプリケーションで人気

- OAuth 2.0<br>
    - 主に認可に使用されるが、SSOにも活用可能

具体的に、SSO を活用しているサービスには、以下のようになものがある

- AWS SSO<br>
    AWS コンソール UI における SSO で、SAML 2.0 を使用している。<br>
    AWS SSO における認証フローは、以下のようになる<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/1aaaec6d-4a37-4671-9487-b3dc4a84c668" />


## CORS [Cross-Origin Resource Sharing]

<img width="800" alt="image" src="https://github.com/user-attachments/assets/aed2a3d1-bcc8-418b-af96-518a99eb2166" />

CORS [Cross-Origin Resource Sharing] （オリジン間リソース共有）は、あるオリジン（URLのドメイン・ポート番号）で動作しているウェブアプリケーション（Javascript）に対して、異なるオリジンにある選択されたリソース（APIなど）へのアクセス権を与えるよう”ブラウザーに”指示するための仕組み（※ あくまでブラウザに指示するための仕組み）

> オリジン：ウェブコンテンツにアクセスするために使われる URL の｛*スキーム* （プロトコル）・ ホスト （ドメイン）・ポート番号 ｝のこと

CORS を回避（別オリジン間でのアクセス制限をなくす）には、別オリジン（APIなど）のレスポンスヘッダーに以下のレスポンスヘッダーを付与すればよい

- `Access-Control-Allow-Origin`
    - 許可するドメインを指定しています
- `Access-Control-Allow-Methods`
    - 許可するHTTPメソッド（GET, POST）を指定
- `Access-Control-Allow-Headers`
    - リクエストに含まれるヘッダーの種類を指定します。

## 参考サイト

- xxx