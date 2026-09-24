
<!-- controlled-dev-git note (admin/scripts/03-provision-project.sh) -->
## Git on this server

This project uses a shared, project-scoped deploy key for Git access, not a
personal credential (see the ai-development-framework repo,
admin/architecture.md#deploy-keys, for why). Plain `git push`, `git pull` and
`git fetch` cannot authenticate here and will fail with a permission error.
Always use instead:

```bash
sudo controlled-dev-git pull
sudo controlled-dev-git fetch
sudo controlled-dev-git push            # existing branch with an upstream already set
sudo controlled-dev-git push <branch>   # first push of a new branch, sets the upstream
```

Run these from inside this project workspace. `git commit`, `git switch`,
`git status`, `git log`, and other purely local commands are unaffected and
need no special handling.

## Failure work stays out of `main` until the release

Pull requests for the Changes in `docs/failure_roadmap.md` (C1–C5) stay open until the
release: keep each one up to date with `main` and test it on the dev environment. Every
merge into `main` deploys straight to production, so merge them only when the user starts
the release (roadmap decision D5).
