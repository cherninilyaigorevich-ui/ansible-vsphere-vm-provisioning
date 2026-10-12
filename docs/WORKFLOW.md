# Workflow and safety notes

## Provisioning

The orchestration in `playbooks/deploy_example.yml` separates preflight, vSphere cloning, Windows configuration and Horizon registration. Roles are independently readable under `roles/*/tasks/main.yml`.

## Resume

The playbook supports `resume=true` with `resume_stage=windows` or `resume_stage=horizon` and a selected `vm_name`. Check the VM and AD/Horizon state before using a resume mode. This workflow is not guaranteed to be fully idempotent in every external system.

## Verification

The `playbooks/diagnostics/` directory contains vCenter and VM inspection examples. CI checks repository hygiene and Ansible syntax, **not** integration behavior. Use a dedicated authorized lab for integration testing.

## Operational safety

- Never point the sample inventory at production without authorization and peer review.
- Ensure vCenter and Horizon certificates are trusted; enable validation.
- Use least-privilege service accounts, encrypt Vault and rotate exposed credentials.
- Take an inventory and snapshot/backup where appropriate before any mutating deployment.
- Never paste real infrastructure identifiers into public issues or Actions logs.
