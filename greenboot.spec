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
install -Dpm 0644 %{name}.target %{buildroot}%{_unitdir}/%{name}.target
install -Dpm 0644 %{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -Dpm 0644 %{name}.service %{buildroot}%{_unitdir}/%{name}-script-runner.service
install -Dpm 0755 %{name}.sh %{buildroot}%{_libexecdir}/%{name}/%{name}.sh
install -Dpm 0755 %{name}.sh %{buildroot}%{_libexecdir}/%{name}/%{name}-script-runner.sh
mkdir -p %{buildroot}%{_sysconfdir}/%{name}.d/required
mkdir    %{buildroot}%{_sysconfdir}/%{name}.d/wanted

%check
# TODO

%files
%doc README.md
%license LICENSE
%{_unitdir}/%{name}.target
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-script-runner.service
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}.sh
%{_libexecdir}/%{name}/%{name}-script-runner.sh
%dir %{_sysconfdir}/%{name}.d/required
%dir %{_sysconfdir}/%{name}.d/wanted

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
