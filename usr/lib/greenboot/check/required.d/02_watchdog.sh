#!/bin/bash
set -eo pipefail

source_configuration_file() {
  GREENBOOT_CONFIGURATION_FILE=/etc/greenboot/greenboot.conf
  if test -f "$GREENBOOT_CONFIGURATION_FILE"; then
    # shellcheck source=etc/greenboot/greenboot.conf
    source $GREENBOOT_CONFIGURATION_FILE
  fi
}

set_grace_period() {
    DEFAULT_GRACE_PERIOD=24 # default to 24 hours

    if [ -n "$GREENBOOT_WATCHDOG_GRACE_PERIOD" ]; then
        GRACE_PERIOD=$GREENBOOT_WATCHDOG_GRACE_PERIOD
    else
        GRACE_PERIOD=$DEFAULT_GRACE_PERIOD
    fi
}

check_if_there_is_a_watchdog() {
    if wdctl 2>/dev/null ; then
      return 0
    else
      return 1
    fi
}

check_if_current_boot_is_wd_triggered() {
    if check_if_there_is_a_watchdog ; then
      WDCTL_OUTPUT=$(wdctl --flags-only --noheadings | grep -c '1$' || true)
      if [ "$WDCTL_OUTPUT" -gt 0 ]; then
        # This means the boot was watchdog triggered
        # TO-DO: maybe do a rollback here?
        echo "Watchdog triggered after recent update"
        exit 1
      fi
    else
      # There's no watchdog, so nothing to be done here
      exit 0
    fi
}

# This is in order to test check_if_current_boot_is_wd_triggered
# function within a container
if [ "${1}" != "--source-only" ]; then
  if ! check_if_there_is_a_watchdog ; then
    echo "No watchdog on the system, skipping check"
    exit 0
  fi

  source_configuration_file
  if [ "${GREENBOOT_WATCHDOG_CHECK_ENABLED,,}" != "true" ]; then
    echo "Watchdog check is disabled"
    exit 0
  fi

  set_grace_period

  SECONDS_IN_AN_HOUR=$((60 * 60))
  LAST_DEPLOYMENT_TIMESTAMP=$(rpm-ostree status --json | jq .deployments[0].timestamp)

  HOURS_SINCE_LAST_UPDATE=$((($(date +%s) - "$LAST_DEPLOYMENT_TIMESTAMP") / SECONDS_IN_AN_HOUR))
  if [ "$HOURS_SINCE_LAST_UPDATE" -lt "$GRACE_PERIOD" ]; then
      check_if_current_boot_is_wd_triggered
  else
      exit 0
  fi
fi
