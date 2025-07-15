#
# TODO:
#   - think about moving modules to subpackages. At least, those with extra
#     dependencies.
#   - maybe there is no need to pack *.py (are *.pyc enough?)
#
# Conditional build:
%bcond_without	geoip		# without GeoIP support
%bcond_without	mysql		# without MySQL support
%bcond_without	ldap		# without LDAP support
%bcond_without	ffmpeg		# without ffmpeg support
#
Summary:	Fast, Flexible and Lightweight Web server
Summary(pl.UTF-8):	Cherokee - serwer WWW
Name:		cherokee
Version:	1.2.104
Release:	4
License:	GPL v2
Group:		Networking/Daemons
Source0:	https://github.com/cherokee/webserver/archive/v%{version}.zip
# Source0-md5:	1f4fe0f0317c07b93c9cbbf4f843e724
# the last snapshot from https://github.com/cherokee/CTK
Source1:	CTK-20120806.tar.xz
# Source1-md5:	567f087cd6cdf10b89047535cbe94f8e
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Source4:	%{name}.service
Patch0:		%{name}-config.patch
Patch1:		%{name}-panic_path.patch
Patch2:		ffmpeg0.11.patch
Patch3:		time_t_x32.patch
Patch4:		openssl.patch
Patch5:         build.patch
URL:		http://www.cherokee-project.com/
%{?with_geoip:BuildRequires:	GeoIP-devel}
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_ffmpeg:BuildRequires:	ffmpeg-devel >= 1.0}
BuildRequires:	gettext-tools
BuildRequires:	libtool
%{?with_mysql:BuildRequires:	mysql-devel}
%{?with_ldap:BuildRequires:	openldap-devel}
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:	pcre-devel
BuildRequires:	php(fcgi)
BuildRequires:	pkgconfig
BuildRequires:	python-docutils
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts >= 0.4.3.0
Requires:	systemd-units >= 38
Suggests:	%{name}-admin = %{version}-%{release}
Suggests:	php(fcgi)
Provides:	group(cherokee)
Provides:	group(http)
Provides:	user(cherokee)
Provides:	webserver
Provides:	webserver(indexfile)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/cherokee
%define		_wwwhome	/home/services/%{name}
%define		_wwwroot	%{_wwwhome}/html

%description
Cherokee is a flexible, very fast, lightweight Web server. It is
implemented entirely in C, and has no dependencies beyond a standard C
library. It is embeddable and extensible with plug-ins. It supports
on-the-fly configuration by reading files or strings, TLS/SSL via
OpenSSL, virtual hosts, authentication, cache friendly features, PHP,
custom error management, and much more.

%description -l pl.UTF-8
Cherokee to elastyczny, bardzo szybki i lekki serwer WWW. Jest
zaimplementowany całkowicie w C i nie ma zależności poza standardową
biblioteką C. Jest osadzalny i rozbudowywalny poprzez wtyczki.
Obsługuje konfigurację w locie poprzez odczyt plików lub łańcuchów
znaków, TLS/SSL poprzez OpenSSL, hosty wirtualne, uwierzytelnianie,
opcje związane z pamięcią podręczną, PHP, własne zarządzanie błędami i
wiele więcej.

%package admin
Summary:	Cherokee web server administration interface
Summary(pl.UTF-8):	Interfejs administracyjny serwera WWW Cherokee
Group:		Networking/Daemons
Requires:	%{name} = %{version}-%{release}
Requires:	python
Requires:	python-modules

%description admin
Cherokee web server administration interface.

%description admin -l pl.UTF-8
Interfejs administracyjny serwera WWW Cherokee.

%package devel
Summary:	Header files for Cherokee web server
Summary(pl.UTF-8):	Pliki nagłówkowe dla serwera WWW Cherokee
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for Cherokee web server.

%description devel -l pl.UTF-8
Pliki nagłówkowe dla serwera WWW Cherokee.

%package libs
Summary:	Cherokee web server libraries
Summary(pl.UTF-8):	Biblioteki serwera WWW Cherokee
Group:		Libraries

%description libs
Cherokee web server libraries.

%description libs -l pl.UTF-8
Biblioteki serwera WWW Cherokee.

%prep
%setup -qn webserver-%{version} -a1
%patch -P0 -p1
%patch -P1 -p1
#%%patch2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1

