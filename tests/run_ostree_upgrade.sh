#!/bin/bash
set -euo pipefail

rpm-ostree upgrade
# In order to activate grub2's Boot Couting feature,
# boot_counter must be set to a number >= 1, and boot_success=0
grub2-editenv - set boot_success=0
# set initial counter (maxCount)
grub2-editenv - set boot_counter=3
reboot
