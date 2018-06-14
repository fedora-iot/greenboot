#!/bin/bash
set -euo pipefail

echo "FAILURE! Boot status is RED" | systemd-cat -t "greenboot" -p emerg

exit 0
