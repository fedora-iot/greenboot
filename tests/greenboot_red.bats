load common.bash

function setup() {
    mkdir -p $GREENBOOT_DEFAULT_RED_PATH $GREENBOOT_ETC_RED_PATH
    cp testing_files/30_red_script.sh $GREENBOOT_DEFAULT_RED_PATH/30_red_script.sh
    cp testing_files/30_red_script.sh $GREENBOOT_ETC_RED_PATH/40_red_script.sh
}

@test "Test greenboot red command" {
    run $GREENBOOT_BIN_PATH red
    [ "$status" -eq 0 ]
    [[ "$output" == *"Health Check FAILURE"* ]]
    [[ "$output" == *"30_red_script.sh"* ]]
    [[ "$output" == *"40_red_script.sh"* ]]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_RED_PATH/30_red_script.sh
    rm $GREENBOOT_ETC_RED_PATH/40_red_script.sh
}
