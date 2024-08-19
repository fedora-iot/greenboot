%global debug_package %{nil}

Name:               greenboot
Version:            0.15.5
Release:            1%{?dist}
Summary:            Generic Health Check Framework for systemd
License:            LGPLv2+

%global repo_owner  fedora-iot
%global repo_name   %{name}
%global repo_tag    v%{version}

URL:                https://github.com/%{repo_owner}/%{repo_name}
Source0:            https://github.com/%{repo_owner}/%{repo_name}/archive/%{repo_tag}.tar.gz

ExcludeArch: s390x
BuildRequires:      systemd-rpm-macros
%{?systemd_requires}
Requires:           systemd >= 240
Requires:           grub2-tools-minimal
Requires:           rpm-ostree
Requires:           bootupd
# PAM is required to programatically read motd messages from /etc/motd.d/*
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

%description
%{summary}.

%package default-health-checks
Summary:            Series of optional and curated health checks
Requires:           %{name} = %{version}-%{release}
Requires:           util-linux
Requires:           jq
Provides:           greenboot-update-platforms-check
Obsoletes:          greenboot-update-platforms-check <= 0.12.0

%description default-health-checks
%{summary}.

%prep
%setup -q

%build

%install
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
install -D -t %{buildroot}%{_prefix}/lib/bootupd/grub2-static/configs.d grub2/greenboot.cfg
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_unitdir}/greenboot-healthcheck.service.d
mkdir -p %{buildroot}%{_tmpfilesdir}
install -DpZm 0755 usr/libexec/greenboot/* %{buildroot}%{_libexecdir}/%{name}
install -DpZm 0644 usr/lib/motd.d/boot-status %{buildroot}%{_exec_prefix}/lib/motd.d/boot-status
install -DpZm 0644 usr/lib/systemd/system/greenboot-healthcheck.service.d/10-network-online.conf %{buildroot}%{_unitdir}/greenboot-healthcheck.service.d/10-network-online.conf
install -DpZm 0644 usr/lib/systemd/system/*.target %{buildroot}%{_unitdir}
install -DpZm 0644 usr/lib/systemd/system/*.service %{buildroot}%{_unitdir}
install -DpZm 0644 usr/lib/tmpfiles.d/greenboot-status-motd.conf %{buildroot}%{_tmpfilesdir}/greenboot-status-motd.conf
install -DpZm 0755 usr/lib/greenboot/check/required.d/* %{buildroot}%{_prefix}/lib/%{name}/check/required.d
install -DpZm 0755 usr/lib/greenboot/check/wanted.d/* %{buildroot}%{_prefix}/lib/%{name}/check/wanted.d
install -DpZm 0644 etc/greenboot/greenboot.conf %{buildroot}%{_sysconfdir}/%{name}/greenboot.conf

%post
%systemd_post greenboot-healthcheck.service
%systemd_post greenboot-loading-message.service
%systemd_post greenboot-task-runner.service
%systemd_post redboot-task-runner.service
%systemd_post redboot.target
%systemd_post greenboot-status.service
%systemd_post greenboot-grub2-set-counter.service
%systemd_post greenboot-grub2-set-success.service
%systemd_post greenboot-rpm-ostree-grub2-check-fallback.service
%systemd_post redboot-auto-reboot.service

%post default-health-checks
%systemd_post greenboot-loading-message.service

%preun
%systemd_preun greenboot-healthcheck.service
%systemd_preun greenboot-loading-message.service
%systemd_preun greenboot-task-runner.service
%systemd_preun redboot-task-runner.service
%systemd_preun redboot.target
%systemd_preun greenboot-status.service
%systemd_preun greenboot-grub2-set-counter.service
%systemd_preun greenboot-grub2-set-success.service
%systemd_preun greenboot-rpm-ostree-grub2-check-fallback.service

%preun default-health-checks
%systemd_preun greenboot-loading-message.service

%postun
%systemd_postun greenboot-healthcheck.service
%systemd_postun greenboot-loading-message.service
%systemd_postun greenboot-task-runner.service
%systemd_postun redboot-task-runner.service
%systemd_postun redboot.target
%systemd_postun greenboot-status.service
%systemd_postun greenboot-grub2-set-counter.service
%systemd_postun greenboot-grub2-set-success.service
%systemd_postun greenboot-rpm-ostree-grub2-check-fallback.service

%postun default-health-checks
%systemd_postun greenboot-loading-message.service

%files
%doc README.md
%license LICENSE
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}
%{_libexecdir}/%{name}/greenboot-loading-message
%{_unitdir}/greenboot-healthcheck.service
%{_unitdir}/greenboot-loading-message.service
%{_unitdir}/greenboot-task-runner.service
%{_unitdir}/redboot-task-runner.service
%{_unitdir}/redboot.target
%dir %{_prefix}/lib/%{name}
%dir %{_prefix}/lib/%{name}/check
%dir %{_prefix}/lib/%{name}/check/required.d
%{_prefix}/lib/%{name}/check/required.d/00_required_scripts_start.sh
%dir %{_prefix}/lib/%{name}/check/wanted.d
%{_prefix}/lib/%{name}/check/wanted.d/00_wanted_scripts_start.sh
%dir %{_prefix}/lib/%{name}/green.d
%dir %{_prefix}/lib/%{name}/red.d
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/check
%dir %{_sysconfdir}/%{name}/check/required.d
%dir %{_sysconfdir}/%{name}/check/wanted.d
%dir %{_sysconfdir}/%{name}/green.d
%dir %{_sysconfdir}/%{name}/red.d
%{_exec_prefix}/lib/motd.d/boot-status
%{_libexecdir}/%{name}/greenboot-status
%{_tmpfilesdir}/greenboot-status-motd.conf
%{_prefix}/lib/bootupd/grub2-static/configs.d/*.cfg
%{_unitdir}/greenboot-status.service
%{_libexecdir}/%{name}/greenboot-grub2-set-counter
%{_libexecdir}/%{name}/greenboot-grub2-set-success
%{_libexecdir}/%{name}/greenboot-boot-remount
%{_unitdir}/greenboot-grub2-set-success.service
%{_unitdir}/greenboot-grub2-set-counter.service
%{_libexecdir}/%{name}/greenboot-rpm-ostree-grub2-check-fallback
%{_unitdir}/greenboot-rpm-ostree-grub2-check-fallback.service
%{_libexecdir}/%{name}/redboot-auto-reboot
%{_unitdir}/redboot-auto-reboot.service
%{_sysconfdir}/%{name}/greenboot.conf

%files default-health-checks
%{_prefix}/lib/%{name}/check/required.d/01_repository_dns_check.sh
%{_prefix}/lib/%{name}/check/wanted.d/01_update_platforms_check.sh
%{_unitdir}/greenboot-healthcheck.service.d/10-network-online.conf
%{_prefix}/lib/%{name}/check/required.d/02_watchdog.sh

%changelog
* Fri Aug 16 2024 saypaul <paul.sayan@gmail.com> - 0.15.5-1
- The 0.15.5 release
- Auto-detect image type and use correct rollback
- Support for read only /boot mount
- Warn users of missing disabled healthchecks
- Add feature to disable healthchecks

* Fri Feb 17 2023 Paul Whalen <pwhalen@fedoraproject.org> - 0.15.4-1
- The 0.15.4 release
- Fix update_platforms_check script 

* Mon Nov 28 2022 Paul Whalen <pwhalen@fedoraproject.org> - 0.15.3-1
- The 0.15.3 release
- revert service-monitor

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
