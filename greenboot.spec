%global debug_package %{nil}
%bcond_without check
%global with_bundled 1
%global with_packit 0
%global __cargo_skip_build 0
%global __cargo_is_lib() false
%global forgeurl https://github.com/fedora-iot/greenboot

Version:            1.1.12

%forgemeta

Name:               greenboot
Release:            1%{?dist}
Summary:            Generic Health Check Framework for systemd
License:            LGPLv2+

URL:            %{forgeurl}
Source:         %{forgesource}
%if ! 0%{?with_packit}
%if "%{?commit}" != ""
Source1:        %{name}-%{commit}-vendor.tar.gz
%else
Source1:        %{name}-%{version}-vendor.tar.gz
%endif
%endif

ExcludeArch:    s390x i686 %{power64}

%if 0%{?rhel} && !0%{?eln}
BuildRequires:  rust-toolset
%else
BuildRequires:  rust-packaging
%endif
BuildRequires:      systemd-rpm-macros
%{?systemd_requires}
Requires:           systemd >= 240
Requires:           rpm-ostree
# PAM is required to programmatically read motd messages from /etc/motd.d/*
# This causes issues with RHEL-8 as the fix isn't there an el8 is on pam-1.3.x
Requires:           pam >= 1.4.0
# While not strictly necessary to generate the motd, the main use-case of this package is to display it on SSH login
Recommends:         openssh
# List of bundled crates in vendor tarball, generated with:
# cargo metadata --locked --format-version 1 | CRATE_NAME="greenboot" ./bundled-provides.jq
Provides: bundled(crate(ahash)) = 0.7.6
Provides: bundled(crate(aho-corasick)) = 0.7.20
Provides: bundled(crate(anstream)) = 0.2.6
Provides: bundled(crate(anstyle)) = 0.3.5
Provides: bundled(crate(anstyle-parse)) = 0.1.1
Provides: bundled(crate(anstyle-wincon)) = 0.2.0
Provides: bundled(crate(anyhow)) = 1.0.70
Provides: bundled(crate(async-trait)) = 0.1.68
Provides: bundled(crate(atty)) = 0.2.14
Provides: bundled(crate(autocfg)) = 1.1.0
Provides: bundled(crate(base64)) = 0.13.1
Provides: bundled(crate(bitflags)) = 1.3.2
Provides: bundled(crate(block-buffer)) = 0.10.4
Provides: bundled(crate(cc)) = 1.0.79
Provides: bundled(crate(cfg-if)) = 1.0.0
Provides: bundled(crate(clap)) = 4.2.0
Provides: bundled(crate(clap_builder)) = 4.2.0
Provides: bundled(crate(clap_derive)) = 4.2.0
Provides: bundled(crate(clap_lex)) = 0.4.1
Provides: bundled(crate(concolor-override)) = 1.0.0
Provides: bundled(crate(concolor-query)) = 0.3.3
Provides: bundled(crate(config)) = 0.13.3
Provides: bundled(crate(cpufeatures)) = 0.2.6
Provides: bundled(crate(crypto-common)) = 0.1.6
Provides: bundled(crate(digest)) = 0.10.6
Provides: bundled(crate(dlv-list)) = 0.3.0
Provides: bundled(crate(env_logger)) = 0.7.1
Provides: bundled(crate(errno)) = 0.3.0
Provides: bundled(crate(errno-dragonfly)) = 0.1.2
Provides: bundled(crate(figlet-rs)) = 0.1.5
Provides: bundled(crate(generic-array)) = 0.14.7
Provides: bundled(crate(getrandom)) = 0.2.8
Provides: bundled(crate(glob)) = 0.3.1
Provides: bundled(crate(hashbrown)) = 0.12.3
Provides: bundled(crate(heck)) = 0.4.1
Provides: bundled(crate(hermit-abi)) = 0.1.19
Provides: bundled(crate(hermit-abi)) = 0.3.1
Provides: bundled(crate(humantime)) = 1.3.0
Provides: bundled(crate(io-lifetimes)) = 1.0.9
Provides: bundled(crate(is-terminal)) = 0.4.6
Provides: bundled(crate(itoa)) = 1.0.6
Provides: bundled(crate(json5)) = 0.4.1
Provides: bundled(crate(lazy_static)) = 1.4.0
Provides: bundled(crate(libc)) = 0.2.140
Provides: bundled(crate(linked-hash-map)) = 0.5.6
Provides: bundled(crate(linux-raw-sys)) = 0.3.0
Provides: bundled(crate(log)) = 0.4.17
Provides: bundled(crate(memchr)) = 2.5.0
Provides: bundled(crate(memoffset)) = 0.6.5
Provides: bundled(crate(minimal-lexical)) = 0.2.1
Provides: bundled(crate(nix)) = 0.25.1
Provides: bundled(crate(nom)) = 7.1.3
Provides: bundled(crate(once_cell)) = 1.17.1
Provides: bundled(crate(ordered-multimap)) = 0.4.3
Provides: bundled(crate(pathdiff)) = 0.2.1
Provides: bundled(crate(pest)) = 2.5.6
Provides: bundled(crate(pest_derive)) = 2.5.6
Provides: bundled(crate(pest_generator)) = 2.5.6
Provides: bundled(crate(pest_meta)) = 2.5.6
Provides: bundled(crate(pin-utils)) = 0.1.0
Provides: bundled(crate(pretty_env_logger)) = 0.4.0
Provides: bundled(crate(proc-macro2)) = 1.0.54
Provides: bundled(crate(quick-error)) = 1.2.3
Provides: bundled(crate(quote)) = 1.0.26
Provides: bundled(crate(regex)) = 1.7.3
Provides: bundled(crate(regex-syntax)) = 0.6.29
Provides: bundled(crate(ron)) = 0.7.1
Provides: bundled(crate(rust-ini)) = 0.18.0
Provides: bundled(crate(rustix)) = 0.37.4
Provides: bundled(crate(ryu)) = 1.0.13
Provides: bundled(crate(serde)) = 1.0.159
Provides: bundled(crate(serde_derive)) = 1.0.159
Provides: bundled(crate(serde_json)) = 1.0.95
Provides: bundled(crate(sha2)) = 0.10.6
Provides: bundled(crate(strsim)) = 0.10.0
Provides: bundled(crate(syn)) = 1.0.109
Provides: bundled(crate(syn)) = 2.0.11
Provides: bundled(crate(termcolor)) = 1.2.0
Provides: bundled(crate(thiserror)) = 1.0.40
Provides: bundled(crate(thiserror-impl)) = 1.0.40
Provides: bundled(crate(toml)) = 0.5.11
Provides: bundled(crate(typenum)) = 1.16.0
Provides: bundled(crate(ucd-trie)) = 0.1.5
Provides: bundled(crate(unicode-ident)) = 1.0.8
Provides: bundled(crate(utf8parse)) = 0.2.1
Provides: bundled(crate(version_check)) = 0.9.4
Provides: bundled(crate(wasi)) = 0.11.0+wasi_snapshot_preview1
Provides: bundled(crate(winapi)) = 0.3.9
Provides: bundled(crate(winapi-i686-pc-windows-gnu)) = 0.4.0
Provides: bundled(crate(winapi-util)) = 0.1.5
Provides: bundled(crate(winapi-x86_64-pc-windows-gnu)) = 0.4.0
Provides: bundled(crate(windows-sys)) = 0.45.0
Provides: bundled(crate(windows-targets)) = 0.42.2
Provides: bundled(crate(windows_aarch64_gnullvm)) = 0.42.2
Provides: bundled(crate(windows_aarch64_msvc)) = 0.42.2
Provides: bundled(crate(windows_i686_gnu)) = 0.42.2
Provides: bundled(crate(windows_i686_msvc)) = 0.42.2
Provides: bundled(crate(windows_x86_64_gnu)) = 0.42.2
Provides: bundled(crate(windows_x86_64_gnullvm)) = 0.42.2
Provides: bundled(crate(windows_x86_64_msvc)) = 0.42.2
Provides: bundled(crate(yaml-rust)) = 0.4.5

