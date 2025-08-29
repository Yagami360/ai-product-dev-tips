# Claude Code GitHub Actions を使用して PR レビューを自動化する

## 方法

1. Claude の API キーを作成する

    <img width="500" height="405" alt="Image" src="https://github.com/user-attachments/assets/db479178-e777-4b29-b596-353bc876eb5c" />

2. 以下のリンクから **Claude GitHubアプリをインストール**してリポジトリに追加する

    https://github.com/apps/claude

    <img width="500" height="411" alt="Image" src="https://github.com/user-attachments/assets/ab03351a-dea1-45cc-b1af-9cb82cde3989" />

3. Claude API キーの環境変数 `ANTHROPIC_API_KEY` を各リポジトリの GitHub シークレットに追加する

    <img width="728" height="606" alt="Image" src="https://github.com/user-attachments/assets/baa344ee-a0cf-4377-9ffc-b95f6279f0d9" />

4. レポジトリに GitHubActions の定義ファイルを追加する

    以下の2つのワークフローファイルを `.github/workflows/` ディレクトリに配置します：

## ワークフロー設定

### 🚀 PR作成専用ワークフロー（claude-pr-creator.yml）

自動でコード実装からPR作成まで行うワークフローです。

**トリガー条件:**
- 新しいブランチ（main/master/develop以外）へのプッシュ
- Issueで `@claude-create-pr` と入力
- 指定ユーザーがIssueにアサインされた場合

**用途:**
- プッシュ時の自動PR作成
- Issue要件からのコード実装＋PR作成
- 開発作業の完全自動化

## 使い方

1. **プッシュ時の自動PR作成**
   ```bash
   git checkout -b feature/new-feature
   git add .
   git commit -m "新機能を追加"
   git push origin feature/new-feature
   ```
   → 自動でPRが作成される

2. **Issue要件からのPR作成**
   - Issueを作成し、`@claude-create-pr` とコメント
   - または自分自身をIssueにアサイン
   → Claudeが要件を読み取ってコード実装＋PR作成

## 設定例

### claude-pr-creator.yml（PR作成専用）
```yaml
name: Claude PR Creator

on:
  push:
    branches-ignore:
      - main
      - master
      - develop
  issues:
    types: [opened, assigned]

jobs:
  claude-pr-creator:
    if: |
      (github.event_name == 'push' && github.ref != 'refs/heads/main' && github.ref != 'refs/heads/master' && github.ref != 'refs/heads/develop') ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude-create-pr') || contains(github.event.issue.title, '@claude-create-pr') || github.event.issue.assignee.login == 'Yagami360'))
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Claude PR Creator
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          trigger_phrase: "@claude-create-pr"
          assignee_trigger: "Yagami360"
          claude_args: |
            --allowedTools "Bash(git checkout -b *),Bash(git add *),Bash(git commit *),Bash(git push *),Bash(gh pr create *),Bash(gh pr list),Bash(gh pr view *),Bash(npm install),Bash(npm run build),Bash(npm run test:*),Bash(npm run lint:*)"
            --max-turns 8
            --system-prompt "常に日本語でレスポンスしてください。あなたはPR作成専用のアシスタントです。実際にコードを書いて実装し、PRを作成してください。"
```

## 参考サイト

- https://docs.anthropic.com/ja/docs/claude-code/github-actions
