#!/bin/bash
set -euo pipefail

if [ "$(systemctl is-active greenboot.target)" = "active" ]; then
   echo "Health Check: SUCCESS"
else
   echo "Health Check: FAILURE! Starting rollback..." >&2
   # TODO: verify rpm-ostree status has an older entry to boot back into
   rpm-ostree rollback --reboot
fi
