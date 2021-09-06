FROM fedora
RUN dnf install -y git findutils systemd grub2-tools-minimal util-linux jq

RUN git clone https://github.com/bats-core/bats-core.git
WORKDIR /bats-core
RUN ./install.sh /usr/local

COPY ./usr/libexec/greenboot /usr/libexec/greenboot
COPY ./usr/lib/greenboot/check /usr/lib/greenboot/check
RUN mkdir -p /etc/greenboot/{green.d,red.d,check}
RUN mkdir /etc/greenboot/check/{required.d,wanted.d}
COPY ./etc/greenboot/greenboot.conf /etc/greenboot/greenboot.conf

COPY ./tests /testing
COPY ./tests/testing_files/fedora_iot.conf /etc/ostree/remotes.d/fedora_iot.conf

WORKDIR /testing
ENTRYPOINT [ "/bin/bash", "launch_all_tests.sh" ]
