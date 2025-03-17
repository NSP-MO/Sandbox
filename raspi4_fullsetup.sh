#!/bin/bash

# Update package list and upgrade system
sudo apt-get update && sudo apt upgrade -y

# Install and configure RealVNC
sudo apt-get install -y realvnc-vnc-viewer
sudo systemctl enable vncserver-x11-serviced
sudo systemctl start vncserver-x11-serviced

# Install and configure Samba
sudo apt-get install -y samba samba-common-bin
sudo mkdir -p /shared  # Original script creates /shared (potential conflict)

# Backup original Samba config and create new configuration
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
cat <<EOL | sudo tee /etc/samba/smb.conf
[shared]
    path=/home/vtol2/shared
    writeable=Yes
    create mask=0777
    directory mask=0777
    public=no
EOL

# Create Samba user (ensure 'vtol2' system user exists first)
sudo smbpasswd -a vtol2

# Restart Samba services
sudo systemctl restart smbd
sudo systemctl restart nmbd

echo "VNC and Samba configuration completed."