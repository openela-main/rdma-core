Name: rdma-core
Version: 44.0
Release: 2%{?dist}.1
Summary: RDMA core userspace libraries and daemons

# Almost everything is licensed under the OFA dual GPLv2, 2 Clause BSD license
#  providers/ipathverbs/ Dual licensed using a BSD license with an extra patent clause
#  providers/rxe/ Incorporates code from ipathverbs and contains the patent clause
#  providers/hfi1verbs Uses the 3 Clause BSD license
License: GPLv2 or BSD
Url: https://github.com/linux-rdma/rdma-core
Source: https://github.com/linux-rdma/rdma-core/releases/download/v%{version}/%{name}-%{version}.tar.gz
Source1: ibdev2netdev
# Upstream had removed rxe_cfg from upstream git repo. RHEL-8.X has
# to keep it for backward compatibility. 'rxe_cfg' and 'rxe_cfg.8.gz'
# are extracted from libibverbs-26.0-8.el8 .
Source2: rxe_cfg
Source3: rxe_cfg.8.gz
# 0001-0003: https://github.com/linux-rdma/rdma-core/pull/1308
Patch1: 0001-util-fix-overflow-in-remap_node_name.patch
Patch2: 0002-infiniband-diags-drop-unnecessary-nodedesc-local-cop.patch
Patch3: 0003-libibnetdisc-fix-printing-a-possibly-non-NUL-termina.patch
# RHEL specific patch for OPA ibacm plugin
Patch300: 0001-ibacm-acm.c-load-plugin-while-it-is-soft-link.patch
Patch301: 0002-systemd-drop-Protect-options-not-supported-in-RHEL-8.patch
Patch9000: 0003-CMakeLists-disable-providers-that-were-not-enabled-i.patch
Patch9998: 9998-kernel-boot-Do-not-perform-device-rename-on-OPA-devi.patch
Patch9999: 9999-udev-keep-NAME_KERNEL-as-default-interface-naming-co.patch
# Do not build static libs by default.
%define with_static %{?_with_static: 1} %{?!_with_static: 0}

# 32-bit arm is missing required arch-specific memory barriers,
ExcludeArch: %{arm}

BuildRequires: binutils
BuildRequires: cmake >= 2.8.11
BuildRequires: gcc
BuildRequires: libudev-devel
BuildRequires: pkgconfig
BuildRequires: pkgconfig(libnl-3.0)
BuildRequires: pkgconfig(libnl-route-3.0)
BuildRequires: python3-docutils
%ifarch %{valgrind_arches}
BuildRequires: valgrind-devel
%endif
BuildRequires: systemd
BuildRequires: systemd-devel
%if 0%{?fedora} >= 32 || 0%{?rhel} >= 8
%define with_pyverbs %{?_with_pyverbs: 1} %{?!_with_pyverbs: %{?!_without_pyverbs: 1} %{?_without_pyverbs: 0}}
%else
%define with_pyverbs %{?_with_pyverbs: 1} %{?!_with_pyverbs: 0}
%endif
%if %{with_pyverbs}
BuildRequires: python3-devel
BuildRequires: python3-Cython
%else
%if 0%{?rhel} >= 8 || 0%{?fedora} >= 30
BuildRequires: python3
%else
BuildRequires: python
%endif
%endif

BuildRequires: sed
BuildRequires: perl-generators

Requires: pciutils
# Red Hat/Fedora previously shipped redhat/ as a stand-alone
# package called 'rdma', which we're supplanting here.
Provides: rdma = %{version}-%{release}
Obsoletes: rdma < %{version}-%{release}
Provides: rdma-ndd = %{version}-%{release}
Obsoletes: rdma-ndd < %{version}-%{release}
# the ndd utility moved from infiniband-diags to rdma-core
Conflicts: infiniband-diags <= 1.6.7

# Since we recommend developers use Ninja, so should packagers, for consistency.
%define CMAKE_FLAGS %{nil}
%if 0%{?fedora} >= 23 || 0%{?rhel} >= 8
# Ninja was introduced in FC23
BuildRequires: ninja-build
%define CMAKE_FLAGS -GNinja
%define make_jobs ninja-build -v %{?_smp_mflags}
%define cmake_install DESTDIR=%{buildroot} ninja-build install
%else
# Fallback to make otherwise
BuildRequires: make
%define make_jobs make VERBOSE=1 %{?_smp_mflags}
%define cmake_install DESTDIR=%{buildroot} make install
%endif

BuildRequires: pandoc

%description
RDMA core userspace infrastructure and documentation, including initialization
scripts, kernel driver-specific modprobe override configs, IPoIB network
scripts, dracut rules, and the rdma-ndd utility.

