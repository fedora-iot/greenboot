#!/bin/bash
set -euo pipefail

## Set up vagrant-libvirt
# getent group libvirt
# groups ${USER}
# sudo gpasswd -a ${USER} libvirt
# newgrp libvirt
## Fix for Silverblue
# sudo restorecon -Rv /etc/libvirt # -> Relabeled /etc/libvirt from system_u:object_r:virt_etc_rw_t:s0 to system_u:object_r:virt_etc_t:s0

## TODO: Convert into Ansible Playbook; this can't really be run as a script

cd atomic

vagrant up

# v0.7: Workaround for https://github.com/fedora-selinux/selinux-policy/issues/242
# vagrant ssh -c 'sudo semanage fcontext -a -t pam_var_run_t "/var/run/motd\.d(/.*)?"; \
#                 sudo restorecon -Rv /var/run/motd.d;'

vagrant ssh -c 'sudo systemctl enable greenboot greenboot-healthcheck greenboot-status; \
                echo "rebooting..." && sudo systemctl reboot;'
sleep 15

vagrant ssh -c 'sudo journalctl -u greenboot-healthcheck -u boot-complete.target -u greenboot -u redboot -u greenboot-status'

# Check Green Status MotD
# vagrant ssh

vagrant ssh -c 'sudo rpm-ostree cleanup -m; \
                sudo rpm-ostree install greenboot-failing-unit; \
                sudo grub2-editenv - set boot_success=0; \
                sudo grub2-editenv - set boot_counter=1; \
                echo "rebooting..." && sudo systemctl reboot;'

vagrant ssh -c 'sudo journalctl -u greenboot-healthcheck -u boot-complete.target -u greenboot -u redboot -u greenboot-status'

# Check Red Status MotD
# vagrant ssh

cd ..
