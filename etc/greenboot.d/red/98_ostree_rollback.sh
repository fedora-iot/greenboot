#!/bin/bash
set -euo pipefail

rpm-ostree rollback --reboot
