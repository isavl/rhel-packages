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

%global goipath github.com/cloudnativelabs/kube-router

%global godocs CONTRIBUTING.md README.md
%global golicenses LICENSE

%global commit 6af898bc8d39648cf4f238542e00b411afa33162
%global shortcommit %{lua:print(string.sub(rpm.expand("%{?commit}"), 1, 7))}

%global debug_package %{nil}

%if %{with_patches}
%global autosetup_opts -p1
%else
%global autosetup_opts -N
%endif

##
## Rpmbuild variables.
##

###############################################################################
# Packages
###############################################################################

##
## kube-router
##

Name: kube-router

Version: 1.0.1

Release: 1%{?dist}

Summary: A turnkey solution for kubernetes networking

License: ASL 2.0

URL: https://kube-router.io

Source0: kube-router-%{version}.tar.gz

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)
BuildRequires: systemd

Requires: conntrack-tools
Requires: iproute
Requires: ipset
Requires: iptables
Requires: ipvsadm
Requires: kmod

%description
With all features enabled, kube-router is a lean yet powerful alternative to
several network components used in typical kubernetes clusters. All this from
a single DaemonSet/Binary. It doesn't get any easier.

%gopkg

###############################################################################
# Prepare
###############################################################################

%prep

%autosetup %{?autosetup_opts}

%goprep -e -k -s %{_builddir}/kube-router-%{version}

###############################################################################
# Build
###############################################################################

%build

export LDFLAGS="\
    -X '%{goipath}/pkg/cmd.buildDate=$(date -u +%FT%T%z)' \
    -X '%{goipath}/pkg/cmd.version=%{version}' "

%gobuild -o %{gobuilddir}/bin/kube-router %{goipath}/cmd/kube-router

###############################################################################
# Install
###############################################################################

%install

install -d %{buildroot}/%{_bindir}
install -p -m 0755 %{gobuilddir}/bin/kube-router %{buildroot}/%{_bindir}/kube-router

install -d -m 755 %{buildroot}/%{_tmpfilesdir}

install -d -m 755 %{buildroot}/%{_unitdir}

install -d -m 750 %{buildroot}/%{_sharedstatedir}/kube-router

install -d -m 755 %{buildroot}/%{_localstatedir}/log/kube-router

%gopkginstall

###############################################################################
# Check
###############################################################################

%check

###############################################################################
# Post
###############################################################################

##
## kube-router
##

%pre

%post

%preun

%postun

###############################################################################
# Files
###############################################################################

##
## kube-router
##

%files

%dir %attr(750,root,root) %{_sharedstatedir}/kube-router
%dir %attr(755,root,root) %{_localstatedir}/log/kube-router

%{_bindir}/kube-router

%doc CONTRIBUTING.md README.md

%license LICENSE

%gopkgfiles

###############################################################################
# Changelog
###############################################################################

%changelog

* Sat Aug 8 2020 Igor Savlook <isav@alzari.pw> 1.0.1-1
- initializing rpm packaging
