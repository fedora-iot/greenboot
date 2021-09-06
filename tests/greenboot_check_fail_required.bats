load common.bash

function setup() {
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/
}

@test "Test greenboot check with required scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -ne 0 ]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/10_failing_check.sh
}
