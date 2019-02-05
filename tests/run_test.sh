## Set up vagrant-libvirt
# getent group libvirt
# groups ${USER}
# sudo gpasswd -a ${USER} libvirt
# newgrp libvirt
## Fix for Silverblue
# sudo restorecon -Rv /etc/libvirt # -> Relabeled /etc/libvirt from system_u:object_r:virt_etc_rw_t:s0 to system_u:object_r:virt_etc_t:s0

cd atomic

vagrant up
# Use the failing check to test red boot status behaviour
# vagrant ssh -c 'ln -s /home/vagrant/sync/10_failing_check.sh /etc/greenboot/check/required.d/10_failing_check.sh'

# Workaround for https://github.com/fedora-selinux/selinux-policy/issues/242
vagrant ssh -c 'sudo semanage fcontext -a -t pam_var_run_t "/var/run/motd.d(/.*)?"; \
                sudo restorecon -Rv /var/run/motd.d;'

vagrant ssh -c 'sudo systemctl enable greenboot greenboot-healthcheck bootstatus-motd; \
                sudo systemctl reboot;'
sleep 15

vagrant ssh -c 'sudo journalctl -u greenboot-healthcheck -u boot-complete.target -u greenboot -u redboot -u bootstatus-motd'

# vagrant ssh -c 'sudo rpm-ostree upgrade; \
#                 sudo grub2-editenv - set boot_success=0; \
#                 sudo grub2-editenv - set boot_counter=3; \
#                 sudo systemctl reboot;'

cd ..
