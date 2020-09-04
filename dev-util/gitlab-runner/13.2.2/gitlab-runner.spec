###############################################################################
# General
###############################################################################

##
## Build options enabled by default.
##
## Use either --without <opt> in mock/rpmbuild/etc. command or force values
## to 0 in here to disable them.
##
## Example:
##   %%global with_example %%{?_without_example: 0} %%{?!_without_example: 1}
##

# Build with patches.
%global with_patches %{?_without_patches: 0} %{?!_without_patches: 1}

##
## Build options disabled by default.
##
## Use either --with <opt> in mock/rpmbuild/etc. command or force values
## to 1 in here to enable them.
##
## Example:
##   %%global with_example %%{?_with_example: 1} %%{?!_with_example: 0}
##

##
## Default variables.
##

%global goipath gitlab.com/gitlab-org/gitlab-runner

%global commit a784a4b19be0c0d2bc14e7be58693a259b4c5d8a
%global shortcommit %{lua:print(string.sub(rpm.expand("%{?commit}"), 1, 7))}

##
## Rpmbuild variables.
##

%global debug_package %{nil}

###############################################################################
# Packages
###############################################################################

##
## gitlab-runner
##

Name: gitlab-runner

Version: 13.2.2

Release: 1%{?dist}

Summary: Runs tasks and sends the results to GitLab

License: MIT

URL: https://gitlab.com

Source0: gitlab-runner-%{version}.tar.gz

Source10: gitlab-runner.service

Source20: config.toml

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)
BuildRequires: systemd

%description
It runs tasks and sends the results to GitLab. GitLab-CI is the open-source
continuous integration service included with GitLab that
coordinates the testing. The old name of this project was
GitLab CI Multi Runner but please use "GitLab Runner" (without CI)
from now on.

##
## gitlab-runner-helper
##

%package helper

Summary: Helper for gitlab runner

%description helper
Helper for gitlab runner.

###############################################################################
# Prepare
###############################################################################

%prep

%if %{with_patches}
%autosetup -p1
%else
%autosetup -N
%endif

%goprep -e -k -s %{_builddir}/gitlab-runner-%{version}

###############################################################################
# Build
###############################################################################

%build

export LDFLAGS="\
    -X '%{goipath}/common.NAME=gitlab-runner' \
    -X '%{goipath}/common.VERSION=%{version}' \
    -X '%{goipath}/common.REVISION=%{commit}' \
    -X '%{goipath}/common.BRANCH=v%{version}' \
    -X '%{goipath}/common.BUILT=$(date -u +%FT%T%z)' "

%gobuild -o %{gobuilddir}/bin/gitlab-runner %{goipath}
%gobuild -o %{gobuilddir}/bin/gitlab-runner-helper %{goipath}/apps/gitlab-runner-helper

###############################################################################
# Install
###############################################################################

%install

install -d -m 755 %{buildroot}/%{_sysconfdir}/gitlab-runner
install -p -m 644 %{SOURCE20} %{buildroot}/%{_sysconfdir}/gitlab-runner/config.toml

install -d %{buildroot}/%{_bindir}
install -p -m 755 %{gobuilddir}/bin/gitlab-runner %{buildroot}/%{_bindir}/gitlab-runner
install -p -m 755 %{gobuilddir}/bin/gitlab-runner-helper %{buildroot}/%{_bindir}/gitlab-runner-helper

install -d -m 755 %{buildroot}/%{_unitdir}
install -p -m 644 %{SOURCE10} %{buildroot}/%{_unitdir}/gitlab-runner.service

install -d -m 750 %{buildroot}/%{_sharedstatedir}/gitlab-runner

install -d -m 755 %{buildroot}/%{_localstatedir}/log/gitlab-runner

###############################################################################
# Check
###############################################################################

%check

###############################################################################
# Post
###############################################################################

##
## ${pkg_name}
##

%pre

getent group gitlab-runner >/dev/null || groupadd -r gitlab-runner
getent passwd gitlab-runner >/dev/null || useradd -r -d %{_sharedstatedir}/gitlab-runner -G gitlab-runner -g gitlab-runner -s %{_sbindir}/nologin gitlab-runner

%post

%systemd_post gitlab-runner.service

%preun

%systemd_preun gitlab-runner.service

%postun

%systemd_postun_with_restart gitlab-runner.service

###############################################################################
# Files
###############################################################################

##
## gitlab-runner
##

%files

%dir %attr(750,gitlab-runner,gitlab-runner) %{_sharedstatedir}/gitlab-runner
%dir %attr(755,gitlab-runner,gitlab-runner) %{_localstatedir}/log/gitlab-runner

%config(noreplace) %{_sysconfdir}/gitlab-runner/*

%{_bindir}/gitlab-runner

%{_unitdir}/gitlab-runner.service

%doc CHANGELOG.md CONTRIBUTING.md NOTICE README.md

%license LICENSE

##
## gitlab-runner-helper
##

%files helper

%{_bindir}/gitlab-runner-helper

%doc CHANGELOG.md CONTRIBUTING.md NOTICE README.md

%license LICENSE

###############################################################################
# Changelog
###############################################################################

%changelog

* Tue Aug 11 2020 Igor Savlook <isav@alzari.pw> - 13.2.2-1
- initializing rpm packaging
