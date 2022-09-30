%global debug_package %{nil}
%bcond_without check
%global with_bundled 1
%global with_packit 1
%global __cargo_skip_build 0
%global __cargo_is_lib() false
%global forgeurl https://github.com/fedora-iot/greenboot

Version:            0.99.0

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
Provides:           greenboot-auto-update-fallback
Obsoletes:          greenboot-auto-update-fallback <= 0.12.0
Provides:           greenboot-grub2
Obsoletes:          greenboot-grub2 <= 0.12.0
Provides:           greenboot-reboot
Obsoletes:          greenboot-reboot <= 0.12.0
Provides:           greenboot-status
Obsoletes:          greenboot-status <= 0.12.0
Provides:           greenboot-rpm-ostree-grub2
Obsoletes:          greenboot-rpm-ostree-grub2 <= 0.12.0
# List of bundled crate in vendor tarball, generated with:
# cargo metadata --locked --format-version 1 | CRATE_NAME="greenboot" ./bundled-provides.jq
Provides: bundled(crate(ahash)) = 0.7.6
Provides: bundled(crate(aho-corasick)) = 0.7.19
Provides: bundled(crate(anyhow)) = 1.0.65
Provides: bundled(crate(async-trait)) = 0.1.57
Provides: bundled(crate(atty)) = 0.2.14
Provides: bundled(crate(autocfg)) = 1.1.0
Provides: bundled(crate(base64)) = 0.13.0
Provides: bundled(crate(bitflags)) = 1.3.2
Provides: bundled(crate(block-buffer)) = 0.10.3
Provides: bundled(crate(cfg-if)) = 1.0.0
Provides: bundled(crate(clap)) = 4.0.4
Provides: bundled(crate(clap_derive)) = 4.0.1
Provides: bundled(crate(clap_lex)) = 0.3.0
Provides: bundled(crate(config)) = 0.13.2
Provides: bundled(crate(cpufeatures)) = 0.2.5
Provides: bundled(crate(crypto-common)) = 0.1.6
Provides: bundled(crate(digest)) = 0.10.5
Provides: bundled(crate(dlv-list)) = 0.3.0
Provides: bundled(crate(env_logger)) = 0.7.1
Provides: bundled(crate(generic-array)) = 0.14.6
Provides: bundled(crate(getrandom)) = 0.2.7
Provides: bundled(crate(glob)) = 0.3.0
Provides: bundled(crate(hashbrown)) = 0.12.3
Provides: bundled(crate(heck)) = 0.4.0
Provides: bundled(crate(hermit-abi)) = 0.1.19
Provides: bundled(crate(humantime)) = 1.3.0
Provides: bundled(crate(itoa)) = 1.0.3
Provides: bundled(crate(json5)) = 0.4.1
Provides: bundled(crate(lazy_static)) = 1.4.0
Provides: bundled(crate(libc)) = 0.2.133
Provides: bundled(crate(linked-hash-map)) = 0.5.6
Provides: bundled(crate(log)) = 0.4.17
Provides: bundled(crate(memchr)) = 2.5.0
Provides: bundled(crate(memoffset)) = 0.6.5
Provides: bundled(crate(minimal-lexical)) = 0.2.1
Provides: bundled(crate(nix)) = 0.25.0
Provides: bundled(crate(nom)) = 7.1.1
Provides: bundled(crate(once_cell)) = 1.15.0
Provides: bundled(crate(ordered-multimap)) = 0.4.3
Provides: bundled(crate(os_str_bytes)) = 6.3.0
Provides: bundled(crate(pathdiff)) = 0.2.1
Provides: bundled(crate(pest)) = 2.3.1
Provides: bundled(crate(pest_derive)) = 2.3.1
Provides: bundled(crate(pest_generator)) = 2.3.1
Provides: bundled(crate(pest_meta)) = 2.3.1
Provides: bundled(crate(pin-utils)) = 0.1.0
Provides: bundled(crate(pretty_env_logger)) = 0.4.0
Provides: bundled(crate(proc-macro-error)) = 1.0.4
Provides: bundled(crate(proc-macro-error-attr)) = 1.0.4
Provides: bundled(crate(proc-macro2)) = 1.0.43
Provides: bundled(crate(quick-error)) = 1.2.3
Provides: bundled(crate(quote)) = 1.0.21
Provides: bundled(crate(regex)) = 1.6.0
Provides: bundled(crate(regex-syntax)) = 0.6.27
Provides: bundled(crate(ron)) = 0.7.1
Provides: bundled(crate(rust-ini)) = 0.18.0
Provides: bundled(crate(ryu)) = 1.0.11
Provides: bundled(crate(serde)) = 1.0.144
Provides: bundled(crate(serde_derive)) = 1.0.144
Provides: bundled(crate(serde_json)) = 1.0.85
Provides: bundled(crate(sha1)) = 0.10.5
Provides: bundled(crate(strsim)) = 0.10.0
Provides: bundled(crate(syn)) = 1.0.100
Provides: bundled(crate(termcolor)) = 1.1.3
Provides: bundled(crate(thiserror)) = 1.0.35
Provides: bundled(crate(thiserror-impl)) = 1.0.35
Provides: bundled(crate(toml)) = 0.5.9
Provides: bundled(crate(typenum)) = 1.15.0
Provides: bundled(crate(ucd-trie)) = 0.1.5
Provides: bundled(crate(unicode-ident)) = 1.0.4
Provides: bundled(crate(version_check)) = 0.9.4
Provides: bundled(crate(wasi)) = 0.11.0+wasi_snapshot_preview1
Provides: bundled(crate(winapi)) = 0.3.9
Provides: bundled(crate(winapi-i686-pc-windows-gnu)) = 0.4.0
Provides: bundled(crate(winapi-util)) = 0.1.5
Provides: bundled(crate(winapi-x86_64-pc-windows-gnu)) = 0.4.0
Provides: bundled(crate(yaml-rust)) = 0.4.5

%description
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
rustflags = %{__global_rustflags_toml}
 
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
  dist/systemd/system/*.service
# add config
mkdir -p %{buildroot}%{_exec_prefix}/lib/motd.d/
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/check/required.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/check/wanted.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/green.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/red.d
mkdir -p %{buildroot}%{_prefix}/lib/%{name}/check/required.d
mkdir    %{buildroot}%{_prefix}/lib/%{name}/check/wanted.d
mkdir    %{buildroot}%{_prefix}/lib/%{name}/green.d
mkdir    %{buildroot}%{_prefix}/lib/%{name}/red.d
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_unitdir}/greenboot-healthcheck.service.d
mkdir -p %{buildroot}%{_tmpfilesdir}

%post
%systemd_post greenboot.service
%systemd_post greenboot-trigger.service

%preun
%systemd_preun greenboot.service
%systemd_preun greenboot-trigger.service

%postun
%systemd_postun greenboot.service
%systemd_postun greenboot-trigger.service

%files
%doc README.md
%license LICENSE
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}
%{_unitdir}/greenboot.service
%{_unitdir}/greenboot-trigger.service
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
