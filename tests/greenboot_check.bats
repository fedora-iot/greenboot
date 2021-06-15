load common.bash

@test "illegal command" {
  run $GREENBOOT_BIN_PATH bananas
  [ "$status" -eq 127 ]
  [ "$output" = "Illegal Command" ]
}

@test "check" {
    run $GREENBOOT_BIN_PATH check
    [ "$status" -eq 0 ]
    [[ "$output" == *"Running Required Health Check Scripts..."* ]]
}
