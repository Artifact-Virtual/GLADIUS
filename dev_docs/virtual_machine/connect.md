# Windows VM Connection Guide

## Instance Details
- **Name:** `windows-vm-8gb`
- **Zone:** `europe-west1-b`
- **External IP:** `34.38.5.70`
- **Machine Type:** `e2-standard-2` (2 vCPU, 8 GB RAM)
- **Disk:** 50 GB Standard Persistent Disk
- **OS:** Windows Server 2022 Datacenter

## Connection Steps

### 1. Generate Windows Password
You needs a username and password to log in via RDP. Run this command in your local terminal:

```powershell
gcloud compute reset-windows-password windows-vm-8gb `
    --zone=europe-west1-b `
    --user=[YOUR_USERNAME]
```
*Replace `[YOUR_USERNAME]` with your desired username (e.g., `admin`).*
*Save the password outputted by this command!*

### 2. Connect via RDP (Remote Desktop Protocol)
1.  Open **Remote Desktop Connection** on your local computer.
2.  Enter the computer: `34.38.5.70`
3.  Click **Connect**.
4.  Enter the `[YOUR_USERNAME]` and the **Password** generated in Step 1.
5.  Accept the certificate warning if prompted.

### 3. Configure Chrome Remote Desktop (Optional)
Chrome and Chrome Remote Desktop were installed automatically via startup script. To enable remote access via Google:

1.  Log in to the VM via RDP (Step 2).
2.  Open **Google Chrome** inside the VM.
3.  Navigate to [https://remotedesktop.google.com/headless](https://remotedesktop.google.com/headless).
4.  Click **Begin**, then **Next**, then **Authorize**.
5.  Copy the **PowerShell** command provided by Google.
6.  Open **PowerShell** inside the VM (search for "PowerShell" -> Right Click -> Run as Administrator).
7.  Paste the command and run it.
8.  Set a PIN when prompted.

You can now access the VM from [https://remotedesktop.google.com/access](https://remotedesktop.google.com/access) without needing the RDP client or dynamic IP.
