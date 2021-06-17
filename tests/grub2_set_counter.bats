load common.bash

function setup() {
    $GRUB2_SET_COUNTER_BIN_PATH
}

@test "Test Grub2 set counter" {
    run $GRUB2_EDITENV list
    [[ "$output" == *"boot_counter=3"* ]]
    [[ "$output" == *"boot_success=0"* ]]
}

function teardown() {
    $GRUB2_EDITENV - unset boot_counter
    $GRUB2_EDITENV - unset boot_success
}