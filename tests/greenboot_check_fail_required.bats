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

@test "Test greenboot exits when one required script fails" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -ne 0 ]  # Ensure greenboot exits with a non-zero status

    # Count occurrences of failing scripts in the output
    fail_count=$(echo "$output" | grep -E "FAILURE" | \
    grep -c -E "10_failing_check.sh|20_failing_check.sh|30_failing_check.sh|40_failing_check.sh")

    # Ensure only one failing script is reported
    [ "$fail_count" -eq 1 ]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/10_failing_check.sh
    rm $GREENBOOT_DEFAULT_CHECK_PATH/required.d/20_failing_check.sh
    rm $GREENBOOT_ETC_CHECK_PATH/required.d/30_failing_check.sh
    rm $GREENBOOT_ETC_CHECK_PATH/required.d/40_failing_check.sh
}
