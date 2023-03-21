load common.bash

function setup() {
    mkdir -p $GREENBOOT_DEFAULT_GREEN_PATH $GREENBOOT_ETC_GREEN_PATH
    cp testing_files/20_green_script.sh $GREENBOOT_DEFAULT_GREEN_PATH/20_green_script.sh
    cp testing_files/20_green_script.sh $GREENBOOT_ETC_GREEN_PATH/30_green_script.sh
}

@test "Test greenboot green command" {
    run $GREENBOOT_BIN_PATH green
    [ "$status" -eq 0 ]
    [[ "$output" == *"Health Check SUCCESS"* ]]
    [[ "$output" == *"20_green_script.sh"* ]]
    [[ "$output" == *"30_green_script.sh"* ]]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_GREEN_PATH/20_green_script.sh
    rm $GREENBOOT_ETC_GREEN_PATH/30_green_script.sh
}
