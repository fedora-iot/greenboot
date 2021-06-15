Name:               greenboot-failing-unit
Version:            1.0
Release:            1%{?dist}
Summary:            Failing healthcheck unit for testing greenboot red status
License:            LGPLv2+
URL:                https://github.com/%{repo_owner}/%{repo_name}
BuildArch:          noarch
Requires:           greenboot

%description
%{summary}.

%prep

%build

%install
mkdir -p    %{buildroot}%{_sysconfdir}/greenboot/check/required.d/
cat <<EOF > %{buildroot}%{_sysconfdir}/greenboot/check/required.d/10_failing_check.sh
#!/bin/bash
set -euo pipefail
echo "This is a failing script"
exit 1
EOF

%post

%preun

%postun

%files
%{_sysconfdir}/greenboot/check/required.d/10_failing_check.sh

%changelog
* Wed Feb 13 2019 Christian Glombek <lorbus@fedoraproject.org> - 1.0-1
- Initial RPM Spec
