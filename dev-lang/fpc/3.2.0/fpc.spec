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

# Bootstrap fpc compiler.
%global with_bootstrap %{?_with_bootstrap: 1} %{?!_with_bootstrap: 0}

##
## Default variables.
##

%if %{with_verbose}
%global make_opts V=1
%else
%global make_opts -s
%endif

%global fpc_opts -k"--build-id"
%global fpc_debug_opts -gl

%ifarch %{arm}
%global fpc_opts -dFPC_ARMHF -k"--build-id"
%global ppc_name ppcarm
%global fpc_arch_name arm
%else
%ifarch aarch64
%global ppc_name ppca64
%global fpc_arch_name aarch64
%else
%ifarch ppc64
%global ppc_name ppcppc64
%global fpc_arch_name powerpc64
%else
%ifarch ppc64le
%global fpc_opts -Cb- -Caelfv2 -k"--build-id"
%global ppc_name ppcppc64
%global fpc_arch_name powerpc64
%else
%ifarch x86_64
%global ppc_name ppcx64
%global fpc_arch_name x86_64
%else
%global ppc_name ppc386
%global fpc_arch_name i386
%endif
%endif
%endif
%endif
%endif

##
## Rpmbuild variables.
##

###############################################################################
# Packages
###############################################################################

##
## fpc
##

Name: fpc

Version: 3.2.0

Release: 1%{?dist}

Summary: Free Pascal Compiler

License: GPLv2+ and LGPLv2+ with exceptions

URL: http://www.freepascal.org

Source0: fpc-%{version}.tar.gz

Source10: default.cft
Source11: fpc.cft
Source12: fppkg.cfg

# On Fedora we do not want stabs debug-information (even on 32 bit platforms).
# https://bugzilla.redhat.com/show_bug.cgi?id=1475223
Patch0001: 0001-fpc-3.2.0-dwarf-debug.patch

# Allow for reproducible builds.
# https://bugzilla.redhat.com/show_bug.cgi?id=1778875
Patch0002: 0002-fpc-3.2.0-honor_SOURCE_DATE_EPOCH_in_date.patch

# Upstream assumes /usr/lib/ for aarch64, but Fedora uses /usr/lib64/.
Patch0003: 0003-fpc-3.2.0-fix-lib-paths-on-aarch64.patch

ExclusiveArch: %{arm} aarch64 %{ix86} ppc64le x86_64

BuildRequires: gcc
BuildRequires: glibc-devel
BuildRequires: make
BuildRequires: tetex-fonts
BuildRequires: tex(latex)
BuildRequires: tex(tex)

%if %{with_bootstrap}
BuildRequires: fpc-bootstrap >= 3.2.0
%else
BuildRequires: fpc
%endif

Requires: binutils
Requires: gpm
Requires: ncurses

%description
Free Pascal is a free 32/64bit Pascal Compiler. It comes with a run-time
library and is fully compatible with Turbo Pascal 7.0 and nearly Delphi
compatible. Some extensions are added to the language, like function
overloading and generics. Shared libraries can be linked. This package
contains the command-line compiler and utilities. Provided units are the
runtime library (RTL), free component library (FCL) and packages.

##
## fpc-doc
##

%package doc

Summary: Free Pascal Compiler - documentation and examples

%description doc
Package contains the documentation (in pdf format) and examples
of Free Pascal.

##
## fpc-src
##

%package src

Summary: Free Pascal Compiler - sources

BuildArch: noarch

%description src
Package contains the sources of Free Pascal, for documentation or
automatical code generation purposes.

###############################################################################
# Prepare
###############################################################################

%prep

%setup -q

%if %{with_patches}
pushd fpcsrc
%patch0001
%patch0002
%patch0003
popd
%endif

###############################################################################
# Build
###############################################################################

%build

mkdir -p fpc_src
cp -a fpcsrc/packages fpc_src
cp -a fpcsrc/rtl fpc_src
rm -rf fpc_src/packages/extra/amunits
rm -rf fpc_src/packages/extra/winunits

pushd fpcsrc

STARTPP=%{ppc_name}
NEWPP=$(pwd)/compiler/%{ppc_name}
DATA2INC=$(pwd)/utils/data2inc

# FIXME: -j1 as there is a race on armv7hl - seen on "missing" 'prt0.o' and 'dllprt0.o'.
make %{?make_opts} -j1 compiler_cycle FPC=${STARTPP} OPT="%{fpc_opts} %{fpc_debug_opts}"

make %{?_smp_mflags} %{?make_opts} rtl_clean rtl_smart FPC=${NEWPP} OPT="%{fpc_opts}"

make %{?_smp_mflags} %{?make_opts} packages_smart FPC=${NEWPP} OPT="%{fpc_opts}"

make %{?_smp_mflags} %{?make_opts} utils_all FPC=${NEWPP} DATA2INC=${DATA2INC} OPT="%{fpc_opts} %{fpc_debug_opts}"

popd

# FIXME: -j1 as there is a race - seen on "missing" `rtl.xct'.
make %{?make_opts} -j1 -C fpcdocs pdf FPC=${NEWPP}

###############################################################################
# Install
###############################################################################

%install

pushd fpcsrc

