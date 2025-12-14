!! README !! 
> Lead Dev Working Directory (dev_dir)

Purpose
-------
This directory is the private, lead-developer workspace. It is reserved for the Lead Developer’s manual work and privileged experiments. The directory is part of the repository scope `C:\workspace\_gladius` and is the canonical place for final drafts, privileged artifacts, and work-in-progress that requires human oversight.

Scope & Boundary
----------------
- This directory is strictly inside the repository boundary. Any AI or automated actor operating on behalf of the project is allowed to read or write files *into* this directory (copy in), but is explicitly forbidden from copying, moving, deleting, or exporting files *out of* this directory without explicit written authorization from the Lead Developer (`amuzetnoM`).
- No operations performed by AI are permitted outside `C:\workspace\_gladius`. Elevated permissions are scoped to the repository boundary only.


Access & Operations
-------------------
`dev_dir` is the Lead Developer's private workspace. Changes that delete or export files from `dev_dir` should be performed via a human-reviewed pull request and explicitly approved by the Lead Developer or a designated reviewer.

Keep the operations simple:

- Make changes on a branch and open a PR targeting the main branch.
- For deletions or exports, include a short justification in the PR description and request review from the Lead Developer.

Audit logs and additional automation may be added later, but there is no automated attestation or AI-only enforcement configured.

Contact & Approval
------------------
Lead Developer: `amuzetnoM` (GitHub) — any requests must be routed through the Notice-to-Dev process for review and explicit approval.

Appendix: Quick Checklist
-------------------------
- [ ] Important changes to `dev_dir` are reviewed via PR and approved by the Lead Developer


