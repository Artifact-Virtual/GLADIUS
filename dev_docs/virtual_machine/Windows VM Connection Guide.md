
## Instance Details
- **Name:** `windows-vm-8gb`
- **Zone:** `europe-west1-b`
- **External IP:** `34.38.5.70`
- **Machine Type:** `e2-standard-2` (2 vCPU, 8 GB RAM)
- **Disk:** 50 GB Standard Persistent Disk
- **OS:** Windows Server 2022 Datacenter

## Quick Connect
**RDP File:** [windows-vm.rdp](file:///c:/workspace/.ssh/windows-vm.rdp)
*(Double-click this file to connect)*

## Credentials
- **Username:** `gladius_user`
- **Password:** `M?j,:Mlr?QaBU#+`

## Web Access (Chrome Remote Desktop)
If configured (see below), access via:
[https://remotedesktop.google.com/access](https://remotedesktop.google.com/access)

---

## Detailed Setup Instructions

### 1. RDP Connection (Manual)
1.  Open **Remote Desktop Connection**.
2.  Computer: `34.38.5.70`
3.  User: `gladius_user`
4.  Password: `M?j,:Mlr?QaBU#+`

### 2. Chrome Remote Desktop Setup
*Requires one-time setup inside the VM.*

1.  Log in via RDP using the credentials above.
2.  Open **Google Chrome** (installed automatically).
3.  Go to [https://remotedesktop.google.com/headless](https://remotedesktop.google.com/headless).
4.  Follow the prompts to Authorize.
5.  Copy the **PowerShell** command.
6.  Open **PowerShell** (Run as Administrator) in the VM.
7.  Run the command and set a PIN.
