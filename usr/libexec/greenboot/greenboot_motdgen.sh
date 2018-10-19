#!/bin/bash
set -euo pipefail

if [ ! -d /etc/motd.d ]; then
    mkdir /etc/motd.d
fi

if [ "$(systemctl is-active greenboot.target)" = "active" ]; then
    greenboot_logs=$(journalctl -u greenboot.service -p 0..5 -b -0 -o cat)
    printf '%s\n' "$greenboot_logs" > /etc/greenboot/motd
else
    redboot_logs=$(journalctl -u redboot.service -p 0..5 -b -0 -o cat)
    printf '%s\n' "$redboot_logs" > /etc/greenboot/motd
    current_healthcheck_logs=$(journalctl -u greenboot-healthcheck.service -p 0..2 -b 0 -o cat)
    printf '%\n' "$current_healthcheck_logs" >> /etc/greenboot/motd
fi

if grub2-editenv list | grep -q "^boot_counter=-1$"; then
    prev_healthcheck_logs=$(journalctl -u greenboot-healthcheck.service -p 0..2 -b -1 -o cat)
    printf 'The current boot seems to be a fallback boot. Showing health check logs from previous boot:\n%s\n' "$prev_healthcheck_logs" >> /etc/greenboot/motd
fi

# remove the following line and write above directly to /run/motd.d/greenboot
# once https://github.com/linux-pam/linux-pam/pull/69 is merged
ln -snf /etc/greenboot/motd /etc/motd.d/greenboot
