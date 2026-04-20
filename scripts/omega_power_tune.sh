#!/bin/bash
# Applies extreme power tuning limits using ryzenadj for sustained compilation loads

if ! command -v ryzenadj &> /dev/null; then
    echo "ryzenadj not found! Emerge sys-power/ryzenadj first."
    exit 1
fi

echo "Applying Strix Point Power Limits (54W Sustained)..."
# Set Sustained Power Limit to 54W, Fast Limit to 65W, Temp Target to 95C
ryzenadj --stapm-limit=54000 --fast-limit=65000 --slow-limit=54000 --tctl-temp=95

echo "Setting CPU governor to performance..."
for cpufreq in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo "performance" > $cpufreq
done

echo "Tuning Complete."