%package devel
Summary: RDMA core development libraries and headers
Requires: libibverbs%{?_isa} = %{version}-%{release}
Provides: libibverbs-devel = %{version}-%{release}
Obsoletes: libibverbs-devel < %{version}-%{release}
Requires: libibumad%{?_isa} = %{version}-%{release}
Provides: libibumad-devel = %{version}-%{release}
Obsoletes: libibumad-devel < %{version}-%{release}
Requires: librdmacm%{?_isa} = %{version}-%{release}
Provides: librdmacm-devel = %{version}-%{release}
Obsoletes: librdmacm-devel < %{version}-%{release}
Provides: ibacm-devel = %{version}-%{release}
Obsoletes: ibacm-devel < %{version}-%{release}
Requires: infiniband-diags%{?_isa} = %{version}-%{release}
Provides: infiniband-diags-devel = %{version}-%{release}
Obsoletes: infiniband-diags-devel < %{version}-%{release}
Provides: libibmad-devel = %{version}-%{release}
Obsoletes: libibmad-devel < %{version}-%{release}
%if %{with_static}
# Since our pkg-config files include private references to these packages they
# need to have their .pc files installed too, even for dynamic linking, or
# pkg-config breaks.
BuildRequires: pkgconfig(libnl-3.0)
BuildRequires: pkgconfig(libnl-route-3.0)
%endif

%description devel
RDMA core development libraries and headers.

%package -n infiniband-diags
Summary: InfiniBand Diagnostic Tools
Requires: libibumad%{?_isa} = %{version}-%{release}
Provides: perl(IBswcountlimits)
Provides: libibmad = %{version}-%{release}
Obsoletes: libibmad < %{version}-%{release}
Obsoletes: openib-diags < 1.3

%description -n infiniband-diags
This package provides IB diagnostic programs and scripts needed to diagnose an
IB subnet.  infiniband-diags now also provides libibmad.  libibmad provides
low layer IB functions for use by the IB diagnostic and management
programs. These include MAD, SA, SMP, and other basic IB functions.

%package -n libibverbs
Summary: A library and drivers for direct userspace use of RDMA (InfiniBand/iWARP/RoCE) hardware
Provides: libcxgb4 = %{version}-%{release}
Obsoletes: libcxgb4 < %{version}-%{release}
Provides: libefa = %{version}-%{release}
Obsoletes: libefa < %{version}-%{release}
Provides: libhfi1 = %{version}-%{release}
Obsoletes: libhfi1 < %{version}-%{release}
Provides: libirdma = %{version}-%{release}
Obsoletes: libirdma < %{version}-%{release}
Provides: libmlx4 = %{version}-%{release}
Obsoletes: libmlx4 < %{version}-%{release}
%ifnarch s390
Provides: libmlx5 = %{version}-%{release}
Obsoletes: libmlx5 < %{version}-%{release}
%endif
Provides: librxe = %{version}-%{release}
Obsoletes: librxe < %{version}-%{release}

%description -n libibverbs
libibverbs is a library that allows userspace processes to use RDMA
"verbs" as described in the InfiniBand Architecture Specification and
the RDMA Protocol Verbs Specification.  This includes direct hardware
access from userspace to InfiniBand/iWARP adapters (kernel bypass) for
fast path operations.

Device-specific plug-in ibverbs userspace drivers are included:

- libbxnt_re: Broadcom NetXtreme-E RoCE HCA
- libcxgb4: Chelsio T4 iWARP HCA
- libefa: Amazon Elastic Fabric Adapter
- libhfi1: Intel Omni-Path HFI
- libhns: HiSilicon Hip06 SoC
- libirdma: Intel Ethernet Connection RDMA
- libmlx4: Mellanox ConnectX-3 InfiniBand HCA
- libmlx5: Mellanox Connect-IB/X-4+ InfiniBand HCA
- libqedr: QLogic QL4xxx RoCE HCA
- librxe: A software implementation of the RoCE protocol
- libsiw: A software implementation of the iWarp protocol
- libvmw_pvrdma: VMware paravirtual RDMA device

%package -n libibverbs-utils
Summary: Examples for the libibverbs library
Requires: libibverbs%{?_isa} = %{version}-%{release}
# rxe_cfg uses commands provided by these packages
Requires: iproute
Requires: ethtool

%description -n libibverbs-utils
Useful libibverbs example programs such as ibv_devinfo, which
displays information about RDMA devices.

%package -n ibacm
Summary: InfiniBand Communication Manager Assistant
%{?systemd_requires}
Requires: libibumad%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n ibacm
The ibacm daemon helps reduce the load of managing path record lookups on
large InfiniBand fabrics by providing a user space implementation of what
is functionally similar to an ARP cache.  The use of ibacm, when properly
configured, can reduce the SA packet load of a large IB cluster from O(n^2)
to O(n).  The ibacm daemon is started and normally runs in the background,
user applications need not know about this daemon as long as their app
uses librdmacm to handle connection bring up/tear down.  The librdmacm
library knows how to talk directly to the ibacm daemon to retrieve data.

%package -n iwpmd
Summary: iWarp Port Mapper userspace daemon
%{?systemd_requires}

%description -n iwpmd
iwpmd provides a userspace service for iWarp drivers to claim
tcp ports through the standard socket interface.

