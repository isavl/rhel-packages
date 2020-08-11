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

%global goipath github.com/coredns/coredns

%global godocs README.md
%global golicenses LICENSE

%global commit f59c03d09c3a3a12f571ad1087b979325f3dae30
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
## corends
##

Name: coredns

Version: 1.7.0

Release: 1%{?dist}

Summary: DNS and service discovery

License: APL 2.0

URL: https://coredns.io

Source0: coredns-%{version}.tar.gz

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)
BuildRequires: systemd

%description
CoreDNS is different from other DNS servers, such as (all excellent) BIND,
Knot, PowerDNS and Unbound (technically a resolver, but still worth a
mention), because it is very flexible, and almost all functionality is
outsourced into plugins. Plugins can be stand-alone or work together to
perform a "DNS function".

%gopkg

###############################################################################
# Prepare
###############################################################################

%prep

%autosetup %{?autosetup_opts}

%goprep -e -k -s %{_builddir}/coredns-%{version}

###############################################################################
# Build
###############################################################################

%build

export LDFLAGS="\
    -X '%{goipath}/coremain.GitCommit=%{commit}' "

%gobuild -o %{gobuilddir}/bin/coredns %{goipath}

###############################################################################
# Install
###############################################################################

%install

install -d %{buildroot}/%{_bindir}
install -p -m 0755 %{gobuilddir}/bin/coredns %{buildroot}/%{_bindir}/coredns

install -d -m 755 %{buildroot}/%{_tmpfilesdir}

install -d -m 755 %{buildroot}/%{_unitdir}

install -d -m 750 %{buildroot}/%{_sharedstatedir}/coredns

install -d -m 755 %{buildroot}/%{_localstatedir}/log/coredns

%gopkginstall

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

getent group coredns >/dev/null || groupadd -r coredns
getent passwd coredns >/dev/null || useradd -r -d %{_sharedstatedir}/coredns -G coredns -g coredns -s %{_sbindir}/nologin coredns

%post

%preun

%postun

###############################################################################
# Files
###############################################################################

##
## coredns
##

%files

%dir %attr(750,coredns,coredns) %{_sharedstatedir}/coredns
%dir %attr(755,coredns,coredns) %{_localstatedir}/log/coredns

%{_bindir}/*

%doc README.md

%license LICENSE

%gopkgfiles

###############################################################################
# Changelog
###############################################################################

%changelog

* Tue Aug 11 2020 Igor Savlook <isav@alzari.pw> 1.7.0-1
- initializing rpm packaging
