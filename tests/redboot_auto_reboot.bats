load common.bash
REDBOOT_AUTO_REBOOT=$GREENBOOT_USR_ROOT_PATH/redboot-auto-reboot

function setup() {
    $GRUB2_EDITENV - unset boot_counter
}

@test "Test system unhealthy but boot_counter unset" {
    run $REDBOOT_AUTO_REBOOT
    [[ "$output" == *"<0>SYSTEM is UNHEALTHY"* ]]
    [ "$status" = 1 ]
}

@test "Test fallback boot detected but system still unhealthy" {
    run $GRUB2_EDITENV - set boot_counter=-1
    run $REDBOOT_AUTO_REBOOT
    [[ "$output" == *"<0>FALLBACK BOOT DETECTED"* ]]
    [ "$status" = 2 ]
}

@test "Test system unhealthy but bootloader entry count -le 1 " {
    run $GRUB2_EDITENV - set boot_counter=1
    run $REDBOOT_AUTO_REBOOT
    [[ "$output" == *"<0>SYSTEM is UNHEALTHY"* ]]
    [ "$status" = 3 ]
}

function teardown() {
    $GRUB2_EDITENV - unset boot_counter
}
