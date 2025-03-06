#!/bin/bash
set -euox pipefail

# Dumps details about the instance running the CI job.
echo -e "\033[0;36m"
cat << EOF
------------------------------------------------------------------------------
CI MACHINE SPECS
------------------------------------------------------------------------------
     Hostname: $(uname -n)
         User: $(whoami)
         CPUs: $(nproc)
          RAM: $(free -m | grep -oP '\d+' | head -n 1) MB
         DISK: $(df --output=size -h / | sed '1d;s/[^0-9]//g') GB
         ARCH: $(uname -m)
       KERNEL: $(uname -r)
------------------------------------------------------------------------------
EOF
echo -e "\033[0m"

# Get OS info
source /etc/os-release

# Setup variables
TEST_UUID=qcow2-$((1 + RANDOM % 1000000))
TEMPDIR=$(mktemp -d)
GUEST_ADDRESS=192.168.100.50
SSH_OPTIONS=(-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5)
SSH_KEY=key/ostree_key
SSH_KEY_PUB=$(cat "${SSH_KEY}".pub)
EDGE_USER=core
EDGE_USER_PASSWORD=foobar

case "${ID}-${VERSION_ID}" in
    "fedora-41")
        OS_VARIANT="fedora-unknown"
        BASE_IMAGE_URL="quay.io/fedora/fedora-bootc:41"
        BIB_URL="quay.io/centos-bootc/bootc-image-builder:latest"
        BOOT_ARGS="uefi"
        ;;
    "fedora-42")
        OS_VARIANT="fedora-unknown"
        BASE_IMAGE_URL="quay.io/fedora/fedora-bootc:42"
        BIB_URL="quay.io/centos-bootc/bootc-image-builder:latest"
        BOOT_ARGS="uefi"
        ;;
    "centos-9")
        OS_VARIANT="centos-stream9"
        BASE_IMAGE_URL="quay.io/centos-bootc/centos-bootc:stream9"
        BIB_URL="quay.io/centos-bootc/bootc-image-builder:latest"
        BOOT_ARGS="uefi,firmware.feature0.name=secure-boot,firmware.feature0.enabled=no"
        ;;
    "centos-10")
        OS_VARIANT="centos-stream9"
        BASE_IMAGE_URL="quay.io/centos-bootc/centos-bootc:stream10"
        BIB_URL="quay.io/centos-bootc/bootc-image-builder:latest"
        BOOT_ARGS="uefi,firmware.feature0.name=secure-boot,firmware.feature0.enabled=no"
        ;;
    "rhel-9.6")
        OS_VARIANT="rhel9-unknown"
        BASE_IMAGE_URL="registry.stage.redhat.io/rhel9/rhel-bootc:9.6"
        BIB_URL="registry.stage.redhat.io/rhel9/bootc-image-builder:9.6"
        BOOT_ARGS="uefi"
        ;;
    "rhel-10.0")
        OS_VARIANT="rhel10-unknown"
        BASE_IMAGE_URL="registry.stage.redhat.io/rhel10/rhel-bootc:10.0"
        BIB_URL="registry.stage.redhat.io/rhel10/bootc-image-builder:10.0"
        BOOT_ARGS="uefi"
        ;;
    *)
        echo "unsupported distro: ${ID}-${VERSION_ID}"
        exit 1;;
esac

# Colorful output.
function greenprint {
    echo -e "\033[1;32m${1}\033[0m"
}

check_result () {
    greenprint "🎏 Checking for test result"
    if [[ $RESULTS == 1 ]]; then
        greenprint "💚 Success"
    else
        greenprint "❌ Failed"
        exit 1
    fi
}

# Wait for the ssh server up to be.
wait_for_ssh_up () {
    SSH_STATUS=$(sudo ssh "${SSH_OPTIONS[@]}" -i "${SSH_KEY}" ${EDGE_USER}@"${1}" '/bin/bash -c "echo -n READY"')
    if [[ $SSH_STATUS == READY ]]; then
        echo 1
    else
        echo 0
    fi
}

###########################################################
##
## Prepare before run test
##
###########################################################
greenprint "Installing required packages"
sudo dnf install -y podman qemu-img firewalld qemu-kvm libvirt-client libvirt-daemon-kvm libvirt-daemon virt-install rpmdevtools ansible-core
ansible-galaxy collection install community.general

# Start firewalld
greenprint "Start firewalld"
sudo systemctl enable --now firewalld

# Check ostree_key permissions
KEY_PERMISSION_PRE=$(stat -L -c "%a %G %U" key/ostree_key | grep -oP '\d+' | head -n 1)
echo -e "${KEY_PERMISSION_PRE}"
if [[ "${KEY_PERMISSION_PRE}" != "600" ]]; then
   greenprint "💡 File permissions too open...Changing to 600"
   chmod 600 ./key/ostree_key
