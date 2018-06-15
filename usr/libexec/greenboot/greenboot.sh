#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

run_required_scripts () {
  echo "Running Required Health Check Scripts..."
  local required_scripts=`find /etc/greenboot.d/check/required -name '*.sh'`
  local rc=0
  for script in $required_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -ne 0 ]; then
      echo -e "\e[1;31mRequired Health Check Script '$(basename $script)' FAILURE (exit code '$rc')\e[0m" >&2
      exit $rc
    fi
    echo -e "\e[1;32mRequired Health Check Script '$(basename $script)' SUCCESS\e[0m"
  done
}

run_wanted_scripts () {
  echo "Running Wanted Health Check Scripts..."
  local wanted_scripts=`find /etc/greenboot.d/check/wanted -name '*.sh'`
  local rc=0
  for script in $wanted_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -eq 0 ]; then
      echo -e "\e[1;32mWanted Health Check Script '$(basename $script)' SUCCESS\e[0m"
    else
      echo -e "\e[1;31mWanted Health Check Script '$(basename $script)' FAILURE (exit code '$rc'). Continuing...\e[0m" >&2
    fi
  done
}

run_green_scripts () {
  echo "Running Green Scripts..."
  local green_scripts=`find /etc/greenboot.d/green -name '*.sh'`
  local rc=0
  for script in $green_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -eq 0 ]; then
      echo -e "\e[1;32mGreen Script '$(basename $script)' SUCCESS\e[0m"
    else
      echo -e "\e[1;31mGreen Script '$(basename $script)' FAILURE (exit code '$rc'). Continuing...\e[0m" >&2
    fi
  done
}

run_red_scripts () {
  echo "Running Red Scripts..."
  local red_scripts=`find /etc/greenboot.d/red -name '*.sh'`
  local rc=0
  for script in $red_scripts; do
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -eq 0 ]; then
      echo -e "\e[1mRed Script '$(basename $script)' SUCCESS\e[0m"
    else
      echo -e "\e[1;31mRed Script '$(basename $script)' FAILURE (exit code '$rc'). Continuing...\e[0m" >&2
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
    echo -e "\e[31mIllegal Command\e[0m" >&2
    exit 127
    ;;
esac
