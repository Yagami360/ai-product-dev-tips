# Claude Code GitHub Actions を使用して PR 説明文作成を自動化する

## 方法

1. Claude の API キーを作成する

    <img width="500" height="405" alt="Image" src="https://github.com/user-attachments/assets/db479178-e777-4b29-b596-353bc876eb5c" />

2. 以下のリンクから **Claude GitHubアプリをインストール**してリポジトリに追加する

    https://github.com/apps/claude

    <img width="500" height="411" alt="Image" src="https://github.com/user-attachments/assets/ab03351a-dea1-45cc-b1af-9cb82cde3989" />

3. Claude API キーの環境変数 `ANTHROPIC_API_KEY` を各リポジトリの GitHub シークレットに追加する

    <img width="728" height="606" alt="Image" src="https://github.com/user-attachments/assets/baa344ee-a0cf-4377-9ffc-b95f6279f0d9" />

4. Claude Code GitHub Actions を使用した GitHubActions ワークフローを作成する

    [.github/workflows/claude-pr-description.yml](../../.github/workflows/claude-pr-description.yml)

## 参考サイト

- https://docs.anthropic.com/ja/docs/claude-code/github-actions