fi

# Setup libvirt
greenprint "Starting libvirt service and configure libvirt network"
sudo tee /etc/polkit-1/rules.d/50-libvirt.rules > /dev/null << EOF
polkit.addRule(function(action, subject) {
    if (action.id == "org.libvirt.unix.manage" &&
        subject.isInGroup("adm")) {
            return polkit.Result.YES;
    }
});
EOF
sudo systemctl start libvirtd
sudo virsh list --all > /dev/null
sudo tee /tmp/integration.xml > /dev/null << EOF
<network xmlns:dnsmasq='http://libvirt.org/schemas/network/dnsmasq/1.0'>
  <name>integration</name>
  <uuid>1c8fe98c-b53a-4ca4-bbdb-deb0f26b3579</uuid>
  <forward mode='nat'>
    <nat>
      <port start='1024' end='65535'/>
    </nat>
  </forward>
  <bridge name='integration' zone='trusted' stp='on' delay='0'/>
  <mac address='52:54:00:36:46:ef'/>
  <ip address='192.168.100.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.100.2' end='192.168.100.254'/>
      <host mac='34:49:22:B0:83:30' name='vm-1' ip='192.168.100.50'/>
      <host mac='34:49:22:B0:83:31' name='vm-2' ip='192.168.100.51'/>
      <host mac='34:49:22:B0:83:32' name='vm-3' ip='192.168.100.52'/>
    </dhcp>
  </ip>
  <dnsmasq:options>
    <dnsmasq:option value='dhcp-vendorclass=set:efi-http,HTTPClient:Arch:00016'/>
    <dnsmasq:option value='dhcp-option-force=tag:efi-http,60,HTTPClient'/>
    <dnsmasq:option value='dhcp-boot=tag:efi-http,&quot;http://192.168.100.1/httpboot/EFI/BOOT/BOOTX64.EFI&quot;'/>
  </dnsmasq:options>
</network>
EOF
if ! sudo virsh net-info integration > /dev/null 2>&1; then
    sudo virsh net-define /tmp/integration.xml
fi
if [[ $(sudo virsh net-info integration | grep 'Active' | awk '{print $2}') == 'no' ]]; then
    sudo virsh net-start integration
fi

