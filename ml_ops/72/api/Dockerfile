FROM golang:1.17-alpine

# UNIX コマンドのインストール
RUN apk update && apk add git

# /api ディレクトリ以下にライブラリをインストール
WORKDIR /api
RUN go mod init api

#
WORKDIR /api
