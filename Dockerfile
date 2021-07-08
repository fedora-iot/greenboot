FROM fedora
RUN dnf install -y git findutils systemd grub2-tools-minimal

RUN git clone https://github.com/bats-core/bats-core.git
WORKDIR /bats-core
RUN ./install.sh /usr/local

COPY ./usr/libexec/greenboot /usr/libexec/greenboot
COPY ./etc/greenboot/check /etc/greenboot/check

WORKDIR /testing
COPY ./tests .

COPY ./tests/testing_files/fedora_iot.conf /etc/ostree/remotes.d/fedora_iot.conf
ENTRYPOINT [ "/bin/bash", "launch_all_tests.sh" ]