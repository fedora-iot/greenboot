load common.bash

function setup() {
    mkdir -p $GREENBOOT_DEFAULT_CHECK_PATH $GREENBOOT_ETC_CHECK_PATH

    # 02_watchdog.sh can't be checked within the container at the moment
    # due to rpm-ostree, hence moving it out of the required directory
    # for this test
    mv $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh /tmp/02_watchdog.sh
    
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/10_failing_check.sh
    cp testing_files/10_failing_check.sh $GREENBOOT_ETC_CHECK_PATH/wanted.d/20_failing_check.sh
}

@test "Test greenboot check with wanted scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -eq 0 ]
    [[ "$output" == *"10_failing_check.sh"* ]]
    [[ "$output" == *"20_failing_check.sh"* ]]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/10_failing_check.sh
    rm $GREENBOOT_ETC_CHECK_PATH/wanted.d/20_failing_check.sh
    mv /tmp/02_watchdog.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh
}
