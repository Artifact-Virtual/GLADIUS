<#
setup_odyssey_ssh.ps1
Interactive script to generate an SSH key, upload the public key to a GCE VM,
create a new user, install the public key, set permissions, and add sudo access.

Run:
powershell -ExecutionPolicy Bypass -File .\setup_odyssey_ssh.ps1
#>

param(
  [string]$Project = "",
  [string]$Zone = "",
  [string]$Instance = "odyssey",
  [string]$NewUser = "odysseyai",
  [string]$KeyPath = "$env:USERPROFILE\.ssh\odyssey_ai_key",
  [switch]$UseIap,
  [string]$ExternalIP = ""
)

function Read-IfEmpty {
  param($val, $prompt)
  if (-not $val) {
    $v = Read-Host $prompt
    return $v
  }
  return $val
}

$Project = Read-IfEmpty $Project "GCP Project ID (enter if not set)"
$Zone    = Read-IfEmpty $Zone "GCE Zone (e.g. us-central1-a)"
$Instance = Read-IfEmpty $Instance "Instance name (default 'odyssey')"
$NewUser = Read-IfEmpty $NewUser "New local username to create on VM (default 'odysseyai')"

Write-Host "Key will be at: $KeyPath (private) and $KeyPath.pub (public)"

if (-not (Test-Path -Path (Split-Path $KeyPath))) {
  New-Item -ItemType Directory -Path (Split-Path $KeyPath) -Force | Out-Null
}

if (-not (Test-Path $KeyPath)) {
  ssh-keygen -t ed25519 -f $KeyPath -N "" -C "${NewUser}_gce_key" | Out-Null
  Write-Host "Key generated."
} else {
  Write-Host "Key already exists; using existing key at $KeyPath"
}

$LocalPub = "${KeyPath}.pub"
if (-not (Test-Path $LocalPub)) {
  Write-Error "Public key not found at $LocalPub"
  exit 1
}

# Confirm before making changes
Write-Host ""
Write-Host "Summary:"
Write-Host "Project: $Project"
Write-Host "Zone: $Zone"
Write-Host "Instance: $Instance"
Write-Host "New user: $NewUser"
if ($UseIap) { Write-Host "Using IAP tunnel: yes" }
if ($ExternalIP) { Write-Host "External IP (for direct ssh tests): $ExternalIP" }
$ok = Read-Host "Proceed with uploading key and creating user? (y/N)"
if ($ok -ne 'y' -and $ok -ne 'Y') { Write-Host "Aborted."; exit 0 }

# Prepare remote tmp path
$RemoteTmp = "/tmp/${NewUser}_gce_key.pub"

# gcloud scp the pubkey to the instance (uses IAP if requested)
$scpArgs = @("compute","scp",$LocalPub,"$($Instance):$RemoteTmp","--zone=$Zone","--project=$Project")
if ($UseIap) { $scpArgs += "--tunnel-through-iap" }

Write-Host "Uploading public key to instance..."
gcloud @scpArgs
if ($LASTEXITCODE -ne 0) {
  Write-Error "gcloud scp failed. Ensure gcloud is authenticated and instance is reachable."
  exit 1
}

# Build remote command to create user and set up authorized_keys
$remoteCmd = @"
sudo useradd -m -s /bin/bash $($NewUser) || true;
sudo mkdir -p /home/$($NewUser)/.ssh;
sudo cat $RemoteTmp | sudo tee -a /home/$($NewUser)/.ssh/authorized_keys;
sudo chown -R $($NewUser):$($NewUser) /home/$($NewUser)/.ssh;
sudo chmod 700 /home/$($NewUser)/.ssh;
sudo chmod 600 /home/$($NewUser)/.ssh/authorized_keys;
echo '$($NewUser) ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/$($NewUser);
sudo chmod 440 /etc/sudoers.d/$($NewUser);
sudo rm -f $RemoteTmp
"@

# Execute remote command via gcloud compute ssh
$sshArgs = @("compute","ssh","$($Instance)","--zone=$Zone","--project=$Project","--command",$remoteCmd)
if ($UseIap) { $sshArgs += "--tunnel-through-iap" }

Write-Host "Creating user and installing public key on the VM..."
gcloud @sshArgs
if ($LASTEXITCODE -ne 0) {
  Write-Error "gcloud compute ssh failed to run remote setup. Check instance status and permissions."
  exit 1
}

Write-Host "Remote setup completed."

# Provide test commands
Write-Host ""
Write-Host "To test now:"
if ($ExternalIP) {
  Write-Host "Direct SSH test (from this machine):"
  Write-Host "ssh -i `"$KeyPath`" $NewUser@$ExternalIP"
} else {
  $gcloudTest = "gcloud compute ssh $Instance --zone=$Zone --project=$Project --ssh-key-file=$KeyPath"
  if ($UseIap) { $gcloudTest += " --tunnel-through-iap" }
  Write-Host "Use gcloud to SSH (recommended):"
  Write-Host $gcloudTest
}

Write-Host ""
Write-Host "If you want, run the test now. When you're connected, validate sudo access:"
Write-Host "sudo -l"