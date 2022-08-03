# elixir:1.13.1-slim に phoenix はインストール済み
FROM elixir:1.13.1-slim

RUN apt-get update && apt-get install -y \
    inotify-tools \
    git \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# phoenix 関連のライブラリ更新
RUN mix do \
    local.hex --force, \
    local.rebar --force, \
    archive.install --force hex phx_new


WORKDIR /api
