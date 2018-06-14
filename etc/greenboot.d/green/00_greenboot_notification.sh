#!/bin/bash
set -euo pipefail

echo "SUCCESS! Boot status is GREEN" | systemd-cat -t "greenboot" -p notice

exit 0
