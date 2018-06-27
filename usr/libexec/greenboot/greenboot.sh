#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

run_required_scripts () {
  echo "Running Required Health Check Scripts..."
  local required_scripts=`find /etc/greenboot/check/required.d -name '*.sh'`
  local rc=0
  for script in $required_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -ne 0 ]; then
      echo "Required Health Check Script '$(basename $script)' FAILURE (exit code '$rc')" >&2
      exit $rc
    fi
    echo "Required Health Check Script '$(basename $script)' SUCCESS"
  done
}

run_wanted_scripts () {
  echo "Running Wanted Health Check Scripts..."
  local wanted_scripts=`find /etc/greenboot/check/wanted.d -name '*.sh'`
  local rc=0
  for script in $wanted_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -eq 0 ]; then
      echo "Wanted Health Check Script '$(basename $script)' SUCCESS"
    else
      echo "Wanted Health Check Script '$(basename $script)' FAILURE (exit code '$rc'). Continuing..." >&2
    fi
  done
}

run_green_scripts () {
  echo "Running Green Scripts..."
  local green_scripts=`find /etc/greenboot/green.d -name '*.sh'`
  local rc=0
  for script in $green_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -eq 0 ]; then
      echo "Green Script '$(basename $script)' SUCCESS"
    else
      echo "Green Script '$(basename $script)' FAILURE (exit code '$rc'). Continuing..." >&2
    fi
  done
}

run_red_scripts () {
  echo "Running Red Scripts..."
  local red_scripts=`find /etc/greenboot/red.d -name '*.sh'`
  local rc=0
  for script in $red_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -eq 0 ]; then
      echo "Red Script '$(basename $script)' SUCCESS"
    else
      echo "Red Script '$(basename $script)' FAILURE (exit code '$rc'). Continuing..." >&2
    fi
  done
}

case "$@" in
  "check")
    run_required_scripts || exit 1
    run_wanted_scripts
    ;;
  "green")
    run_green_scripts
    ;;
  "red")
    run_red_scripts
    ;;
  *)
    echo "Illegal Command" >&2
    exit 127
    ;;
esac
