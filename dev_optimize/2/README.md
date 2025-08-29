# Claude Code GitHub Actions を使用して PR 作成＆レビューを自動化する

## 方法

1. Claude の API キーを作成する

    <img width="500" height="405" alt="Image" src="https://github.com/user-attachments/assets/db479178-e777-4b29-b596-353bc876eb5c" />

1. 以下のリンクから **Claude GitHubアプリをインストール**してリポジトリに追加する

    https://github.com/apps/claude

    <img width="500" height="411" alt="Image" src="https://github.com/user-attachments/assets/ab03351a-dea1-45cc-b1af-9cb82cde3989" />

    インストールされていることを確認

    <img width="500" height="613" alt="Image" src="https://github.com/user-attachments/assets/2bbf2f89-3408-4214-90a9-72964882fc56" />

1. Claude API キーの環境変数 `ANTHROPIC_API_KEY` を各リポジトリの GitHub シークレットに追加する

    <img width="728" height="606" alt="Image" src="https://github.com/user-attachments/assets/baa344ee-a0cf-4377-9ffc-b95f6279f0d9" />

1. リポジトリ設定でワークフロー権限変更

    Settings → → Actions → General から設定

    <img width="500" height="729" alt="Image" src="https://github.com/user-attachments/assets/2e7978b5-4bdf-429c-a604-212964455baa" />

1. レポジトリに GitHubActions の定義ファイルを追加する

    https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml の GitHubAction 定義ファイルをコピーして、レポジトリの `` に配置する 

## 参考サイト

- https://docs.anthropic.com/ja/docs/claude-code/github-actions
