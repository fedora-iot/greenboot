load common.bash

function setup() {
    source $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh --source-only
}

@test "Ensure watchdog check is working" {
    run check_if_current_boot_is_wd_triggered
    [ "$status" -eq 0 ]
}
