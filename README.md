# greenboot
Generic Health Check Framework for systemd

## Installation
On Fedora Silverblue, IoT or Atomic Host:
```
rpm-ostree install greenboot greenboot-status greenboot-ostree-grub2

systemctl reboot
```

## Usage
Place shell scripts representing *health checks* that **MUST NOT FAIL** in the `/etc/greenboot/check/required.d` directory. 
Place shell scripts representing *health checks* that **MAY FAIL** in the `/etc/greenboot/check/wanted.d` directory.
Place shell scripts you want to run *after* a boot has been declared **successful** in `/etc/greenboot/green.d`.
Place shell scripts you want to run *after* a boot has been declared **failed** in `/etc/greenboot/red.d`.

Unless greenboot is enabled by default in your distribution, enable it by running `systemctl enable greenboot greenboot-healthcheck greenboot-status`.
It will automatically start during the next boot process and run its checks.

When you `ssh` into the machine after that, a boot status message will be shown.

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


## Health Checks with systemd services
Overall boot success is measured against `boot-complete.target`.
Ordering of units can be achieved using standard systemd vocabulary.

### Required Checks
Create a oneshot health check service unit that **MUST NOT FAIL**, e.g. `/etc/systemd/system/required-check.service`. Run `systemctl enable required-check` to enable it.

```
[Unit]
Description=Custom Required Health Check
Before=boot-complete.target

[Service]
Type=oneshot
ExecStart=/usr/libexec/mytestsuite/required-check

[Install]
RequiredBy=boot-complete.target
```

### Wanted Checks
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
```
