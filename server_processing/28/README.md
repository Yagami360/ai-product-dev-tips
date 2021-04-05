# 【uWSGI】docker + nginx + uWSGI + Flask を用いた Web-API の構築
Flask を用いれば、nginx や uWSGI がなくとも、Flaskの run メソッドを使用して、簡単に Web-API を構築することができる。<br>
しかしながら、この Flaskの run メソッドは、テスト用環境での使用のみが推奨されており、本番環境での使用は推奨されていない。（例えば、Flask でのメモリ使用量が爆発してしまうなどの不具合が発生するケースがある）

そのため、Flask を用いて本番環境の Web-API を構築する際には、下図のように「client ↔ nginx ↔ uWSGI ↔ Flask」の構成でシステムを構築するのが通例になっている。<br>

<img src="https://user-images.githubusercontent.com/25688193/113583847-1b5ee800-9665-11eb-9a73-3b47c60942ce.png" width="400"><br>

## ■ 手順
ここでは、以下のような構成の Web-API を構築する際の手順を示す。<br>
<img src="https://user-images.githubusercontent.com/25688193/113584380-cb345580-9665-11eb-8647-b77ceee06663.png" width="400"><br>

xxx


## ■ 参考サイト
- https://serip39.hatenablog.com/entry/2020/07/06/070000
- https://qiita.com/souchan-t/items/8fb5a5df85882c295d96
