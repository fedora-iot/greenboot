load common.bash

function setup() {
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/10_failing_check.sh
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/20_failing_check.sh
}

@test "Test greenboot check with required scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -eq 1 ]
}

@test "Test greenboot runs all required scripts even if one fails" {
    run $GREENBOOT_BIN_PATH check
    [[ "$output" == *"10_failing_check"* ]]
    [[ "$output" == *"20_failing_check"* ]]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/10_failing_check.sh
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/20_failing_check.sh
}