###########################################################
##
## Build greenboot rpm packages
##
###########################################################
greenprint "Building greenboot packages"
pushd .. && \
shopt -s extglob
version=$(cat greenboot.spec |grep Version|awk '{print $2}')
rm -rf greenboot-${version}/ rpmbuild/
mkdir -p rpmbuild/BUILD rpmbuild/RPMS rpmbuild/SOURCES rpmbuild/SPECS rpmbuild/SRPMS
mkdir greenboot-${version}
cp -r !(rpmbuild|greenboot-${version}|build.sh) greenboot-${version}/
tar -cvf v${version}.tar.gz  greenboot-${version}/
mv v${version}.tar.gz rpmbuild/SOURCES/
rpmbuild -bb --define="_topdir ${PWD}/rpmbuild" greenboot.spec
chmod +x rpmbuild/RPMS/x86_64/*.rpm && \
cp rpmbuild/RPMS/x86_64/*.rpm tests/ && popd

###########################################################
##
## Build bootc container with greenboot installed
##
###########################################################
greenprint "Building bootc container with greenboot installed"
podman login quay.io -u ${QUAY_USERNAME} -p ${QUAY_PASSWORD}
podman login registry.stage.redhat.io -u ${STAGE_REDHAT_IO_USERNAME} -p ${STAGE_REDHAT_IO_TOKEN}
tee Containerfile > /dev/null << EOF
FROM ${BASE_IMAGE_URL}
# Copy the local RPM files into the container
COPY greenboot-*.rpm /tmp/
RUN dnf install -y \
    /tmp/greenboot-*.rpm && \
    systemctl enable greenboot-grub2-set-counter \
    greenboot-grub2-set-success.service greenboot-healthcheck.service \
    greenboot-loading-message.service greenboot-rpm-ostree-grub2-check-fallback.service \
    redboot-auto-reboot.service redboot-task-runner.service redboot.target
# Clean up by removing the local RPMs if desired
RUN rm -f /tmp/greenboot-*.rpm
EOF
podman build  --retry=5 --retry-delay=10s -t quay.io/${QUAY_USERNAME}/greenboot-bootc:${TEST_UUID} -f Containerfile .
greenprint "Pushing bootc container to quay.io"
podman push quay.io/${QUAY_USERNAME}/greenboot-bootc:${TEST_UUID}

###########################################################
##
## BIB to convert bootc container to qcow2/iso images
##
###########################################################
greenprint "Using BIB to convert container to qcow2"
tee config.json > /dev/null << EOF
{
  "blueprint": {
    "customizations": {
      "user": [
        {
          "name": "${EDGE_USER}",
          "password": "${EDGE_USER_PASSWORD}",
          "key": "${SSH_KEY_PUB}",
          "groups": [
            "wheel"
          ]
        }
      ]
    }
  }
}
EOF
sudo rm -fr output && mkdir -p output
podman run \
    --rm \
    -it \
    --privileged \
    --pull=newer \
    --security-opt label=type:unconfined_t \
    -v $(pwd)/config.json:/config.json \
    -v $(pwd)/output:/output \
    -v /var/lib/containers/storage:/var/lib/containers/storage \
    ${BIB_URL} \
    --type qcow2 \
    --config /config.json \
    --rootfs xfs \
    quay.io/${QUAY_USERNAME}/greenboot-bootc:${TEST_UUID}

###########################################################
##
## Provision vm with qcow2/iso artifacts
##
###########################################################
greenprint "Installing vm with bootc qcow2/iso image"
mv $(pwd)/output/qcow2/disk.qcow2 /var/lib/libvirt/images/${TEST_UUID}-disk.qcow2
LIBVIRT_IMAGE_PATH_UEFI=/var/lib/libvirt/images/${TEST_UUID}-disk.qcow2
sudo restorecon -Rv /var/lib/libvirt/images/
sudo virt-install  --name="${TEST_UUID}-uefi"\
                   --disk path="${LIBVIRT_IMAGE_PATH_UEFI}",format=qcow2 \
                   --ram 3072 \
                   --vcpus 2 \
                   --network network=integration,mac=34:49:22:B0:83:30 \
                   --os-type linux \
                   --os-variant ${OS_VARIANT} \
                   --boot ${BOOT_ARGS} \
                   --nographics \
                   --noautoconsole \
                   --wait=-1 \
                   --import \
                   --noreboot
greenprint "Starting UEFI VM"
sudo virsh start "${TEST_UUID}-uefi"

# Check for ssh ready to go.
greenprint "🛃 Checking for SSH is ready to go"
for _ in $(seq 0 30); do
    RESULTS="$(wait_for_ssh_up $GUEST_ADDRESS)"
    if [[ $RESULTS == 1 ]]; then
        echo "SSH is ready now! 🥳"
        break
    fi
    sleep 10
done
check_result

###########################################################
##
## Build upgrade container with failing-unit installed
##
###########################################################
greenprint "Building upgrade container"
tee Containerfile > /dev/null << EOF
FROM quay.io/${QUAY_USERNAME}/greenboot-bootc:${TEST_UUID}
RUN dnf install -y https://kite-webhook-prod.s3.amazonaws.com/greenboot-failing-unit-1.0-1.el8.noarch.rpm
EOF
podman build  --retry=5 --retry-delay=10s -t quay.io/${QUAY_USERNAME}/greenboot-bootc:${TEST_UUID} -f Containerfile .
greenprint "Pushing upgrade container to quay.io"
podman push quay.io/${QUAY_USERNAME}/greenboot-bootc:${TEST_UUID}

###########################################################
##
## Bootc upgrade and check if greenboot can rollback
##
###########################################################
greenprint "Bootc upgrade and reboot"
sudo ssh "${SSH_OPTIONS[@]}" -i "${SSH_KEY}" ${EDGE_USER}@${GUEST_ADDRESS} "echo ${EDGE_USER_PASSWORD} |sudo -S bootc upgrade"
sudo ssh "${SSH_OPTIONS[@]}" -i "${SSH_KEY}" ${EDGE_USER}@${GUEST_ADDRESS} "echo ${EDGE_USER_PASSWORD} |nohup sudo -S systemctl reboot &>/dev/null & exit"

# Wait vm to finish the fallback
sleep 240

# Check for ssh ready to go.
greenprint "🛃 Checking for SSH is ready to go"
for _ in $(seq 0 30); do
    RESULTS="$(wait_for_ssh_up $GUEST_ADDRESS)"
    if [[ $RESULTS == 1 ]]; then
        echo "SSH is ready now! 🥳"
        break
    fi
    sleep 10
done
check_result

# Add instance IP address into /etc/ansible/hosts
tee ${TEMPDIR}/inventory > /dev/null << EOF
[greenboot_guest]
${GUEST_ADDRESS}

[greenboot_guest:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_user=${EDGE_USER}
ansible_private_key_file=${SSH_KEY}
ansible_ssh_common_args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
ansible_become=yes
ansible_become_method=sudo
ansible_become_pass=${EDGE_USER_PASSWORD}
EOF

# Test greenboot functionality
ansible-playbook -v -i /${TEMPDIR}/inventory greenboot-bootc.yaml || RESULTS=0

# Test result checking
check_result
exit 0