%package -n libibumad
Summary: OpenFabrics Alliance InfiniBand umad (userspace management datagram) library

%description -n libibumad
libibumad provides the userspace management datagram (umad) library
functions, which sit on top of the umad modules in the kernel. These
are used by the IB diagnostic and management tools, including OpenSM.

%package -n librdmacm
Summary: Userspace RDMA Connection Manager
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n librdmacm
librdmacm provides a userspace RDMA Communication Management API.

%package -n librdmacm-utils
Summary: Examples for the librdmacm library
Requires: librdmacm%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n librdmacm-utils
Example test programs for the librdmacm library.

%package -n srp_daemon
Summary: Tools for using the InfiniBand SRP protocol devices
Obsoletes: srptools <= 1.0.3
Provides: srptools = %{version}-%{release}
Obsoletes: openib-srptools <= 0.0.6
%{?systemd_requires}
Requires: libibumad%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n srp_daemon
In conjunction with the kernel ib_srp driver, srp_daemon allows you to
discover and use SCSI devices via the SCSI RDMA Protocol over InfiniBand.

%if %{with_pyverbs}
%package -n python3-pyverbs
Summary: Python3 API over IB verbs
%{?python_provide:%python_provide python3-pyverbs}
Requires: librdmacm%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n python3-pyverbs
Pyverbs is a Cython-based Python API over libibverbs, providing an
easy, object-oriented access to IB verbs.
%endif

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch300 -p1
%patch301 -p1
%if 0%{?fedora}
%patch9998 -p1
%endif
%if 0%{?rhel}
%patch9000 -p1
%patch9999 -p1
%endif

%build

# New RPM defines _rundir, usually as /run
%if 0%{?_rundir:1}
%else
%define _rundir /var/run
%endif

%{!?EXTRA_CMAKE_FLAGS: %define EXTRA_CMAKE_FLAGS %{nil}}

# Pass all of the rpm paths directly to GNUInstallDirs and our other defines.
%cmake %{CMAKE_FLAGS} \
         -DCMAKE_BUILD_TYPE=Release \
         -DCMAKE_INSTALL_BINDIR:PATH=%{_bindir} \
         -DCMAKE_INSTALL_SBINDIR:PATH=%{_sbindir} \
         -DCMAKE_INSTALL_LIBDIR:PATH=%{_libdir} \
         -DCMAKE_INSTALL_LIBEXECDIR:PATH=%{_libexecdir} \
         -DCMAKE_INSTALL_LOCALSTATEDIR:PATH=%{_localstatedir} \
         -DCMAKE_INSTALL_SHAREDSTATEDIR:PATH=%{_sharedstatedir} \
         -DCMAKE_INSTALL_INCLUDEDIR:PATH=%{_includedir} \
         -DCMAKE_INSTALL_INFODIR:PATH=%{_infodir} \
         -DCMAKE_INSTALL_MANDIR:PATH=%{_mandir} \
         -DCMAKE_INSTALL_SYSCONFDIR:PATH=%{_sysconfdir} \
         -DCMAKE_INSTALL_SYSTEMD_SERVICEDIR:PATH=%{_unitdir} \
         -DCMAKE_INSTALL_INITDDIR:PATH=%{_initrddir} \
         -DCMAKE_INSTALL_RUNDIR:PATH=%{_rundir} \
         -DCMAKE_INSTALL_DOCDIR:PATH=%{_docdir}/%{name} \
         -DCMAKE_INSTALL_UDEV_RULESDIR:PATH=%{_udevrulesdir} \
         -DCMAKE_INSTALL_PERLDIR:PATH=%{perl_vendorlib} \
         -DENABLE_IBDIAGS_COMPAT:BOOL=False \
%if %{with_static}
         -DENABLE_STATIC=1 \
%endif
         %{EXTRA_CMAKE_FLAGS} \
%if %{defined __python3}
         -DPYTHON_EXECUTABLE:PATH=%{__python3} \
         -DCMAKE_INSTALL_PYTHON_ARCH_LIB:PATH=%{python3_sitearch} \
%endif
%if %{with_pyverbs}
         -DNO_PYVERBS=0
%else
         -DNO_PYVERBS=1
%endif
%make_jobs

%install
%cmake_install

mkdir -p %{buildroot}/%{_sysconfdir}/rdma

# Red Hat specific glue
%global dracutlibdir %{_prefix}/lib/dracut
%global sysmodprobedir %{_prefix}/lib/modprobe.d
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{dracutlibdir}/modules.d/05rdma
mkdir -p %{buildroot}%{sysmodprobedir}
install -D -m0644 redhat/rdma.mlx4.conf %{buildroot}/%{_sysconfdir}/rdma/mlx4.conf
install -D -m0755 redhat/rdma.modules-setup.sh %{buildroot}%{dracutlibdir}/modules.d/05rdma/module-setup.sh
install -D -m0644 redhat/rdma.mlx4.sys.modprobe %{buildroot}%{sysmodprobedir}/libmlx4.conf
install -D -m0755 redhat/rdma.mlx4-setup.sh %{buildroot}%{_libexecdir}/mlx4-setup.sh
rm -f %{buildroot}%{_sysconfdir}/rdma/modules/rdma.conf
install -D -m0644 redhat/rdma.conf %{buildroot}%{_sysconfdir}/rdma/modules/rdma.conf
# ibdev2netdev helper script
install -D -m0755 %{SOURCE1} %{buildroot}%{_bindir}/

