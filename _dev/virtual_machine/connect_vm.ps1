$VM_IP = "35.195.25.106"
$SSH_USER = "ali_shakil_backup_gmail_com"
$SSH_KEY = "C:\Users\alish\.ssh\google_compute_engine"

Write-Host "Establishing SSH Tunnels..."
# Start VNC Tunnel (Port 5901)
Start-Process ssh -ArgumentList "-L 5901:127.0.0.1:5901 -N -i $SSH_KEY $SSH_USER@$VM_IP" -WindowStyle Hidden

# Start VS Code Server Tunnel (Port 8080)
Start-Process ssh -ArgumentList "-L 8080:127.0.0.1:8080 -N -i $SSH_KEY $SSH_USER@$VM_IP" -WindowStyle Hidden

Write-Host "Tunnels active. VNC: localhost:5901, Code: localhost:8080"
Write-Host "Connecting to shell..."

# Connect interactively
ssh -i $SSH_KEY $SSH_USER@$VM_IP