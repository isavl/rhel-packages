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

# Build core package. Used when only kernel headers package is needed.
%global with_core %{?_without_core: 0} %{?!_without_core: 1}

# Build headers package.
%global with_headers %{?_without_headers: 0} %{?!_without_headers: 1}

# Build debuginfo package.
%global with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}

# Build devel package.
%global with_devel %{?_without_devel: 0} %{?!_without_devel: 1}

# Build vdso directories installed.
%global with_vdso %{?_without_vdso: 0} %{?!_without_vdso: 1}

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

# Compress kernel modules.
%global with_compress_modules %{?_with_compress_modules: 1} %{?!_with_compress_modules: 0}

# Cross compilation.
%global with_cross %{?_with_cross: 1} %{?!_with_cross: 0}

# Sign kernel image.
%global with_sign_kernel %{?_with_sign_kernel: 1} %{?!_with_sign_kernel: 0}

# Sign kernel modules.
%global with_sign_modules %{?_with_sign_modules: 1} %{?!_with_sign_modules: 0}

# Check all C source with sparse tool. This will add to make 'C=1' option.
%global with_sparse %{?_with_sparse: 1} %{?!_with_sparse: 0}

##
## Default variables.
##

%global kernel_version %{version}-%{release}.%{_target_cpu}

# Sparse blows up on ppc.
%ifnarch ppc64le
%global with_sparse 0
%endif

# Don't build noarch kernels or headers (duh).
%ifarch noarch
%global with_core 0
%global with_devel 0
%global with_headers 0
%endif

%ifarch i386 i686
%global asm_arch x86
%global hdr_arch i386
%global kernel_arch i386

%global kernel_image arch/x86/boot/bzImage
%global kernel_image_pkgname vmlinuz

%global make_target bzImage
%endif

%ifarch x86_64
%global asm_arch x86
%global hdr_arch x86_64
%global kernel_arch x86_64

%global kernel_image arch/x86/boot/bzImage
%global kernel_image_pkgname vmlinuz

%global make_target bzImage
%endif

%ifarch %{arm}
%global asm_arch arm
%global hdr_arch arm
%global kernel_arch arm

%global kernel_image arch/arm/boot/zImage
%global kernel_image_pkgname vmlinuz

# http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
%global kernel_mflags KALLSYMS_EXTRA_PASS=1

%global make_target bzImage

%ifnarch armv7hl
# Only build headers/perf/tools on the base arm arches just like we used
# to only build them on i386 for x86.
%global with_headers 0
%global with_cross_headers 0
%endif
%endif

%ifarch aarch64
%global asm_arch arm64
%global hdr_arch arm64
%global kernel_arch arm64

%global kernel_image arch/arm64/boot/Image
%global kernel_image_pkgname vmlinux

%global make_target Image
%endif

%ifarch ppc64le
%global asm_arch powerpc
%global hdr_arch powerpc
%global kernel_arch powerpc

%global kernel_image vmlinux
%global kernel_image_elf 1
%global kernel_image_pkgname vmlinux

%global make_target vmlinux
%endif

%ifarch s390x
%global asm_arch s390
%global hdr_arch s390
%global kernel_arch s390

%global kernel_image arch/s390/boot/bzImage
%global kernel_image_pkgname vmlinuz

%global make_target bzImage
%endif

%if %{with_sparse}
%define sparse_mflags C=1
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuild_arches. Do _NOT_ use the 'ExclusiveArch' line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
#
# Which is a BadThing(tm).
#
# We only build kernel-headers on the following...
%global nobuild_arches i386

%if %{with_compress_modules}
%global compress_modules_sed -e 's/\.ko$/\.ko.xz/'
%endif

%if %{with_cross}
%global cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%endif

%if %{with_vdso}
%ifarch armv7hl
%global with_vdso 0
%endif
%endif

%global make make %{?cross_opts}

%if %{with_verbose}
%global make_opts V=1
%else
%global make_opts -s
%endif

%global _bootdir /boot
%global _efidir %{_bootdir}/efi/fedora
%global _modulesdir /lib/modules
%global _kernelmodulesdir %{_modulesdir}/%{kernel_version}
%global _debuginfodir /usr/lib/debug

