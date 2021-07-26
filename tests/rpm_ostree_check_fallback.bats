load common.bash

function setup() {
    $GRUB2_SET_COUNTER_BIN_PATH
}

@test "Test there's no rollback when boot_counter != -1" {
    run $RPM_OSTREE_CHECK_FALLBACK_PATH
    [[ "$output" != *"FALLBACK BOOT DETECTED"* ]]
}

function teardown() {
    $GRUB2_EDITENV - unset boot_counter
    $GRUB2_EDITENV - unset boot_success
}
