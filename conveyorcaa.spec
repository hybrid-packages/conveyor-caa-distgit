%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global pypi_name conveyorcaa

Name:		conveyorcaa
Epoch:		1
Version:	XXX
Release:	XXX
Summary:	ConveyorAgent

License:	ASL 2.0
URL:   		https://github.com/Hybrid-Cloud/conveyorcaa
Source0:	https://github.com/Hybrid-Cloud/%{name}/%{name}-%{upstream_version}.tar.gz

# Source1:        conveyorcaa-dist.conf
Source2:        conveyorcaa.logrotate
Source3:        conveyorcaa.sudoers

Source10:       conveyorcaa.service

BuildArch:		noarch
BuildRequires:  intltool
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-pbr
BuildRequires:  python-d2to1

Requires:       python-%{pypi_name} = %{epoch}:%{version}-%{release}

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
Requires(pre):    shadow-utils

%description
Conveyor

%package -n python-%{pypi_name}
Summary:        Conveyor Code

Requires:       python-anyjson
Requires:       python-babel
Requires:       python-cryptography >= 1.0
Requires:       python-decorator
Requires:       python-eventlet >= 0.17.4
Requires:       python-glanceclient >= 1:2.0.0
Requires:       python-greenlet
Requires:       python-iso8601 >= 0.1.9
Requires:       python-keystoneclient >= 1:1.6.0
Requires:       python-keystonemiddleware >= 4.0.0
Requires:       python-netaddr
Requires:       python-oslo-cache >= 0.8.0
Requires:       python-oslo-concurrency >= 2.3.0
Requires:       python-oslo-config >= 3.4.0
Requires:       python-oslo-context >= 2.2.0
Requires:       python-oslo-db >= 4.1.0
Requires:       python-oslo-i18n >= 2.1.0
Requires:       python-oslo-log >= 1.14.0
Requires:       python-oslo-messaging >= 4.0.0
Requires:       python-oslo-middleware >= 3.0.0
Requires:       python-oslo-policy >= 0.5.0
Requires:       python-oslo-reports >= 0.6.0
Requires:       python-oslo-rootwrap >= 2.0.0
Requires:       python-oslo-serialization >= 2.1.0
Requires:       python-oslo-service >= 1.0.0
Requires:       python-oslo-utils >= 3.4.0
Requires:       python-oslo-versionedobjects >= 1.4.0
Requires:       python-paste-deploy
Requires:       python-paste
Requires:       python-pbr
Requires:       python-requests
Requires:       python-routes
Requires:       python-six >= 1.9.0
Requires:       python-webob >= 1.2.3

%description -n python-%{pypi_name}
Conveyor Code


%package -n python-%{pypi_name}-tests
Summary:        Conveyor tests
Requires:       python-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n python-%{pypi_name}-tests
Conveyor tests

%prep
%setup -q -n conveyorcaa-%{upstream_version}

find . \( -name .gitignore -o -name .placeholder \) -delete

find conveyorcaa -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +

sed -i 's/%{version}.%{milestone}/%{version}/' PKG-INFO

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Setup directories
install -d -m 750 %{buildroot}%{_sysconfdir}/conveyorcaa
install -d -m 750 %{buildroot}%{_localstatedir}/log/conveyorcaa
install -d -m 755 %{buildroot}%{_sharedstatedir}/conveyorcaa

# Install config files
# install -p -D -m 640 %{SOURCE1} %{buildroot}%{_datarootdir}/conveyorcaa/conveyorcaa-dist.conf
install -p -D -m 755 etc/conveyorcaa/conveyorcaa.conf %{buildroot}%{_sysconfdir}/conveyorcaa/conveyorcaa.conf
install -p -D -m 755 etc/conveyorcaa/conveyorcaa-paste.ini %{buildroot}%{_sysconfdir}/conveyorcaa/conveyorcaa-paste.ini
install -p -D -m 755 etc/conveyorcaa/aws_volume_types.json %{buildroot}%{_sysconfdir}/conveyorcaa/aws_volume_types.json

# Install initscripts for conveyorcaa services
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/conveyorcaa.service

# Install sudoers
install -p -D -m 440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/conveyorcaa

# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/conveyorcaa

# Install pid directory
# install -d -m 755 %{buildroot}%{_localstatedir}/run/conveyorcaa

# Remove unneeded in production stuff
rm -f %{buildroot}%{_bindir}/conveyorcaa-debug
rm -fr %{buildroot}%{python2_sitelib}/run_tests.*
rm -f %{buildroot}/usr/share/doc/conveyorcaa/README*

%pre -n python-%{pypi_name}
getent group conveyorcaa >/dev/null || groupadd -r conveyorcaa
if ! getent passwd conveyorcaa >/dev/null; then
    useradd -r -g conveyorcaa -G conveyorcaa -s /sbin/nologin -c "Conveyor Daemons" conveyorcaa
fi
exit 0

%post
%systemd_post conveyorcaa

%preun
%systemd_preun conveyorcaa

%postun
%systemd_postun_with_restart conveyorcaa

%files
%dir %{_sysconfdir}/conveyorcaa
%config(noreplace) %attr(-, root, conveyorcaa) %{_sysconfdir}/conveyorcaa/conveyorcaa.conf
%config(noreplace) %attr(-, root, conveyorcaa) %{_sysconfdir}/conveyorcaa/conveyorcaa-paste.ini
%config(noreplace) %attr(-, root, conveyorcaa) %{_sysconfdir}/conveyorcaa/aws_volume_types.json
%config(noreplace) %{_sysconfdir}/logrotate.d/conveyorcaa
%config(noreplace) %{_sysconfdir}/sudoers.d/conveyorcaa
# %attr(-, root, conveyorcaa) %{_datadir}/conveyorcaa/conveyorcaa-dist.conf

%dir %attr(0750, conveyorcaa, root) %{_localstatedir}/log/conveyorcaa
# %dir %attr(0755, conveyorcaa, root) %{_localstatedir}/run/conveyorcaacaa

%{_bindir}/*
%{_unitdir}/*.service
# %{_datarootdir}/conveyorcaacaa

%defattr(-, conveyorcaa, conveyorcaa, -)
%dir %{_sharedstatedir}/conveyorcaa

%files -n python-%{pypi_name}
%{?!_licensedir: %global license %%doc}
%license LICENSE
%{python2_sitelib}/conveyorcaa
%{python2_sitelib}/conveyorcaa-*.egg-info
%exclude %{python2_sitelib}/conveyorcaa/tests

%files -n python-%{pypi_name}-tests
%license LICENSE
%{python2_sitelib}/conveyorcaa/tests

%changelog
