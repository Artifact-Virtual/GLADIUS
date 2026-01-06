#!/bin/bash
set -eux

# Basic updates and packages for ML worker
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip git curl wget ca-certificates apt-transport-https build-essential

# Create user `sirius` with sudo if not exists
if ! id -u sirius >/dev/null 2>&1; then
  useradd -m -s /bin/bash -G sudo sirius
  echo "sirius ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/sirius
  chmod 0440 /etc/sudoers.d/sirius
fi

# Ensure SSH keys
mkdir -p /home/sirius/.ssh
if [ -f /var/lib/google/ssh/keys ]; then
  cat /var/lib/google/ssh/keys >> /home/sirius/.ssh/authorized_keys || true
fi
chmod 700 /home/sirius/.ssh || true
chmod 600 /home/sirius/.ssh/authorized_keys || true
chown -R sirius:sirius /home/sirius/.ssh || true

# Prepare ML worker folder and venv
sudo -u sirius mkdir -p /home/sirius/ml_worker
sudo -u sirius python3 -m venv /home/sirius/ml_worker/venv || true
/home/sirius/ml_worker/venv/bin/pip install --upgrade pip || true

# Placeholder service unit (user should place code or we will scp it later)
cat > /etc/systemd/system/ml-worker.service <<'EOF'
[Unit]
Description=ML Worker
After=network.target

[Service]
Type=simple
User=sirius
WorkingDirectory=/home/sirius/ml_worker
ExecStart=/home/sirius/ml_worker/venv/bin/python -m ml_worker --config /home/sirius/ml_worker/config.json
Restart=on-failure
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ml-worker.service || true

echo "startup complete"