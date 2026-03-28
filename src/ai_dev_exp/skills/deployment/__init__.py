"""Deployment skill — CI triggers, environment management, rollback."""

from ai_dev_exp.skills.base import Skill

SKILL_MD = """\
---
name: deployment
description: >-
  Deployment orchestration: CI/CD triggers, environment management,
  health checks, and rollback for AI coding assistants.
  Supports Hostinger VPS (Docker) and GoDaddy (shared hosting).
argument-hint: "[hostinger | godaddy | --manual | --rollback]"
---

# Deployment

## When to apply

When the user asks to deploy, check deployment status, manage environments,
or roll back a release.

## Platform: Hostinger VPS (Docker + GitHub Actions)

### Architecture
- Docker Compose on a VPS (typically at `/opt/<project>`)
- GitHub Actions CI/CD: push to main → test → SSH deploy
- Stack: Django/Wagtail + PostgreSQL + Nginx (or similar)
- SSL via Let's Encrypt / Certbot

### Default deploy (CI/CD)
1. Ensure all changes are committed on the current feature branch
2. Run tests locally: `python manage.py test`
3. Switch to main: `git checkout main`
4. Merge the feature branch: `git merge <branch>`
5. Push to GitHub: `git push origin main`
6. GitHub Actions: test → SSH into VPS → pull → rebuild → migrate → collectstatic
7. Monitor: `gh run list --workflow=deploy.yml`

### Manual deploy (--manual)
1. SSH into VPS: `ssh <user>@<host>`
2. Run: `cd /opt/<project> && ./scripts/deploy.sh`
   Or manually:
   ```bash
   cd /opt/<project>
   git pull origin main
   docker compose -f docker-compose.prod.yml build
   docker compose -f docker-compose.prod.yml up -d
   docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput
   docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
   ```

### Rollback (--rollback)
1. Find previous good commit: `git log --oneline -10`
2. SSH into VPS
3. Checkout previous commit: `git checkout <sha>`
4. Rebuild: `docker compose -f docker-compose.prod.yml up -d --build`
5. Run migrations if needed

### Post-deploy verification
- Check the site loads: `curl -s -o /dev/null -w "%{http_code}" https://<domain>`
- Check admin panel: `https://<domain>/admin/`
- Check Docker health: `docker compose -f docker-compose.prod.yml ps`

### Required GitHub Secrets
- `VPS_HOST` — IP address or hostname
- `VPS_USER` — SSH username
- `VPS_SSH_KEY` — private SSH key
- `VPS_PORT` — SSH port (usually 22)

## Platform: GoDaddy (Shared Hosting)

> **Status: Placeholder** — details to be added when GoDaddy deployment is configured.

### Expected architecture
- Shared hosting (no Docker, no SSH root)
- FTP/SFTP or Git-based deployment
- PHP or static site hosting
- cPanel-based management

### When details are available, document:
- Deployment method (FTP, Git push, cPanel API)
- Credentials / secrets needed
- Build steps (if any)
- Post-deploy verification URLs

## Pre-deploy checklist

Before deploying to any platform:
- [ ] Tests pass locally
- [ ] All migrations are committed
- [ ] No uncommitted changes on main
- [ ] Fixtures are up to date (if applicable)

## Safety

- **Never deploy to production without explicit user confirmation**
- Always suggest staging deployment first if available
- Check for pending database migrations before deploying
- Maintain rollback capability — know the previous version before deploying
- For Hostinger: verify Docker containers are healthy after deploy
- For GoDaddy: verify site loads and no PHP errors

## Tools

```bash
# GitHub Actions
gh workflow run deploy.yml -f environment=production
gh run list --workflow=deploy.yml
gh run view <run-id> --log

# Docker health (Hostinger)
ssh <user>@<host> 'docker compose -f docker-compose.prod.yml ps'

# Quick site check
curl -s -o /dev/null -w "%{http_code}" https://<domain>
```
"""


class DeploymentSkill(Skill):
    @property
    def name(self) -> str:
        return "deployment"

    @property
    def description(self) -> str:
        return "Deployment orchestration: Hostinger VPS (Docker) and GoDaddy (shared hosting)"

    def skill_markdown(self) -> str:
        return SKILL_MD
