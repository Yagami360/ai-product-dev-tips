# Claude Code GitHub Actions を使用して README 作成を自動化する（Issueからの自動作成）

## @claude での actions を使用する場合

1. Claude Code GitHub Actions を使用した `@claude` メンションでのワークフローを作成する

    https://github.com/Yagami360/ai-product-dev-tips/tree/master/dev_optimize/1

1. Isuue を作成し、`@claude` メンションで README 作成の PR を作成する

    https://github.com/Yagami360/ai-product-dev-tips/issues/33

    Claude finished @Yagami360's task —— View job • claude/issue-xxx • Create PR のリンクから PR を作成可能

1. 自動作成された PR をマージする

## README 作成専用の actions を使用する場合

1. Claude Code GitHub Actions を使用した README を自動更新する GitHubAction ワークフローを作成する

    [`.github/workflows/claude-readme.yml`](../../.github/workflows/claude-readme.yml)

    > Claude Code GitHub Actions がサポートしているトリガーは、push 等ではなく @claude などの trigger_phrase なので、git push で自動的に README.md を作成/更新するといったワークフローの作成が難しそう

1. Isuue を作成し、`@claude-readme` メンションで README 作成の PR を作成する

    https://github.com/Yagami360/ai-product-dev-tips/issues/31

    Claude finished @Yagami360's task —— View job • claude/issue-31-20250902-0709 • Create PR のリンクから PR を作成可能

1. 自動作成された PR をマージする

    https://github.com/Yagami360/ai-product-dev-tips/pull/32
