#!/bin/bash

# Update package list
sudo apt-get update && sudo apt upgrade -y

# Install Samba
sudo apt-get install -y samba samba-common-bin

# Create samba directory
sudo mkdir -p /shared

# Configure Samba
sudo nano /etc/samba/smb.conf

# Backup the original Samba configuration file
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

# Create a new Samba configuration
cat <<EOL | sudo tee /etc/samba/smb.conf
[global]
    workgroup = WORKGROUP
    server string = Samba Server %v
    netbios name = ubuntu
    security = user
    map to guest = bad user
    dns proxy = no

[Public]
    path = /samba/public
    browsable = yes
    writable = yes
    guest ok = yes
    read only = no
EOL

# Create the directory for the public share
sudo mkdir -p /samba/public
sudo chown -R nobody:nogroup /samba/public
sudo chmod -R 0775 /samba/public

# Restart Samba services
sudo systemctl restart smbd
sudo systemctl restart nmbd

echo "Samba installation and configuration complete."