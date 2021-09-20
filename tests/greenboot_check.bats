load common.bash

function setup() {
  # This checks that the /etc/greenboot/check path works as well 
  # as the /usr/lib/greenboot/check one
  mv $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/* $GREENBOOT_ETC_CHECK_PATH/wanted.d/
}

@test "Test greenboot with illegal command" {
  run $GREENBOOT_BIN_PATH bananas
  [ "$status" -eq 127 ]
  [ "$output" = "Illegal Command" ]
}

@test "Test greenboot check with the default hc scripts" {
  run $GREENBOOT_BIN_PATH check
  [ "$status" -eq 0 ]
  [[ "$output" == *"Running Required Health Check Scripts..."* ]]
}

function teardown() {
  mv $GREENBOOT_ETC_CHECK_PATH/wanted.d/* $GREENBOOT_DEFAULT_CHECK_PATH/wanted.d/
}