# rxe_cfg
install -D -m0755 %{SOURCE2} %{buildroot}%{_bindir}/
install -D -m0644 %{SOURCE3} %{buildroot}%{_mandir}/man8/

# ibacm
bin/ib_acme -D . -O
# multi-lib conflict resolution hacks (bug 1429362)
sed -i -e 's|%{_libdir}|/usr/lib|' %{buildroot}%{_mandir}/man7/ibacm_prov.7
sed -i -e 's|%{_libdir}|/usr/lib|' ibacm_opts.cfg
install -D -m0644 ibacm_opts.cfg %{buildroot}%{_sysconfdir}/rdma/

# Delete the package's init.d scripts
rm -rf %{buildroot}/%{_initrddir}/

%ldconfig_scriptlets -n libibverbs

%ldconfig_scriptlets -n libibumad

%ldconfig_scriptlets -n librdmacm

%post -n rdma-core
if [ -x /sbin/udevadm ]; then
/sbin/udevadm trigger --subsystem-match=infiniband --action=change || true
/sbin/udevadm trigger --subsystem-match=net --action=change || true
/sbin/udevadm trigger --subsystem-match=infiniband_mad --action=change || true
fi

%post -n ibacm
%systemd_post ibacm.service
%preun -n ibacm
%systemd_preun ibacm.service
%postun -n ibacm
%systemd_postun_with_restart ibacm.service

%post -n srp_daemon
%systemd_post srp_daemon.service
%preun -n srp_daemon
%systemd_preun srp_daemon.service
%postun -n srp_daemon
%systemd_postun_with_restart srp_daemon.service

%post -n iwpmd
%systemd_post iwpmd.service
%preun -n iwpmd
%systemd_preun iwpmd.service
%postun -n iwpmd
%systemd_postun_with_restart iwpmd.service

%files
%dir %{_sysconfdir}/rdma
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/70-persistent-ipoib.rules
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/rxe.md
%doc %{_docdir}/%{name}/udev.md
%doc %{_docdir}/%{name}/tag_matching.md
%config(noreplace) %{_sysconfdir}/rdma/mlx4.conf
%config(noreplace) %{_sysconfdir}/rdma/modules/infiniband.conf
%config(noreplace) %{_sysconfdir}/rdma/modules/iwarp.conf
%config(noreplace) %{_sysconfdir}/rdma/modules/opa.conf
%config(noreplace) %{_sysconfdir}/rdma/modules/rdma.conf
%config(noreplace) %{_sysconfdir}/rdma/modules/roce.conf
%dir %{_sysconfdir}/modprobe.d
%ifnarch s390
%config(noreplace) %{_sysconfdir}/modprobe.d/mlx4.conf
%endif
%{_unitdir}/rdma-hw.target
%{_unitdir}/rdma-load-modules@.service
%dir %{dracutlibdir}
%dir %{dracutlibdir}/modules.d
%dir %{dracutlibdir}/modules.d/05rdma
%{dracutlibdir}/modules.d/05rdma/module-setup.sh
%dir %{_udevrulesdir}
%{_udevrulesdir}/../rdma_rename
%{_udevrulesdir}/60-rdma-ndd.rules
%{_udevrulesdir}/60-rdma-persistent-naming.rules
%{_udevrulesdir}/75-rdma-description.rules
%{_udevrulesdir}/90-rdma-hw-modules.rules
%{_udevrulesdir}/90-rdma-ulp-modules.rules
%{_udevrulesdir}/90-rdma-umad.rules
%dir %{sysmodprobedir}
%{sysmodprobedir}/libmlx4.conf
%{_libexecdir}/mlx4-setup.sh
%{_sbindir}/rdma-ndd
%{_bindir}/ibdev2netdev
%{_unitdir}/rdma-ndd.service
%{_mandir}/man7/rxe*
%{_mandir}/man8/rdma-ndd.*
%license COPYING.*

