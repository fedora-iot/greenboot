# How to develop Greenboot

## How to test your changes
### Container 
Ideal for quick development and making sure GitHub tests are going to pass but before creating a pull request, [try it out first in a VM with Fedora IoT and/or RHEL For Edge](#fedora-iot-or-rfe)

Comment the line `ENTRYPOINT [ "/bin/bash", "launch_all_tests.sh" ]` in Dockerfile.

Add this to a `docker-compose.yml` file:

``` yaml
version: "3.8"
services: 
  greenboot:
    privileged: true
    build: .
    container_name: greenboot
    image: greenboot
    volumes:
      - /run/systemd/journal:/run/systemd/journal
    working_dir: /testing
    command: sleep infinity
```


Run this script
``` bash
#!/bin/bash
set -e

# Bring down the previous environment in case there was one
docker-compose down

docker-compose up --build -d
docker exec -it greenboot /bin/bash
docker-compose down
```

### Fedora IoT or RFE:
As `/usr` is mounted as a read-only directory:

- If you want to test health checks, place them under `/etc/greenboot/check/required.d` or `/etc/greenboot/check/wanted.d`. I personally would go for `wanted.d` first to make sure that you don't end up in a full loop of reboots in case your script goes wrong.

- If you’re editing any of the services under `/usr/lib` or `/usr/libexec`, you have two options:
    - place the updated file under `/etc/systemd/system/{same_name_as_in_usr_lib} `and systemd will take this file with more priority.
    - Advanced version: unlock the deployment and add your files in the proper `/usr` directory.

## Unit testing
Health checks, when possible, have been unit-tested with [BATS](https://bats-core.readthedocs.io/en/stable/writing-tests.html). These tests are placed under the [`tests` folder](https://github.com/fedora-iot/greenboot/blob/main/tests).

Every file with the `.bats` extension will be tested.
For declaring/using common environment variables, use [`common.bash`](https://github.com/fedora-iot/greenboot/blob/main/tests/common.bash). You can source them in your BATS file.
If you need to add a file, please use [`tests/testing_files` folder](https://github.com/fedora-iot/greenboot/blob/main/tests/testing_files).