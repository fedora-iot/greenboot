# greenboot
Generic Health Check Framework for systemd

## Usage
The following directory structure is created:

```
/etc
└── greenboot
    ├── check
    │   ├── required.d
    │   └── wanted.d
    ├── green.d
    └── red.d
```

### Custom Health Checks
You have multiple options to customize greenboot’s health checking behaviour:

* Drop scripts representing health checks that MUST NOT FAIL in order to reach a GREEN boot status into `/etc/greenboot/check/required.d`.
* Drop scripts representing health checks that MAY FAIL into `/etc/greenboot/check/wanted.d`.
* Create oneshot health check service units that MUST NOT FAIL like the following and drop them into `/etc/systemd/system` (don't forget to `systemctl enable` them afterwards):
```
[Unit]
Description=Custom Required Health Check
Before=greenboot.target

[Service]
Type=oneshot
ExecStart=/path/to/service

[Install]
RequiredBy=greenboot.target
```
* Create oneshot health check service units that MAY FAIL like the following and drop them into `/etc/systemd/system` (don't forget to `systemctl enable` them afterwards):
```
[Unit]
Description=Custom Wanted Health Check
Before=greenboot.target

[Service]
Type=oneshot
ExecStart=/path/to/service

[Install]
WantedBy=greenboot.target
```

### Custom GREEN Status Procedures
* Drop scripts representing procedures you want to run after a GREEN boot status has been reached into `/etc/greenboot/green.d`.

### Custom RED Status Procedures
* Drop scripts representing procedures you want to run after a RED boot status has been reached into `/etc/greenboot/red.d`.
