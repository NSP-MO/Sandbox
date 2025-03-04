#!/bin/bash

# Update package list
sudo apt-get update && sudo apt upgrade -y

# Install RealVNC Viewer
sudo apt-get install -y realvnc-vnc-viewer

# Enable and start the RealVNC Virtual Network Computing Server (Check for the issues, not tested)
sudo systemctl enable vncserver-x11-serviced
sudo systemctl start vncserver-x11-serviced