%if %{with_patches}
%global _autosetup_opts -p1
%else
%global _autosetup_opts -N
%endif

##
## Rpmbuild variables.
##

%if %{with_debuginfo}
%undefine _debuginfo_subpackages
%undefine _debugsource_packages
%undefine _find_debuginfo_dwz_opts
%undefine _include_minidebuginfo
%undefine _unique_build_ids
%undefine _unique_debug_names
%undefine _unique_debug_srcs

%global debug_package %{nil}

%global _build_id_links alldebug

%global _find_debuginfo_opts -r -p '/.*/%{kernel_version}/.*|/.*%{kernel_version}(\.debug)?' -o debuginfo.list

%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1

%ifnarch noarch
%global __debug_package 1
%endif
%endif

# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
%define __modules_install_post \
if [ "%{with_sign_modules}" -eq "1" ]; then \
    if [ "%{with_core}" -ne "0" ]; then \
        %{SOURCE410} certs/signing_key.pem.sign certs/signing_key.x509.sign %{buildroot}/%{_kernelmodulesdir} \
    fi \
fi \
\
# Mark kernel modules back to non-executable. \
find %{buildroot}/%{_kernelmodulesdir} -type f -name "*.ko" -exec chmod u-x {} +; \
\
if [ "%{with_compress_modules}" -eq "1" ]; then \
    find %{buildroot}/%{_kernelmodulesdir} -type f -name "*.ko" -exec xz -T0 {} +; \
fi \
%{nil} # end define __modsign_install_post

