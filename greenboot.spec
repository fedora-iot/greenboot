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
install -Dpm 0644 %{name}.service %{buildroot}%{_unitdir}/%{name}-requires.service
install -Dpm 0644 %{name}.service %{buildroot}%{_unitdir}/%{name}-wants.service
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/requires
mkdir    %{buildroot}%{_sysconfdir}/%{name}/wants
install -Dpm 0755 %{name}.sh %{buildroot}%{_libexecdir}/%{name}/%{name}.sh

%check
# TODO

%files
%doc README.md
%license LICENSE
%{_unitdir}/%{name}.target
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-requires.service
%{_unitdir}/%{name}-wants.service
%dir %{_sysconfdir}/%{name}/requires
%dir %{_sysconfdir}/%{name}/wants
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/%{name}.sh

%changelog
* Mon Jun 04 2018 Christian Glombek <lorbus@fedoraproject.org> - pre-alpha
- Add greenboot.target, remove greenboot-failure.service
- Use bash script for greenboot.service
- Add services to run required/wanted scripts

* Wed May 23 2018 Christian Glombek <lorbus@fedoraproject.org> - pre-alpha
- Initial RPM Spec
