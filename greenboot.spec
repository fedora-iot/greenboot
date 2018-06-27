%global github_owner    LorbusChris
%global github_project  greenboot
%global github_branch   master
%global build_timestamp %(date +"%Y%m%d%H%M%%S")

Name:               greenboot
Version:            0.2
Release:            1%{?dist}
Summary:            Generic Health Check Framework for systemd
License:            LGPLv2+
URL:                https://github.com/%{github_owner}/%{github_project}
Source0:            https://github.com/%{github_owner}/%{github_project}/archive/%{github_branch}.tar.gz

BuildArch:          noarch
BuildRequires:      systemd
%{?systemd_requires}
Requires:           systemd

%description
%{summary}.

%package motd
Summary:            MotD updater for greenboot
Requires:           pam >= 1.3.1

%description motd
Message of the Day updater for greenboot

%package ostree
Summary:            OSTree specific scripts for greenboot

%description ostree
OSTree specific scripts for greenboot

%package reboot
Summary:            Reboot on red status for greenboot

%description reboot
Reboot on red status for greenboot

%prep
%setup -n %{github_project}-%{version}

%build

%install
install -Dpm 0755 usr/libexec/greenboot/greenboot.sh %{buildroot}%{_libexecdir}/%{name}/%{name}.sh
install -Dpm 0644 usr/lib/systemd/system/greenboot.target %{buildroot}%{_unitdir}/greenboot.target
install -Dpm 0644 usr/lib/systemd/system/greenboot-healthcheck.service %{buildroot}%{_unitdir}/greenboot-healthcheck.service
install -Dpm 0644 usr/lib/systemd/system/greenboot.service %{buildroot}%{_unitdir}/greenboot.service
install -Dpm 0644 usr/lib/systemd/system/redboot.service %{buildroot}%{_unitdir}/redboot.service
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/check/required.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/check/wanted.d
mkdir    %{buildroot}%{_sysconfdir}/%{name}/green.d
install -Dpm 0755 etc/greenboot/green.d/00_greenboot_motd.sh %{buildroot}%{_sysconfdir}/%{name}/green.d/00_greenboot_motd.sh
mkdir    %{buildroot}%{_sysconfdir}/%{name}/red.d
install -Dpm 0755 etc/greenboot/red.d/00_redboot_motd.sh %{buildroot}%{_sysconfdir}/%{name}/red.d/00_redboot_motd.sh
install -Dpm 0755 etc/greenboot/red.d/98_ostree_rollback.sh %{buildroot}%{_sysconfdir}/%{name}/red.d/98_ostree_rollback.sh
install -Dpm 0755 etc/greenboot/red.d/99_reboot.sh %{buildroot}%{_sysconfdir}/%{name}/red.d/99_reboot.sh
install -Dpm 0644 etc/greenboot/motd/greenboot.motd %{buildroot}%{_sysconfdir}/%{name}/motd/greenboot.motd
install -Dpm 0644 etc/greenboot/motd/redboot.motd %{buildroot}%{_sysconfdir}/%{name}/motd/redboot.motd
mkdir -p %{buildroot}/run/greenboot
mkdir -p %{buildroot}%{_sysconfdir}/motd.d
ln -snf /run/greenboot/motd %{buildroot}%{_sysconfdir}/motd.d/greenboot

%post
%systemd_post greenboot.target
%systemd_post greenboot.service
%systemd_post greenboot-healthcheck.service
%systemd_post redboot.service

%preun
%systemd_preun greenboot.target
%systemd_preun greenboot.service
%systemd_preun greenboot-healthcheck.service
%systemd_preun redboot.service

%postun
%systemd_postun_with_restart greenboot.target
%systemd_postun_with_restart greenboot.service
%systemd_postun_with_restart greenboot-healthcheck.service
%systemd_postun_with_restart redboot.service

%check
# TODO

%files
%doc README.md
%license LICENSE
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}.sh
%{_unitdir}/greenboot.target
%{_unitdir}/greenboot-healthcheck.service
%{_unitdir}/greenboot.service
%{_unitdir}/redboot.service
%dir %{_sysconfdir}/%{name}/check/required.d
%dir %{_sysconfdir}/%{name}/check/wanted.d
%dir %{_sysconfdir}/%{name}/green.d
%dir %{_sysconfdir}/%{name}/red.d

%files motd
%{_sysconfdir}/%{name}/motd/greenboot.motd
%{_sysconfdir}/%{name}/motd/redboot.motd
%{_sysconfdir}/%{name}/green.d/00_greenboot_motd.sh
%{_sysconfdir}/%{name}/red.d/00_redboot_motd.sh
%dir /run/greenboot
%config %{_sysconfdir}/motd.d/greenboot

%files ostree
%{_sysconfdir}/%{name}/red.d/98_ostree_rollback.sh

%files reboot
%{_sysconfdir}/%{name}/red.d/99_reboot.sh

%changelog
* Thu Jun 14 2018 Christian Glombek <lorbus@fedoraproject.org> - 0.1-1
- Version 0.1
