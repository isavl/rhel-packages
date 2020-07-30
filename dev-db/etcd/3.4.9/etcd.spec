###############################################################################
# General
###############################################################################

##
## Build options enabled by default.
##
## Use either --without <opt> in mock/rpmbuild/etc. command or force values
## to 0 in here to disable them.
##

# Build with check stage.
%global with_check %{?_without_check: 0} %{?!_without_check: 1}

# Build with patches.
%global with_patches %{?_without_patches: 0} %{?!_without_patches: 1}

##
## Build options disabled by default.
##
## Use either --with <opt> in mock/rpmbuild/etc. command or force values
## to 1 in here to enable them.
##

##
## Default variables.
##

%global goipath go.etcd.io/etcd
%global goaltipaths github.com/coreos/etcd

%global golicenses LICENSE NOTICE
%global godocs CONTRIBUTING.md README.md README-*.md READMEv2-etcdctl.md Documentation

%global gosupfiles integration/fixtures/* etcdserver/api/v2http/testdata/*

%global commit d67e094272de95088201360add7b2e76f1a6b3b8
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
## etcd
##

Name: etcd

Version: 3.4.9

Release: 1%{?dist}

Summary: Highly-available key value store for shared configuration and service discovery

License: ASL 2.0

URL: https://etcd.io

Source0: etcd-%{version}.tar.gz

Source10: etcd.tmpfile
Source11: etcd.service

Source20: etcd.conf

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)
BuildRequires: systemd

%description
Strongly consistent, distributed key-value store that provides a reliable
way to store data that needs to be accessed by a distributed system or cluster
of machines. It gracefully handles leader elections during network partitions
and can tolerate machine failure, even in the leader node.

%gopkg

###############################################################################
# Prepare
###############################################################################

%prep

%autosetup %{?autosetup_opts}

%goprep -e -k -s %{_builddir}/etcd-%{version}

for d in client clientv3 contrib etcdctl functional hack; do
    mv $d/README.md README-$d.md
done

mv etcdctl/READMEv2.md READMEv2-etcdctl.md

###############################################################################
# Build
###############################################################################

%build

export LDFLAGS="\
    -X %{goipath}/version.GitSHA=%{commit} "

%gobuild -o %{gobuilddir}/bin/etcd %{goipath}
%gobuild -o %{gobuilddir}/bin/etcdctl %{goipath}/etcdctl

###############################################################################
# Install
###############################################################################

%install

install -d -m 755 %{buildroot}/%{_sysconfdir}/etcd
install -p -m 644 %{SOURCE20} %{buildroot}/%{_sysconfdir}/etcd/etcd.conf

install -d %{buildroot}/%{_bindir}
install -p -m 0755 %{gobuilddir}/bin/etcd %{buildroot}/%{_bindir}/etcd
install -p -m 0755 %{gobuilddir}/bin/etcdctl %{buildroot}/%{_bindir}/etcdctl

install -d -m 755 %{buildroot}/%{_tmpfilesdir}
install -p -m 644 %{SOURCE10} %{buildroot}/%{_tmpfilesdir}/etcd.conf

install -d -m 755 %{buildroot}/%{_unitdir}
install -p -m 644 %{SOURCE11} %{buildroot}/%{_unitdir}/etcd.service

install -d -m 750 %{buildroot}/%{_sharedstatedir}/etcd

install -d -m 755 %{buildroot}/%{_localstatedir}/log/etcd

%gopkginstall

###############################################################################
# Check
###############################################################################

%check

%if %{with_check}
%gocheck \
    -d clientv3 \
    -d clientv3/balancer \
    -d clientv3/integration \
    -d clientv3/ordering \
    -d clientv3/snapshot \
    -d e2e \
    -d functional/rpcpb \
    -d functional/tester \
    -d integration \
    -d pkg/expect \
    -d pkg/flags \
    -d pkg/proxy \
    -d pkg/tlsutil \
    -d pkg/transport \
    -d tools/functional-tester/etcd-agent \
    -t raft \
    -t tests/e2e
%endif

###############################################################################
# Post
###############################################################################

##
## etcd
##

%pre

getent group etcd >/dev/null || groupadd -r etcd
getent passwd etcd >/dev/null || useradd -r -d %{_sharedstatedir}/etcd -G etcd -g etcd -s %{_sbindir}/nologin etcd

%post

%systemd_post etcd.service

%preun

%systemd_preun etcd.service

%postun

%systemd_postun_with_restart etcd.service

###############################################################################
# Files
###############################################################################

##
## etcd
##

%files

%dir %attr(750,etcd,etcd) %{_sharedstatedir}/etcd
%dir %attr(755,etcd,etcd) %{_localstatedir}/log/etcd

%config(noreplace) %{_sysconfdir}/etcd/*

%{_bindir}/etcd
%{_bindir}/etcdctl

%{_tmpfilesdir}/etcd.conf

%{_unitdir}/etcd.service

%license LICENSE NOTICE

%doc CONTRIBUTING.md README.md README-*.md READMEv2-etcdctl.md Documentation

%gopkgfiles

###############################################################################
# Changelog
###############################################################################

%changelog

* Wed Jul 29 2020 Igor Savlook <isav@alzari.pw> - 3.4.9-1
- initializing rpm packaging
