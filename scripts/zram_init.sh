#!/bin/bash
# Initializes 10GB of ZRam at Priority 100 to sustain 24-thread compilation

# Ensure module is loaded
modprobe zram

# Configure 10GB size
zramctl --find --size 10G

# Activate with high priority
swapon /dev/zram0 -p 100

echo "ZRam initialized: 10GB at Priority 100."
