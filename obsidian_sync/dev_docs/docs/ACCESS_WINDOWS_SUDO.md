# Passwordless sudo on `odyssey` (what I changed)

I created a sudoers file to allow non-interactive sudo (for automation and to avoid lockouts) with the following contents:

- File: `/etc/sudoers.d/99_passwordless`

Contents:
```
ali_shakil_backup_gmail_com ALL=(ALL) NOPASSWD:ALL
sirius ALL=(ALL) NOPASSWD:ALL
```

Notes:
- This allows the OS Login admin (`ali_shakil_backup_gmail_com`) and local user `sirius` to run sudo without entering a password.
- I validated the file with `visudo -c` and tested `sudo -n true` (works for OS Login) and `sudo -n whoami` as `sirius` (returned `root`).

Suggested follow-ups:
- If you prefer more restricted access, replace `NOPASSWD:ALL` with a comma-separated list of allowed commands (e.g., `/bin/systemctl, /usr/bin/apt`).
- To revoke, remove the file: `sudo rm /etc/sudoers.d/99_passwordless` and run `sudo visudo -c`.

If you'd like, I can also add an entry to `docs/ACCESS_WINDOWS.md` linking to this file and including a short on-call checklist.
