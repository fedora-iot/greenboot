#!/bin/bash
set -euo pipefail

# Determine if the current boot is a fallback boot
if grub2-editenv list | grep -q "^boot_counter=-1$"; then
  # If booted into fallback deployment, clean up bootloader entries (rollback)
  rpm-ostree rollback
fi
