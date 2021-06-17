load common.bash

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
