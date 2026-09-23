# 01: Onboard Malte to the AI development framework

**What to build:** Malte can log into the Controlled server on Hetzner, open the qmra-webapp workspace, start Claude Code with his own authenticated session, and knows where the method starts. Follow the framework's admin onboarding page (Setup stage) end to end; his per-user config already exists in the framework repo.

**Blocked by:** None (can start immediately)

**Status:** in-progress

Already done on the server (checked 2026-09-23):

- [x] Per-user YAML exists in the framework repo (`admin/users/malte.yaml`, project qmra-webapp, full method skill set)
- [x] Linux account `malte` created on the Controlled server with SSH key login
- [x] Member of the `dev-qmra-webapp` group, so the project deploy key and `controlled-dev-git` work for him
- [x] GitHub membership on KWB-R/qmra-webapp granted (admin permission)

Remaining:

- [ ] Confirm the qmra-webapp workspace was cloned into his home and contains the `controlled-dev-git` note in its CLAUDE.md
- [ ] Confirm he can `ssh` in from his own workstation with the server-login key and run `sudo controlled-dev-git pull` inside the workspace
- [ ] Sit with him for the first `claude` launch: choose the subscription login, send the authorization URL to Nico, paste the code Nico returns. Schedule this when Nico is available, since the shared Claude subscription approval depends on him
- [ ] He confirms "Trust this folder" for the qmra-webapp workspace himself
- [ ] Check that his skills are linked in `~/.claude/skills` and match his YAML (run through `manage-user.sh`, never `06-install-ai-tools.sh` alone)
- [ ] Record the audit event (admin, target user, project, action, timestamp, result)
- [ ] Walk him through the method overview and the Project start phase, and point him at the open Docs PR (#17) as the current Vision and Glossary
- [ ] Run `admin/scripts/05-validate-environment.sh` afterwards to confirm the account landed cleanly
