load common.bash

function setup() {
  # 02_watchdog.sh can't be checked within the container at the moment
  # due to rpm-ostree, hence moving it out of the required directory
  # for this test
  mv $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh /tmp/02_watchdog.sh
 
  # This checks that the /etc/greenboot/check path works as well 
  # as the /usr/lib/greenboot/check one
  mv $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/* $GREENBOOT_ETC_CHECK_PATH/wanted.d/
}

@test "Test greenboot with unknown argument" {
  run $GREENBOOT_BIN_PATH bananas
  [ "$status" -eq 1 ]
  [ "$output" = "Unknown argument, exiting." ]
}

@test "Test greenboot check with the default hc scripts" {
  run $GREENBOOT_BIN_PATH check
  [ "$status" -eq 0 ]
  [[ "$output" == *"Running Required Health Check Scripts..."* ]]
}

function teardown() {
  mv /tmp/02_watchdog.sh $GREENBOOT_DEFAULT_CHECK_PATH/required.d/02_watchdog.sh
  mv $GREENBOOT_ETC_CHECK_PATH/wanted.d/* $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/
}
