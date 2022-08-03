# Elixir の Mix におけるプロジェクトとは、`mix.exs` という名前のファイルに配置されたモジュールで `Mix.Project` を使用して定義する。
defmodule MyApp.MixProject do
    use Mix.Project

    def project do
        [
            app: :my_app,
            version: "1.0.0",
            elixir: "~> 1.13",
        ]
    end
end