%description
%{summary}.

%package default-health-checks
Summary:            Series of optional and curated health checks
Requires:           %{name} = %{version}-%{release}
Requires:           util-linux
Requires:           jq

%description default-health-checks
%{summary}.

%prep
%forgeautosetup
%if ! 0%{?with_packit}
tar xvf %{SOURCE1}
%endif
%if ! 0%{?with_bundled}
%cargo_prep
%else
mkdir -p .cargo
cat >.cargo/config << EOF
[build]
rustc = "%{__rustc}"
rustdoc = "%{__rustdoc}"
flags = ["-j4", "-Z", "avoid-dev-deps", "--profile release"]
%if 0%{?rhel} && !0%{?eln}
rustflags = flags
%else
rustflags = "flags"
%endif
 
[install]
root = "%{buildroot}%{_prefix}"
 
[term]
verbose = true
 
[source.crates-io]
replace-with = "vendored-sources"
 
[source.vendored-sources]
directory = "vendor"
EOF
%endif

%if ! 0%{?with_bundled}
%generate_buildrequires
%cargo_generate_buildrequires
%endif

%build
%cargo_build

%install
%cargo_install
# `greenboot` should not be executed directly by users, so we move the binary
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mv %{buildroot}%{_bindir}/greenboot %{buildroot}%{_libexecdir}/%{name}/%{name}
install -Dpm0644 -t %{buildroot}%{_unitdir} \
  usr/lib/systemd/system/*.service
# add config
mkdir -p %{buildroot}%{_exec_prefix}/lib/motd.d/
mkdir -p %{buildroot}%{_libexecdir}/%{name}
install -Dpm0644 -t %{buildroot}%{_sysconfdir}/%{name} etc/greenboot/greenboot.conf
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/check/required.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/check/wanted.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/green.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/red.d
mkdir -p %{buildroot}%{_prefix}/lib/%{name}/check/required.d
mkdir    %{buildroot}%{_prefix}/lib/%{name}/check/wanted.d
mkdir    %{buildroot}%{_prefix}/lib/%{name}/green.d
mkdir    %{buildroot}%{_prefix}/lib/%{name}/red.d
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_tmpfilesdir}
install -DpZm 0755 usr/lib/greenboot/check/required.d/* %{buildroot}%{_prefix}/lib/%{name}/check/required.d
install -DpZm 0755 usr/lib/greenboot/check/wanted.d/* %{buildroot}%{_prefix}/lib/%{name}/check/wanted.d

%post
%systemd_post greenboot-healthcheck.service
%systemd_post greenboot-rollback.service

%preun
%systemd_preun greenboot-healthcheck.service
%systemd_preun greenboot-rollback.service

%postun
%systemd_postun greenboot-healthcheck.service
%systemd_postun greenboot-rollback.service

%files
%doc README.md
%license LICENSE
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}
%{_unitdir}/greenboot-healthcheck.service
%{_unitdir}/greenboot-rollback.service
%{_sysconfdir}/%{name}/greenboot.conf
%dir %{_prefix}/lib/%{name}
%dir %{_prefix}/lib/%{name}/check
%dir %{_prefix}/lib/%{name}/check/required.d
%dir %{_prefix}/lib/%{name}/check/wanted.d
%dir %{_prefix}/lib/%{name}/green.d
%dir %{_prefix}/lib/%{name}/red.d
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/check
%dir %{_sysconfdir}/%{name}/check/required.d
%dir %{_sysconfdir}/%{name}/check/wanted.d
%dir %{_sysconfdir}/%{name}/green.d
%dir %{_sysconfdir}/%{name}/red.d

%files default-health-checks
%{_prefix}/lib/%{name}/check/required.d/01_repository_dns_check.sh
%{_prefix}/lib/%{name}/check/wanted.d/01_update_platforms_check.sh
%{_prefix}/lib/%{name}/check/required.d/02_watchdog.sh

%changelog
* Thu Sep 08 2022 Peter Robinson <pbrobinson@fedoraproject.org> - 0.15.2-1
- The 0.15.2 release

* Tue Aug 09 2022 Peter Robinson <pbrobinson@fedoraproject.org> - 0.15.1-1
- Add conf during installation

* Thu Jul 21 2022 Sayan Paul <saypaul@fedoraproject.org> - 0.15.0-1
- The 0.15.0 release
- Add service-monitor

* Thu Nov 18 2021 Peter Robinson <pbrobinson@fedoraproject.org> - 0.14.0-1
- The 0.14.0 release
- Add watchdog-triggered boot check
- Ensure all required health checks are run

* Wed Nov 10 2021 Peter Robinson <pbrobinson@fedoraproject.org> - 0.13.1-1
- Update to 0.13.1

* Mon Jul 26 2021 Jose Noguera <jnoguera@redhat.com> - 0.12.0-1
- Update to 0.12.0
- Add ability to configure maximum number of boot attempts via env var and config file.
- Add How does it work section to README.
- Add CI via GitHub Actions and unit testing with BATS.
- Add update platforms DNS resolution and connection checker as health checks out of the box

* Sat Jan 16 2021 Peter Robinson <pbrobinson@fedoraproject.org> - 0.11.0-2
- Make arch specific due to grub availability on s390x
- Resolves: rhbz#1915241

* Thu Aug 13 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.11.0-1
- Update to 0.11.0

* Thu Jun 11 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 0.10.3-2
- Update changelog

* Fri Jun 05 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.10.3-1
- Update to 0.10.3

* Wed Jun 03 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.10.2-1
- Update to 0.10.2

* Wed May 27 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.10-1
- Update to 0.10

* Mon May 04 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.9-2
- Added missing requires to grub2 and rpm-ostree-grub2 packages
- Run %%setup quietly

* Fri Apr 03 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.9-1
- Update to v0.9
- Update repo_owner

* Wed Feb 05 2020 Christian Glombek <lorbus@fedoraproject.org> - 0.8-1
- Update to v0.8
- Add guard against bootlooping in redboot-auto-reboot.service

* Mon Apr 01 2019 Christian Glombek <lorbus@fedoraproject.org> - 0.7-1
- Update to v0.7
- Rename ostree-grub2 subpackage to  rpm-ostree-grub2 to be more explicit
- Add auto-update-fallback meta subpackage

* Wed Feb 13 2019 Christian Glombek <lorbus@fedoraproject.org> - 0.6-1
- Update to v0.6
- Integrate with systemd's boot-complete.target
- Rewrite motd sub-package and rename to status

* Fri Oct 19 2018 Christian Glombek <lorbus@fedoraproject.org> - 0.5-1
- Update to v0.5

* Tue Oct 02 2018 Christian Glombek <lorbus@fedoraproject.org> - 0.4-2
- Spec Review

* Thu Jun 14 2018 Christian Glombek <lorbus@fedoraproject.org> - 0.4-1
- Initial Package
