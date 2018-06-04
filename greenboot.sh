#!/bin/bash
if [ "$(systemctl is-active greenboot.target)" = "active" ]; then
   echo "Greenboot Health Check: SUCCESS" | systemd-cat -p notice
else
   echo "Greenboot Health Check: FAILURE! Rolling back..." | systemd-cat -p emerg
   # TODO: verify rpm-ostree status has more than one entry
   rpm-ostree rollback
   reboot
fi
