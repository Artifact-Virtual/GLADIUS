#!/bin/bash
set -eux

# Basic updates and packages
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip git curl wget ca-certificates apt-transport-https \
  wine64 wine32 build-essential libfontconfig1 libfreetype6

# Create user `sirius` with sudo if not exists
if ! id -u sirius >/dev/null 2>&1; then
  useradd -m -s /bin/bash -G sudo sirius
  echo "sirius ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/sirius
  chmod 0440 /etc/sudoers.d/sirius
fi

# Ensure SSH keys (project metadata) are available to the user
mkdir -p /home/sirius/.ssh
if [ -f /var/lib/google/ssh/keys ]; then
  cat /var/lib/google/ssh/keys >> /home/sirius/.ssh/authorized_keys || true
fi
chmod 700 /home/sirius/.ssh || true
chmod 600 /home/sirius/.ssh/authorized_keys || true
chown -R sirius:sirius /home/sirius/.ssh || true

# Prepare a placeholder for the repo and venv
sudo -u sirius mkdir -p /home/sirius/herald
sudo -u sirius python3 -m venv /home/sirius/herald/venv || true
/home/sirius/herald/venv/bin/pip install --upgrade pip || true

# Systemd unit to run Herald (will be a no-op until repo is placed and config provided)
cat > /etc/systemd/system/herald.service <<'EOF'
[Unit]
Description=Herald trading service
After=network.target

[Service]
Type=simple
User=sirius
WorkingDirectory=/home/sirius/herald
ExecStart=/home/sirius/herald/venv/bin/python -m herald --config /home/sirius/herald/config.json --enable-rpc --rpc-host=127.0.0.1
Restart=on-failure
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable herald.service || true

# Download MT5 installer to /home/sirius/Downloads for manual Wine install later
sudo -u sirius mkdir -p /home/sirius/Downloads
sudo -u sirius wget -O /home/sirius/Downloads/mt5setup.exe "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe" || true
chown -R sirius:sirius /home/sirius

# Mark script complete
echo "startup complete"