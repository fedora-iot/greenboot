load common.bash

MAX_BOOT_ATTEMPTS=2
MAX_BOOT_ATTEMPTS_DEFAULT=3
MAX_BOOT_ATTEMPTS_ENV_VAR=4
MAX_BOOT_ATTEMPTS_CONFIG_FILE=5

CONFIG_FILE_PATH=$GREENBOOT_ETC_ROOT_PATH/greenboot.conf

@test "Test Grub2 set counter with default values" {
    $GRUB2_SET_COUNTER_BIN_PATH
    run $GRUB2_EDITENV list
    [[ "$output" == *"boot_counter=$MAX_BOOT_ATTEMPTS_DEFAULT"* ]]
    [[ "$output" == *"boot_success=0"* ]]
}

@test "Test Grub2 set counter with input variable" {
    $GRUB2_SET_COUNTER_BIN_PATH $MAX_BOOT_ATTEMPTS
    run $GRUB2_EDITENV list
    [[ "$output" == *"boot_counter=$MAX_BOOT_ATTEMPTS"* ]]
    [[ "$output" == *"boot_success=0"* ]]
}

@test "Test Grub2 set counter with env variable" {
    GREENBOOT_MAX_BOOT_ATTEMPTS=$MAX_BOOT_ATTEMPTS_ENV_VAR $GRUB2_SET_COUNTER_BIN_PATH
    run $GRUB2_EDITENV list
    [[ "$output" == *"boot_counter=$MAX_BOOT_ATTEMPTS_ENV_VAR"* ]]
    [[ "$output" == *"boot_success=0"* ]]
}

@test "Test Grub2 set counter with config file" {
    echo GREENBOOT_MAX_BOOT_ATTEMPTS=$MAX_BOOT_ATTEMPTS_CONFIG_FILE >> $CONFIG_FILE_PATH
    $GRUB2_SET_COUNTER_BIN_PATH
    run $GRUB2_EDITENV list
    [[ "$output" == *"boot_counter=$MAX_BOOT_ATTEMPTS_CONFIG_FILE"* ]]
    [[ "$output" == *"boot_success=0"* ]]
}

function teardown() {
    $GRUB2_EDITENV - unset boot_counter
    $GRUB2_EDITENV - unset boot_success
    rm -f $CONFIG_FILE_PATH
}
