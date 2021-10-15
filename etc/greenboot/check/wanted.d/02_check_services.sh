#!/bin/bash

SERVICES=( sshd NetworkManager greenboot-healthcheck 1sshd )

check_if_service_exists() {
    systemctl list-units | grep --quiet "$service".service || rc=$?
    if [[ -n $rc ]]; then
        echo "$service doesn't exist"
        return 1
    fi
    return 0
}

is_service_active() {
    systemctl is-active --quiet "$service".service || rc=$?
    if [[ -n $rc ]]; then
        echo "$service is down, rebooting"
        exit 1
    fi
}

for service in ${SERVICES[*]}; do
    service_exists=$(check_if_service_exists "$service")
    if [[ service_exists -eq 0 ]]; then
        is_service_active "$service"
    fi
done