#!/bin/bash
set -eux
# create dragonfly user and install provided public key
useradd -m -s /bin/bash dragonfly || true
mkdir -p /home/dragonfly/.ssh
cat > /home/dragonfly/.ssh/authorized_keys <<'PUB'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3Cs4pI78Il/56kbLpK8oeMFiVtyrX/tYH89QBZjoJXWwJxNEUUztS7SKPpd5iEmT+EiA69+js7h7uCH0iHa2u7tvuJRbYNyNYp3UBtESo1enarj4Yy7ZyCBR9h4Ka1+4aBQPjfmfSTBKzTXueFKgwAy/w74y6y7Ed7oFuOs+N35UDZww1pCra6r/PthTAAKxbZmC4H+MbbszOd2o2MuKT6rxZKvd1dOof+tzvIriLEsCXBSZ62jcqkO1Dyvzyu9gxhvXlpI90hNjhIOsY6jj5g8Em477deDT6P3xN01Vb/8V8P3/pBEXKWdjMnYNR+JNpWQCSLXRN/WGLLvMWyjgP DESKTOP-PC8B32Q\alish@DESKTOP-PC8B32Q

PUB
chown -R dragonfly:dragonfly /home/dragonfly/.ssh
chmod 700 /home/dragonfly/.ssh
chmod 600 /home/dragonfly/.ssh/authorized_keys
echo 'dragonfly ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/dragonfly
chmod 440 /etc/sudoers.d/dragonfly

# set ali_shakil_backup_gmail_com password
echo 'ali_shakil_backup_gmail_com:sirius' | chpasswd || true

# remove passwords for other non-system users (UID>=1000) except ali and dragonfly
awk -F: '>=1000 {print }' /etc/passwd | grep -v -E '^(ali_shakil_backup_gmail_com|dragonfly)$' | while read u; do
  passwd -d "" || true
done

# configure TigerVNC for ali_shakil_backup_gmail_com on :1 with no VNC password
pkill Xtigervnc || true
su - ali_shakil_backup_gmail_com -c 'vncserver -kill :1' || true

cat > /etc/systemd/system/tigervnc@.service <<'SERVICE'
[Unit]
Description=TigerVNC Server for %i
After=network.target

[Service]
Type=forking
User=%i
PAMName=login
PIDFile=/home/%i/.vnc/%H:%i.pid
ExecStartPre=-/usr/bin/vncserver -kill :%i
ExecStart=/usr/bin/vncserver :%i -geometry 1280x800 -SecurityTypes None
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable tigervnc@ali_shakil_backup_gmail_com.service || true
systemctl start tigervnc@ali_shakil_backup_gmail_com.service || true

# Done
