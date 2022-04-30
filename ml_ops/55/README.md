# 【GCP】GKE 上の Web-API に対して Google Cloud Armor の WAF 機能を使用してクライアントIP単位での RateLimit 制限を行う

多数のユーザーからアクセス数されるような API においては、RateLimit 制限を導入して、ユーザー度のリクエスト回数に制限を課すことで、API の処理負荷を軽減させるのは有効な方法の１つである。

ここでは、Google Cloud Armor の WAF 機能 [Web Application Firewall] を使用してクライアントIP単位での RateLimit 制限を行う方法を記載する。

ここで API は、GKE 上にデプロイするケースを考える。理由は Google Cloud Armor がロードバランサー（GKEだと自動的に構成される）に対して適用される機能であるためである。GCE で API を構築する場合は、別途ロードバランサーを組み込む必要があると思われる

> RateLimit：一定時間あたりにリクエストできる回数

> WAF [Web Application Firewall] : Web アプリケーションに対する "SQL インジェクション", "クロスサイトスクリプティング" といったアプリケーションレイヤの攻撃を検知し、防御するための仕組み。

## ■ 方法

1. Google Cloud Armor 用のサービスアカウントを作成する。<br>
	Google Cloud Armor 用のサービスアカウントを作成し、作成したサービスアカウントにGoogle Cloud Armor のセキュリティポリシーの IAM 権限を付与する<br>
	```sh
	```

	> `roles/compute.securityAdmin` が Google Cloud Armor のセキュリティポリシーの IAM 権限になるので、これを作成した

1. GKE 上で動作するする API をデプロイする<br>
	1. 

1. GKE クラスタにサービスアカウントを適用する

1. GKE のロードバランサーに適用するためのセキュリティポリシーを作成する<br>
	GKE の外部 HTTP(S) ロードバランサーに適用するためのセキュリティポリシーを作成する

	```sh
	$ gcloud compute security-policies create ${SECURITY_POLICY_NAME}
	```

1. セキュリティーポリシーのルール（RateLimit 制限）を作成する<br>
	作成した GKE のロードバランサーに適用するためのセキュリティポリシーに対して、セキュリティーポリシーのルール（ここでは、RateLimit 制限）を設定する
	```sh
	$ gcloud compute security-policies rules create ${PRIORITY}
		--security-policy=${SECURITY_POLICY_NAME}
		(--expression=${EXPRESSION} | --src-ip-ranges=${SRC_IP_RANGE})
		--action "throttle"
		--rate-limit-threshold-count=$RATE_LIMIT_THRESHOLD_COUNT
		--rate-limit-threshold-interval-sec=$RATE_LIMIT_THRESHOLD_INTERVAL_SEC
		--conform-action=[allow]
		--exceed-action=[deny-403|deny-404|deny-429|deny-502|redirect]
		--exceed-redirect-type=[google-recaptcha|external-302]
		--exceed-redirect-target=$REDIRECT_URL
		--enforce-on-key=[IP | ALL | HTTP-HEADER | XFF-IP | HTTP-COOKIE]
		--enforce-on-key-name=[$HTTP_HEADER_NAME|$HTTP_COOKIE_NAME]
	```
	```sh
	# 例
	gcloud compute security-policies rules create 10 \
		--security-policy sec-policy     \
		--src-ip-ranges="0.0.0.0/1"     \
		--action=throttle                \
		--rate-limit-threshold-count=100 \
		--rate-limit-threshold-interval-sec=60 \
		--conform-action=allow           \
		--exceed-action=deny-429         \
		--enforce-on-key=IP
	```

	- `${PRIORITY}` : セキュリティールールの優先度
	- `--src-ip-ranges` : RateLimit 制限をかけるクライアントIPの範囲（CIDR 表記で指定）
	- `--rate-limit-threshold-count` : 指定された時間間隔内で許可されるクライアントあたりのリクエスト数。最小値は 1、最大値は 10,000 です。
	- `--rate-limit-threshold-interval-sec` : 時間間隔の秒数。値は 60、120、180、240、300、600、900、1200、1800、2700、3600 秒のいずれかにする必要があります。
	- `--enforce-on-key` : RateLimit 制限対象のクライアントを特定するための値
		- `ALL` : リクエストがルールの一致条件を満たすすべてのクライアントの単一キー。
		- `IP` : リクエストがルールの一致条件を満たすクライアントの送信元 IP アドレスごとに一意のキー。
		- `HTTP-HEADER` : 
		- `XFF-IP` : クライアントのオリジナルの送信元 IP アドレス
		- `HTTP-COOKIE` : 

	> RateLimit 制限をかけるクライアントIPの範囲 `--src-ip-ranges` を設定しないといけないので、クライアントIPをリクエスト時ではなく、デプロイ時に予め知っておく必要がある。`--src-ip-ranges` の範囲を増やせば、全クライアントに対して RateLimit 制限をかけることが可能？

	> - CIDR 表記<br>
	> `198.51.100.xxx/24` のような形で、IPアドレスの後ろに `/` と２進数のサブネットマスクにおける１の個数を書く表記方法。<br>
	> 例えば、/16 => 11111111.11111111.00000000.00000000 => 255.255.0.0 のサブネットマスクとなり、<br>
	> /24 => 11111111.11111111.11111111.00000000 => 255.255.255.0 のサブネットマスクとなる。<br>

1. セキュリティポリシーをバックエンドサービス（ロードバランサー）に接続する
	```sh
	$ gcloud compute backend-services update ${BACKEND_SERVICE_NAME} \
    	--security-policy ${SECURITY_POLICY_NAME}
	```

1. FastAPI での Web-API のコードを作成する<br>

1. FastAPI サーバーの Dockerfile を作成する<br>

1. docker-compose を作成する<br>
	docker-compose を使って、API サーバーの起動や停止を行う場合は、`docker-compose.yml` も作成する

1. API サーバーを起動する<br>
	```sh
	$ docker-compose -f docker-compose.yml stop
	$ docker-compose -f docker-compose.yml up -d
	```

1. リクエスト処理を送信する<br>
	`curl` コマンドなどで、起動した API サーバーのエンドポイントにアクセスし、リクエスト処理を行う。
	```sh
	$ curl http://${HOST}:${PORT}
	```

## ■ 参考サイト
- https://cloud.google.com/armor/docs/rate-limiting-overview
- https://cloud.google.com/armor/docs/configure-security-policies#gcloud
- https://qiita.com/irotoris/items/8d6be7b0afd9b8afc321