# greenboot
Generic Health Check Framework for systemd on [rpm-ostree](https://coreos.github.io/rpm-ostree/) based systems

## Installation
Greenboot is very modular. It's comprised of several sub-packages, each of them adding specific functionalities.

In order to get a full Greenboot installationon Fedora Silverblue, Fedora IoT or Fedora CoreOS:
```
rpm-ostree install greenboot greenboot-status greenboot-rpm-ostree-grub2 greenboot-grub2 greenboot-reboot greenboot-update-platforms-check

systemctl reboot
```

### Subpackages
- **status:** Posts Greenboot status to MOTD.
- **rpm-ostree-grub2:** Checks if current boot it's a fallback boot.
- **grub2:** Sets GRUB2 environment variables that will be taken into account for determine the status of the boot.
- **reboot:** Reboots the system in case Greenboot checks haven't passed.
- **update-platforms-check:** Checks if the update platforms are still reachable and DNS resolvable.

## How does it work?
- `greenboot-rpm-ostree-grub2-check-fallback.service` runs **before** `greenboot-healthcheck.service` and checks whether the GRUB2 environment variable `boot_counter` is -1. 
  - If it is -1, this would mean that the system is in a fallback deployment and would execute `rpm-ostree rollback` to go back to the previous, working deployment. 
  - If `boot_counter` is not -1, nothing is done in this step.
- `greenboot-healthcheck.service` runs **before** systemd's [boot-complete.target](https://www.freedesktop.org/software/systemd/man/systemd.special.html#boot-complete.target). It launches `/usr/libexec/greenboot/greenboot check`, which runs the `required.d` and `wanted.d` scripts.
  - If any script in the `required.d` folder fails, `redboot.target` is called.
    - It triggers `redboot-task-runner.service`, which launches `/usr/libexec/greenboot/greenboot red`. This will run the scripts in `red.d` folder.
    - After the above:
      - `redboot-auto-reboot.service` is run. It performs a series of checks to determine if there's a requirement for manual intervention. If there's not, it reboots the system.
  - If all scripts in `required.d` folder succeeded:
    - `boot-complete.target` is reached.
    - `greenboot-grub2-set-success.service` is run. It unsets `boot_counter` GRUB env var and sets `boot_success` GRUB env var to 1.
    - `greenboot-task-runner.service` launches `/usr/libexec/greenboot/greenboot green`, which runs the scripts in `green.d` folder, scripts that are meant to be run after a successful update.
    - `greenboot-status.service` is run, creating the MOTD with a success message.

## Usage

### Configuration
At the moment, it is possible to customize the following parameters via the config file `/etc/greenboot/greenboot.conf`. Some of these parameters can be configured as well via environment variables, and those will be explicitely called out in the following list:
- **GREENBOOT_MONITOR_SERVICES**: List of systemd services that are essential to the device performance. If they're not active when the device boots, Greenboot will mark the boot as "red", scripts in `/etc/greenboot/red.d` will be executed and will reboot the device.
- **GREENBOOT_MAX_BOOT_ATTEMPTS**. Maximum number of boot attempts. These parameter can be configured as well via an environment variable with the same name. Bear in mind that the configuration file value will take more precedence than the environment variable one.

### Health checks with bash scripts

Place shell scripts representing *health checks* that **MUST NOT FAIL** in the `/etc/greenboot/check/required.d` directory. 
Place shell scripts representing *health checks* that **MAY FAIL** in the `/etc/greenboot/check/wanted.d` directory.
Place shell scripts you want to run *after* a boot has been declared **successful** in `/etc/greenboot/green.d`.
Place shell scripts you want to run *after* a boot has been declared **failed** in `/etc/greenboot/red.d`.

Unless greenboot is enabled by default in your distribution, enable it by running `systemctl enable greenboot-task-runner greenboot-healthcheck greenboot-status greenboot-loading-message`.
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

#### Health checks included with Greenboot
The `greenboot-update-platforms-check` subpackage ships with the following checks:
- **Check if repositories URLs are still DNS solvable**: This script is under `/etc/greenboot/check/required.d/01_repository_dns_check.sh` and makes sure that DNS queries to repository URLs are still available.
- **Check if update platforms are still reachable**: This script is under `/etc/greenboot/check/wanted.d/01_update_platform_check.sh` and tries to connect and get a 2XX or 3XX HTTP code from the update platforms defined in `/etc/ostree/remotes.d`.
- **Check if certain services are active at boot time**: This script is under `/etc/greenboot/check/required.d/02_update_platform_check.sh`. It makes sure that a user-defined array of services are active at boot time.

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