%files devel
%doc %{_docdir}/%{name}/MAINTAINERS
%dir %{_includedir}/infiniband
%dir %{_includedir}/rdma
%{_includedir}/infiniband/*
%{_includedir}/rdma/*
%if %{with_static}
%{_libdir}/lib*.a
%endif
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/efadv*
%{_mandir}/man3/ibv_*
%{_mandir}/man3/rdma*
%{_mandir}/man3/umad*
%{_mandir}/man3/*_to_ibv_rate.*
%{_mandir}/man7/rdma_cm.*
%ifnarch s390
%{_mandir}/man3/mlx5dv*
%{_mandir}/man3/mlx4dv*
%{_mandir}/man7/efadv*
%{_mandir}/man7/mlx5dv*
%{_mandir}/man7/mlx4dv*
%endif
%{_mandir}/man3/ibnd_*

%files -n infiniband-diags
%{_sbindir}/ibaddr
%{_mandir}/man8/ibaddr*
%{_sbindir}/ibnetdiscover
%{_mandir}/man8/ibnetdiscover*
%{_sbindir}/ibping
%{_mandir}/man8/ibping*
%{_sbindir}/ibportstate
%{_mandir}/man8/ibportstate*
%{_sbindir}/ibroute
%{_mandir}/man8/ibroute.*
%{_sbindir}/ibstat
%{_mandir}/man8/ibstat.*
%{_sbindir}/ibsysstat
%{_mandir}/man8/ibsysstat*
%{_sbindir}/ibtracert
%{_mandir}/man8/ibtracert*
%{_sbindir}/perfquery
%{_mandir}/man8/perfquery*
%{_sbindir}/sminfo
%{_mandir}/man8/sminfo*
%{_sbindir}/smpdump
%{_mandir}/man8/smpdump*
%{_sbindir}/smpquery
%{_mandir}/man8/smpquery*
%{_sbindir}/saquery
%{_mandir}/man8/saquery*
%{_sbindir}/vendstat
%{_mandir}/man8/vendstat*
%{_sbindir}/iblinkinfo
%{_mandir}/man8/iblinkinfo*
%{_sbindir}/ibqueryerrors
%{_mandir}/man8/ibqueryerrors*
%{_sbindir}/ibcacheedit
%{_mandir}/man8/ibcacheedit*
%{_sbindir}/ibccquery
%{_mandir}/man8/ibccquery*
%{_sbindir}/ibccconfig
%{_mandir}/man8/ibccconfig*
%{_sbindir}/dump_fts
%{_mandir}/man8/dump_fts*
%{_sbindir}/ibhosts
%{_mandir}/man8/ibhosts*
%{_sbindir}/ibswitches
%{_mandir}/man8/ibswitches*
%{_sbindir}/ibnodes
%{_mandir}/man8/ibnodes*
%{_sbindir}/ibrouters
%{_mandir}/man8/ibrouters*
%{_sbindir}/ibfindnodesusing.pl
%{_mandir}/man8/ibfindnodesusing*
%{_sbindir}/ibidsverify.pl
%{_mandir}/man8/ibidsverify*
%{_sbindir}/check_lft_balance.pl
%{_mandir}/man8/check_lft_balance*
%{_sbindir}/dump_lfts.sh
%{_mandir}/man8/dump_lfts*
%{_sbindir}/dump_mfts.sh
%{_mandir}/man8/dump_mfts*
%{_sbindir}/ibstatus
%{_mandir}/man8/ibstatus*
%{_mandir}/man8/infiniband-diags*
%{_libdir}/libibmad*.so.*
%{_libdir}/libibnetdisc*.so.*
%{perl_vendorlib}/IBswcountlimits.pm
%config(noreplace) %{_sysconfdir}/infiniband-diags/error_thresholds
%config(noreplace) %{_sysconfdir}/infiniband-diags/ibdiag.conf

%files -n libibverbs
%dir %{_sysconfdir}/libibverbs.d
%dir %{_libdir}/libibverbs
%{_libdir}/libefa.so.*
%{_libdir}/libibverbs*.so.*
%{_libdir}/libibverbs/*.so
%ifnarch s390
%{_libdir}/libmlx5.so.*
%{_libdir}/libmlx4.so.*
%endif
%config(noreplace) %{_sysconfdir}/libibverbs.d/*.driver
%doc %{_docdir}/%{name}/libibverbs.md

%files -n libibverbs-utils
%{_bindir}/ibv_*
%{_mandir}/man1/ibv_*
%{_bindir}/rxe_cfg
%{_mandir}/man8/rxe*

%files -n ibacm
%config(noreplace) %{_sysconfdir}/rdma/ibacm_opts.cfg
%{_bindir}/ib_acme
%{_sbindir}/ibacm
%{_mandir}/man1/ib_acme.*
%{_mandir}/man7/ibacm.*
%{_mandir}/man7/ibacm_prov.*
%{_mandir}/man8/ibacm.*
%{_unitdir}/ibacm.service
%{_unitdir}/ibacm.socket
%dir %{_libdir}/ibacm
%{_libdir}/ibacm/*
%doc %{_docdir}/%{name}/ibacm.md

%files -n iwpmd
%{_sbindir}/iwpmd
%{_unitdir}/iwpmd.service
%config(noreplace) %{_sysconfdir}/rdma/modules/iwpmd.conf
%config(noreplace) %{_sysconfdir}/iwpmd.conf
%{_udevrulesdir}/90-iwpmd.rules
%{_mandir}/man8/iwpmd.*
%{_mandir}/man5/iwpmd.*

%files -n libibumad
%{_libdir}/libibumad*.so.*

%files -n librdmacm
%{_libdir}/librdmacm*.so.*
%dir %{_libdir}/rsocket
%{_libdir}/rsocket/*.so*
%doc %{_docdir}/%{name}/librdmacm.md
%{_mandir}/man7/rsocket.*

%files -n librdmacm-utils
%{_bindir}/cmtime
%{_bindir}/mckey
%{_bindir}/rcopy
%{_bindir}/rdma_client
%{_bindir}/rdma_server
%{_bindir}/rdma_xclient
%{_bindir}/rdma_xserver
%{_bindir}/riostream
%{_bindir}/rping
%{_bindir}/rstream
%{_bindir}/ucmatose
%{_bindir}/udaddy
%{_bindir}/udpong
%{_mandir}/man1/cmtime.*
%{_mandir}/man1/mckey.*
%{_mandir}/man1/rcopy.*
%{_mandir}/man1/rdma_client.*
%{_mandir}/man1/rdma_server.*
%{_mandir}/man1/rdma_xclient.*
%{_mandir}/man1/rdma_xserver.*
%{_mandir}/man1/riostream.*
%{_mandir}/man1/rping.*
%{_mandir}/man1/rstream.*
%{_mandir}/man1/ucmatose.*
%{_mandir}/man1/udaddy.*
%{_mandir}/man1/udpong.*

%files -n srp_daemon
%config(noreplace) %{_sysconfdir}/srp_daemon.conf
%config(noreplace) %{_sysconfdir}/rdma/modules/srp_daemon.conf
%{_libexecdir}/srp_daemon/start_on_all_ports
%{_unitdir}/srp_daemon.service
%{_unitdir}/srp_daemon_port@.service
%{_sbindir}/ibsrpdm
%{_sbindir}/srp_daemon
%{_sbindir}/srp_daemon.sh
%{_sbindir}/run_srp_daemon
%{_udevrulesdir}/60-srp_daemon.rules
%{_mandir}/man5/srp_daemon.service.5*
%{_mandir}/man5/srp_daemon_port@.service.5*
%{_mandir}/man8/ibsrpdm.8*
%{_mandir}/man8/srp_daemon.8*
%doc %{_docdir}/%{name}/ibsrpdm.md

%if %{with_pyverbs}
%files -n python3-pyverbs
%{python3_sitearch}/pyverbs
%{_docdir}/%{name}/tests/*.py
%endif

%changelog
* Wed Feb 08 2023 Michal Schmidt <mschmidt@redhat.com> - 44.0-2.1
- Do not use unsupported Protect* options in systemd unit files.
- Resolves: rhbz#2141462

* Wed Feb 08 2023 Michal Schmidt <mschmidt@redhat.com> - 44.0-2
- Update to upstream release v44.0
- Resolves: rhbz#2110934, rhbz#2112931, rhbz#2142691

* Fri Aug 05 2022 Michal Schmidt <mschmidt@redhat.com> - 41.0-1
- Update to upstream release v41.0
- Resolves: rhbz#2049518

* Thu Jan 06 2022 Honggang Li <honli@redhat.com> - 37.2-1
- Update to upstream v37.2 release for fixes
- Resolves: bz2008509, bz2024865, bz1915555

* Tue Nov 09 2021 Honggang Li <honli@redhat.com> - 37.1-1
- Update to upstream v37.1 release for features and fixes
- Resolves: bz1982200, bz1990120, bz1982131

* Fri May 14 2021 Honggang Li <honli@redhat.com> - 35.0-1
- Update to upstream v35 release for features and fixes
- Resolves: bz1915311

* Thu Jan 28 2021 Honggang Li <honli@redhat.com> - 32.0-4
- Update to upstream stable release v32.1
- Fix mlx5 pyverbs CQ test
- Resolves: bz1915745, bz1907377

* Tue Dec 22 2020 Honggang Li <honli@redhat.com> - 32.0-3
- libqedr: Set XRC functions only in RoCE mode
- Resolves: bz1894516

* Tue Dec 08 2020 Honggang Li <honli@redhat.com> - 32.0-2
- Backport bug fixes applied after upstream v32.0
- Resolves: bz1902613, bz1875265

* Tue Nov 03 2020 Honggang Li <honli@redhat.com> - 32.0-1
- Update to upstream v32 release for features and fixes
- Support Amazon Elastic Fabric Adapter
- Enable pyverbs
- Add a check for udevadm in the specfile
- Resolves: bz1851721, bz1856076, bz1887396, bz1868804

* Tue Jun 09 2020 Honggang Li <honli@redhat.com> - 29.0-3
- BuildRequires perl-generators
- Backport upstream stable-v29 commits
- Resolves: bz1845420

* Mon May 18 2020 Honggang Li <honli@redhat.com> - 29.0-2
- Suppress ibdev2netdev warning messgae
- Unversioned documentation directory
- Resolves: bz1794904, bz1824853

* Tue Apr 14 2020 Honggang Li <honli@redhat.com> - 29.0-1
- Update to upstream v29 release for features and fixes
- Resolves: bz1790624

* Fri Feb 07 2020 Honggang Li <honli@redhat.com> - 26.0-8
- Fix an ibacm segfault issue for dual port HCA support IB and Ethernet
- Resolves: bz1793736

* Tue Dec 17 2019 Honggang Li <honli@redhat.com> - 26.0-7
- Build with Ninja.
- Resolves: bz1783254

* Fri Dec 13 2019 Honggang Li <honli@redhat.com> - 26.0-6
- Remove dangling symlink
- Resolves: bz1782828

* Wed Dec 11 2019 Honggang Li <honli@redhat.com> - 26.0-5
- Remove EFA driver
- Fix rpm dependency issue
- Resolves: bz1781454, bz1781457

* Mon Dec 09 2019 Honggang Li <honli@redhat.com> - 26.0-4
- libbnxt_re support for some new device ids and generation id
- Resolves: bz1779948

* Tue Nov 19 2019 Jarod Wilson <jarod@redhat.com> - 26.0-3
- Make rdma-core-devel Obsoletes infiniband-diags due to man3/ibnd_*
- Related: rhbz#1722257

* Thu Nov 14 2019 Jarod Wilson <jarod@redhat.com> - 26.0-2
- Add Obsoletes/Provides pair for infiniband-diags-devel
- Pull in upstream stable-v26 branch patches
- Fix %%postun scriptlet failures by removing superfluous -p options
- Add new BuildRequires: on pandoc
- Related: rhbz#1722257

* Thu Nov 14 2019 Jarod Wilson <jarod@redhat.com> - 26.0-1
- Update to upstream v26 release for features and fixes
- Resolves: rhbz#1722257

* Tue Jul 23 2019 Jarod Wilson <jarod@redhat.com> - 24.0-1
- Update to upstream v24 release for features and fixes

* Mon Jun 24 2019 Jarod Wilson <jarod@redhat.com> - 22.3-1
- Update to upstream v22.3 stable release for fixes
- Enable support for Broadcom 57500 hardware
- Enable support for Mellanox ConnectX-6 DX hardware
- Resolves: rhbz#1678276
- Resolves: rhbz#1687435

* Thu Jan 10 2019 Jarod Wilson <jarod@redhat.com> - 22-2
- Fix up covscan shellcheck warnings in ibdev2netdev
- Related: rhbz#1643904

* Thu Jan 10 2019 Jarod Wilson <jarod@redhat.com> - 22-1
- Update to upstream v22 release for features and fixes
- Include legacy ibdev2netdev helper script
- Resolves: rhbz#1643904

* Tue Nov 27 2018 Jarod Wilson <jarod@redhat.com> - 19.1-1
- Update to v19.1 stable branch release
- Fix SRQ support in libi40iw
- Backport libqedr support for SRQ
- Resolves: rhbz#1639692
- Switch rxe_cfg from ifconfig to iproute2
- Resolves: rhbz#1640637

* Thu Aug 30 2018 Jarod Wilson <jarod@redhat.com> - 19-3
- Drop R: initscripts, since we've removed initscripts
- Resolves: rhbz#1610284

* Fri Aug  3 2018 Florian Weimer <fweimer@redhat.com> - 19-2
- Honor %%{valgrind_arches}

* Thu Jul 19 2018 Jarod Wilson <jarod@redhat.com> 19-1
- Rebase to upstream rdma-core v19 release

* Mon Jul 02 2018 Jarod Wilson <jarod@redhat.com> 18.1-3
- Adjust python deps for python3-only world

* Thu Jun 21 2018 Jarod Wilson <jarod@redhat.com> 18.1-2
- Disable nes, mthca and ipath libibverbs providers, this
  old hardware is no longer supported, and fix disabling
  of cxgb3 and ocrdma

* Fri Jun 15 2018 Jarod Wilson <jarod@redhat.com> 18.1-1
- Rebase to upstream rdma-core v18.1 stable release

* Thu May 03 2018 Jarod Wilson <jarod@redhat.com> 17.1-2
- Match kernel ABI with kernel v4.17 for 32-on-64bit compatibility

* Mon Apr 16 2018 Jarod Wilson <jarod@redhat.com> 17.1-1
- Rebase to upstream rdma-core v17.1 stable release
- No more libibcm or ib sysv initscripts
- Remove ibverbs provider for unsupported CXGB3 devices
- Remove ibverbs provider for unsupported OCRDMA devices
- Resolves: rhbz#1492324
- Resolves: rhbz#1492924
- Resolves: rhbz#1503621
- Resolves: rhbz#1504528
- Resolves: rhbz#1504581
- Resolves: rhbz#1503723

* Tue Feb 27 2018 Jarod Wilson <jarod@redhat.com> 15-7
- i40iw: revoke systemd udev rules auto-load on i40e hardware, due to
  causing problems with suspend and resume, and fall back to load via
  systemd rdma initscript.
- Resolves: rhbz#1561566

* Mon Feb 19 2018 Jarod Wilson <jarod@redhat.com> 15-6
- libbnxt_re: fix lat test failure in event mode
- Resolves: rhbz#1545248

* Tue Feb 06 2018 Jarod Wilson <jarod@redhat.com> 15-5
- libmlx4: report RSS caps for improved DPDK support
- Fix double mutex unlock in iwpmd
- Resolves: rhbz#1527350
- Resolves: rhbz#1542362

* Mon Jan 15 2018 Jarod Wilson <jarod@redhat.com> 15-4
- Add support for extended join multicast API in librdmacm
- Add support for striding RQ on mlx5
- Resolves: rhbz#1515487, rhbz#1516571

* Tue Dec 26 2017 Honggang Li <honli@redhat.com> 15-3
- srp_daemon: Don't create async_ev_thread if only run once
- srp_daemon: Remove unsupported systemd configurations
- srp_daemon: Start srp_daemon service after network target
- Resolves: bz1525193
- Resolves: bz1528671

* Mon Nov 13 2017 Jarod Wilson <jarod@redhat.com> 15-2
- Fix ibacm segfault and improper multicast handling
- Resolves: rhbz#1502745
- Resolves: rhbz#1502759

* Fri Sep 22 2017 Jarod Wilson <jarod@redhat.com> 15-1
- Update to upstream v15 release
- Resolves: rhbz#1494607

* Wed Aug 09 2017 Jarod Wilson <jarod@redhat.com> - 14-4
- Make use of systemd_requires, own srp_daemon dir

* Tue Aug 01 2017 Jarod Wilson <jarod@redhat.com> - 14-3
- Revert work-around for ppc64le library issues
- Add Obsoletes/Provides for libusnic_verbs

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 25 2017 Jarod Wilson <jarod@redhat.com> - 14-1
- Update to upstream v14 release
- Sync packaging updates from RHEL and upstream

* Tue May 30 2017 Jarod Wilson <jarod@redhat.com> 13-7
- Add support for mlx5 Expand raw packet capabilities
- Resolves: rhbz#1456561

* Mon May 22 2017 Jarod Wilson <jarod@redhat.com> 13-6
- Clean up htonll/ntohll handling for opa-ff/infiniband-diags compile
- Add necessary Provides/Obsoletes for old -static packages
- Remove ibverbs providers that we aren't currently able to support
- Resolves: rhbz#1453096, rhbz#1451607

* Wed Apr 26 2017 Honggang Li <honli@redhat.com> 13-5
- rdma-ndd: Fix a busy loop for aarch64 platform
- Resolves: bz1442789

* Thu Apr 13 2017 Honggang Li <honli@redhat.com> 13-4
- srp_daemon: Don't rely on attribute offset in get_shared_pkeys
- Resolves: bz1432964

* Mon Apr 03 2017 Jarod Wilson <jarod@redhat.com> - 13-3
- Add necessary Provides/Obsoletes for rdma-ndd (rhbz 1437804)

* Mon Mar 27 2017 Jarod Wilson <jarod@redhat.com> - 13-2
- Build what we can on s390, don't exclude it entirely (rhbz 1434029)

* Tue Mar 21 2017 Jarod Wilson <jarod@redhat.com> - 13-1
- Update to rdma-core v13 release (rhbz 1404035)
- Mellanox mlx5 Direct Verbs support (rhbz 1426430)
- Get build working on s390x, less mlx5 (rhbz 1434029)

* Mon Mar 20 2017 Jarod Wilson <jarod@redhat.com> - 12-5
- Fix up multi-lib conflicts in ibacm files (rhbz 1429362)

* Mon Mar 13 2017 Jarod Wilson <jarod@redhat.com> - 12-4
- Clean up devel files list
- Fix up a few dependencies rpmdiff complained about (rhbz 1404035)
- Add Requires: pciutils for dracut to behave in minimalist cases (rhbz 1429046)
- Adjust Conflicts: on infiniband-diags to match RHEL packaging (rhbz 1428785)

* Mon Mar 06 2017 Jarod Wilson <jarod@redhat.com> - 12-3
- Take libi40iw out of tech-preview state (rhbz 1428930)
- Add ibv_*_pingpong man pages (rhbz 1416541)

* Thu Feb 09 2017 Jarod Wilson <jarod@redhat.com> - 12-2
- Make sure ocrdma module is classified as tech-preview (rhbz 1418224)

* Fri Jan 27 2017 Jarod Wilson <jarod@redhat.com> - 12-1
- Update to upstream final v12 release

* Wed Jan 25 2017 Jarod Wilson <jarod@redhat.com> - 12-0.1.rc3.1
- Initial import to Fedora package database via post-v12-rc3 git snapshot
