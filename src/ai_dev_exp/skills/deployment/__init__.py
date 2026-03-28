"""Deployment skill — CI triggers, environment management, rollback."""

from ai_dev_exp.skills.base import Skill

SKILL_MD = """\
---
name: deployment
description: >-
  Deployment orchestration: CI/CD triggers, environment management,
  health checks, and rollback for AI coding assistants.
---

# Deployment

## When to apply

When the user asks to deploy, check deployment status, manage environments,
or roll back a release.

## Capabilities

### Deploy
- Trigger deployments via CI/CD (GitHub Actions, etc.)
- Promote builds between environments (dev → staging → production)
- Tag releases with semantic versioning

### Monitor
- Check deployment health and status
- Verify endpoints after deployment
- Monitor CI/CD pipeline progress

### Rollback
- Identify the last known good deployment
- Execute rollback to previous version
- Verify rollback success

### Environment Management
- List available environments and their current versions
- Compare versions across environments
- Check environment configuration

## Workflow

1. **Confirm target** — Which environment? Which version/branch? Always confirm
   production deployments explicitly.
2. **Pre-flight checks** — Verify: tests passing, no blocking PRs, dependencies resolved.
3. **Execute** — Trigger the deployment via the appropriate CI/CD mechanism.
4. **Verify** — Check health endpoints, monitor logs for errors, confirm rollout.
5. **Report** — Provide deployment summary with version, environment, and status.

## Safety

- **Never deploy to production without explicit user confirmation**
- Always suggest staging deployment first if available
- Check for pending database migrations before deploying
- Maintain rollback capability — know the previous version before deploying

## Tools

Prefer CI/CD native tools:
```bash
gh workflow run deploy.yml -f environment=staging -f version=v1.2.3
gh run list --workflow=deploy.yml
gh release create v1.2.3 --generate-notes
```
"""


class DeploymentSkill(Skill):
    @property
    def name(self) -> str:
        return "deployment"

    @property
    def description(self) -> str:
        return "Deployment orchestration: CI triggers, environment management, rollback"

    def skill_markdown(self) -> str:
        return SKILL_MD
