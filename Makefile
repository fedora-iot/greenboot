RELEASE ?= 0
TARGETDIR ?= target

ifeq ($(RELEASE),1)
	PROFILE ?= release
	CARGO_ARGS = --release
else
	PROFILE ?= debug
	CARGO_ARGS =
endif

.PHONY: all
all: build check

.PHONY: build
build:
	cargo build "--target-dir=${TARGETDIR}" ${CARGO_ARGS}

.PHONY: install
install: build
	install -D -t ${DESTDIR}/usr/libexec "${TARGETDIR}/${PROFILE}/greenboot"
	install -D -m 644 -t ${DESTDIR}/usr/lib/systemd/system dist/systemd/system/*.service

.PHONY: check
check:
	cargo test "--target-dir=${TARGETDIR}"