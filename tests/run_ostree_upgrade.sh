#!/bin/bash
set -euo pipefail

rpm-ostree upgrade
grub2-editenv - set boot_success=0
grub2-editenv - set boot_counter=3
reboot
