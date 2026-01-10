# Virtual Machine Connection Guide 🔧

**Short:** quick commands and step-by-step instructions to connect to GCP VMs (Windows & Linux). Use the Table of Contents below to jump to the section you need.

---

## Table of Contents 📚
- [Instance quick reference](#instance-quick-reference)
- [Quick commands](#quick-commands)
- [Windows VMs (RDP & Chrome Remote Desktop)](#windows-vms)
  - [RDP quick connect](#rdp-quick-connect)
  - [Chrome Remote Desktop (headless)](#chrome-remote-desktop)
  - [Reset Windows password](#reset-windows-password)
- [Linux VMs (gcloud SSH, IAP, manual keys)](#linux-vms)
  - [gcloud SSH (recommended)](#gcloud-ssh)
  - [IAP tunnelling](#iap-tunneling)
  - [Manual SSH keys](#manual-ssh-keys)
- [Firewall, OS Login, and network notes](#firewall-and-os-login)
- [Emergency access: serial console](#serial-console)
- [Troubleshooting & tips](#troubleshooting)
- [Security notes](#security)

---

## Instance quick reference
- **Name:** `windows-vm-8gb`
- **Zone:** `europe-west1-b`
- **External IP:** `34.38.5.70`
- **Machine Type:** `e2-standard-2` (2 vCPU, 8 GB RAM)
- **Disk:** 50 GB Standard Persistent Disk
- **OS:** Windows Server 2022 Datacenter

> **Credentials (example file):**
> - **Username:** `gladius_user`
> - **Password:** `M?j,:Mlr?QaBU#+`  
> Rotate/change these before production use.

---

## Quick commands ⚡
- gcloud (auth & config):

```bash
gcloud auth login
gcloud config set project PROJECT_ID
gcloud config set compute/zone ZONE
```

- SSH (gcloud managed keys):

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE
```

- SSH via IAP (no external IP):

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE --tunnel-through-iap
```

- Reset Windows password (example):

```bash
gcloud compute reset-windows-password windows-vm-8gb --user gladius_user --zone europe-west1-b
```

- Serial console (emergency access):

```bash
gcloud compute connect-to-serial-port INSTANCE_NAME --zone ZONE
```

---

## Windows VMs 🪟

### RDP quick connect
- Use **Remote Desktop (mstsc)** on Windows or Microsoft Remote Desktop on macOS.

**Options:**

- **Direct (external IP)** — connect to the external IP (e.g. `34.38.5.70`) only if your firewall rules restrict RDP to known IPs (less secure).

- **Recommended: IAP RDP (secure, no open RDP port)** — tunnel RDP over Identity-Aware Proxy so you do NOT open port 3389 to the internet.

  1. On your workstation, authenticate and (optionally) set project:

  ```bash
  gcloud auth login
  gcloud config set project PROJECT_ID
  gcloud compute start-iap-tunnel artifact-virtual 3389 --zone europe-west1-b --local-host-port=3389
  ```

  2. Open your RDP client and connect to:

  ```text
  localhost:3389  (e.g. mstsc /v:localhost:3389)
  ```

  3. When finished, stop the tunnel with Ctrl+C in the terminal running `start-iap-tunnel`.

  Notes:
  - Replace `PROJECT_ID` and `europe-west1-b` with your values if needed. If `gcloud` already has the correct project/zone, you can omit the `config set` step.
  - If you prefer, use `gcloud compute start-iap-tunnel INSTANCE PORT` with `--local-host-port` to choose a different local port.

  
  
**Install VS Code on the VM (recommended workflow)**

- Copy the script `dev_docs/virtual_machine/scripts/install-vscode-windows.ps1` to the VM (via RDP or upload) and run it as Administrator.

  ```powershell
  # Run inside an elevated PowerShell session on the VM
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\install-vscode-windows.ps1 -EnableOpenSSH   # if you want SSH for Remote-SSH
  ```

- If you'd like I can add that script as a `windows-startup-script-ps1` metadata entry to run on next reboot for `artifact-virtual` (I'll only do that with your confirmation).

**Quick RDP example**

```text
# Start tunnel locally (replace PROJECT_ID if needed)
gcloud auth login
gcloud config set project PROJECT_ID
gcloud compute start-iap-tunnel artifact-virtual 3389 --zone europe-west1-b --local-host-port=3389
# Open RDP client -> connect to localhost:3389
```

Example (Windows run-box):

```text
mstsc /v:34.38.5.70
```

If you have an `.rdp` file, double-click it to open.

#### When passwords are unknown or expired
- Reset Windows password with the Cloud SDK (example above) or via the Cloud Console -> Compute Engine -> VM instances -> Set Windows password.

### Chrome Remote Desktop (headless)
Use when you want web-based remote access:
1. RDP into the VM (once) and open Chrome.
2. Visit: https://remotedesktop.google.com/headless and follow prompts.
3. Copy the generated PowerShell command and run it as Administrator.
4. Set a PIN and access via https://remotedesktop.google.com/access

---

## Linux VMs 🐧

### gcloud SSH (recommended)
- Install Google Cloud SDK on your machine and authenticate:

```bash
gcloud auth login
gcloud config set project PROJECT_ID
gcloud config set compute/zone ZONE
```

- Connect:

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE
```

This handles SSH key creation and metadata automatically.

### IAP tunneling (no external IP)
- Useful for secure access when instances are internal-only.

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE --tunnel-through-iap
```

Ensure the IAP API is enabled and your account has the required IAM roles (IAP-secured Tunnel User, Compute Instance Admin / custom as needed).

### Manual SSH keys (optional)
- Generate a key and add it to instance metadata or project metadata:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/my_gcp_key -C "your_email@example.com"
cat ~/.ssh/my_gcp_key.pub
# Add key to instance metadata:
gcloud compute instances add-metadata INSTANCE_NAME \
  --metadata ssh-keys="USERNAME:$(cat ~/.ssh/my_gcp_key.pub)" --zone ZONE
ssh -i ~/.ssh/my_gcp_key USERNAME@EXTERNAL_IP
```

If **OS Login** is enabled, use `gcloud compute os-login ssh-keys add --key-file=~/.ssh/my_gcp_key.pub` instead (and ensure correct IAM roles).

---

## Firewall and OS Login ⚙️
- Allow port 22 for SSH (if you use external IPs):

```bash
gcloud compute firewall-rules create allow-ssh --allow tcp:22 --direction=INGRESS --network default --target-tags ssh || true
```

- If OS Login is used, grant `roles/compute.osLogin` (or `roles/compute.osAdminLogin` for sudo) and add SSH keys via OS Login.

---

## Emergency access: serial console 🚨
When networking or SSH fails, the serial console can provide a shell for recovery (requires console access enabled in instance settings):

```bash
gcloud compute connect-to-serial-port INSTANCE_NAME --zone ZONE
```

Use this to inspect boot logs, enable networking, or fix SSH configuration.

---

## Troubleshooting & tips 🔍
- Increase SSH verbosity to diagnose connection issues:

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE --ssh-flag="-vvv"
# or
ssh -i ~/.ssh/my_gcp_key -vvv USERNAME@EXTERNAL_IP
```

- If RDP fails: check Windows firewall, RDP service, and Network tags.
- If Chrome Remote Desktop fails: ensure the host agent is installed and the service is running (check Services.msc).
- Check instance metadata for accidental SSH key removal.
- Use the Cloud Console to view serial port output and system logs.

---

## Security notes 🔐
- **Rotate passwords** and avoid storing plaintext credentials in repo files.
- Prefer **gcloud-managed keys** or **OS Login** (centralized key management + IAM).
- Use IAP for internal-only VMs; restrict firewall rules.

---

> Tip: Provide your **Project ID**, **Zone**, **Instance name**, and preferred **username** and I can add an exact command example for your specific VM (e.g. a ready-to-run `gcloud compute ssh` or `gcloud compute reset-windows-password` command).

---

## Appendix: Useful references
- Google Cloud SDK: https://cloud.google.com/sdk/docs
- IAP: https://cloud.google.com/iap
- OS Login: https://cloud.google.com/compute/docs/oslogin
- Chrome Remote Desktop: https://remotedesktop.google.com/


---

## GCP Linux VM — SSH Access 🔧

Follow these steps to SSH into a Google Compute Engine instance from Linux or macOS.

### Prerequisites
- Install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install
- Authenticate and set project/zone:

```bash
gcloud auth login
gcloud config set project PROJECT_ID
gcloud config set compute/zone ZONE
```

### Quick connect (recommended)
Use `gcloud` to SSH; it manages keys automatically:

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE
```

If the instance has no external IP, use IAP tunneling:

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE --tunnel-through-iap
```

(Ensure your account has the necessary IAM permissions for IAP and Compute Engine.)

### Manual SSH key (optional)
If you prefer to manage keys yourself:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/my_gcp_key -C "your_email@example.com"
cat ~/.ssh/my_gcp_key.pub
# Add the public key to instance metadata:
gcloud compute instances add-metadata INSTANCE_NAME \
  --metadata ssh-keys="USERNAME:$(cat ~/.ssh/my_gcp_key.pub)" --zone ZONE
# Or add via Console -> Compute Engine -> Metadata -> SSH Keys
ssh -i ~/.ssh/my_gcp_key USERNAME@EXTERNAL_IP
```

### Troubleshooting 🔍
- Firewall: allow port 22 (if needed):

```bash
gcloud compute firewall-rules create allow-ssh --allow tcp:22 --direction=INGRESS --network default --target-tags ssh || true
```

- If **OS Login** is enabled: assign the `roles/compute.osLogin` (or `roles/compute.osAdminLogin` for sudo) role to your account and add your SSH key with:

```bash
gcloud compute os-login ssh-keys add --key-file=~/.ssh/my_gcp_key.pub
```

- Increase SSH verbosity to diagnose issues:

```bash
gcloud compute ssh USERNAME@INSTANCE_NAME --zone ZONE --ssh-flag="-vvv"
# or
ssh -i ~/.ssh/my_gcp_key -vvv USERNAME@EXTERNAL_IP
```

- When SSH is unavailable, use the serial console for emergency access:

```bash
gcloud compute connect-to-serial-port INSTANCE_NAME --zone ZONE
```

---

> Tip: If you'd like, provide **project ID**, **zone**, and **instance name** and I can add a short, specific example command for your VM.

*Requires one-time setup inside the VM.*

1.  Log in via RDP using the credentials above.
2.  Open **Google Chrome** (installed automatically).
3.  Go to [https://remotedesktop.google.com/headless](https://remotedesktop.google.com/headless).
4.  Follow the prompts to Authorize.
5.  Copy the **PowerShell** command.
6.  Open **PowerShell** (Run as Administrator) in the VM.
7.  Run the command and set a PIN.
