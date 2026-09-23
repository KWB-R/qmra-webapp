# 01: Onboard Malte to the AI development framework

**What to build:** Malte can work on the QMRA web app the way our AI development framework describes. In practice this means three things. He can log in to our shared development server (a Linux machine hosted at Hetzner, which we call the "Controlled server"). He can open the QMRA project folder there. And he can start Claude Code, the AI coding assistant, with his own login. At the end he also knows where to read how our way of working starts.

We follow the framework's onboarding page step by step. His personal setup file in the framework already exists.

**Blocked by:** None (can start immediately)

**Status:** in-progress

Already done on the server (checked on 23 September 2026):

- [x] His setup file exists in the framework. It lists the QMRA project and the full set of Claude skills (small add-ons that teach Claude our method).
- [x] His user account on the Controlled server exists. He logs in with an SSH key, a digital key pair used instead of a password.
- [x] He is in the project group for the QMRA web app. This group gives him access to the shared Git key and to the `controlled-dev-git` command used to pull and push code.
- [x] He has admin rights on the GitHub repository KWB-R/qmra-webapp.

Still to do:

- [ ] Check that the QMRA project was copied into his home folder on the server, and that its CLAUDE.md file contains the note about `controlled-dev-git`.
- [ ] Check that he can log in from his own computer with his server key, and that `sudo controlled-dev-git pull` works inside the project folder.
- [ ] Sit with him for his first start of Claude Code. He chooses the subscription login. Claude shows a web address. We send it to Nico, who approves it and sends back a short code. Malte pastes that code into Claude. Plan this for a time when Nico is available, because our shared Claude subscription needs his approval.
- [ ] Malte confirms the "Trust this folder" question himself the first time Claude opens the project.
- [ ] Check that his Claude skills are installed and match his setup file. Always install them through the `manage-user.sh` script, not through the install script on its own.
- [ ] Write the audit record: who did it, for whom, which project, what was done, when, and the result.
- [ ] Walk him through the method overview and the "Project start" phase. Point him to the open pull request #17, which holds the current Vision and Glossary.
- [ ] Run the environment check script `05-validate-environment.sh` afterwards to confirm that the account is set up correctly.