%{__sed} -E -i -e '1s,#!\s*/usr/bin/env\s+python2(\s|$),#!%{__python}\1,' -e '1s,#!\s*/usr/bin/env\s+python(\s|$),#!%{__python}\1,' \
      admin/CTK/CTK-run.pre \
      admin/server.py \
      admin/upgrade_config.py \
      cherokee/cherokee-admin-launcher \
      cherokee/cherokee-tweak

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
po/admin/generate_POTFILESin.py > po/admin/POTFILES.in
%configure \
	--with-php=/usr/bin/php.cgi \
	--disable-static \
	--enable-os-string="PLD Linux" \
	--sysconfdir=/etc \
	--with-wwwroot=%{_wwwroot} \
	--with-wwwuser=cherokee \
	--with-wwwgroup=http \
	%{!?with_geoip:--without-geoip} \
	%{!?with_mysql:--without-mysql} \
	%{!?with_ffmpeg:--without-ffmpeg} \
	%{!?with_ldap:--without-ldap}

# workaround for missing pot file and no way to build it
touch po/admin/cherokee.pot
touch po/admin/*.po

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{pam.d,sysconfig,rc.d/init.d} \
		$RPM_BUILD_ROOT/var/log/%{name} \
		$RPM_BUILD_ROOT%{systemdunitdir}

%{__make} -j1 install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}/cherokee.service

# users don't need this
mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/cherokee-panic

# modules dlopened by *.so
rm -f $RPM_BUILD_ROOT%{_libdir}/cherokee/lib*.la

# unify manual dir
rm -rf html
mv $RPM_BUILD_ROOT%{_docdir}/%{name} html

# provided via %doc
rm $RPM_BUILD_ROOT/etc/cherokee/cherokee.conf.perf_sample

# compile python modules, otherwise *.pyc may get generated on runtime
# and stay after package removal
%py_comp $RPM_BUILD_ROOT%{_datadir}/cherokee/admin/

# seems like this is not needed on Linux
rm $RPM_BUILD_ROOT%{_bindir}/cherokee-macos-askpass

mv $RPM_BUILD_ROOT%{_localedir}/{sv_SE,sv}
%find_lang %{name}


%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 161 cherokee
%groupadd -g 51 http
%useradd -u 161 -d %{_wwwhome} -c "Cherokee User" -g cherokee cherokee
%addusertogroup cherokee http

%post
if [ "$1" = "2" -a -e %{_sysconfdir}/cherokee.conf ]; then
	%{_datadir}/%{name}/admin/upgrade_config.py %{_sysconfdir}/cherokee.conf
fi
/sbin/chkconfig --add %{name}
%service %{name} restart "Cherokee webserver"
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove cherokee
	%groupremove cherokee
	%groupremove http
fi
%systemd_reload

%triggerpostun -- %{name} < 1.2.103-1
%systemd_trigger %{name}.service

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS html performance.conf.sample
%dir %attr(750,root,root) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cherokee.conf

%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/cherokee
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cherokee
%attr(754,root,root) /etc/rc.d/init.d/cherokee
%{systemdunitdir}/%{name}.service

%attr(755,root,root) %{_bindir}/CTK-run
%attr(755,root,root) %{_bindir}/cget
%attr(755,root,root) %{_bindir}/cherokee-tweak
%attr(755,root,root) %{_sbindir}/cherokee
%attr(755,root,root) %{_sbindir}/cherokee-panic
%attr(755,root,root) %{_sbindir}/cherokee-worker

%dir %{_libdir}/cherokee
%attr(755,root,root) %{_libdir}/cherokee/libplugin_admin.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_and.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_authlist.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_bind.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_cgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_combined.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_common.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_custom_error.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_custom.so
%{?with_mysql:%attr(755,root,root) %{_libdir}/cherokee/libplugin_dbslayer.so}
%attr(755,root,root) %{_libdir}/cherokee/libplugin_deflate.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_directory.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_dirlist.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_drop.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_empty_gif.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_error_nn.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_error_redir.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_evhost.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_exists.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_extensions.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_failover.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_fcgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_file.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_from.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_fullpath.so
%{?with_geoip:%attr(755,root,root) %{_libdir}/cherokee/libplugin_geoip.so}
%attr(755,root,root) %{_libdir}/cherokee/libplugin_gzip.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_header.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_htdigest.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_htpasswd.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_ip_hash.so
%{?with_ldap:%attr(755,root,root) %{_libdir}/cherokee/libplugin_ldap.so}
%attr(755,root,root) %{_libdir}/cherokee/libplugin_libssl.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_method.so
%{?with_mysql:%attr(755,root,root) %{_libdir}/cherokee/libplugin_mysql.so}
%attr(755,root,root) %{_libdir}/cherokee/libplugin_ncsa.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_not.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_or.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_pam.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_plain.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_post_report.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_post_track.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_proxy.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_redir.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_rehost.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_render_rrd.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_request.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_round_robin.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_rrd.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_scgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_secdownload.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_server_info.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_ssi.so
%if %{with ffmpeg}
%attr(755,root,root) %{_libdir}/cherokee/libplugin_streaming.so
%endif
%attr(755,root,root) %{_libdir}/cherokee/libplugin_target_ip.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_tls.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_url_arg.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_uwsgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_v_or.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_wildcard.so

%{_mandir}/man1/cget.1*
%{_mandir}/man1/cherokee.1*
%{_mandir}/man1/cherokee-tweak.1*
%{_mandir}/man1/cherokee-worker.1*

%dir %{_datadir}/cherokee
%{_datadir}/cherokee/deps
%{_datadir}/cherokee/icons
%{_datadir}/cherokee/themes

%dir %{_wwwhome}
%dir %{_wwwroot}
%config(missingok) %{_wwwroot}/*

%dir %attr(750,cherokee,logs) /var/log/%{name}

%dir %attr(771,root,cherokee) /var/lib/%{name}
%dir %attr(771,cherokee,cherokee) /var/lib/%{name}/graphs
%dir %attr(771,cherokee,cherokee) /var/lib/%{name}/graphs/images

%files admin -f %{name}.lang
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/cherokee-admin
%attr(755,root,root) %{_bindir}/cherokee-admin-launcher
%{_mandir}/man1/cherokee-admin.1*
%{_mandir}/man1/cherokee-admin-launcher.1*
%dir %{_datadir}/cherokee/admin
%{_datadir}/cherokee/admin/cherokee.conf.sample
%{_datadir}/cherokee/admin/performance.conf.sample
%{_datadir}/cherokee/admin/*.html
%attr(755,root,root) %{_datadir}/cherokee/admin/*.py
%{_datadir}/cherokee/admin/*.pyc
%{_datadir}/cherokee/admin/static
%dir %{_datadir}/cherokee/admin/CTK
%dir %{_datadir}/cherokee/admin/CTK/CTK
%{_datadir}/cherokee/admin/CTK/CTK/*.py
%{_datadir}/cherokee/admin/CTK/CTK/*.pyc
%{_datadir}/cherokee/admin/CTK/static
%dir %{_datadir}/cherokee/admin/plugins
%{_datadir}/cherokee/admin/plugins/*.py
%{_datadir}/cherokee/admin/plugins/*.pyc
%dir %{_datadir}/cherokee/admin/wizards
%{_datadir}/cherokee/admin/wizards/*.py
%{_datadir}/cherokee/admin/wizards/*.pyc
#%dir %{_datadir}/cherokee/admin/market
#%{_datadir}/cherokee/admin/market/*.py
#%{_datadir}/cherokee/admin/market/*.pyc
%dir %{_datadir}/cherokee/admin/icons
%{_datadir}/cherokee/admin/icons/*.png
%{_datadir}/cherokee/admin/icons/*.svg

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcherokee-base.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-base.so.0
%attr(755,root,root) %{_libdir}/libcherokee-client.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-client.so.0
%attr(755,root,root) %{_libdir}/libcherokee-server.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-server.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cherokee-config
%attr(755,root,root) %{_libdir}/libcherokee-base.so
%attr(755,root,root) %{_libdir}/libcherokee-client.so
%attr(755,root,root) %{_libdir}/libcherokee-server.so
%{_libdir}/libcherokee-base.la
%{_libdir}/libcherokee-client.la
%{_libdir}/libcherokee-server.la
%{_includedir}/cherokee
%{_pkgconfigdir}/cherokee.pc
%{_aclocaldir}/cherokee.m4
%{_mandir}/man1/cherokee-config.1*
