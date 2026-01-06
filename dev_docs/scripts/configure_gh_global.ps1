param(
    [switch]$SetEnvVariable
)

# Configure Git and GH globally for this user.
# - Ensures gh auth this is available (use gh auth login --with-token to store securely)
# - Sets Git credential helper to manager-core (recommended on Windows)
# - Optionally sets GITHUB_PAT as a user environment variable (less secure)

Write-Host "Configuring global Git/GitHub settings..."

# Set Git credential helper to manager-core
git config --global credential.helper manager-core
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to set git credential.helper manager-core. Ensure Git is installed."
} else {
    Write-Host "git credential.helper set to manager-core"
}

# Confirm gh is authenticated
Write-Host "Checking gh auth status..."
gh auth status --show-token

# Optionally set the GITHUB_PAT as a persistent user environment variable
if ($SetEnvVariable) {
    Write-Host "Setting GITHUB_PAT as a user environment variable (will persist across sessions)."
    if (-not (Test-Path -Path ./gold_standard/secrets.env)) {
        Write-Host "No local secrets.env found. Prompting for PAT (input hidden)."
        $secureToken = Read-Host -AsSecureString "Enter PAT"
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
        try { $token = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) } finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
    } else {
        $token = (Get-Content ./gold_standard/secrets.env | Select-String 'GITHUB_PAT' | ForEach-Object { $_.ToString().Split('=',2)[1].Trim().Trim('"') })
        Write-Host "Using token from ./gold_standard/secrets.env"
    }
    if ($token) {
        setx GITHUB_PAT $token | Out-Null
        Write-Host "GITHUB_PAT set for user (requires new shell session)."
    } else {
        Write-Error "No token provided; skipping setx."
    }
}

# Try docker login if docker is present
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    Write-Host "Docker found; attempting ghcr login using current token in gh auth or environment."
    $pat = $null
    try {
        $pat = gh auth status --show-token | Select-String -Pattern 'Token: ' | ForEach-Object { $_.ToString().Split(':',2)[1].Trim() }
    } catch {
        Write-Host "Could not extract token from gh; will look for GITHUB_PAT environment variable."
    }
    if (-not $pat -and $env:GITHUB_PAT) { $pat = $env:GITHUB_PAT }
    if ($pat) {
        $pat | docker login ghcr.io -u (gh api user --jq '.login') --password-stdin
        if ($LASTEXITCODE -ne 0) { Write-Error "docker login failed. Ensure PAT has write:packages scope." } else { Write-Host "Docker login succeeded." }
    } else {
        Write-Host "No PAT available to login to GHCR. Set GITHUB_PAT or run 'gh auth login --with-token'."
    }
} else {
    Write-Host "Docker not found; skip GHCR login. Run this script on the VM where Docker is installed to finish GHCR setup."
}

Write-Host "Done. Verify with 'gh auth status --show-token' and 'git config --global --list'."