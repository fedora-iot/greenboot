#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

run_required_scripts () {
  local required_scripts=`ls /etc/greenboot.d/check/required/*.sh`
  set +e
  for script in $required_scripts; do
    bash $script
    if [ $? -ne 0 ]; then
      echo "FAILURE (exit code '$?')" | systemd-cat -t "greenboot Check Script: '$script'" -p emerg
      break
    else
      echo "SUCCESS" | systemd-cat -t "greenboot Check Script: '$script'" -p notice
    fi
  done || exit 1
  set -e
}

run_wanted_scripts () {
  local wanted_scripts=`ls /etc/greenboot.d/check/wanted/*.sh`
  set +e
  for script in $wanted_scripts; do
    bash $script
    if [ $? -ne 0 ]; then
      echo "FAILURE (exit code '$?')" | systemd-cat -t "greenboot Check Script: '$script'" -p warning
    else
      echo "SUCCESS" | systemd-cat -t "greenboot Check Script: '$script'" -p notice
    fi
  done
  set -e
}

run_green_scripts () {
  local green_scripts=`ls /etc/greenboot.d/green/*.sh`
  set +e
  for script in $green_scripts; do
    bash $script
    if [ $? -ne 0 ]; then
      echo "FAILURE (exit code '$?')" | systemd-cat -t "greenboot Success Script: '$script'" -p warning
    else
      echo "SUCCESS" | systemd-cat -t "greenboot Success Script: '$script'" -p notice
    fi
  done
  set -e
}

run_red_scripts () {
  local red_scripts=`ls /etc/greenboot.d/red/*.sh`
  set +e
  for script in $red_scripts; do
    bash $script
    if [ $? -ne 0 ]; then
      echo "FAILURE (exit code '$?')" | systemd-cat -t "greenboot Failure Script: '$script'" -p warning
    else
      echo "SUCCESS" | systemd-cat -t "greenboot Failure Script: '$script'" -p notice
    fi
  done
  set -e
}

case "$@" in
  "check")
    run_required_scripts
    run_wanted_scripts
    ;;
  "green")
    run_green_scripts
    ;;
  "red")
    run_red_scripts
    ;;
  *)
    echo "Unknown Option" | systemd-cat -t "greenboot.sh" -p warning
    ;;
esac
