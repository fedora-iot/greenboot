load common.bash

function setup() {
    mkdir -p $GREENBOOT_RED_PATH
    cp testing_files/30*.sh $GREENBOOT_RED_PATH/ 
}

@test "check with wanted scripts failing" {
    run $GREENBOOT_BIN_PATH red
    [ "$status" -eq 0 ]
    [[ "$output" == *"Health Check FAILURE"* ]]
}

function teardown() {
    rm $GREENBOOT_RED_PATH/30*.sh    
}