# Override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
%define __spec_install_post \
    %{?__debug_package: %{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    %{__modules_install_post}

###############################################################################
# Packages
###############################################################################

##
## linux
##

Name: linux

Version: 5.8.1

Release: 200%{?dist}

Summary: The Linux kernel

License: GPLv2 and Redistributable, no modification permitted

URL: https://www.kernel.org/

Source0: linux-%{version}.tar.gz

Source141: linux-defconfig-aarch64
#Source142: linux-defconfig-armv7hl
#Source143: linux-defconfig-i686
Source144: linux-defconfig-x86_64

Source410: mod-sign.sh
Source411: x509.genkey

BuildConflicts: rhbuildsys(DiskFree) < 24Gb

BuildRequires: bash
BuildRequires: bc
BuildRequires: binutils
BuildRequires: bison
BuildRequires: bzip2
BuildRequires: diffutils
BuildRequires: elfutils-devel
BuildRequires: findutils
BuildRequires: flex
BuildRequires: gawk
BuildRequires: gcc
BuildRequires: gcc-plugin-devel
BuildRequires: gzip
BuildRequires: hmaccalc
BuildRequires: hostname
BuildRequires: kmod
BuildRequires: lz4
BuildRequires: m4
BuildRequires: make
BuildRequires: net-tools
BuildRequires: openssl
BuildRequires: openssl-devel
BuildRequires: patch
BuildRequires: perl-Carp
BuildRequires: perl-devel
BuildRequires: perl-generators
BuildRequires: perl-interpreter
BuildRequires: redhat-rpm-config
BuildRequires: rsync
BuildRequires: tar
BuildRequires: xz

%if 0%{?fedora} || 0%{?rhel} > 7
# Used to mangle unversioned shebangs to be Python 3.
BuildRequires: /usr/bin/pathfix.py
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu
BuildRequires: gcc-%{_build_arch}-linux-gnu
%endif

%if %{with_debuginfo}
BuildConflicts: rpm < 4.13.0.1-19
BuildRequires: elfutils
BuildRequires: rpm-build
%endif

%if %{with_sparse}
BuildRequires: sparse
%endif

%if %{with_sign_kernel}
BuildRequires: pesign >= 0.10-4
%endif

%ifnarch %{nobuild_arches}
Conflicts: xfsprogs < 4.3.0-1
Conflicts: xorg-x11-drv-vmmouse < 13.0.99

%ifarch ppc64le
Obsoletes: kernel-bootwrapper
%endif

Provides: linux = %{version}-%{release}
Provides: linux-%{_target_cpu} = %{version}-%{release}
Provides: linux-uname-r = %{kernel_version}

Provides: linux-core = %{version}-%{release}
Provides: linux-core-%{_target_cpu} = %{version}-%{release}
Provides: linux-core-uname-r = %{kernel_version}

Provides: linux-modules = %{version}-%{release}
Provides: linux-modules-%{_target_cpu} = %{version}-%{release}
Provides: linux-modules-uname-r = %{kernel_version}

Provides: linux-modules-extra = %{version}-%{release}
Provides: linux-modules-extra-%{_target_cpu} = %{version}-%{release}
Provides: linux-modules-extra-uname-r = %{kernel_version}

Provides: kernel = %{version}-%{release}
Provides: kernel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-uname-r = %{kernel_version}

Provides: kernel-core = %{version}-%{release}
Provides: kernel-core-%{_target_cpu} = %{version}-%{release}
Provides: kernel-core-uname-r = %{kernel_version}

Provides: kernel-modules = %{version}-%{release}
Provides: kernel-modules-%{_target_cpu} = %{version}-%{release}
Provides: kernel-modules-uname-r = %{kernel_version}

Provides: kernel-modules-extra = %{version}-%{release}
Provides: kernel-modules-extra-%{_target_cpu} = %{version}-%{release}
Provides: kernel-modules-extra-uname-r = %{kernel_version}

Provides: kernel-drm-nouveau = 16

Provides: installonlypkg(kernel)
Provides: installonlypkg(kernel-module)

# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
Requires(pre): coreutils
Requires(pre): dracut >= 027
Requires(pre): systemd >= 203-2
Requires(pre): /usr/bin/kernel-install

Requires(pre): linux-firmware >= 20150904-56.git6ebf5d57

Requires(preun): systemd >= 200

# We can't let RPM do the dependencies automatic because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel proper to function.
AutoProv: yes
AutoReq: no
%endif

# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN
# ARCHITECTURE BUILD. SET %%nobuild_arches (ABOVE) INSTEAD.
ExclusiveArch: i386 i686 x86_64 s390x %{arm} aarch64 ppc64le

ExclusiveOS: Linux

%description
This package contains the Linux kernel (vmlinuz), the core of any
Linux operating system. The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.

##
## linux-debuginfo
##

%package debuginfo

Summary: Debug information for package kernel

Provides: linux-debuginfo-%{_target_cpu} = %{version}-%{release}

Provides: kernel-debuginfo = %{version}-%{release}
Provides: kernel-debuginfo-%{_target_cpu} = %{version}-%{release}

Provides: installonlypkg(kernel)

AutoReqProv: no

%description debuginfo
This package provides debug information for package linux.
This is required to use SystemTap with linux-%{kernel_version}.

##
## linux-devel
##

%package devel

Summary: Development package for building linux modules to match the kernel

Provides: linux-devel-%{_target_cpu} = %{version}-%{release}
Provides: linux-devel-uname-r = %{kernel_version}

Provides: kernel-devel = %{version}-%{release}
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-devel-uname-r = %{kernel_version}

Provides: installonlypkg(kernel)

Requires: findutils
Requires: perl-interpreter

Requires(pre): findutils

AutoReqProv: no

%description devel
This package provides linux headers and makefiles sufficient to build modules
against the linux package.

##
## linux-headers
##

%package headers

Summary: Header files for the Linux kernel for use by glibc

Obsoletes: glibc-kernheaders < 3.0-46
Obsoletes: kernel-headers < %{version}-%{release}

Provides: glibc-kernheaders = 3.0-46
Provides: kernel-headers = %{version}-%{release}

%description headers
Includes the C header files that specify the interface between
the Linux kernel and userspace libraries and programs.
The header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

###############################################################################
# Prepare
###############################################################################

%prep

%autosetup %{?_autosetup_opts}

%if 0%{?fedora} || 0%{?rhel} > 7
# Mangle /usr/bin/python shebangs to /usr/bin/python3.
# Mangle all Python shebangs to be Python 3 explicitly.
#
# -p preserves timestamps
# -n prevents creating ~backup files
# -i specifies the interpreter for the shebang
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/bloat-o-meter
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/diffconfig
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/jobserver-exec
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" scripts/show_delta
%endif

mv COPYING COPYING-%{version}

# Get rid of unwanted files resulting from patch fuzz.
find . \( -name "*.orig" -o -name "*~" \) -delete >/dev/null

# Remove unnecessary SCM files.
find . -name .gitignore -delete >/dev/null

###############################################################################
# Build
###############################################################################

%build

# These are for host programs that get built as part of the kernel and
# are required to be packaged in linux-devel for building external modules.
# Since they are userspace binaries, they are required to pickup the hardening
# flags defined in the macros. The --build-id=uuid is a trick to get around
# debuginfo limitations: Typically, find-debuginfo.sh will update the build
# id of all binaries to allow for parllel debuginfo installs. The kernel
# can't use this because it breaks debuginfo for the vDSO so we have to
# use a special mechanism for kernel and modules to be unique. Unfortunately,
# we still have userspace binaries which need unique debuginfo and because
# they come from the kernel package, we can't just use find-debuginfo.sh to
# rewrite only those binaries. The easiest option right now is just to have
# the build id be a uuid for the host programs.
#
# Note we need to disable these flags for cross builds because the flags
# from redhat-rpm-config assume that host == target so target arch
# flags cause issues with the host compiler.
%if !%{with_cross}
%define build_hostcflags %{?build_cflags}
%define build_hostldflags %{?build_ldflags} -Wl,--build-id=uuid
%endif

%if %{with_core}

cp_vmlinux() {
    eu-strip --remove-comment -o "$2" "$1"
}

# When the bootable image is just the ELF kernel, strip it.
# We already copy the unstripped file into the debuginfo package.
if [ "%{kernel_image}" = "vmlinux" ]; then
    copy_kernel=cp_vmlinux
else
    copy_kernel=cp
fi

%if %{with_sign_kernel} || %{with_sign_modules}
cp %{SOURCE411} certs/
%endif

cp %{_sourcedir}/linux-defconfig-%{_target_cpu} .config

# Make kernel config.
make %{?make_opts} \
    HOSTCFLAGS="%{?build_hostcflags}" \
    HOSTLDFLAGS="%{?build_hostldflags}" \
    ARCH=%{kernel_arch} \
    olddefconfig

# This ensures build-ids are unique to allow parallel debuginfo.
sed -i -e "s/^CONFIG_BUILD_SALT.*/CONFIG_BUILD_SALT=\"%{kernel_version}\"/" .config

# Make sure EXTRAVERSION says what we want it to say.
sed -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}/" Makefile

# Make kernel image.
%{make} %{?_smp_mflags} %{?kernel_mflags} %{?sparse_mflags} %{?make_opts} \
    HOSTCFLAGS="%{?build_hostcflags}" \
    HOSTLDFLAGS="%{?build_hostldflags}" \
    ARCH=%{kernel_arch} \
    %{make_target}

# Make kernel modules.
%{make} %{?_smp_mflags} %{?sparse_mflags} %{?make_opts} \
    HOSTCFLAGS="%{?build_hostcflags}" \
    HOSTLDFLAGS="%{?build_hostldflags}" \
    ARCH=%{kernel_arch} \
    modules

mkdir -p %{buildroot}/%{_bootdir}
mkdir -p %{buildroot}/%{_kernelmodulesdir}

%if %{with_debuginfo}
mkdir -p %{buildroot}/%{_debuginfodir}/%{_bootdir}
%endif

%ifarch %{arm} aarch64
# Make and install kernel device tree blobs (dtb).
%{make} %{?make_opts} \
    ARCH=%{kernel_arch} \
    INSTALL_DTBS_PATH=%{buildroot}/%{_bootdir}/dtb-%{kernel_version} \
    dtbs dtbs_install

    cp -r %{buildroot}/%{_bootdir}/dtb-%{kernel_version} \
        %{buildroot}/%{_kernelmodulesdir}/dtb

    find arch/%{kernel_arch}/boot/dts -name "*.dtb" -type f -delete
%endif

install -m 644 .config %{buildroot}/%{_bootdir}/config-%{kernel_version}
install -m 644 .config %{buildroot}/%{_kernelmodulesdir}/config
install -m 644 System.map %{buildroot}/%{_bootdir}/System.map-%{kernel_version}
install -m 644 System.map %{buildroot}/%{_kernelmodulesdir}/System.map

# We estimate the size of the initramfs because rpm needs to take this size
# into consideration when performing disk space calculations.
dd if=/dev/zero of=%{buildroot}/boot/initramfs-%{kernel_version}.img bs=1M count=20

if [ -f arch/%{kernel_arch}/boot/zImage.stub ]; then
    cp arch/%{kernel_arch}/boot/zImage.stub %{buildroot}/%{_bootdir}/zImage.stub-%{kernel_version} || :
    cp arch/%{kernel_arch}/boot/zImage.stub %{buildroot}/%{_kernelmodulesdir}/zImage.stub-%{kernel_version} || :
fi

%if %{with_sign_kernel}
# Sign the image if we're using EFI.
%pesign -s -i %{kernel_image} -o Image.signed

if [ ! -s Image.signed ]; then
    echo "pesign failed"
    exit 1
fi

mv Image.signed %{kernel_image}
%endif

# Install kernel image.
$copy_kernel %{kernel_image} %{buildroot}/%{_bootdir}/%{kernel_image_pkgname}-%{kernel_version}
chmod 755 %{buildroot}/%{_bootdir}/%{kernel_image_pkgname}-%{kernel_version}
cp %{buildroot}/%{_bootdir}/%{kernel_image_pkgname}-%{kernel_version} %{buildroot}/%{_kernelmodulesdir}/%{kernel_image_pkgname}

# Hmac sign the kernel for FIPS.
ls -l %{buildroot}/%{_bootdir}/%{kernel_image_pkgname}-%{kernel_version}
sha512hmac %{buildroot}/%{_bootdir}/%{kernel_image_pkgname}-%{kernel_version} | sed -e "s,%{buildroot},," > %{buildroot}/%{_bootdir}/.%{kernel_image_pkgname}-%{kernel_version}.hmac
cp %{buildroot}/%{_bootdir}/.%{kernel_image_pkgname}-%{kernel_version}.hmac %{buildroot}/%{_kernelmodulesdir}/.%{kernel_image_pkgname}.hmac

# Install kernel modules.
#
# Override $(mod-fw) because we don't want it to install any firmware
# we'll get it from the linux-firmware package and we don't want conflicts.
%{make} %{?make_opts} \
    ARCH=%{kernel_arch} \
    INSTALL_MOD_PATH=%{buildroot} \
    KERNELRELEASE=%{kernel_version} \
    mod-fw= \
    modules_install

# Install kernel vdso.
%if %{with_vdso}
%{make} %{?make_opts} \
    ARCH=%{kernel_arch} \
    INSTALL_MOD_PATH=%{buildroot} \
    KERNELRELEASE=%{kernel_version} \
    vdso_install

rm -rf %{buildroot}/%{_kernelmodulesdir}/vdso/.build-id
%endif

# Save the headers/makefiles etc for building modules against.
#
# This all looks scary, but the end result is supposed to be:
#   - all arch relevant include/ files
#   - all Makefile/Kconfig files
#   - all script/ files

rm -f %{buildroot}/%{_kernelmodulesdir}/build
rm -f %{buildroot}/%{_kernelmodulesdir}/source

mkdir -p %{buildroot}/%{_kernelmodulesdir}/build
(cd %{buildroot}/%{_kernelmodulesdir}; ln -s build source)

# Directories for additional modules per module-init-tools, kbuild/modules.txt.
mkdir -p %{buildroot}/%{_kernelmodulesdir}/extra
mkdir -p %{buildroot}/%{_kernelmodulesdir}/updates

# Copy everything.
cp --parents $(find -type f -name "Makefile*" -o -name "Kconfig*") \
    %{buildroot}/%{_kernelmodulesdir}/build
cp Module.symvers %{buildroot}/%{_kernelmodulesdir}/build
cp System.map %{buildroot}/%{_kernelmodulesdir}/build
if [ -s Module.markers ]; then
    cp Module.markers %{buildroot}/%{_kernelmodulesdir}/build
fi

# Drop all but the needed Makefiles/Kconfig files.
rm -rf %{buildroot}/%{_kernelmodulesdir}/build/Documentation
rm -rf %{buildroot}/%{_kernelmodulesdir}/build/include
rm -rf %{buildroot}/%{_kernelmodulesdir}/build/scripts

cp .config %{buildroot}/%{_kernelmodulesdir}/build
cp -a scripts %{buildroot}/%{_kernelmodulesdir}/build

if [ -f tools/objtool/objtool ]; then
    cp -a tools/objtool/objtool %{buildroot}/%{_kernelmodulesdir}/build/tools/objtool/ || :

    # These are a few files associated with objtool.
    cp -a --parents tools/build/Build %{buildroot}/%{_kernelmodulesdir}/build/
    cp -a --parents tools/build/Build.include %{buildroot}/%{_kernelmodulesdir}/build/
    cp -a --parents tools/build/fixdep.c %{buildroot}/%{_kernelmodulesdir}/build/
    cp -a --parents tools/scripts/utilities.mak %{buildroot}/%{_kernelmodulesdir}/build/

    # Also more than necessary but it's not that many more files.
    cp -a --parents tools/lib/str_error_r.c %{buildroot}/%{_kernelmodulesdir}/build/
    cp -a --parents tools/lib/string.c %{buildroot}/%{_kernelmodulesdir}/build/
    cp -a --parents tools/lib/subcmd/* %{buildroot}/%{_kernelmodulesdir}/build/
    cp -a --parents tools/objtool/* %{buildroot}/%{_kernelmodulesdir}/build/
fi

if [ -d arch/%{kernel_arch}/scripts ]; then
    cp -a arch/%{kernel_arch}/scripts %{buildroot}/%{_kernelmodulesdir}/build/arch/%{_arch} || :
fi

if [ -f arch/%{kernel_arch}/*lds ]; then
    cp -a arch/%{kernel_arch}/*lds %{buildroot}/%{_kernelmodulesdir}/build/arch/%{_arch}/ || :
fi

if [ -f arch/%{asm_arch}/kernel/module.lds ]; then
    cp -a --parents arch/%{asm_arch}/kernel/module.lds %{buildroot}/%{_kernelmodulesdir}/build/
fi

if [ -d arch/%{asm_arch}/include ]; then
    cp -a --parents arch/%{asm_arch}/include %{buildroot}/%{_kernelmodulesdir}/build/
fi

cp -a include %{buildroot}/%{_kernelmodulesdir}/build/include

rm -f %{buildroot}/%{_kernelmodulesdir}/build/scripts/*.o
rm -f %{buildroot}/%{_kernelmodulesdir}/build/scripts/*/*.o

%ifarch aarch64
# arch/arm64/include/asm/xen references arch/arm
cp -a --parents arch/arm/include/asm/xen %{buildroot}/%{_kernelmodulesdir}/build/
# arch/arm64/include/asm/opcodes.h references arch/arm
cp -a --parents arch/arm/include/asm/opcodes.h %{buildroot}/%{_kernelmodulesdir}/build/
%endif

%ifarch ppc64le
cp -a --parents arch/%{kernel_arch}/lib/crtsavres.[So] %{buildroot}/%{_kernelmodulesdir}/build/
%endif

%ifarch %{ix86} x86_64
# Files for 'make prepare' to succeed with kernel-devel.
cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/entry/syscalls/syscallhdr.sh %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/entry/syscalls/syscalltbl.sh %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/tools/relocs.c %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/tools/relocs.h %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/tools/relocs_32.c %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/tools/relocs_64.c %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/tools/relocs_common.c %{buildroot}/%{_kernelmodulesdir}/build/

# Yes this is more includes than we probably need. Feel free to sort out
# dependencies if you so choose.
cp -a --parents arch/x86/boot/ctype.h %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/boot/string.c %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/boot/string.h %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/purgatory/entry64.S %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/purgatory/purgatory.c %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/purgatory/setup-x86_64.S %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents arch/x86/purgatory/stack.S %{buildroot}/%{_kernelmodulesdir}/build/
cp -a --parents tools/include/* %{buildroot}/%{_kernelmodulesdir}/build/
%endif

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built.
touch -r \
    %{buildroot}/%{_kernelmodulesdir}/build/Makefile \
    %{buildroot}/%{_kernelmodulesdir}/build/include/generated/uapi/linux/version.h

# Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
cp %{buildroot}/%{_kernelmodulesdir}/build/.config \
    %{buildroot}/%{_kernelmodulesdir}/build/include/config/auto.conf

%if %{with_debuginfo}
eu-readelf -n vmlinux | grep "Build ID" | awk '{print $NF}' > vmlinux.id
cp vmlinux.id %{buildroot}/%{_kernelmodulesdir}/build/vmlinux.id

# Save the vmlinux file for kernel debugging into the linux-debuginfo package.
mkdir -p %{buildroot}/%{_debuginfodir}/%{_kernelmodulesdir}
cp vmlinux %{buildroot}/%{_debuginfodir}/%{_kernelmodulesdir}
%endif

# Mark kernel modules executable so that strip-to-file can strip them.
find %{buildroot}/%{_kernelmodulesdir} -type f -name "*.ko" | xargs --no-run-if-empty chmod u+x

# Detect missing or incorrect license tags.
(
    find %{buildroot}/%{_kernelmodulesdir} -name '*.ko' | xargs /sbin/modinfo -l | \
        grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$'
) && exit 1

%if %{with_sign_modules}
# Save the signing keys so we can sign the modules in __modsign_install_post.
cp certs/signing_key.pem certs/signing_key.pem.sign
cp certs/signing_key.x509 certs/signing_key.x509.sign
%endif

# Move the devel headers out of the root file system.
mkdir -p %{buildroot}/usr/src/kernels
mv %{buildroot}/%{_kernelmodulesdir}/build %{buildroot}/usr/src/kernels/%{kernel_version}

# This is going to create a broken link during the build, but we don't use
# it after this point. We need the link to actually point to something
# when linux-devel is installed, and a relative link doesn't work across
# the F17 UsrMove feature.
ln -sf /usr/src/kernels/%{kernel_version} %{buildroot}/%{_kernelmodulesdir}/build

# Prune junk from linux-devel.
find %{buildroot}/usr/src/kernels -name ".*.cmd" -delete

%endif

###############################################################################
# Install
###############################################################################

%install

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}

make %{?make_opts} \
    ARCH=%{hdr_arch} \
    INSTALL_HDR_PATH=%{buildroot}/usr \
    headers_install

find %{buildroot}/usr/include \
    \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

%endif

###############################################################################
# Post
###############################################################################

##
## linux
##

%if %{with_core}

%preun

/bin/kernel-install remove %{kernel_version} %{_kernelmodulesdir}/%{kernel_image_pkgname} || exit $?

%post

/sbin/depmod -a %{kernel_version}

%posttrans

/bin/kernel-install add %{kernel_version} %{_kernelmodulesdir}/%{kernel_image_pkgname} || exit $?

%postun

/sbin/depmod -a %{kernel_version}

%endif

###############################################################################
# Files
###############################################################################

##
## linux
##

%if %{with_core}

%files

%attr(600,root,root) %{_kernelmodulesdir}/System.map

%ifarch %{arm} aarch64
%ghost %{_bootdir}/dtb-%{kernel_version}
%endif

%ghost %{_bootdir}/.%{kernel_image_pkgname}-%{kernel_version}.hmac
%ghost %{_bootdir}/System.map-%{kernel_version}
%ghost %{_bootdir}/config-%{kernel_version}
%ghost %{_bootdir}/initramfs-%{kernel_version}.img
%ghost %{_bootdir}/%{kernel_image_pkgname}-%{kernel_version}

%{_kernelmodulesdir}

%license COPYING-%{version}

%endif

##
## linux-debuginfo
##

%if %{with_debuginfo}

%files debuginfo -f debuginfo.list -f debugfiles.list

%endif

##
## linux-devel
##

%if %{with_devel}

%files devel

%defverify(not mtime)

/usr/src/kernels/%{kernel_version}

%endif

##
## linux-headers
##

%if %{with_headers}

%files headers

/usr/include

%endif

###############################################################################
# Changelog
###############################################################################

%changelog

* Wed Aug 19 2020 Igor Savlook <isav@alzari.pw> - 5.8.1-200
- initializing rpm packaging
