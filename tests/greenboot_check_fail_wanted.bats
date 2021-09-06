load common.bash

function setup() {
    # 02_watchdog.sh can't be checked within the container at the moment
    # due to rpm-ostree, hence moving it out of the required directory
    # for this test
    mv $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh /tmp/02_watchdog.sh
    
    cp testing_files/10_failing_check.sh $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/
}

@test "Test greenboot check with wanted scripts failing" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -eq 0 ]
}

function teardown() {
    rm $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/10_failing_check.sh
    mv /tmp/02_watchdog.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh
}
