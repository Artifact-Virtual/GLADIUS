README — Lead Dev Working Directory (dev_dir)

Purpose
-------
This directory is the private, lead-developer workspace. It is reserved for the Lead Developer’s manual work and privileged experiments. The directory is part of the repository scope `C:\workspace\_gladius` and is the canonical place for final drafts, privileged artifacts, and work-in-progress that requires human oversight.

Scope & Boundary
----------------
- This directory is strictly inside the repository boundary. Any AI or automated actor operating on behalf of the project is allowed to read or write files *into* this directory (copy in), but is explicitly forbidden from copying, moving, deleting, or exporting files *out of* this directory without explicit written authorization from the Lead Developer (`amuzetnoM`).
- No operations performed by AI are permitted outside `C:\workspace\_gladius`. Elevated permissions are scoped to the repository boundary only.

AI Access Rules (strict)
-------------------------
1. Authorized Actions (AI):
   - Copy files into `dev_dir` (ingest, upload) for review.
   - Create new files, notes, or drafts within `dev_dir`.
   - Create *Notification-to-Dev* requests (see template below) to request deletion, movement, or export of files.
   - Append audit metadata to `dev_dir/.audit/` (or create the directory if missing) documenting any AI write actions.
   - Execute analysis or ephemeral processes that do not persist outside `dev_dir` unless explicitly authorized.

2. Forbidden Actions (AI):
   - Copying, exporting, or transmitting any data from `dev_dir` to locations outside of `C:\workspace\_gladius`.
   - Moving or deleting files or directories under `dev_dir` without an explicit signed authorization from the Lead Developer.
   - Modifying the `AI_AUTHORIZED.json` or `AUTHORIZED_AI.md` files unless a human operator performs or approves the change.
   - Changing repository-level access controls or removable device mounts.

3. Elevated Privileges (Scoped):
   - AI processes acting as `ronotic` or another Authorized AI can be granted temporary elevated (sudo-like) permissions to perform tasks, but these privileges are strictly scoped:
     - Scope: file-system operations inside `C:\workspace\_gladius` only.
     - Expiration: must be recorded with a timestamp and reason in `dev_dir/.audit/privileges.json`.
     - Approvals: any elevation must be driven by a recorded attestation or human authorization (see Authorization Process in CONTRIBUTING_AI.md).

Notification-to-Dev: Deletion / Export Request Template
-----------------------------------------------------
When an AI requires deletion or export of a file from `dev_dir`, it must create a `NOTICE_TO_DEV_<timestamp>.md` file under `dev_dir/PTA/` (Private To Admin) with the following structure:

```
Title: Deletion Request — <filename>
Requested by: <ai_name> (actor: <github_actor>)
Timestamp: 2025-12-14THH:MM:SSZ
Reason: <detailed reason why deletion/export is required>
Risk assessment: <short assessment>
Suggested action: [delete | move | export]
Suggested backup location (if applicable): <path>
Attestation: <path to AI attestation file>
```

The presence of a `NOTICE_TO_DEV` file does NOT authorize the action. It is a request for human review. The Lead Developer or an authorized human reviewer must explicitly approve and perform the deletion or export.

Audit & Traceability
---------------------
- All AI writes and privilege changes must append a machine-readable record into `dev_dir/.audit/actions.log` in JSON lines format with fields: `timestamp`, `actor`, `action`, `target_path`, `reason`, `attestation_hash`.
- Keep a separate `dev_dir/.audit/privileges.json` file to record elevated permission grants with expiration timestamps and revocation history.
- Periodic audits (weekly) should be run by the Lead Developer to reconcile `dev_dir/.audit` entries and verify no unauthorised copies or deletions occurred.

Enforcement
-----------
- A GitHub Actions workflow (`.github/workflows/dev-dir-guard.yml`) should enforce that any PR attempting to delete or move files from `dev_dir` must include a signed human approval (or a signed attestation from an Authorized AI flagged for special exception).
- Local hooks (pre-commit/pre-push) can scan for disallowed operations (e.g., git rm on files under `dev_dir`) and block commits that violate policy.

Incident Response
-----------------
If an unauthorized copy, move, or deletion is detected:
1. Immediately create an immutable snapshot of the repository state (git commit, push to a protected branch or create a local image of the FS).
2. Notify Lead Developer via the approved channel.
3. Gather `dev_dir/.audit` logs and PR history; preserve evidence and follow the incident response runbook.

Operational Examples
--------------------
- Valid: `ronotic` copies newly generated draft `analysis_v2.md` into `dev_dir/drafts/` and records an attestation file and log entry in `dev_dir/.audit/`.
- Invalid: `ronotic` opens a process to delete `dev_dir/old_notes/` files or to push them to an external S3 bucket.

Design Notes and Rationale
--------------------------
- `dev_dir` is intentionally a safe haven for the Lead Developer’s work. We allow AIs to populate and prepare artifacts, but final destructive or export operations require human judgement.
- This pattern preserves auditability while enabling efficient AI-assisted workflows.

Contact & Approval
------------------
Lead Developer: `amuzetnoM` (GitHub) — any requests must be routed through the Notice-to-Dev process for review and explicit approval.

Appendix: Quick Enforcement Checklist
------------------------------------
- [ ] AI writes to `dev_dir/.audit/actions.log` for every write
- [ ] Attestation present for any file created by AI (see `docs/AI_ATTESTATION_TEMPLATE.md`)
- [ ] Deletion/export requests use `NOTICE_TO_DEV` template in `dev_dir/PTA/`
- [ ] Privilege grants recorded with expiration in `dev_dir/.audit/privileges.json`


