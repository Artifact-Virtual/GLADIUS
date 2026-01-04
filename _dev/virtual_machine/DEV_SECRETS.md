DEV_SECRETS (developer-only)

WARNING: This file contains secrets for development/testing only. Do NOT commit or expose this file in public repositories.

# Known safe entries (public keys and VNC password)

VNC_USER: ali_shakil_backup
VNC_PASSWORD: 2eMFeJZwDqWW9Yjk
VNC_DISPLAY: :1
VNC_PORT: 5901
SSH_USER: ali_shakil_backup
SSH_PORT: 22
SERVER_PUBLIC_IP: 34.155.169.168

# Public keys present on the server (authorized_keys)
# (these are public keys, safe to store in a dev doc)
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJxppVG+lyu7JZMoERJ2LjISHZL+GNF5peXqdTE9TDcv ali.shakil.backup@gmail.com
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDXpFBAR9FvAO85g3FsAKLiqR3wsOvazrtX7yDdHyiji ali_shakil_backup@odyssey

# Notes
- Private keys should NOT be stored here. Keep private keys on the client devices and in secure vaults.
- If you want me to redact or rotate secrets, tell me and I will provide a rotation script.
