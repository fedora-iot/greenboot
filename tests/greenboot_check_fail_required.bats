load common.bash

function setup() {
    mkdir -p $GREENBOOT_DEFAULT_CHECK_PATH $GREENBOOT_ETC_CHECK_PATH
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/10_failing_check.sh
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/20_failing_check.sh
    cp testing_files/10_failing_check.sh $GREENBOOT_ETC_CHECK_PATH/required.d/30_failing_check.sh
    cp testing_files/10_failing_check.sh $GREENBOOT_ETC_CHECK_PATH/required.d/40_failing_check.sh
}

@test "Test greenboot check with required scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -ne 0 ]
}

@test "Test greenboot runs all required scripts even if one fails" {
    run $GREENBOOT_BIN_PATH check
    [[ "$output" == *"10_failing_check"* ]]
    [[ "$output" == *"20_failing_check"* ]]
    [[ "$output" == *"30_failing_check"* ]]
    [[ "$output" == *"40_failing_check"* ]]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/10_failing_check.sh
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/20_failing_check.sh
    rm $GREENBOOT_ETC_CHECK_PATH/required.d/30_failing_check.sh
    rm $GREENBOOT_ETC_CHECK_PATH/required.d/40_failing_check.sh
}
