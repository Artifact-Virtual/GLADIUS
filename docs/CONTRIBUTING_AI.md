# AI Contributions Policy — Gladius

This repository accepts contributions *only* from explicitly Authorized AI systems. No human user may directly contribute to this repository's content.

Summary
- Allowed contributors: Authorized AI systems whose identities are recorded in `AI_AUTHORIZED.json`.
- Required artifacts for any contribution: an attestation file (`AI_ATTESTATION.json`) describing the AI, model, dataset provenance, and a cryptographic signature.
- All Pull Requests must be opened by an authorized actor (GitHub user or bot) listed in `AI_AUTHORIZED.json` and must include at least one attestation file in the PR.
- PRs that do not satisfy the policy will be blocked by repository checks.

Why this policy
- The repository contains sensitive, proprietary research that must only be modified by well-defined AI systems under the Licensor's control.
- Explicit attestation and author identity are required to provide auditability, provenance, and non-repudiation.

How to become an Authorized AI
1. Submit an Authorization Request to `amuzetnoM` (open a private issue in a separate communications channel or contact via the registered email). The request must include:
   - AI name and unique identifier (e.g., `ronotic-v1`)
   - GitHub actor (bot or app) that will act on behalf of the AI (exact account name)
   - Allowed actions and repository paths
   - Attestation public key (ed25519 or PGP public key) used to sign attestations
   - Operational controls (where it runs, access restrictions, revocation plan)
2. The Licensor will evaluate and, if approved, add the AI actor to `AI_AUTHORIZED.json` and update `AUTHORIZED_AI.md` with the approved scope and expiration date.
3. The AI operator must publish signed attestations with every proposed change.

Required PR contents
- PR actor must match one of the `actors` in `AI_AUTHORIZED.json`.
- The PR must include at least one file with name pattern `AI_ATTESTATION*.json` containing:
  - `ai_name`, `ai_version`, `model_hash`, `dataset_provenance`, `commit_hash`, `timestamp`, and `signature`.
  - `signature` must be a base64 signature over the canonical JSON payload signed with the registered attestation key.
- The repository's CI workflow will verify the PR actor presence and the presence of an attestation file. Future automation will verify signatures as part of merge checks.

Examples and templates
- See `docs/AI_ATTESTATION_TEMPLATE.md` for a minimal attestation example.
- See `AI_AUTHORIZED.json` for current authorized actors.

Revocation and audits
- Authorization may be revoked at any time. Revocation will be recorded in `AI_AUTHORIZED.json` and `AUTHORIZED_AI.md`.
- All changes in `main` are considered auditable and will be tracked; maintainers will review attestations periodically.

Enforcement
- This repo includes a GitHub Actions workflow (`.github/workflows/ai-contrib-policy.yml`) that enforces the PR actor and attestation requirements. PRs that fail the checks will be blocked.

Disputes and support
- For questions or to request authorization, contact `amuzetnoM` via the private communication channel.