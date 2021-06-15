load common.bash

function setup() {
    cp testing_files/10*.sh $GREENBOOT_CHECK_PATH/wanted.d/ 
}

@test "check with wanted scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -eq 0 ]
}

function teardown() {
    rm $GREENBOOT_CHECK_PATH/wanted.d/10*.sh    
}