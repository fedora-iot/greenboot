# Greenboot
Generic Health Check Framework for systemd

## Usage
Define your health checks as systemd service units and place them in
`/etc/systemd/system`.

Create symbolic links to the critical ones (i.e. those that MUST NOT fail) in
`/etc/systemd/system/greenboot.service.requires`
and to the non-critical ones (i.e. those that MAY fail) in
`/etc/systemd/system/greenboot.service.wants`.

The provided units in the `tests` directory are solely meant for testing purposes.
