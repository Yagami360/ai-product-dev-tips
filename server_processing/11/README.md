# 【GCP】GCP の認証システム

## ■ 基本事項
- Cloud IAM (Identity and Access Management)<br>
    GCP のリソースに対して、誰（メンバー）がどのようなアクセス権（ロール）を持つか定義し、アクセス制御を管理する機能<br>
    Cloud IAM では、以下のタイプのメンバーが存在する<br>
    - Google アカウント<br>
    - **サービスアカウント : Google Service Account (GSA)**<br>
    - Google グループ<br>
    - G Suite ドメイン<br>
    - Cloud Identity ドメイン<br>
    <img src="https://user-images.githubusercontent.com/25688193/105953596-c6c44d00-60b6-11eb-92b9-657128d75882.png" width="300"><br>

- サービスアカウント : Google Service Account (GSA)
    ユーザーではなくアプリケーションや各種リソース（GCE,GCS,GKEなど）に対して付与される特殊な Google アカウントで、アプリケーションや各種リソースが各種 Google サービス（GSCなど）にアクセスするために必要となる。
    サービスアカウントは、アカウント固有のメールアドレスで識別され、以下のような種類が存在する。<br>
    - ユーザー管理サービスアカウント<br>
        Compute Engine APIがプロジェクトで有効になっている場合、デフォルトでCompute Engineサービスアカウントが作成される。アカウント名は以下の形式。
        ```yml
        [PROJECT-NUMBER]-compute@developer.gserviceaccount.com
        ```
        プロジェクトにGoogle App Engineアプリケーションが含まれている場合、デフォルトのApp Engineサービスアカウントがプロジェクトにデフォルトで作成される。アカウント名は以下の形式。
        ```yml
        [PROJECT-ID]@appspot.gserviceaccount.com
        ```
    - Google 管理サービスアカウント<br>
        Google が作成、所有、管理するためのサービスアカウント。
        例としては、Google APIサービスアカウントなどが相当する。
        ```yml
        [PROJECT_NUMBER]@cloudservices.gserviceaccount.com
        ```

- アクセス権限に関する概念<br>
    - 権限と役割（ロール）<br>
        編集権限、閲覧権限などのユーザーに付与される権限。権限を直接ユーザーに割り当てることはできない。ユーザーの権限の設定は、役割（ロール）をユーザーに付与すること行える。
    - ポリシー（Cloud IAM ポリシー）<br>
        誰がどの種類のアクセス権を持つかの定義の集合

- OAuth2.0<br>
    ｛Googleアカウント・GCPリソース｝の２者間ではなく、｛Googleアカウント・クライアント・GCPリソース｝の三者間での認証システム<br>
    GCP の認証・認可は API キーでの方法を除いて、全て OAuth2 ベースでやり取りされている。<br>
    <img src="https://user-images.githubusercontent.com/25688193/105955693-06406880-60ba-11eb-8344-ddb8a6ff2d4d.png" width="500">


## ■ GCP での認証方法

### 1. API キーを使う認証（OAuth不使用）
1. 使用する API を有効化
1. APIキーの作成
    1. [GUI画面](https://console.developers.google.com/apis/credentials?project=my-project2-303004)から「認証情報を作成」ボタンをクリック。
    1. 「APIキー」を選択
1. [API キーを作成しました] ダイアログ ボックスにある新たに作成されたキーの値を保管する

### 2. OAuth を使う認証 / OAuth 2.0 クライアント ID
1. 使用する API を有効化
1. プロジェクト内ではじめてクライアントIDを作成する場合は、「OAuth同意画面」を設定
1. OAuthクライアントIDの作成
    1. [GUI画面](https://console.developers.google.com/apis/credentials?project=my-project2-303004)から「認証情報を作成」ボタンをクリック。
    1. 「OAuthクライアントID」を選択
    1. xxx

### 3. OAuth を使う認証 / 認可タイプ : サービスアカウント
1. 使用する API を有効化
1. サービスアカウント作成
    1. [GUI画面](https://console.developers.google.com/apis/credentials?project=my-project2-303004)から「認証情報を作成」ボタンをクリック。
    1. 「サービスアカウント」を選択    
    1. 基本的に必要最小限のロールで作成
1. サービスアカウントキーの作成
    1. 作成した「サービスアカウント」の編集ボタンをクリック
    1. 「鍵を追加」ボタンをクリック
1. json ファイル（サービスアカウントキー）をダウンロードし、保管しておく
1. アプリケーションコード側でサービスアカウントキーを登録し、アプリケーションから GCPリソースにアクセスできるようにする
    - シェルスクリプト上で設定する場合<br>
        ```sh
        export GOOGLE_APPLICATION_CREDENTIALS=${サービスアカウントキー.json}
        ```
    - python コード上で設定する場合<br>
        ```python
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'サービスアカウントキー.json'
        ```

## ■ 参照サイト
- https://qiita.com/NagaokaKenichi/items/02e723511d244c82bd82
- https://medium.com/google-cloud-jp/gcp-%E3%81%A8-oauth2-91476f2b3d7f
- http://homework.hatenablog.jp/entry/2016/11/30/134132