%global github_owner		LorbusChris
%global github_project	greenboot
%global github_branch 	master
%global build_timestamp	%(date +"%Y%m%d%H%M%%S")

Name:								greenboot
Version:						canary
Release:						%{build_timestamp}%{?dist}
Summary:						Generic Health Check Framework for systemd
License:						LGPLv2+
URL:								https://github.com/%{github_owner}/%{github_project}
Source0:						https://github.com/%{github_owner}/%{github_project}/archive/%{github_branch}.tar.gz

BuildArch:					noarch
BuildRequires:			systemd
%{?systemd_requires}
Requires:						systemd

%description
%{summary}.

%prep
%setup -n %{github_project}-%{version}

%build

%install
install -Dpm 0644 greenboot.service %{buildroot}%{_unitdir}/greenboot.service
install -Dpm 0644 greenboot-failure.service %{buildroot}%{_unitdir}/greenboot-failure.service
mkdir -p %{buildroot}%{_sysconfdir}/systemd/system/greenboot.service.requires
mkdir    %{buildroot}%{_sysconfdir}/systemd/system/greenboot.service.wants

%check
# TODO

%files
%doc README.md
%license LICENSE
%{_unitdir}/greenboot.service
%{_unitdir}/greenboot-failure.service
%dir %{_sysconfdir}/systemd/system/greenboot.service.requires
%dir %{_sysconfdir}/systemd/system/greenboot.service.wants

%changelog
* Wed May 23 2018 Christian Glombek <lorbus@fedoraproject.org> - pre-alpha
- Initial RPM Spec
