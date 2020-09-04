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

%global goipath helm.sh/helm/v3

%global commit 7ba38da8aa892192b68ea549c1c76ae53bffde49
%global shortcommit %{lua:print(string.sub(rpm.expand("%{?commit}"), 1, 7))}

##
## Rpmbuild variables.
##

%global debug_package %{nil}

###############################################################################
# Packages
###############################################################################

##
## helm
##

Name: helm

Version: 3.3.0

Release: 1%{?dist}

Summary: A tool that streamlines installing and managing kubernetes applications

License: APL 2.0

URL: https://helm.sh

Source0: helm-%{version}.tar.gz

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)

%description
Helm helps you manage Kubernetes applications - Helm Charts help you define,
install, and upgrade even the most complex Kubernetes application.
Charts are easy to create, version, share, and publish - so start using Helm
and stop the copy-and-paste.

###############################################################################
# Prepare
###############################################################################

%prep

%if %{with_patches}
%autosetup -p1
%else
%autosetup -N
%endif

%goprep -e -k -s %{_builddir}/helm-%{version}

###############################################################################
# Build
###############################################################################

%build

export LDFLAGS="\
    -X '%{goipath}/v3/internal/version.metadata=' \
    -X '%{goipath}/v3/internal/version.gitCommit=%{commit}' \
    -X '%{goipath}/v3/internal/version.gitTreeState=clean' \
    -X '%{goipath}/v3/internal/version.version=%{version}' "

%gobuild -o %{gobuilddir}/bin/helm %{goipath}/cmd/helm

###############################################################################
# Install
###############################################################################

%install

install -d %{buildroot}/%{_bindir}
install -p -m 0755 %{gobuilddir}/bin/helm %{buildroot}/%{_bindir}/helm

###############################################################################
# Check
###############################################################################

%check

###############################################################################
# Post
###############################################################################

##
## helm
##

%pre

%post

%preun

%postun

###############################################################################
# Files
###############################################################################

##
## helm
##

%files

%{_bindir}/helm

%doc README.md

%license LICENSE

###############################################################################
# Changelog
###############################################################################

%changelog

* Thu Aug 13 2020 Igor Savlook <isav@alzari.pw> 3.3.0-1
- initializing rpm packaging
