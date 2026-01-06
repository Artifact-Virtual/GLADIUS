# VM Access Setup Guide: SSH Key-Based Access with Auto-Login Desktop

This guide provides a comprehensive, step-by-step manual for setting up and maintaining secure, persistent access to the Google Cloud Platform (GCP) Virtual Machine (VM) named "odyssey" using SSH key-based authentication with automatic desktop login. It covers the current configuration, setup, troubleshooting, and maintenance to ensure reliable access without recurring issues. The VM is configured for passwordless SSH login directly to the desktop environment.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Current VM Status](#current-vm-status)
3. [GCP VM Creation (Already Done)](#gcp-vm-creation-already-done)
4. [SSH Key Setup and Passwordless Access](#ssh-key-setup-and-passwordless-access)
5. [Desktop Environment and Auto-Login Configuration](#desktop-environment-and-auto-login-configuration)
6. [Firewall and Security](#firewall-and-security)
7. [Connecting to the VM](#connecting-to-the-vm)
8. [Reboot Testing and Persistence](#reboot-testing-and-persistence)
9. [Herald Environment Setup](#herald-environment-setup)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance and Best Practices](#maintenance-and-best-practices)

## Prerequisites

### 1. Google Cloud Platform (GCP) Account
- **Account**: `ali.shakil.backup@gmail.com`.
- **Project**: `artifact-virtual` (project ID: `artifact-virtual`).
- **Permissions**: Ensure the account has Editor or Owner role on the project, plus `roles/iap.tunnelResourceAccessor` for secure tunneling if needed.

### 2. Local Machine Setup
- **Operating System**: Windows 10/11.
- **Google Cloud SDK (gcloud)**:
  - Installed and authenticated with `ali.shakil.backup@gmail.com`.
  - Project set to `artifact-virtual`, zone to `europe-west1-b`.
- **SSH Keys**:
  - Keys are stored in `C:\Users\alish\.ssh\google_compute_engine` and `google_compute_engine.pub`.
  - Public key added to GCP project metadata for user `ali_shakil_backup_gmail_com`.

### 3. Network Requirements
- **Internet Connection**: Stable broadband.
- **Firewall/Antivirus**: Ensure local firewall allows outbound SSH (port 22).

## Current VM Status

- **VM Name**: odyssey
- **Zone**: europe-west1-b
- **External IP**: 35.195.25.106 (updated as of December 23, 2025)
- **OS**: Ubuntu 22.04 LTS
- **CPU/RAM**: 4 vCPUs, 16GB RAM
- **Disk**: 100GB SSD
- **User**: ali_shakil_backup_gmail_com
- **Access**: SSH key-only (password authentication disabled), auto-login to XFCE desktop.
- **Services**: LightDM for display manager, XFCE desktop environment, VS Code CLI installed.
- **Status**: Running (start if needed: `gcloud compute instances start odyssey --zone=europe-west1-b --project=artifact-virtual`)

## GCP VM Creation (Already Done)

The VM "odyssey" was created with:
- Command: `gcloud compute instances create odyssey --machine-type=e2-standard-4 --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --boot-disk-size=100GB --boot-disk-type=pd-standard --zone=europe-west1-b`
- If recreating, ensure to reapply SSH keys and configurations.

## SSH Key Setup and Passwordless Access

1. **Add SSH Key to Project Metadata**:
   - Retrieve public key: `type C:\Users\alish\.ssh\google_compute_engine.pub`
   - Add to GCP: `gcloud compute project-info add-metadata --metadata ssh-keys="ali_shakil_backup_gmail_com:<public_key>" --project=artifact-virtual`
   - Reset VM to apply: `gcloud compute instances reset odyssey --zone=europe-west1-b --project=artifact-virtual`

2. **Disable Password Authentication**:
   - SSH into VM: `ssh -o StrictHostKeyChecking=no -i C:\Users\alish\.ssh\google_compute_engine ali_shakil_backup_gmail_com@35.195.25.106`
   - Run: `echo "PasswordAuthentication no" | sudo tee /etc/ssh/sshd_config.d/99-gce-hardening.conf && sudo systemctl restart sshd`

3. **Disable User Password**:
   - `sudo passwd -d ali_shakil_backup_gmail_com`

## Desktop Environment and Auto-Login Configuration

1. **Install XFCE and LightDM**:
   - `sudo apt update && sudo apt install -y lightdm xfce4 xfce4-goodies`

2. **Configure Auto-Login**:
   - `sudo sh -c 'echo -e "\n[Seat:*]\nautologin-user=ali_shakil_backup_gmail_com\nautologin-user-timeout=0" >> /etc/lightdm/lightdm.conf'`
   - Reboot to apply: `sudo reboot`

## Firewall and Security

- **GCP Firewall**: Default SSH allowed. Additional rules exist (e.g., VNC if set up).
- **Security**: SSH key-only, no passwords. Auto-login enabled for convenience (monitor for security implications).

## VS Code Server Installation

VS Code Server provides a web-based VS Code interface for seamless editing, building, and managing code on the VM.

1. **Firewall Rule**:
   - *Skipped for security*. We will use SSH Tunneling instead of exposing port 8080 to the public internet. If the rule exists, consider deleting it: `gcloud compute firewall-rules delete allow-code-server --project=artifact-virtual`

2. **Install VS Code Server**:
   - SSH into VM: `ssh -i C:\Users\alish\.ssh\google_compute_engine ali_shakil_backup_gmail_com@35.195.25.106`
   - Run: `curl -fsSL https://code-server.dev/install.sh | sh`

3. **Configure VS Code Server**:
   - Edit config: `sudo nano ~/.config/code-server/config.yaml`
   - Add:
     ```
     bind-addr: 127.0.0.1:8080
     auth: password
     password: your_secure_password_here
     cert: false
     ```
   - Save and exit.

4. **Run as Service**:
   - Create service: `sudo nano /etc/systemd/system/code-server.service`
   - Add:
     ```
     [Unit]
     Description=VS Code Server
     After=network.target

     [Service]
     Type=simple
     User=ali_shakil_backup_gmail_com
     ExecStart=/usr/bin/code-server --bind-addr 127.0.0.1:8080
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Enable: `sudo systemctl enable code-server`
   - Start: `sudo systemctl start code-server`

5. **Access VS Code Server**:
   - Establish Tunnel: `ssh -L 8080:127.0.0.1:8080 -i C:\Users\alish\.ssh\google_compute_engine ali_shakil_backup_gmail_com@35.195.25.106`
   - Open browser: `http://localhost:8080`
   - Login with the password set.

6. **Persistence**:
   - Service starts on boot. Config in `~/.config/code-server/config.yaml`.

## Connecting to the VM

For convenience, a PowerShell script is provided to establish all necessary tunnels (VNC and VS Code) and open an SSH shell in one step.

1. **Script Location**: `c:\workspace\_dev\virtual_machine\connect_vm.ps1`
2. **Usage**:
   - Open PowerShell.
   - Run: `.\connect_vm.ps1`
   - This will open tunnels for VNC (5901) and VS Code (8080) in the background and drop you into the VM shell.

## Reboot Testing and Persistence

- **Reboot**: `sudo reboot` or `gcloud compute instances reset odyssey --zone=europe-west1-b --project=artifact-virtual`
- **Post-Reboot**: SSH should auto-login to desktop. Configurations are persistent via systemd and config files.

## Herald Environment Setup

- **Repo Path**: `/home/ali_shakil_backup_gmail_com/herald`
- **Venv**: `/home/ali_shakil_backup_gmail_com/herald/venv` (Python 3.10)
- **Activate**: `source /home/ali_shakil_backup_gmail_com/herald/venv/bin/activate`
- **Install**: `pip install -r requirements.txt && pip install -e . --no-deps`
- **Notes**: MetaTrader5 is Windows-only; use Wine for full integration if needed.

## TigerVNC Remote Desktop Setup

1. **Install TigerVNC**:
   - SSH into VM: `ssh -i C:\Users\alish\.ssh\google_compute_engine ali_shakil_backup_gmail_com@35.195.25.106`
   - Run: `sudo apt install -y tigervnc-standalone-server tigervnc-common`

2. **Configure Startup**:
   - Run: `vncpasswd` to set a VNC access password.
   - Create/Edit startup script: `nano ~/.vnc/xstartup`
     ```bash
     #!/bin/sh
     unset SESSION_MANAGER
     unset DBUS_SESSION_BUS_ADDRESS
     exec startxfce4
     ```
   - Make executable: `chmod +x ~/.vnc/xstartup`

3. **Start VNC Server**:
   - Run: `vncserver -localhost yes :1`
   - **Address**: `localhost:5901` (Access via SSH Tunnel)
   - **Tunnel Command**: `ssh -L 5901:127.0.0.1:5901 -N -i C:\Users\alish\.ssh\google_compute_engine ali_shakil_backup_gmail_com@35.195.25.106`

## Troubleshooting

### SSH Issues
- **Connection Fails**: Check VM status and IP. Ensure key is in project metadata.
- **Permission Denied**: Verify key file path and user.

### Desktop Issues
- **No Auto-Login**: Check `/etc/lightdm/lightdm.conf` for autologin settings.
- **Display Manager Fails**: `sudo systemctl status lightdm`

### General
- **VM Not Responding**: Reset or start VM.
- **Logs**: Check `/var/log/auth.log`, `/var/log/lightdm/lightdm.log`

## Maintenance and Best Practices

- **Backups**: Snapshot disk regularly.
- **Updates**: `sudo apt update && sudo apt upgrade`
- **Security**: Monitor access logs. Consider disabling auto-login if security is a concern.
- **Documentation**: This guide is the source of truth; update as changes are made.

By following this guide, you can quickly restore or replicate the current VM setup.