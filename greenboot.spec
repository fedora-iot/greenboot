%global github_owner    LorbusChris
%global github_project  greenboot
%global github_branch   master
%global build_timestamp %(date +"%Y%m%d%H%M%%S")

Name:               greenboot
Version:            canary
Release:            %{build_timestamp}%{?dist}
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

%prep
%setup -n %{github_project}-%{version}

%build

%install
install -Dpm 0755 %{name}.sh %{buildroot}%{_libexecdir}/%{name}/%{name}.sh
install -Dpm 0644 usr/lib/systemd/system/healthcheck.target %{buildroot}%{_unitdir}/healthcheck.target
install -Dpm 0644 usr/lib/systemd/system/healthcheck-script-runner.service %{buildroot}%{_unitdir}/healthcheck-script-runner.service
install -Dpm 0644 usr/lib/systemd/system/greenboot.target %{buildroot}%{_unitdir}/greenboot.target
install -Dpm 0644 usr/lib/systemd/system/greenboot-script-runner.service %{buildroot}%{_unitdir}/greenboot-script-runner.service
install -Dpm 0644 usr/lib/systemd/system/redboot.target %{buildroot}%{_unitdir}/redboot.target
install -Dpm 0644 usr/lib/systemd/system/redboot-script-runner.service %{buildroot}%{_unitdir}/redboot-script-runner.service
install -Dpm 0755 etc/greenboot.d/check/required/00_required_scripts_start.sh %{buildroot}%{_sysconfdir}/%{name}.d/check/required/00_required_scripts_start.sh
install -Dpm 0755 etc/greenboot.d/check/wanted/00_wanted_scripts_start.sh %{buildroot}%{_sysconfdir}/%{name}.d/check/wanted/00_wanted_scripts_start.sh
install -Dpm 0755 etc/greenboot.d/green/00_greenboot_notification.sh %{buildroot}%{_sysconfdir}/%{name}.d/green/00_greenboot_notification.sh
install -Dpm 0755 etc/greenboot.d/red/00_redboot_notification.sh %{buildroot}%{_sysconfdir}/%{name}.d/red/00_redboot_notification.sh

%check
# TODO

%files
%doc README.md
%license LICENSE
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}.sh
%{_unitdir}/healthcheck.target
%{_unitdir}/healthcheck-script-runner.service
%{_unitdir}/greenboot.target
%{_unitdir}/greenboot-script-runner.service
%{_unitdir}/redboot.target
%{_unitdir}/redboot-script-runner.service
%{_sysconfdir}/%{name}.d/check/required/00_required_scripts_start.sh
%{_sysconfdir}/%{name}.d/check/wanted/00_wanted_scripts_start.sh
%{_sysconfdir}/%{name}.d/green/00_greenboot_notification.sh
%{_sysconfdir}/%{name}.d/red/00_redboot_notification.sh

%changelog
* Wed Jun 06 2018 Christian Glombek <lorbus@fedoraproject.org> - pre-alpha
- Add greenboot-script-runner
- Fix unit files by adding [Install] section
- Update README.md

* Mon Jun 04 2018 Christian Glombek <lorbus@fedoraproject.org> - pre-alpha
- Add greenboot.target, remove greenboot-failure.service
- Use bash script for greenboot.service
- Add services to run required/wanted scripts

* Wed May 23 2018 Christian Glombek <lorbus@fedoraproject.org> - pre-alpha
- Initial RPM Spec
