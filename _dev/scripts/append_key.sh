#!/bin/bash
mkdir -p /home/devops/.ssh
cat /tmp/key.txt >> /home/devops/.ssh/authorized_keys
chown devops:devops /home/devops/.ssh /home/devops/.ssh/authorized_keys
chmod 700 /home/devops/.ssh
chmod 600 /home/devops/.ssh/authorized_keys
sed -n '1,240p' /home/devops/.ssh/authorized_keys
