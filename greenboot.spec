Name:               greenboot
Version:            0.6
Release:            1%{?dist}
Summary:            Generic Health Check Framework for systemd
License:            LGPLv2+

%global repo_owner  LorbusChris
%global repo_name   %{name}
%global repo_tag    v%{version}

URL:                https://github.com/%{repo_owner}/%{repo_name}
Source0:            https://github.com/%{repo_owner}/%{repo_name}/archive/%{repo_tag}.tar.gz

BuildArch:          noarch
BuildRequires:      systemd-rpm-macros
%{?systemd_requires}
Requires:           systemd

%description
%{summary}.

%package status
Summary:            Message of the Day updater for greenboot
Requires:           %{name} = %{version}-%{release}
Requires:           pam >= 1.3.1-15
Requires:           openssh

%description status
%{summary}.

%package ostree-grub2
Summary:            Scripts for greenboot on OSTree-based systems using the Grub2 bootloader
Requires:           %{name} = %{version}-%{release}
Requires:           %{name}-grub2 = %{version}-%{release}
Requires:           %{name}-reboot = %{version}-%{release}

%description ostree-grub2
%{summary}.

%package grub2
Summary:            Grub2 specific scripts for greenboot
Requires:           %{name} = %{version}-%{release}

%description grub2
%{summary}.

%package reboot
Summary:            Reboot on red status for greenboot
Requires:           %{name} = %{version}-%{release}

%description reboot
%{summary}.

%prep
%setup

%build

%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/check/required.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/check/wanted.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/green.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/red.d
install -Dpm 0755 usr/libexec/greenboot/greenboot %{buildroot}%{_libexecdir}/%{name}/%{name}
install -Dpm 0755 usr/libexec/greenboot/greenboot-status %{buildroot}%{_libexecdir}/%{name}/greenboot-status
install -Dpm 0644 usr/lib/motd.d/boot-status %{buildroot}%{_exec_prefix}/lib/motd.d/boot-status
install -Dpm 0644 usr/lib/systemd/system/greenboot-healthcheck.service %{buildroot}%{_unitdir}/greenboot-healthcheck.service
install -Dpm 0644 usr/lib/systemd/system/greenboot.service %{buildroot}%{_unitdir}/greenboot.service
install -Dpm 0644 usr/lib/systemd/system/redboot.service %{buildroot}%{_unitdir}/redboot.service
install -Dpm 0644 usr/lib/systemd/system/greenboot-status.service %{buildroot}%{_unitdir}/greenboot-status.service
install -Dpm 0755 etc/greenboot/check/required.d/* %{buildroot}%{_sysconfdir}/%{name}/check/required.d
install -Dpm 0755 etc/greenboot/check/wanted.d/* %{buildroot}%{_sysconfdir}/%{name}/check/wanted.d
install -Dpm 0755 etc/greenboot/green.d/* %{buildroot}%{_sysconfdir}/%{name}/green.d
install -Dpm 0755 etc/greenboot/red.d/* %{buildroot}%{_sysconfdir}/%{name}/red.d

%post
%systemd_post greenboot.service
%systemd_post greenboot-healthcheck.service
%systemd_post redboot.service

%post status
%systemd_post greenboot-status.service

%preun
%systemd_preun greenboot.service
%systemd_preun greenboot-healthcheck.service
%systemd_preun redboot.service

%preun status
%systemd_preun greenboot-status.service

%postun
%systemd_postun_with_restart greenboot.service
%systemd_postun_with_restart greenboot-healthcheck.service
%systemd_postun_with_restart redboot.service

%postun status
%systemd_postun greenboot-status.service

%check
# TODO

%files
%doc README.md
%license LICENSE
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}
%{_unitdir}/greenboot-healthcheck.service
%{_unitdir}/greenboot.service
%{_unitdir}/redboot.service
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/check
%dir %{_sysconfdir}/%{name}/check/required.d
%{_sysconfdir}/%{name}/check/required.d/00_required_scripts_start.sh
%dir %{_sysconfdir}/%{name}/check/wanted.d
%{_sysconfdir}/%{name}/check/wanted.d/00_wanted_scripts_start.sh
%dir %{_sysconfdir}/%{name}/green.d
%dir %{_sysconfdir}/%{name}/red.d

%files status
%{_exec_prefix}/lib/motd.d/boot-status
%{_libexecdir}/%{name}/greenboot-status
%{_unitdir}/greenboot-status.service

%files ostree-grub2
%{_sysconfdir}/%{name}/green.d/01_ostree_grub2_fallback.sh

%files grub2
%{_sysconfdir}/%{name}/green.d/02_grub2_boot_success.sh

%files reboot
%{_sysconfdir}/%{name}/red.d/99_reboot.sh

%changelog
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
