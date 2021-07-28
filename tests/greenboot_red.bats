load common.bash

function setup() {
    mkdir -p $GREENBOOT_RED_PATH
    cp testing_files/30_red_script.sh $GREENBOOT_RED_PATH/
}

@test "Test greenboot red command" {
    run $GREENBOOT_BIN_PATH red
    [ "$status" -eq 0 ]
    [[ "$output" == *"Health Check FAILURE"* ]]
}

function teardown() {
    rm $GREENBOOT_RED_PATH/30_red_script.sh    
}
