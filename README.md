# greenboot
Generic Health Check Framework for systemd on [rpm-ostree](https://coreos.github.io/rpm-ostree/) based systems.

## Table of contents
* [Installation](#installation)
* [Usage](#usage)
  + [Health checks with bash scripts](#health-checks-with-bash-scripts)
    - [Health checks included with subpackage greenboot-default-health-checks](#health-checks-included-with-subpackage-greenboot\-default\-health\-checks)
  + [Health Checks with systemd services](#health-checks-with-systemd-services)
    - [Required Checks](#required-checks)
    - [Wanted Checks](#wanted-checks)
  + [Configuration](#configuration)
* [How does it work](#how-does-it-work)
* [Development](#development)

## Installation
Greenboot is comprised of two packages:
- `greenboot` itself, with all core functionalities: check provided scripts, reboot if these checks don't pass, rollback to previous deployment if rebooting hasn't solved the problem, etc.
- `greenboot-default-health-checks`, a series of optional and curated health checks provided by Greenboot maintainers.

In order to get a full Greenboot installation on Fedora Silverblue, Fedora IoT or Fedora CoreOS:
```
rpm-ostree install greenboot greenboot-default-health-checks

systemctl reboot
```

## Usage

### Health checks with bash scripts
Place shell scripts representing *health checks* that **MUST NOT FAIL** in the `/etc/greenboot/check/required.d` directory. If any script in this folder exits with an error code, the boot will be declared as failed. Error message will appear in both MOTD and in `journalctl -u greenboot-healthcheck.service`.
Place shell scripts representing *health checks* that **MAY FAIL** in the `/etc/greenboot/check/wanted.d` directory. Scripts in this folder can exit with an error code and the boot will not be declared as failed. Error message will appear in both MOTD and in `journalctl -u greenboot-healthcheck.service -b`.
Place shell scripts you want to run *after* a boot has been declared **successful** (green) in `/etc/greenboot/green.d`.
Place shell scripts you want to run *after* a boot has been declared **failed** (red) in `/etc/greenboot/red.d`.

Unless greenboot is enabled by default in your distribution, enable it by running `systemctl enable greenboot-task-runner greenboot-healthcheck greenboot-status greenboot-loading-message greenboot-grub2-set-counter greenboot-grub2-set-success greenboot-rpm-ostree-grub2-check-fallback redboot-auto-reboot redboot-task-runner`.
It will automatically start during the next boot process and run its checks.

When you `ssh` into the machine after that, a boot status message will be shown:

```
Boot Status is GREEN - Health Check SUCCESS
```
```
Boot Status is RED - Health Check FAILURE!
```

Directory structure: 
```
/etc
└── greenboot
    ├── check
    │   ├── required.d
    │   └── wanted.d
    ├── green.d
    └── red.d
```

#### Health checks included with subpackage greenboot-default-health-checks
These health checks are available in `/usr/lib/greenboot/check`, a read-only directory in rpm-ostree systems. If you find a bug in any of them or you have an improvement, please create a PR with such fix/feature and we'll review it and potentially include it.

- **Check if repositories URLs are still DNS solvable**: This script is under `/usr/lib/greenboot/check/required.d/01_repository_dns_check.sh` and makes sure that DNS queries to repository URLs are still available.
- **Check if update platforms are still reachable**: This script is under `/usr/lib/greenboot/check/wanted.d/01_update_platform_check.sh` and tries to connect and get a 2XX or 3XX HTTP code from the update platforms defined in `/etc/ostree/remotes.d`.
- **Check if current boot has been triggered by hardware watchdog**: This script is under `/usr/lib/greenboot/check/required.d/02_watchdog.sh` and checks whether the current boot has been watchdog-triggered or not. If it is, but the reboot has occurred after a certain grace period (default of 24 hours, configurable via `GREENBOOT_WATCHDOG_GRACE_PERIOD=number_of_hours` in `/etc/greenboot/greenboot.conf`), Greenboot won't mark the current boot as red and won't rollback to the previous deployment. If has occurred within the grace period, at the moment the current boot will be marked as red, but Greenboot won't rollback to the previous deployment. It is enabled by default but it can be disabled by modifying `GREENBOOT_WATCHDOG_CHECK_ENABLED` in `/etc/greenboot/greenboot.conf` to `false`.

### Health Checks with systemd services
Overall boot success is measured against `boot-complete.target`.
Ordering of units can be achieved using standard systemd vocabulary.

#### Required Checks
Create a oneshot health check service unit that **MUST NOT FAIL**, e.g. `/etc/systemd/system/required-check.service`. Make sure it calls `redboot.target` when it fails (`OnFailure=redboot.target`). Run `systemctl enable required-check` to enable it.

```
[Unit]
Description=Custom Required Health Check
Before=boot-complete.target
OnFailure=redboot.target
OnFailureJobMode=fail

[Service]
Type=oneshot
ExecStart=/usr/libexec/mytestsuite/required-check

[Install]
RequiredBy=boot-complete.target
WantedBy=multi-user.target
```

#### Wanted Checks
Create a oneshot health check service unit that **MAY FAIL**, e.g. `/etc/systemd/system/wanted-check.service`. Run `systemctl enable wanted-check` to enable it. 

```
[Unit]
Description=Custom Wanted Health Check
Before=boot-complete.target

[Service]
Type=oneshot
ExecStart=/usr/libexec/mytestsuite/wanted-check

[Install]
WantedBy=boot-complete.target
WantedBy=multi-user.target
```

### Configuration
At the moment, it is possible to customize the following parameters via environment variables. These environment variables can be described as well in the config file `/etc/greenboot/greenboot.conf`:
- **GREENBOOT_MAX_BOOT_ATTEMPTS**: Maximum number of boot attempts before declaring the deployment as problematic and rolling back to the previous one.
- **GREENBOOT_WATCHDOG_CHECK_ENABLED**: Enables/disables *Check if current boot has been triggered by hardware watchdog* health check. More info on [Health checks included with subpackage greenboot-default-health-checks](#health-checks-included-with-subpackage-greenboot\-default\-health\-checks) section.
- **GREENBOOT_WATCHDOG_GRACE_PERIOD**: Number of hours after an upgrade that we consider the new deployment as culprit of reboot.

## How does it work
- `greenboot-rpm-ostree-grub2-check-fallback.service` runs **before** `greenboot-healthcheck.service` and checks whether the GRUB2 environment variable `boot_counter` is -1. 
  - If it is -1, this would mean that the system is in a fallback deployment and would execute `rpm-ostree rollback` to go back to the previous, working deployment. 
  - If `boot_counter` is not -1, nothing is done in this step.
- `greenboot-healthcheck.service` runs **before** systemd's [boot-complete.target](https://www.freedesktop.org/software/systemd/man/systemd.special.html#boot-complete.target). It launches `/usr/libexec/greenboot/greenboot check`, which runs the `required.d` and `wanted.d` scripts.
  - If any script in the `required.d` folder fails, `redboot.target` is called.
    - It triggers `redboot-task-runner.service`, which launches `/usr/libexec/greenboot/greenboot red`. This will run the scripts in `red.d` folder.
    - After the above:
      - `greenboot-status.service` is run, creating the MOTD specifying which scripts have failed.
      - `redboot-auto-reboot.service` is run. It performs a series of checks to determine if there's a requirement for manual intervention. If there's not, it reboots the system.
  - If all scripts in `required.d` folder succeeded:
    - `boot-complete.target` is reached.
    - `greenboot-grub2-set-success.service` is run. It unsets `boot_counter` GRUB env var and sets `boot_success` GRUB env var to 1.
    - `greenboot-task-runner.service` launches `/usr/libexec/greenboot/greenboot green`, which runs the scripts in `green.d` folder, scripts that are meant to be run after a successful update.
    - `greenboot-status.service` is run, creating the MOTD with a success message.

## Development
Please refer to [development/README.md](https://github.com/fedora-iot/greenboot/blob/main/development/README.md) file.
