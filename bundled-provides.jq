#!/usr/bin/env -S jq --sort-keys --raw-output --from-file
 
# To be run from a cargo workspace as:
# cargo metadata --locked --format-version 1 | CRATE_NAME="zincati" bundled-provides.jq
 
.packages[] |
  select(.name != env.CRATE_NAME) |
  "Provides: " +
  "bundled(crate(" + .name + "))" +
  " = " +
  ( .version | gsub("-"; "_") )