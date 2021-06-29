# greenboot
Generic Health Check Framework for systemd on [rpm-ostree](https://coreos.github.io/rpm-ostree/) based systems

## Installation
On Fedora Silverblue, Fedora IoT or Fedora CoreOS:
```
rpm-ostree install greenboot greenboot-status greenboot-ostree-grub2

systemctl reboot
```

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
At the moment, it is possible to customize the following parameters via environment variables. These environment variables can be described as well in the config file `/etc/greenboot/greenboot.conf`:
- **GREENBOOT_MAX_BOOT_ATTEMPTS**. Maximum number of boot attempts.

#### Sample `etc/greenboot/greenboot.conf` file
``` bash
GREENBOOT_MAX_BOOT_ATTEMPTS=2
```

### Health checks with bash scripts

Place shell scripts representing *health checks* that **MUST NOT FAIL** in the `/etc/greenboot/check/required.d` directory. 
Place shell scripts representing *health checks* that **MAY FAIL** in the `/etc/greenboot/check/wanted.d` directory.
Place shell scripts you want to run *after* a boot has been declared **successful** in `/etc/greenboot/green.d`.
Place shell scripts you want to run *after* a boot has been declared **failed** in `/etc/greenboot/red.d`.

Unless greenboot is enabled by default in your distribution, enable it by running `systemctl enable greenboot-task-runner greenboot-healthcheck greenboot-status`.
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
