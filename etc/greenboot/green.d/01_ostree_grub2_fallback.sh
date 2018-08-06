#!/bin/bash
set -euo pipefail

# We need to determine whether this boot was a fallback boot
if grub2-editenv list | grep -q "^boot_counter=-1$"; then
  rpm-ostree rollback
fi
