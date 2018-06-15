%global github_owner    LorbusChris
%global github_project  greenboot
%global github_branch   master
%global build_timestamp %(date +"%Y%m%d%H%M%%S")

Name:               greenboot
Version:            0.1
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

%package notifications
Summary:            Notification scripts for greenboot

%description notifications
Notification scripts for greenboot

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
mkdir -p %{buildroot}%{_sysconfdir}/%{name}.d/check/required
install -Dpm 0755 etc/greenboot.d/check/required/00_required_scripts_start.sh %{buildroot}%{_sysconfdir}/%{name}.d/check/required/00_required_scripts_start.sh
mkdir    %{buildroot}%{_sysconfdir}/%{name}.d/check/wanted
install -Dpm 0755 etc/greenboot.d/check/wanted/00_wanted_scripts_start.sh %{buildroot}%{_sysconfdir}/%{name}.d/check/wanted/00_wanted_scripts_start.sh
mkdir    %{buildroot}%{_sysconfdir}/%{name}.d/green
install -Dpm 0755 etc/greenboot.d/green/00_greenboot_notification.sh %{buildroot}%{_sysconfdir}/%{name}.d/green/00_greenboot_notification.sh
mkdir    %{buildroot}%{_sysconfdir}/%{name}.d/red
install -Dpm 0755 etc/greenboot.d/red/00_redboot_notification.sh %{buildroot}%{_sysconfdir}/%{name}.d/red/00_redboot_notification.sh
install -Dpm 0755 etc/greenboot.d/red/98_ostree_rollback.sh %{buildroot}%{_sysconfdir}/%{name}.d/red/98_ostree_rollback.sh
install -Dpm 0755 etc/greenboot.d/red/99_reboot.sh %{buildroot}%{_sysconfdir}/%{name}.d/red/99_reboot.sh

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
%dir %{_sysconfdir}/%{name}.d/check/required
%dir %{_sysconfdir}/%{name}.d/check/wanted
%dir %{_sysconfdir}/%{name}.d/green
%dir %{_sysconfdir}/%{name}.d/red

%files notifications
%{_sysconfdir}/%{name}.d/check/required/00_required_scripts_start.sh
%{_sysconfdir}/%{name}.d/check/wanted/00_wanted_scripts_start.sh
%{_sysconfdir}/%{name}.d/green/00_greenboot_notification.sh
%{_sysconfdir}/%{name}.d/red/00_redboot_notification.sh

%files ostree
%{_sysconfdir}/%{name}.d/red/98_ostree_rollback.sh

%files reboot
%{_sysconfdir}/%{name}.d/red/99_reboot.sh

%changelog
* Thu Jun 14 2018 Christian Glombek <lorbus@fedoraproject.org> - 0.1-1
- Version 0.1
