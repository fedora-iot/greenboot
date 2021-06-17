# Testing

## Fedora IoT 30

In order to be able to easily check the motd output, the preferred way of testing is over ssh.

### Preparation
```bash
# ssh into your machine

# Ensure the following rpms are installed:
# greenboot greenboot-status
# otherwise install them:
build=00876215 && \
    curl https://copr-be.cloud.fedoraproject.org/results/lorbus/greenboot/fedora-30-x86_64/$build-greenboot/greenboot-0.7-1.fc30.noarch.rpm --output greenboot-0.7-1.fc30.noarch.rpm && \
    curl https://copr-be.cloud.fedoraproject.org/results/lorbus/greenboot/fedora-30-x86_64/$build-greenboot/greenboot-grub2-0.7-1.fc30.noarch.rpm --output greenboot-grub2-0.7-1.fc30.noarch.rpm && \
    curl https://copr-be.cloud.fedoraproject.org/results/lorbus/greenboot/fedora-30-x86_64/$build-greenboot/greenboot-reboot-0.7-1.fc30.noarch.rpm --output greenboot-reboot-0.7-1.fc30.noarch.rpm && \
    curl https://copr-be.cloud.fedoraproject.org/results/lorbus/greenboot/fedora-30-x86_64/$build-greenboot/greenboot-rpm-ostree-grub2-0.7-1.fc30.noarch.rpm --output greenboot-rpm-ostree-grub2-0.7-1.fc30.noarch.rpm && \
    curl https://copr-be.cloud.fedoraproject.org/results/lorbus/greenboot/fedora-30-x86_64/$build-greenboot/greenboot-status-0.7-1.fc30.noarch.rpm --output greenboot-status-0.7-1.fc30.noarch.rpm && \
sudo rpm-ostree override replace \
    greenboot-0.7-1.fc30.noarch.rpm \
    greenboot-grub2-0.7-1.fc30.noarch.rpm \
    greenboot-reboot-0.7-1.fc30.noarch.rpm \
    --remove=greenboot-ostree-grub2-0.6-1.fc30.noarch \
    --install=greenboot-rpm-ostree-grub2-0.7-1.fc30.noarch.rpm \
    --install=greenboot-status-0.7-1.fc30.noarch.rpm && \
sudo systemctl reboot

# Enabling services, but let's hold off on enabling redboot-auto-reboot.service for a bit
# so we don't get into reboot-looping through all our boot attempts (i.e. until boot_counter reaches 0)
sudo systemctl enable \
    greenboot-task-runner \
    greenboot-healthcheck \
    greenboot-rpm-ostree-grub2-check-fallback \
    greenboot-grub2-set-counter \
    greenboot-grub2-set-success \
    greenboot-status \
    redboot-task-runner && \
sudo systemctl reboot

```

### Testing

```bash
# Test success to complete checks
#

# When logging in via ssh, you should see the motd for a green boot status:
#
# Boot Status is GREEN - Health Check SUCCESS

# Check all our logs
sudo journalctl -b -0 \
    -u boot-complete.target \
    -u greenboot-task-runner \
    -u greenboot-healthcheck \
    -u greenboot-rpm-ostree-grub2-check-fallback \
    -u greenboot-grub2-set-counter \
    -u greenboot-grub2-set-success \
    -u greenboot-status \
    -u redboot-task-runner \
    -u redboot-auto-reboot \
    -u redboot.target

# check grubenv variables
sudo grub2-editenv list

# the service that sets boot_success to 1 before reboot should be active:
sudo systemctl is-active greenboot-grub2-set-success.service


# Test failure to complete checks
#

# Install sanely failing health check unit to test red boot status behavior
curl https://copr-be.cloud.fedoraproject.org/results/lorbus/greenboot/fedora-30-x86_64/00858207-greenboot-failing-unit/greenboot-failing-unit-1.0-1.fc30.noarch.rpm --output greenboot-failing-unit-1.0-1.fc30.noarch.rpm && \
sudo rpm-ostree install greenboot-failing-unit-1.0-1.fc30.noarch.rpm && \
sudo systemctl reboot

# If greenboot-reboot is disabled, you should see the following when logging in:
#
# Boot Status is RED - Health Check FAILURE!
# Script '10_failing_check.sh' FAILURE (exit code '1')

# Check all our journal logs again
sudo journalctl -b -0 \
    -u boot-complete.target \
    -u greenboot-task-runner \
    -u greenboot-healthcheck \
    -u greenboot-rpm-ostree-grub2-check-fallback \
    -u greenboot-grub2-set-counter \
    -u greenboot-grub2-set-success \
    -u greenboot-status \
    -u redboot-task-runner \
    -u redboot-auto-reboot \
    -u redboot.target

# grubenv should contain:
# boot_counter=2
sudo grub2-editenv list

# the service to set boot_success to 1 before reboot should be inactive (dead):
sudo systemctl status greenboot-grub2-set-success.service

# Let's enable the system to try all the remaining boot attempts at this failing deployment,
# before finally booting back into the rollback deployment automatically.
sudo systemctl enable redboot-auto-reboot && \
sudo systemctl reboot

# After the remaining boot attempts have been tried, log in again and you should see:
#
# Boot Status is GREEN - Health Check SUCCESS
# FALLBACK BOOT DETECTED! Default rpm-ostree deployment has been rolled back.
# Health check logs from previous boot:
# Script '10_failing_check.sh' FAILURE (exit code '1')

# Check all our journal logs again
sudo journalctl -b -0 \
    -u boot-complete.target \
    -u greenboot-task-runner \
    -u greenboot-healthcheck \
    -u greenboot-rpm-ostree-grub2-check-fallback \
    -u greenboot-grub2-set-counter \
    -u greenboot-grub2-set-success \
    -u greenboot-status \
    -u redboot-task-runner \
    -u redboot-auto-reboot \
    -u redboot.target

# grubenv
sudo grub2-editenv list

# the service to set boot_success to 1 before reboot should be active again:
sudo systemctl status greenboot-grub2-set-success.service

```