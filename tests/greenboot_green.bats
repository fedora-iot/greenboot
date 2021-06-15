load common.bash

function setup() {
    mkdir -p $GREENBOOT_GREEN_PATH
    cp testing_files/20*.sh $GREENBOOT_GREEN_PATH/
}

@test "green command" {
    run $GREENBOOT_BIN_PATH green
    [ "$status" -eq 0 ]
    [[ "$output" == *"Health Check SUCCESS"* ]]
}

function teardown() {
    rm $GREENBOOT_GREEN_PATH/20*.sh
}