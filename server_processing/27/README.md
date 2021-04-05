# 【uWSGI】WSGI / uWSGI の基本事項

- WSGI [Web Server Gateway Interface]<br>
    Python で記述された Web アプリケーションと Web サーバー間との通信仕様を定めた通信プロトコル。この WSGI に従ったアプリケーションを動作させたサーバーを WSGI サーバーという<br>
    Flask や Django などのほとんどの Python 製 Web フレームワークは、この WSGI という通信プロトコルに則っている。<br>

- uWSGI<br>
    WSGI サーバーの１種で、アプリケーションサーバー（Flask, Django など）とウェブサーバ（nginxなど）をつなぐサーバ。<br>

- Gunicorn<br>
    xxx


## ■ 参考サイト
- https://www.python.ambitious-engineer.com/archives/1959
- https://qiita.com/morinokami/items/e0efb2ae2aa04a1b148b
- https://serip39.hatenablog.com/entry/2020/07/06/070000
