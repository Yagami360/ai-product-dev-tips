# DNS サーバーの基礎事項


- URL と｛ホスト名・ホスト・ドメイン名｝の関係<br>
    URL: `https://www.example.com:8080/index.html` の場合<br>
    - ホスト名: ↑の URL の中、`www.example.com` の部分
    - ホスト: ↑の URL の中、`www` の部分
    - ドメイン名: ↑の URL の中、`example.com` の部分

- DNS [Domain Name System] サーバー（ネームサーバー）<br>
    <img width="692" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/40970623-b506-49d7-8fca-79021a0cf62c"><br>
    ドメイン名（xxx.com）とIPアドレスを変換する仕組みを提供するサーバー。
    A レコードで定義したドメイン名とIPアドレスの関連づけに基づき、ドメイン名（xxx.com）とIPアドレスを変換する（＝名前解決する）

- DNS レコード<br>
    DNSサーバーの中にテキストで保存された設定で、ドメイン名に関連付けられたIPアドレスやドメインに対するリクエストを処理する方法などを定義している。<br>
    DNS レコードには、以下のような種類がある。

    - A レコード<br>
        ドメイン名（xxx.com）とIPアドレスの関連づけを定義したもの。<br>
        例えば、ドメイン `www.example.jp` => IP アドレス `198.51.100.0` という具合

    - CNAME レコード<br>
        ドメイン名（xxx.com）と別のドメイン名（yyy.com）の関連づけを定義したもの。

- 名前解決<br>
    ドメイン名からIPアドレスを取得するプロセス

- 名前空間<br>
    <img width="709" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/d353c6ff-854e-45b9-9e7d-1557e80115d9"><br>

    ドメイン名（URL:`https://www.yahoo.co.jp`の中、`yahoo.co.jp` の部分）の階層構造を表現したもの

    - ゾーン<br>
        <img width="400" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/07e7dd09-9b2f-4943-b06e-1fa31aa10f02"><br>
        名前空間の範囲の一部。<br>
        例えば、URLの末尾が `jp` の場合は そのドメインは `jp` と名のつくゾーンに所属しているドメインとなり、`yahoo.co.jp` であれば、`jp` ドメインのゾーンにドメイン `yahoo.co.jp` が所属しているということになる。

## Route53 特有の概念

- リゾルバー<br>
    名前解決（＝ドメイン名からIPアドレスを取得するプロセス）をするもの

- ルーティング
    xxx

- ホストゾーン<br>
    ホストゾーンには、以下の２種類がある

    1. パブリックホストゾーン<br>
        インターネット上（＝どこからでも）で、ドメイン名からIPアドレスを取得（＝名前解決）が可能なゾーン

    1. プライベートホストゾーン<br>
        VPC内（＝インターネットからアクセス不可）でのみ、ドメイン名からIPアドレスを取得（＝名前解決）が可能なゾーン
