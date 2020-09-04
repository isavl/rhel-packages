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

# Verbose make, i.e. no silent rules and V=1.
%global with_verbose %{?_without_verbose: 0} %{?!_without_verbose: 1}

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

%if %{with_verbose}
%global make_opts V=1
%else
%global make_opts -s
%endif

%global docdir isl-%{version}

%global gdbprettydir %{_datadir}/gdb/auto-load/%{_libdir}

%global libmajor 15
%global libversion %{libmajor}.1.1

%global old_version 0.14
%global old_libmajor 13
%global old_libversion %{old_libmajor}.1.0

##
## Rpmbuild variables.
##

###############################################################################
# Packages
###############################################################################

##
## isl
##

Name: isl

Version: 0.16.1

Release: 1%{?dist}

Summary: Integer point manipulation library

License: MIT

URL: http://isl.gforge.inria.fr

Source0: isl-%{version}.tar.gz
Source1: isl-%{old_version}.tar.gz

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gcc
BuildRequires: gmp-devel
BuildRequires: libtool
BuildRequires: make
BuildRequires: pkgconfig

Provides: isl = %{old_version}

%description
isl is a library for manipulating sets and relations of integer points
bounded by linear constraints.  Supported operations on sets include
intersection, union, set difference, emptiness check, convex hull,
(integer) affine hull, integer projection, computing the lexicographic
minimum using parametric integer programming, coalescing and parametric
vertex enumeration.  It also includes an ILP solver based on generalized
basis reduction, transitive closures on maps (which may encode infinite
graphs), dependence analysis and bounds on piecewise step-polynomials.

##
## isl-devel
##

%package devel

Summary: Development for building integer point manipulation library

Requires: gmp-devel%{?_isa}
Requires: isl%{?_isa} == %{version}-%{release}

%description devel
isl is a library for manipulating sets and relations of integer points
bounded by linear constraints.  Supported operations on sets include
intersection, union, set difference, emptiness check, convex hull,
(integer) affine hull, integer projection, computing the lexicographic
minimum using parametric integer programming, coalescing and parametric
vertex enumeration.  It also includes an ILP solver based on generalized
basis reduction, transitive closures on maps (which may encode infinite
graphs), dependence analysis and bounds on piecewise step-polynomials.


###############################################################################
# Prepare
###############################################################################

%prep

%setup -a 1 -q -n isl -c

###############################################################################
# Build
###############################################################################

%build

pushd isl-%{old_version}
autoreconf -f -i -v
%configure
make %{?_smp_mflags} %{?make_opts}
popd

pushd isl-%{version}
autoreconf -f -i -v
%configure
make %{?_smp_mflags} %{?make_opts}
popd

###############################################################################
# Install
###############################################################################

%install

pushd isl-%{old_version}
make %{?make_opts} DESTDIR=%{buildroot} install-libLTLIBRARIES
popd

pushd isl-%{version}
make %{?make_opts} DESTDIR=%{buildroot} install
rm -f %{buildroot}/%{_libdir}/libisl.a
rm -f %{buildroot}/%{_libdir}/libisl.la
mkdir -p %{buildroot}/%{_datadir}
mkdir -p %{buildroot}/%{gdbprettydir}
mv %{buildroot}/%{_libdir}/*-gdb.py* %{buildroot}/%{gdbprettydir}
popd

###############################################################################
# Check
###############################################################################

%check

###############################################################################
# Post
###############################################################################

##
## isl
##

%pre

%post

/sbin/ldconfig

%preun

%postun

/sbin/ldconfig

###############################################################################
# Files
###############################################################################

##
## isl
##

%files

%{_libdir}/libisl.so.%{libmajor}
%{_libdir}/libisl.so.%{libversion}
%{_libdir}/libisl.so.%{old_libmajor}
%{_libdir}/libisl.so.%{old_libversion}

%{gdbprettydir}/*

%doc %{docdir}/AUTHORS %{docdir}/ChangeLog %{docdir}/README

%license %{docdir}/LICENSE

##
## isl-devel
##

%files devel

%{_includedir}/*

%{_libdir}/libisl.so
%{_libdir}/pkgconfig/isl.pc

%doc %{docdir}/doc/manual.pdf

###############################################################################
# Changelog
###############################################################################

%changelog

* Thu Sep 3 2020 Igor Savlook <isav@alzari.pw> - 0.16.1-1
- initializing rpm packaging
