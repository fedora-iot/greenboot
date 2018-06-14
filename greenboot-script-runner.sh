#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

run_required_scripts () {
  required_greenboot_scripts=`ls /etc/greenboot.d/required/*.sh`
  set +e
  for script in $required_greenboot_scripts; do
    bash $script
    if [ $? -ne 0 ]; then
      echo "FAILURE (return value '$?')" >&2 | systemd-cat -t "greenboot Script: '$script'" -p emerg
      break
    else
      echo "SUCCESS" | systemd-cat -t "greenboot Script: '$script'" -p notice
    fi
  done || exit 1
  set -e
}

run_required_scripts

run_wanted_scripts () {
  wanted_greenboot_scripts=`ls /etc/greenboot.d/wanted/*.sh`
  set +e
  for script in $wanted_greenboot_scripts; do
    bash $script
    if [ $? -ne 0 ]; then
      echo "FAILURE (return value '$?')" >&2 | systemd-cat -t "greenboot Script: '$script'" -p warning
    else
      echo "SUCCESS" | systemd-cat -t "greenboot Script: '$script'" -p notice
    fi
  done
  set -e
}

run_wanted_scripts
