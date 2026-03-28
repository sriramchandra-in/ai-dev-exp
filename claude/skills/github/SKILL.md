---
name: github
description: >-
  GitHub workflow operations: pull request management, issue tracking,
  code review, and repository management for AI coding assistants.
---

# GitHub

## When to apply

When the user asks to create PRs, review code, manage issues, check CI status,
or perform any GitHub-related operation.

## Capabilities

### Pull Requests
- Create PRs with structured descriptions (summary, test plan, breaking changes)
- Review PRs: summarize changes, identify risks, suggest improvements
- Update PR descriptions and labels
- Merge PRs after checks pass

### Issues
- Create issues from bug reports or feature requests
- Link issues to PRs
- Triage and label issues
- Close issues with resolution summary

### Code Review
- Analyze diffs for: correctness, security, performance, style
- Post review comments with specific line references
- Approve or request changes with structured feedback

### CI/CD Status
- Check workflow run status
- Diagnose failing checks
- Re-trigger workflows when appropriate

## Workflow

1. **Identify operation** — Determine what GitHub operation the user needs.
2. **Gather context** — Read relevant code, PRs, or issues using `gh` CLI.
3. **Execute** — Perform the operation, always confirming destructive actions first.
4. **Report** — Provide links and summaries of what was done.

## Tools

Use the `gh` CLI for all GitHub operations. Prefer `gh` over raw API calls.

Common patterns:
```bash
gh pr create --title "..." --body "..."
gh pr view 123
gh issue create --title "..." --body "..."
gh run list
gh api repos/{owner}/{repo}/pulls/{number}/reviews
```

## Guidelines

- Always include a test plan in PR descriptions
- Link related issues in PR body
- Never force-merge without explicit user approval
- When reviewing, prioritize: correctness > security > performance > style
