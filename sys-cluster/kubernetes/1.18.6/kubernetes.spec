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
## Default values.
##

%global goipath github.com/kubernetes/kubernetes

%global commit 8d5e3a774a7f6c599cf5ec8e7fb40bcd0f07bcab
%global shortcommit %{lua:print(string.sub(rpm.expand("%{?commit}"), 1, 7))}

%global debug_package %{nil}

%if %{with_patches}
%global autosetup_opts -p1
%else
%global autosetup_opts -N
%endif

%if %{with_verbose}
%global make_opts V=1
%else
%global make_opts -s
%endif

##
## Rpmbuild variables.
##

###############################################################################
# Packages
###############################################################################

##
## kubernetes
##

Name: kubernetes

Version: 1.18.6

Release: 1%{?dist}

Summary: Container cluster management

License: ASL 2.0

URL: https://kubernetes.io

Source0: kubernetes-%{version}.tar.gz

ExclusiveArch: %{go_arches}

BuildRequires: compiler(go-compiler)
BuildRequires: go-bindata
BuildRequires: go-md2man
BuildRequires: make
BuildRequires: rsync
BuildRequires: systemd

%description
Kubernetes (K8s) is an open-source system for automating deployment, scaling,
and management of containerized applications. It groups containers that make
up an application into logical units for easy management and discovery.

##
## kubernetes-client
##

%package client

Summary: Kubernetes client tools

%description client
Kubernetes client tools like kubectl.

##
## kubernetes-kubeadm
##

%package kubeadm

Summary: Kubernetes tool for standing up clusters

Requires: containernetworking-plugins
Requires: kubernetes-node = %{version}-%{release}

%description kubeadm
Kubernetes tool for standing up single node or HA clusters.

##
## kubernetes-master
##

%package master

Summary: Kubernetes services for master host

%description master
Kubernetes services for master host like kube-apiserver,
kube-controller-manager and kube-scheduler.

##
## kubernetes-node
##

%package node

Summary: Kubernetes services for node host

Requires: (docker or docker-ce or moby-engine or cri-o)
Requires: conntrack-tools
Requires: socat

%description node
Kubernetes services for node host like kubelet and kube-proxy.

###############################################################################
# Prepare
###############################################################################

%prep

%autosetup %{?autosetup_opts}

###############################################################################
# Build
###############################################################################

%build

export KUBE_GIT_TREE_STATE="clean"
export KUBE_GIT_COMMIT="%{commit}"
export KUBE_GIT_VERSION="v%{version}"

# https://bugzilla.redhat.com/show_bug.cgi?id=1392922#c1
%ifarch ppc64le
export GOLDFLAGS="-linkmode=external"
%endif

bins=(kube-apiserver kube-controller-manager kube-proxy kube-scheduler kubeadm kubectl kubelet)
for bin in "${bins[@]}"; do
    make -j1 %{?make_opts} WHAT="cmd/${bin}"
done

###############################################################################
# Install
###############################################################################

%install

%ifarch aarch64 ppc64le
out_dir="_output/local/go/bin"
%else
out_dir="_output/bin"
%endif

install -d -m 755 %{buildroot}/%{_bindir}

bins=(kube-apiserver kube-controller-manager kube-proxy kube-scheduler kubeadm kubectl kubelet)
for bin in "${bins[@]}"; do
    install -p -m 755 ${out_dir}/${bin} %{buildroot}/%{_bindir}
done

###############################################################################
# Check
###############################################################################

%check

# echo "****** Testing the commands *****"
# ./hack/make-rules/test-cmd.sh

# echo "****** Testing integration ******"
# ./hack/make-rules/test-integration.sh

# In Fedora 20 and RHEL7 the go cover tools isn't available correctly.
# echo "****** Testing the go code ******"
# make %{?make_opts} test

# echo "****** Benchmarking kubernetes ********"
# make %{?make_opts} test \
#     KUBE_COVER="" \
#     KUBE_RACE=" " \
#     KUBE_TEST_ARGS="-- -test.run='^X' -benchtime=1s -bench=. -benchmem"

###############################################################################
# Post
###############################################################################

###############################################################################
# Files
###############################################################################

##
## kubernetes-client
##

%files client

%{_bindir}/kubectl

%doc CHANGELOG/CHANGELOG-*.md CONTRIBUTING.md README.md SUPPORT.md

%license LICENSE

##
## kubernetes-kubeadm
##

%files kubeadm

%{_bindir}/kubeadm

%doc CHANGELOG/CHANGELOG-*.md CONTRIBUTING.md README.md SUPPORT.md

%license LICENSE

##
## kubernetes-master
##

%files master

%{_bindir}/kube-apiserver
%{_bindir}/kube-controller-manager
%{_bindir}/kube-scheduler

%doc CHANGELOG/CHANGELOG-*.md CONTRIBUTING.md README.md SUPPORT.md

%license LICENSE

##
## kubernetes-node
##

%files node

%{_bindir}/kube-proxy
%{_bindir}/kubelet

%doc CHANGELOG/CHANGELOG-*.md CONTRIBUTING.md README.md SUPPORT.md

%license LICENSE

###############################################################################
# Changelog
###############################################################################

%changelog

* Fri Aug 7 2020 Igor Savlook <isav@alzari.pw> 1.18.6-1
- initializing rpm packaging
