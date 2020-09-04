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

##
## Rpmbuild variables.
##

%global debug_package %{nil}

%global __strip /bin/true

###############################################################################
# Packages
###############################################################################

##
## fpc-bootstrap
##

Name: fpc-bootstrap

Version: 3.2.0

Release: 1%{?dist}

Summary: Free Pascal Compiler - bootstrap

License: GPLv2+ and LGPLv2+ with exceptions

URL: http://www.freepascal.org

Source0: fpc-bootstrap-%{version}.tar.gz

%description
Package contains the fpc binaries for various architectures used for bootstrap
fpc.

###############################################################################
# Prepare
###############################################################################

%prep

%autosetup -N

###############################################################################
# Build
###############################################################################

%build

###############################################################################
# Install
###############################################################################

%install

install -d %{buildroot}/%{_bindir}
install -p -m 755 ppc* %{buildroot}/%{_bindir}/

###############################################################################
# Check
###############################################################################

%check

###############################################################################
# Post
###############################################################################

##
## fpc-bootstrap
##

%pre

%post

%preun

%postun

###############################################################################
# Files
###############################################################################

##
## fpc-bootstrap
##

%files

%{_bindir}/*

###############################################################################
# Changelog
###############################################################################

%changelog

* Wed Sep 2 2020 Igor Savlook <isav@alzari.pw> - 3.2.0-1
- initializing rpm packaging
