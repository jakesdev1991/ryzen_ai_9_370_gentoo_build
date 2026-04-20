#!/bin/bash
# Automates environment update and configuration merging after build completion

echo "Running env-update..."
env-update

echo "Sourcing profile..."
source /etc/profile

echo "Post-build synchronization complete. Run 'etc-update' to manually review configuration changes."
