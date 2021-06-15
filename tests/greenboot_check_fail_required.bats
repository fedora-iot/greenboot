load common.bash

function setup() {
    cp testing_files/10*.sh $GREENBOOT_CHECK_PATH/required.d/ 
}

@test "check with required scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -eq 1 ]
}

function teardown() {
    rm $GREENBOOT_CHECK_PATH/required.d/10*.sh    
}