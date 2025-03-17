#!/bin/bash

# Update package list
sudo apt-get update && sudo apt upgrade -y

# Install Samba
sudo apt-get install -y samba samba-common-bin

# Create samba directory
sudo mkdir -p /shared

# Configure Samba
# sudo nano /etc/samba/smb.conf

# Backup the original Samba configuration file
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak

# Create a new Samba configuration
cat <<EOL | sudo tee /etc/samba/smb.conf

[shared]
    path=/home/vtol2/shared
    writeable=Yes
    create mask=0777
    directory mask=0777
    public=no

EOL

# Create user for Samba
sudo smbpasswd -a vtol2

# Restart Samba services
sudo systemctl restart smbd
sudo systemctl restart nmbd

echo "Samba installation and configuration complete."