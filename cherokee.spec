#
# Conditional build:
%bcond_without	geoip		# without GeoIP support
%bcond_without	gnutls		# build with tls=gnutls
%bcond_with	openssl		# build with tls=openssl
#
%if %{with gnutls} || %{with openssl}
%define	with_tls 1
%endif
Summary:	Fast, Flexible and Lightweight Web server
Summary(pl.UTF-8):	Cherokee - serwer WWW
Name:		cherokee
Version:	0.99.29
Release:	0.1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.cherokee-project.com/download/0.99/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	236f17981c0c8908f6911fda239fc3a4
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
Patch1:		%{name}-php-path.patch
Patch2:		%{name}-panic_path.patch
URL:		http://www.cherokee-project.com/
%{?with_geoip:BuildRequires:	GeoIP-devel}
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_gnutls:BuildRequires:	gnutls-devel >= 0.9.99}
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel
%{?with_openssl:BuildRequires:	openssl-devel}
BuildRequires:	pam-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	python-docutils
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post,preun):	rc-scripts
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
Suggests:	php-fcgi
Provides:	group(cherokee)
Provides:	group(http)
Provides:	user(cherokee)
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/cherokee
%define		_wwwhome	/home/services/%{name}
%define		_wwwroot	%{_wwwhome}/html

%description
Cherokee is a flexible, very fast, lightweight Web server. It is
implemented entirely in C, and has no dependencies beyond a standard C
library. It is embeddable and extensible with plug-ins. It supports
on-the-fly configuration by reading files or strings, TLS/SSL (via
GNUTLS or OpenSSL), virtual hosts, authentication, cache friendly
features, PHP, custom error management, and much more.

%description -l pl.UTF-8
Cherokee to elastyczny, bardzo szybki i lekki serwer WWW. Jest
zaimplementowany całkowicie w C i nie ma zależności poza standardową
biblioteką C. Jest osadzalny i rozbudowywalny poprzez wtyczki.
Obsługuje konfigurację w locie poprzez odczyt plików lub łańcuchów
znaków, TLS/SSL (poprzez GNUTLS lub OpenSSL), hosty wirtualne,
uwierzytelnianie, opcje związane z pamięcią podręczną, PHP, własne
zarządzanie błędami i wiele więcej.

%package libs
Summary:	Cherokee web server libraries
Summary(pl.UTF-8):	Biblioteki serwera WWW Cherokee
Group:		Libraries

%description libs
Cherokee web server libraries.

%description libs -l pl.UTF-8
Biblioteki serwera WWW Cherokee.

%package devel
Summary:	Header files for Cherokee web server
Summary(pl.UTF-8):	Pliki nagłówkowe dla serwera WWW Cherokee
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for Cherokee web server.

%description devel -l pl.UTF-8
Pliki nagłówkowe dla serwera WWW Cherokee.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-static \
	--enable-os-string="PLD Linux" \
	%{?with_tls:--enable-tls=%{?with_gnutls:gnutls}%{?with_openssl:openssl}} \
	--sysconfdir=/etc \
	--with-wwwroot=%{_wwwroot} \
	%{!?with_geoip:--without-geoip} \
	PHPCGI=%{_bindir}/php.fcgi

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{pam.d,sysconfig,rc.d/init.d},/var/log/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

# users don't need this
mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/cherokee-panic

# modules dlopened by *.so
rm -f $RPM_BUILD_ROOT%{_libdir}/cherokee/lib*.la

# unify manual dir
rm -rf html
mv $RPM_BUILD_ROOT%{_docdir}/%{name} html

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 161 cherokee
%groupadd -g 51 http
%useradd -u 161 -d %{_wwwhome} -c "Cherokee User" -g cherokee cherokee
%addusertogroup cherokee http

%post
/sbin/chkconfig --add %{name}
%service %{name} restart "Cherokee webserver"
exit 0

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove cherokee
	%groupremove cherokee
	%groupremove http
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog TODO html contrib/*to*.py
%dir %attr(750,root,root) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cherokee.conf
%dir %attr(750,root,root) %{_sysconfdir}/ssl

%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/cherokee
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cherokee
%attr(754,root,root) /etc/rc.d/init.d/cherokee

%attr(755,root,root) %{_bindir}/cget
%attr(755,root,root) %{_bindir}/cherokee-tweak
%attr(755,root,root) %{_bindir}/spawn-fcgi
%attr(755,root,root) %{_sbindir}/cherokee
%attr(755,root,root) %{_sbindir}/cherokee-admin
%attr(755,root,root) %{_sbindir}/cherokee-panic
%attr(755,root,root) %{_sbindir}/cherokee-worker

%dir %{_libdir}/cherokee
%attr(755,root,root) %{_libdir}/cherokee/libplugin_admin.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_and.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_cgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_combined.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_common.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_custom_error.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_dbslayer.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_deflate.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_directory.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_dirlist.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_error_nn.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_error_redir.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_extensions.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_fastcgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_fcgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_file.so
%{?with_geoip:%attr(755,root,root) %{_libdir}/cherokee/libplugin_geoip.so}
%attr(755,root,root) %{_libdir}/cherokee/libplugin_gzip.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_header.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_htdigest.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_htpasswd.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_ldap.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_mirror.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_mysql.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_ncsa.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_not.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_or.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_pam.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_phpcgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_plain.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_proxy.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_redir.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_request.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_round_robin.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_scgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_server_info.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_w3c.so

%{_mandir}/man1/cget.1*
%{_mandir}/man1/cherokee.1*
%{_mandir}/man1/cherokee-admin.1*
%{_mandir}/man1/cherokee-tweak.1*
%{_mandir}/man1/cherokee-worker.1*
# Conflicts: lighttpd
#%%{_mandir}/man1/spawn-fcgi.1*

%dir %{_datadir}/cherokee
%dir %{_datadir}/cherokee/admin
%{_datadir}/cherokee/admin/cherokee.conf.sample
%{_datadir}/cherokee/admin/*.html
%attr(755,root,root) %{_datadir}/cherokee/admin/*.py
%{_datadir}/cherokee/admin/static
%{_datadir}/cherokee/deps
%{_datadir}/cherokee/icons
%{_datadir}/cherokee/mime_types.txt
%{_datadir}/cherokee/themes

%dir %{_wwwhome}
%dir %{_wwwroot}
%config(missingok) %{_wwwroot}/*

%dir %attr(750,cherokee,logs) /var/log/%{name}

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcherokee-base.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-base.so.0
%attr(755,root,root) %{_libdir}/libcherokee-client.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-client.so.0
%attr(755,root,root) %{_libdir}/libcherokee-config.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-config.so.0
%attr(755,root,root) %{_libdir}/libcherokee-server.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libcherokee-server.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cherokee-config
%attr(755,root,root) %{_libdir}/libcherokee-base.so
%attr(755,root,root) %{_libdir}/libcherokee-client.so
%attr(755,root,root) %{_libdir}/libcherokee-config.so
%attr(755,root,root) %{_libdir}/libcherokee-server.so
%{_libdir}/libcherokee-base.la
%{_libdir}/libcherokee-client.la
%{_libdir}/libcherokee-config.la
%{_libdir}/libcherokee-server.la
%{_includedir}/cherokee
%{_pkgconfigdir}/cherokee.pc
%{_aclocaldir}/cherokee.m4
%{_mandir}/man1/cherokee-config.1*