NEWPP=$(pwd)/compiler/%{ppc_name}
NEWFPCMAKE=$(pwd)/utils/fpcm/bin/%{fpc_arch_name}-linux/fpcmake
INSTALL_OPTS="-j1 FPC=${NEWPP} FPCMAKE=${NEWFPCMAKE} \
                INSTALL_PREFIX=%{buildroot}/%{_prefix} \
                INSTALL_LIBDIR=%{buildroot}/%{_libdir} \
                INSTALL_BASEDIR=%{buildroot}/%{_libdir}/fpc/%{version} \
                CODPATH=%{buildroot}/%{_libdir}/fpc/lexyacc \
                INSTALL_DOCDIR=%{buildroot}/%{_defaultdocdir}/fpc \
                INSTALL_BINDIR=%{buildroot}/%{_bindir}
                INSTALL_EXAMPLEDIR=%{buildroot}/%{_defaultdocdir}/fpc/examples"

make compiler_distinstall ${INSTALL_OPTS}
make rtl_distinstall ${INSTALL_OPTS}
make packages_distinstall ${INSTALL_OPTS}
make utils_distinstall ${INSTALL_OPTS}

popd

pushd install
make -C doc ${INSTALL_OPTS}
make -C man ${INSTALL_OPTS} INSTALL_MANDIR=%{buildroot}/%{_mandir}
popd

make -C fpcdocs pdfinstall ${INSTALL_OPTS}

ln -sf ../%{_lib}/fpc/%{version}/%{ppc_name} %{buildroot}/%{_bindir}/%{ppc_name}

# Remove the version number from the documentation directory.
mv %{buildroot}/%{_defaultdocdir}/fpc-%{version}/* %{buildroot}/%{_defaultdocdir}/fpc
rmdir %{buildroot}/%{_defaultdocdir}/fpc-%{version}

# Create a version independent compiler-configuration file with build-id
# enabled by default.
# For this purpose some non-default templates are used. So the samplecfg
# script could not be used and fpcmkcfg is called directly.
%{buildroot}/%{_bindir}/fpcmkcfg -p -t %{SOURCE11} -d "basepath=%{_exec_prefix}" -o %{buildroot}/%{_sysconfdir}/fpc.cfg
# Create the IDE configuration files.
%{buildroot}/%{_bindir}/fpcmkcfg -p -1 -d "basepath=%{_libdir}/fpc/\$fpcversion" -o %{buildroot}/%{_libdir}/fpc/%{version}/ide/text/fp.cfg
%{buildroot}/%{_bindir}/fpcmkcfg -p -2 -o %{buildroot}/%{_libdir}/fpc/%{version}/ide/text/fp.ini
# Create the fppkg configuration files.
%{buildroot}/%{_bindir}/fpcmkcfg -p -t %{SOURCE12} -d CompilerConfigDir=%{_sysconfdir}/fppkg -d arch=%{_arch} -o %{buildroot}/%{_sysconfdir}/fppkg.cfg
%{buildroot}/%{_bindir}/fpcmkcfg -p -t %{SOURCE10} -d fpcbin=%{_bindir}/fpc -d GlobalPrefix=%{_exec_prefix} -d lib=%{_lib} -o %{buildroot}/%{_sysconfdir}/fppkg/default_%{_arch}

# Include the COPYING-information for the compiler/rtl/fcl in the
# documentation.
cp -a fpcsrc/compiler/COPYING.txt %{buildroot}/%{_defaultdocdir}/fpc/COPYING
cp -a fpcsrc/rtl/COPYING.txt %{buildroot}/%{_defaultdocdir}/fpc/COPYING.rtl
cp -a fpcsrc/rtl/COPYING.FPC %{buildroot}/%{_defaultdocdir}/fpc/COPYING.FPC

# The source files.
mkdir -p %{buildroot}/%{_datadir}/fpcsrc
cp -a fpc_src/* %{buildroot}/%{_datadir}/fpcsrc/

# Workaround. Newer rpm versions do not allow garbage.
# Delete lexyacc (the hardcoded library path is necessary because 'make
# install' places this file hardcoded at usr/lib).
rm -rf %{buildroot}/usr/lib/fpc/lexyacc

###############################################################################
# Check
###############################################################################

%check

###############################################################################
# Post
###############################################################################

##
## fpc
##

%pre

%post

%preun

%postun

###############################################################################
# Files
###############################################################################

##
## fpc
##

%files

%config(noreplace) %{_sysconfdir}/fpc.cfg
%config(noreplace) %{_sysconfdir}/fppkg.cfg
%config(noreplace) %{_sysconfdir}/fppkg/default_%{_arch}

%{_bindir}/*
%{_libdir}/fpc
%{_libdir}/libpas2jslib.so*

%{_mandir}/*/*

%dir %{_defaultdocdir}/fpc/

%doc %{_defaultdocdir}/fpc/NEWS
%doc %{_defaultdocdir}/fpc/README
%doc %{_defaultdocdir}/fpc/faq*

%license %{_defaultdocdir}/fpc/COPYING*

##
## fpc-doc
##

%files doc

%dir %{_defaultdocdir}/fpc/

%doc %{_defaultdocdir}/fpc/*.pdf
%doc %{_defaultdocdir}/fpc/*/*

##
## fpc-src
##

%files src

%{_datadir}/fpcsrc

###############################################################################
# Changelog
###############################################################################

%changelog

* Wed Sep 2 2020 Igor Savlook <isav@alzari.pw> - 3.2.0-1
- initializing rpm packaging
