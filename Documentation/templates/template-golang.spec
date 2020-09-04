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

%global goipath ${url}
%global goaltipaths ${url}

%global godocs ${file_list}
%global golicenses ${file_list}

%global gosupfiles ${file_list}

%global commit ${git_commit_sha1}
%global shortcommit %{lua:print(string.sub(rpm.expand("%{?commit}"), 1, 7))}

##
## Rpmbuild variables.
##

%global debug_package %{nil}

###############################################################################
# Packages
###############################################################################

##
## ${pkg_name}
##

Name: ${pkg_name}

Version: ${pkg_version}

Release: 1%{?dist}

Summary: ${pkg_summary}

License: GPL-2.0-or-later

URL: ${pkg_url}

Source0: ${pkg_name}-%{version}.tar.gz

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)
BuildRequires: systemd

%description
${pkg_description}

%gopkg

###############################################################################
# Prepare
###############################################################################

%prep

%if %{with_patches}
%autosetup -p1
%else
%autosetup -N
%endif

%goprep -e -k -s %{_builddir}/${pkg_name}-%{version}

###############################################################################
# Build
###############################################################################

%build

export LDFLAGS="\
    -X %{goipath}/version.GitSHA=%{commit} "

%gobuild -o %{gobuilddir}/bin/${pkg_name} %{goipath}

###############################################################################
# Install
###############################################################################

%install

install -d -m 755 %{buildroot}/%{_sysconfdir}/${pkg_name}

install -d %{buildroot}/%{_bindir}

install -d %{buildroot}/%{_sbindir}

install -d -m 755 %{buildroot}/%{_tmpfilesdir}

install -d -m 755 %{buildroot}/%{_unitdir}

install -d -m 750 %{buildroot}/%{_sharedstatedir}/${pkg_name}

install -d -m 755 %{buildroot}/%{_localstatedir}/log/${pkg_name}

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

getent group ${pkg_name} >/dev/null || groupadd -r ${pkg_name}
getent passwd ${pkg_name} >/dev/null || useradd -r -d %{_sharedstatedir}/${pkg_name} -G ${pkg_name} -g ${pkg_name} -s %{_sbindir}/nologin ${pkg_name}

%post

%systemd_post ${pkg_name}.service

%preun

%systemd_preun ${pkg_name}.service

%postun

%systemd_postun_with_restart ${pkg_name}.service

###############################################################################
# Files
###############################################################################

##
## ${pkg_name}
##

%files

%dir %attr(750,${pkg_name},${pkg_name}) %{_sharedstatedir}/${pkg_name}
%dir %attr(755,${pkg_name},${pkg_name}) %{_localstatedir}/log/${pkg_name}

%config(noreplace) %{_sysconfdir}/${pkg_name}/*

%doc README.md

%license LICENSE

%gopkgfiles

###############################################################################
# Changelog
###############################################################################

%changelog

* ${pack_date} ${packager_name} <${packager_email}> - ${pkg_version}-1
- ${comment}
