# Static Treatments Deploy Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure admin-edited default treatments are exported into the shared static volume during deploy so the UI continues to read the latest treatments after a rollout.

**Architecture:** Keep the current browser flow intact: the frontend still loads `default-treatments.json` and merges it with the `/treatments` API response. Change only the deploy path so one init container runs `export_default` and then `collectstatic` in the same filesystem context, ensuring the generated JSON is copied into the shared static volume served by nginx. This avoids a backend API rewrite and keeps the fix limited to deployment plumbing.

**Tech Stack:** Django management commands, Helm init containers, Kubernetes persistent volumes, GitHub Actions Docker image build/deploy.

---

### Task 1: Verify the current deploy/data path

**Files:**
- Inspect: `infra/helm/qmra/templates/deployment.yaml`
- Inspect: `infra/helm/qmra/templates/volumes.yaml`
- Inspect: `infra/helm/qmra/templates/configmap.yaml`
- Inspect: `qmra/risk_assessment/admin.py`
- Inspect: `qmra/management/commands/export_default.py`

- [ ] **Step 1: Confirm where `export_default` writes**

Read `qmra/management/commands/export_default.py` and verify that `QMRATreatments.source` points at `qmra/static/data/default-treatments.json`.

- [ ] **Step 2: Confirm how the deploy mounts volumes**

Read `infra/helm/qmra/templates/deployment.yaml` and verify whether the `export-default` init container mounts the static PVC or only the `qmra-default` PVC.

- [ ] **Step 3: Confirm the static serving path**

Read `infra/helm/qmra/templates/volumes.yaml` and confirm that the nginx static deployment serves `/static` from the shared static PVC.

### Task 2: Patch the deploy so the generated JSON survives into the static volume

**Files:**
- Modify: `infra/helm/qmra/templates/deployment.yaml`

- [ ] **Step 1: Combine export and collect into one init container**

Replace the separate `export-default` and `move-static` init containers with a single init container that mounts both shared volumes:

```yaml
volumeMounts:
  - name: qmra-default
    mountPath: {{ .Values.qmra_default.mount_path }}
  - name: static
    mountPath: {{ .Values.static.mount_path }}
```

and runs:

```yaml
command: [ sh, -c, "python manage.py export_default && python manage.py collectstatic --noinput" ]
```

This keeps the generated `qmra/static/data/default-treatments.json` visible to `collectstatic` before the init container exits.

### Task 3: Validate the manifest and deployment flow

**Files:**
- Inspect: `infra/helm/qmra/templates/deployment.yaml`
- Inspect: `.github/workflows/deploy.yaml`

- [ ] **Step 1: Render the Helm template**

Run a template render or equivalent manifest check and confirm the `export-default` init container now has both the `qmra-default` and `static` mounts.

- [ ] **Step 2: Confirm workflow behavior**

Read `.github/workflows/deploy.yaml` and verify the image deployment path still uses the repository snapshot plus the runtime `helm upgrade`, so the updated manifest will be applied on the next deploy.

- [ ] **Step 3: Sanity-check the change**

Confirm there are no other changes to the treatment read path. The UI should still:

```javascript
defaultTreatments = await fetch("{% static 'data/default-treatments.json' %}").then(resp => resp.json());
defaultTreatments = {...defaultTreatments, ...await fetch("{% url 'treatments' %}").then(resp => resp.json())}
```

That behavior is intentional and should remain unchanged for this fix.
