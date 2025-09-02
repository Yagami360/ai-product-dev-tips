# Claude Code GitHub Actions + Reusable Workflows を使用して複数レポジトリで PR 自動レビューを導入する際でもメンテナンスが容易にできるようにする

## 方法

1. Claude Code GitHub Actions を使用した共通のワークフローのレポジトリを作成する

    https://github.com/Yagami360/claude-code-custom-actions

    - Claude Code GitHub Actions を使用した共通のワークフロー例

        ```yaml
        name: Claude Code

        on:
        workflow_call:
            inputs:
            trigger_phrase:
                description: 'Phrase to trigger Claude'
                required: false
                default: '@claude'
                type: string
            assignee_trigger:
                description: 'Username to trigger on assignment'
                required: false
                default: ''
                type: string
            max_turns:
                description: 'Maximum conversation turns'
                required: false
                default: 1
                type: number
            system_prompt:
                description: 'Custom system prompt for Claude'
                required: false
                default: '常に日本語で回答してください。コードレビューを行う際は、以下の点に注意してください：1. コーディング標準への準拠、2. 新しいコードにはテストが含まれているか、3. TypeScriptを新しいファイルで使用しているか。簡潔で実用的なフィードバックを提供してください。'
                type: string
            secrets:
            ANTHROPIC_API_KEY:
                description: 'Anthropic API Key'
                required: true

        jobs:
        claude:
            if: |
            github.event_name == 'issue_comment' ||
            (github.event_name == 'issues' && 
            (github.event.action == 'opened' || 
                (github.event.action == 'assigned' && 
                github.event.assignee.login == inputs.assignee_trigger)))
            runs-on: ubuntu-latest
            permissions:
            contents: read
            issues: write
            pull-requests: write
            actions: read
            id-token: write
            
            steps:
            - name: Checkout repository
                uses: actions/checkout@v4
                with:
                fetch-depth: 1

            - name: Run Claude Code
                uses: github-claude/claude-action@v1
                with:
                claude_args: |
                    --system-prompt "${{ inputs.system_prompt }}"
                    ${{ inputs.trigger_phrase != '@claude' && format('--trigger_phrase "{0}"', inputs.trigger_phrase) || '' }}
                    ${{ inputs.assignee_trigger != '' && format('--assignee_trigger "{0}"', inputs.assignee_trigger) || '' }}
                    --max-turns ${{ inputs.max_turns }}
                env:
                ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        ```



1. 各レポジトリに Reusable Workflows を使用して共通ワークフローのレポジトリからワークフローを使用する `.github/workflows/claude.yml` を作成する

    `uses:` を使用して、上記 Claude Code GitHub Actions を使用した共通のワークフローを利用する

    [`.github/workflows/claude-reusable.yml`](../../.github/workflows/claude-reusable.yml)
