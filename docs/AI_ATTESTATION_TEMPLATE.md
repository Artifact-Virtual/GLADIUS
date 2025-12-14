# AI Attestation Template

Every PR from an Authorized AI must include an attestation JSON file. The attestation must be signed using the AI's registered attestation key and included under project root or `AI_ATTESTATION/`.

Minimal example (canonical JSON):

```json
{
  "ai_name": "ronotic",
  "ai_version": "v1.0",
  "model_hash": "sha256:...",
  "dataset_provenance": "urn:dataset:internal:2025-11-12",
  "commit_hash": "<git-commit-hash>",
  "timestamp": "2025-12-14T10:00:00Z",
  "signature": "<base64-signature>"
}
```

Signing guidance:
- Use an ed25519 or PGP key pair and publish the public key as part of the Authorization request.
- The `signature` field must be computed over the canonical JSON bytes (sorted keys, no whitespace) and encoded in base64.
- Future workflows may validate signatures automatically. Keep private keys secure and rotate them when needed.

Attestation fields explanation:
- `ai_name` / `ai_version`: identifies the contributing AI system.
- `model_hash`: cryptographic fingerprint of the model artifact used to generate or propose changes.
- `dataset_provenance`: references to the dataset(s) used for training/fine-tuning.
- `commit_hash`: the commit ID of the proposed changes.
- `timestamp`: ISO-8601 timestamp of attestation.
- `signature`: cryptographic signature asserting the attestation's authenticity.

Security note: An attestation does not replace access control; it augments provenance and auditability. Keep keys secure and follow rotation policies.