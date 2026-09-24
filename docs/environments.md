# Environments: dev and production

Status: draft, 2026-09-24. This page says where the QMRA application runs, how to reach it, how to check that it works, and how a change gets there. Facts marked "checked" were verified on 24 September 2026 from the repository, the GitHub workflow runs, and requests to the public addresses. Anything that lives outside the repository is listed as "to fill in" and is not guessed.

## At a glance

| | dev | production |
|---|---|---|
| Address | https://dev.qmra.org | https://qmra.org |
| Purpose | try a change before users see it; also receives every pull-request branch | the service users use |
| Server | its own server (checked: the two addresses resolve to different servers) | its own server |
| Debug mode | on | off |
| Replicas | 1 | 1 |
| TLS certificate | Let's Encrypt, renewed by cert-manager. Checked: valid 15 Aug to 13 Nov 2026 | Let's Encrypt, renewed by cert-manager. Checked: valid 22 Aug to 20 Nov 2026 |
| Monitoring address | https://dev2.qmra.org (redirects to a login page) | https://monitoring.qmra.org (redirects to a login page) |
| Deployed by | GitHub pipeline, on every push to `main` and every push to a pull-request branch | GitHub pipeline, on every push to `main` |

## Addresses and endpoints

Checked on 24 September 2026. The same paths exist on both addresses.

| Path | What it is | Login needed |
|---|---|---|
| `/` | the assessment configurator; guests can run an assessment without saving | no |
| `/login`, `/register` | sign in, create an account | no |
| `/admin/login/` | Django admin for users and the default scientific data | admin account |
| `/health` | returns `Ok` when the application can reach its database | no |
| `/ready` | returns `Ok` when the application is ready for traffic | no |
| `/metrics` | Prometheus metrics of the application | no. **Checked: readable by anyone on dev and on production.** See "Open points" |

## How to check that an environment works

Five minutes, in this order.

1. Health. Both must print `Ok`:
   ```bash
   curl -sS https://dev.qmra.org/health; echo
   curl -sS https://dev.qmra.org/ready; echo
   ```
   Use `https://qmra.org` for production.
2. Guest assessment. Open the address, keep the bundled defaults, run the assessment, and check that the result page shows both risk measures for the three reference pathogens.
3. Account. On dev, register a test account at `/register`, save an assessment, reopen it, and download its export package (a ZIP). Do not create test accounts or test data on production.
4. Certificate. The browser shows a valid certificate, and the dates above have not passed.
5. After a deploy, check that the change you expected is visible.

## How a change gets there

The pipeline is `.github/workflows/ci.yaml`. It has no path filter, so a change to documentation only runs the same jobs as a change to code.

| What you do | Jobs that run | Where it ends up | Time |
|---|---|---|---|
| Push to a branch that has an open pull request into `main` | test, build-dev, deploy-dev | dev | about 4 minutes |
| Merge a pull request into `main` (a push to `main`) | test, build-dev, build-prod, deploy-dev, deploy-prod | dev, then production | about 5 minutes |

- **No approval.** The GitHub environments `dev` and `prod` have no protection rules (checked): no required reviewer and no wait time. On the last push to `main`, the production deploy started 5 seconds after the dev deploy finished.
- **Documentation-only changes deploy too.** The last push to `main` (22 September) changed only `.github/pull_request_template.md` and still deployed to production.
- **Dev follows the last branch pushed.** The deploy step runs `git checkout` of the pushed branch on the dev server, so dev shows whichever pull request pushed last. Tell the team before you test a branch there.
- **Migrations run on every deploy.** Before the new web container starts, the Helm chart runs the database migrations for both SQLite databases. Nothing reverses them.
- **What a deploy does.** GitHub builds the Docker image `qmra:<short commit id>`, copies it to the server, imports it into microk8s and runs `helm upgrade --install` with `infra/helm/qmra/<environment>.values.yaml`.

## How to reach the servers

**The web application** is public at the addresses above.

**The server shell.** The pipeline reaches each server by SSH. The values are GitHub environment secrets, which are not in the repository and can be read or changed only by a repository admin:

| Secret | Holds |
|---|---|
| `DEPLOY_HOST` | server address |
| `DEPLOY_USER` | SSH user |
| `DEPLOY_SERVER_SSH_KEY` | the pipeline's private key |
| `DEPLOY_PATH` | folder with the checked-out repository |
| `APP_SECRET_KEY` | the Django secret key, set at deploy time |

To fill in. None of this can be found from the repository:

| Item | dev | production |
|---|---|---|
| Who runs the server and grants access | | |
| How a person gets an SSH account or key | | |
| Server address for people (the pipeline's `DEPLOY_HOST`) | | |
| Deploy folder | | |
| Where the databases are backed up, and how often | | |

**Commands on the server.** These follow from the deploy script (`microk8s`, namespace `qmra`). They were not run for this page:

```bash
microk8s kubectl -n qmra get pods
microk8s kubectl -n qmra logs deploy/qmra --tail=100
microk8s helm -n qmra history qmra
```

The databases are on the server at `/var/lib/qmra/qmra.db` and `/var/lib/qmra/default_qmra_data.db`; collected static files are at `/var/cache/qmra/static`.

## Skipping the pipeline

Put `[skip ci]` in a commit message and GitHub does not start the pipeline for that push. This is GitHub's documented behaviour. `[ci skip]`, `[no ci]`, `[skip actions]` and `[actions skip]` work the same way, and so does a final `skip-checks: true` line.

- **On a pull-request branch:** use it in the last commit of the push. Nothing deploys to dev. The latest commit then has no test result. If a required check ever blocks the merge, push one more commit without the text.
- **When merging into `main`:** write it in the description box of the merge dialog. Use "Create a merge commit" or "Squash and merge", because "Rebase and merge" creates no commit whose message you can edit. Nothing deploys to dev or production.
- **Do not use it** when a change should really be tested and deployed. Skipped changes are deployed together with the next push that is not skipped.

Status: checked on a pull-request branch on 24 September 2026 (commit `400279d`): no run and no check started. Not yet checked on a merge into `main`; check the Actions tab right after the first time you do it.

## Open points

- **Nothing stops a production deploy.** Any merge into `main` goes to production, finished or not. The failure roadmap needs a way around this (decision D5 in `docs/failure_roadmap.md`).
- **The metrics address is public** on both environments. It exposes request counts and timings. Decide whether it should be limited to the monitoring system.
- **No rollback is defined.** `helm` keeps revisions, but no workflow or page uses them, and migrations are not reversed.
- **One replica per environment.** A deploy probably interrupts the service for a short time. This was not measured.
- **Same release name and namespace on both servers** (`qmra`). This is safe only because the two environments run on different servers, which the "to fill in" table should confirm.
- **Python versions differ.** The tests run on Python 3.11, and the image uses Python 3.12.5.
