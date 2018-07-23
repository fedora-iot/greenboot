#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

script_runner () {
  local scripts_dir=$1; shift
  local mode=$1; shift
  local start_msg=$1; shift
  echo "$start_msg"
  for script in `find $scripts_dir -name '*.sh'`; do
    local rc=0
    systemd-cat -t "$(basename $script)" bash $script || rc=$?
    if [ $rc -ne 0 ]; then
      local failure_msg="Script '$(basename $script)' FAILURE (exit code '$rc')"
      case "$mode" in
        "relaxed")
          echo "$failure_msg. Continuing..." >&2
          ;;
        "strict")
          echo "$failure_msg" >&2
          exit $rc
      esac
    else
      echo "Script '$(basename $script)' SUCCESS"
    fi
  done
}

case "$1" in
  "check")
    script_runner "/etc/greenboot/check/required.d" "strict" "Running Required Health Check Scripts..." || exit 1
    script_runner "/etc/greenboot/check/wanted.d" "relaxed" "Running Wanted Health Check Scripts..."
    ;;
  "green")
    script_runner "/etc/greenboot/green.d" "relaxed" "Running Green Scripts..."
    ;;
  "red")
    script_runner "/etc/greenboot/red.d" "relaxed" "Running Red Scripts..."
    ;;
  *)
    echo "Illegal Command" >&2
    exit 127
esac
