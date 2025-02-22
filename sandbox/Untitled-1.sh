#!/bin/bash

# Install system dependencies
sudo apt-get update && sudo apt upgrade -y
sudo apt-get install -y \
    python3-pip \
    git \
    build-essential \
    python3-dev \
    python3-opencv \
    python3-wxgtk4.0 \
    python3-matplotlib \
    python3-lxml \
    python3-yaml \
    python3-serial \
    screen \
    libtool \
    autoconf \
    automake \
    tcl \
    tk \
    imagemagick \
    libxml2-dev \
    libxslt-dev \
    python3-pygame

# Clone ArduPilot repository
git clone --recursive https://github.com/ArduPilot/ardupilot.git

cd ardupilot

# Build ArduCopter
Tools/environment_install/install-prereqs-ubuntu.sh -y
source ~/.profile

./waf configure --board sitl
./waf copter
./waf 
./waf clean

sim_vehicle.py -v ArduCopter --map --console

sim_vehicle.py -v ArduCopter -f quad --map --console

# # Packages
# pip install dronekit pymavlink numpy

# pip install pipenv

# python -m pipenv install dronekit pymavlink numpy

# python -m pipenv graph

# python -m pipenv check

# python -m pipenv run python3 - <<END
# # Python code, for example:
# from dronekit import connect, VehicleMode, LocationGlobalRelative
# # ... (rest of the Python code)
# END






# # Clone ArduPilot repository
# if [ ! -d "ardupilot" ]; then
#     git clone https://github.com/ArduPilot/ardupilot.git
#     cd ardupilot
#     git submodule update --init --recursive
#     cd ..
# fi

# # Build ArduCopter SITL
# cd ardupilot
# ./waf configure --board sitl
# ./waf copter

# # Start SITL with parameters in the background
# cd ArduCopter
# sim_vehicle.py -v ArduCopter -f quad --console --map --out=tcp:127.0.0.1:5762 --cmd="param set WP_YAW_BEHAVIOR 0; param fetch" &

# # Wait for SITL to initialize
# echo "Waiting for SITL to initialize..."
# sleep 15

# # Return to original directory and run the mission script
# cd ../../..
# python3 - <<END
# # Paste your Python code here
# from dronekit import connect, VehicleMode, LocationGlobalRelative
# # ... (rest of your Python code)
# END

# # Keep the script running
# wait
# '''