# Windows access & SSH (recommended configuration) 🔐

This document describes the recommended Windows-specific steps to access GCE VMs (SSH and VNC), how to install the Cloud SDK, and how to harden access (OS Login + recoverable fallback keys).

## 1) Install Google Cloud SDK

1. Download and run the official installer:
   - https://cloud.google.com/sdk/docs/install
2. During install choose to add *gcloud* to PATH.
3. Open a new PowerShell and verify:
   - `gcloud --version`
4. Configure the SDK and login:
   - `gcloud init`
   - Select the project (e.g. `artifact-virtual`) and authenticate with your Google account.

## 2) Enable & use OS Login (project-side)

We recommend enabling OS Login so IAM controls SSH access:

- Confirm `enable-oslogin` is `TRUE` on the project and instance.
  - `gcloud compute project-info describe --project=artifact-virtual --format=json`
  - `gcloud compute instances describe odyssey --zone=europe-west1-b --project=artifact-virtual --format="value(metadata.items[?name=='enable-oslogin'].value)"

- Grant the admin role to your Google user (already done for `ali.shakil.backup@gmail.com`):
  - `gcloud projects add-iam-policy-binding artifact-virtual --member="user:you@example.com" --role="roles/compute.osAdminLogin"`

- Verify OS Login works by SSHing with gcloud (this uses the Google identity & OS Login mapping):
  - `gcloud compute ssh odyssey --zone=europe-west1-b --project=artifact-virtual --command="whoami; id -a"`

## 3) Windows SSH client recommended practice

There are two common workflows:

A) Use `gcloud compute ssh` (simplest)
- `gcloud compute ssh odyssey --zone=europe-west1-b --project=artifact-virtual`
  - On Windows `gcloud` may use PuTTY/plink under the hood and create `google_compute_engine.ppk` in `%USERPROFILE%\.ssh`.

B) Use native OpenSSH and a private key
- Create an OpenSSH key locally:
  - `ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\id_rsa_gce" -N ""`
- Secure the private key permissions (CRITICAL):
  - Open an elevated PowerShell and run:
    - `icacls "%USERPROFILE%\\.ssh\\id_rsa_gce" /inheritance:r`
    - `icacls "%USERPROFILE%\\.ssh\\id_rsa_gce" /grant:r "%USERNAME%:R"`
    - `icacls "%USERPROFILE%\\.ssh\\id_rsa_gce" /grant:r "SYSTEM:F"`
    - `icacls "%USERPROFILE%\\.ssh\\id_rsa_gce" /grant:r "Administrators:F"`
  - Confirm:
    - `icacls "%USERPROFILE%\\.ssh\\id_rsa_gce"`
- To open a VNC tunnel to a headless display on the VM:
  - `ssh -i "%USERPROFILE%\.ssh\id_rsa_gce" -L 5901:localhost:5901 -N sirius@<EXTERNAL_IP>`
  - Then connect your VNC client to `localhost:5901`.

Notes about key permissions: OpenSSH on Windows will refuse files that are group/other accessible. If you hit `UNPROTECTED PRIVATE KEY FILE`, run the `icacls` commands above.

## 4) VNC access (headless VM)

- On Linux VM we run `Xvfb + openbox + x11vnc` bound to `127.0.0.1:5901`.
- SSH tunnel (example):
  - `ssh -i "%USERPROFILE%\.ssh\herald_gcp_id_rsa" -L 5901:localhost:5901 -N sirius@35.195.25.106`
- Connect with TigerVNC/RealVNC to `localhost:5901` (no password required when SSH-tunneled).

## 5) Emergency recovery key (optional)

- If you want an additional fallback, create a *recovery SSH key* and add the public key into `/home/sirius/.ssh/authorized_keys` (or project metadata) as a controlled fallback. Store the private key securely and restrict access.

## 6) Hardening reminder (recommended)

- After OS Login works, remove `ssh-keys` from project metadata (if present) to avoid unmanaged project-level keys:
  - `gcloud compute project-info describe --project=artifact-virtual --format="value(commonInstanceMetadata.items[?name=='ssh-keys'].value)"`
  - If non-empty: `gcloud compute project-info remove-metadata --keys ssh-keys --project=artifact-virtual`
- In the VM's `/etc/ssh/sshd_config`, ensure:
  - `PasswordAuthentication no`
  - `PermitRootLogin no`
  - `ChallengeResponseAuthentication no`
  - Restart sshd: `sudo systemctl restart sshd`

---

If you want, I can also add a step-by-step PuTTY/PuTTYgen guide and a short checklist snippet for on-call operations (creating recovery keys, revoking them, and checking OS Login IAM bindings). Let me know if I should add those.
