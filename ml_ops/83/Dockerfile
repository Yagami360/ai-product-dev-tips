FROM elixir:1.13.1-slim

RUN apt-get update && apt-get install -y \
    inotify-tools \
    git \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# phoenix 関連のライブラリ更新
RUN mix local.hex --force
RUN mix local.rebar --force
RUN mix archive.install hex phx_new --force

WORKDIR /api
