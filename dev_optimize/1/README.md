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

    https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml の GitHubAction 定義ファイルをコピーして、レポジトリの `.github/workflows` に配置する

    `claude.yml`

    ```yaml
    name: Claude Code

    on:
    issue_comment:
        types: [created]
    pull_request_review_comment:
        types: [created]
    issues:
        types: [opened, assigned]
    pull_request_review:
        types: [submitted]

    jobs:
    claude:
        if: |
        (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
        (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
        (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
        (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
        runs-on: ubuntu-latest
        permissions:
        contents: write
        pull-requests: write
        issues: write
        id-token: write
        actions: read # Required for Claude to read CI results on PRs
        steps:
        - name: Checkout repository
            uses: actions/checkout@v4
            with:
            fetch-depth: 1

        - name: Run Claude Code
            id: claude
            uses: anthropics/claude-code-action@v1
            # uses: anthropics/claude-code-action@v1-dev
            with:
            anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}

            # This is an optional setting that allows Claude to read CI results on PRs
            additional_permissions: |
                actions: read

            # Optional: Customize the trigger phrase (default: @claude)
            # trigger_phrase: "/claude"

            # Optional: Trigger when specific user is assigned to an issue
            # assignee_trigger: "claude-bot"
            assignee_trigger: "Yagami360"

            # Optional: Configure Claude's behavior with CLI arguments
            # claude_args: |
            #   --model claude-opus-4-1-20250805
            #   --max-turns 10
            #   --allowedTools "Bash(npm install),Bash(npm run build),Bash(npm run test:*),Bash(npm run lint:*)"
            #   --system-prompt "Follow our coding standards. Ensure all new code has tests. Use TypeScript for new files."

            # Optional: Advanced settings configuration
            # settings: |
            #   {
            #     "env": {
            #       "NODE_ENV": "test"
            #     }
            #   }
    ```

## 参考サイト

- https://docs.anthropic.com/ja/docs/claude-code/github-actions
