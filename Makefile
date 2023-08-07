RELEASE ?= 0
TARGETDIR ?= target
SRCDIR ?= .
COMMIT = $(shell (cd "$(SRCDIR)" && git rev-parse HEAD))

RPM_SPECFILE=rpmbuild/SPECS/greenboot-$(COMMIT).spec
RPM_TARBALL=rpmbuild/SOURCES/greenboot-$(COMMIT).tar.gz
VENDOR_TARBALL=rpmbuild/SOURCES/greenboot-$(COMMIT)-vendor.tar.gz

ifeq ($(RELEASE),1)
	PROFILE ?= release
	CARGO_ARGS = --release
else
	PROFILE ?= debug
	CARGO_ARGS =
endif

.PHONY: all
all: build test

$(RPM_SPECFILE):
	mkdir -p $(CURDIR)/rpmbuild/SPECS
	(echo "%global commit $(COMMIT)"; git show HEAD:greenboot.spec) > $(RPM_SPECFILE)

$(RPM_TARBALL):
	mkdir -p $(CURDIR)/rpmbuild/SOURCES
	git archive --prefix=greenboot-$(COMMIT)/ --format=tar.gz HEAD > $(RPM_TARBALL)

$(VENDOR_TARBALL):
	mkdir -p $(CURDIR)/rpmbuild/SOURCES
	cargo vendor target/vendor
	tar -czf $(VENDOR_TARBALL) -C target vendor

.PHONY: build
build:
	cargo build "--target-dir=${TARGETDIR}" ${CARGO_ARGS}

.PHONY: install
install: build
	install -D -t ${DESTDIR}/usr/libexec "${TARGETDIR}/${PROFILE}/greenboot"
	install -D -m 644 -t ${DESTDIR}/usr/lib/systemd/system dist/systemd/system/*.service

.PHONY: test
test:
	cargo test "--target-dir=${TARGETDIR}" -- --test-threads=1

.PHONY: srpm
srpm: $(RPM_SPECFILE) $(RPM_TARBALL) $(VENDOR_TARBALL)
	rpmbuild -bs \
		--define "_topdir $(CURDIR)/rpmbuild" \
		$(RPM_SPECFILE)

.PHONY: rpm
rpm: $(RPM_SPECFILE) $(RPM_TARBALL) $(VENDOR_TARBALL)
	rpmbuild -bb \
		--define "_topdir $(CURDIR)/rpmbuild" \
		$(RPM_SPECFILE)