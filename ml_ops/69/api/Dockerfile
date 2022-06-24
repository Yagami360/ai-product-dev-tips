FROM golang:1.17-alpine

# UNIX コマンドのインストール
RUN apk update && apk add git

# /api ディレクトリ以下に Go ライブラリをインストール
WORKDIR /api
RUN go mod init api
RUN go get -u github.com/gin-gonic/gin

WORKDIR /api