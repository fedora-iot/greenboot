#!/bin/bash

check_if_config_file_exists() {
    GREENBOOT_CONFIGURATION_FILE=/etc/greenboot/greenboot.conf
    if test -f "$GREENBOOT_CONFIGURATION_FILE"; then
        source $GREENBOOT_CONFIGURATION_FILE
        # SERVICES=( "${SERVICES[@]}" "${GREENBOOT_MONITOR_SERVICES[@]}" )
        SERVICES=( "${GREENBOOT_MONITOR_SERVICES[@]}" )
    else
        echo "ERROR: $GREENBOOT_CONFIGURATION_FILE doesn't exist"
        exit 2
    fi
}

check_if_service_exists() {
    local service=$1
    (systemctl list-units | grep --quiet "$service".service)
    echo "$?"
}

is_service_active() {
    local service=$1
    systemctl is-active --quiet "$service".service || local rc=$?
    if [[ -n $rc ]]; then
        echo "$service is down, rebooting"
        exit 1
    fi
}


check_if_config_file_exists
for service in "${SERVICES[@]}"; do
    service_exists=$(check_if_service_exists "$service")
    if [[ $service_exists -ne 0 ]]; then
        echo "WARNING: $service.service can't be found"
    else
        is_service_active "$service"
    fi
done