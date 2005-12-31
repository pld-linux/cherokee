%bcond_with	php		# adds PHP support
%bcond_with	mono	# adds ASPX support
%bcond_with	gnomevfs	# compile the gnomevfs handler (broken)
%bcond_without	gnutls	# build with tls=gnutls
%bcond_with	openssl	# build with tls=openssl
#
%if %{with gnutls} || %{with openssl}
%define	with_tls 1
%endif
Summary:	Fast, Flexible and Lightweight Web server
Summary(pl):	Cherokee - serwer WWW
Name:		cherokee
Version:	0.4.29
Release:	0.4
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.0x50.org/download/0.4/0.4.29/%{name}-%{version}.tar.gz
# Source0-md5:	854e6e61a69781746496012658d8ef98
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://www.0x50.org/
BuildRequires:	fcgi-devel
%{?with_gnomevfs:BuildRequires:	gnome-vfs2-devel >= 2.0}
%{?with_gnutls:BuildRequires:	gnutls-devel >= 0.9.99}
%{?with_openssl:BuildRequires:	openssl-devel}
BuildRequires:	pam-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	zlib-devel
Requires(post):	/sbin/ldconfig
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/cherokee
%define		_wwwhome	/home/services/%{name}
%define		_wwwroot	%{_wwwhome}/html

%description
Cherokee is a flexible, very fast, lightweight Web server. It is
implemented entirely in C, and has no dependencies beyond a standard C
library. It is embeddable and extensible wi th plug-ins. It supports
on-the-fly configuration by reading files or strings, TLS/SSL (via
GNUTLS or OpenSSL), virtual hosts, authentication, cache friendly
features, PHP, custom error management, and much more.

%description -l pl
Cherokee to serwer WWW:
- SZYBKI i ma³y
- mo¿liwy do wbudowania
- rozszerzalny przy pomocy wtyczek
- z mo¿liwo¶ci± przypisania sposobu obs³ugi do ¶cie¿ek
- z obs³ug± serwerów wirtualnych
- z obs³ug± FastCGI
- z obs³ug± kodowania, w tym GZipa
- z obs³ug± loggerów, w tym NCSA
- z dynamiczn± lub statyczn± kompilacj± wtyczek
- z obs³ug± strumieni
- wykonuj±cy popularne zadania: praca jako demon, obs³uga typów MIME,
  logowanie poprzez sysloga, po³±czenia keep-alive, dzia³anie w
  ¶rodowisku chrootowanym
- o przejrzystym kodzie ;-)
- bêd±cy oprogramowaniem wolnodostêpnym.

%package devel
Summary:	Header files for Cherokee web server
Summary(pl):	Pliki nag³ówkowe dla serwera WWW Cherokee
Group:		Development/Libraries
Requires:	%{name} = %{version}

%description devel
Header files for Cherokee web server.

%description devel -l pl
Pliki nag³ówkowe dla serwera WWW Cherokee.

%prep
%setup -q

%build
%configure \
	--sysconfdir=/etc \
	--with-wwwroot=%{_wwwroot} \
	--disable-static \
	%{?with_gnomevfs:--enable-gnomevfs} \
	%{?with_tls:--enable-tls=%{?with_gnutls:gnutls}%{?with_openssl:openssl}} \
	--enable-pthreads \
	%{?with_php:--with-php=DIR} \
	%{?with_mono:--with-mono=DIR}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

# modules dlopened by *.so
rm -f $RPM_BUILD_ROOT%{_libdir}/cherokee/lib*.la

# unify manual dir
rm -rf html
mv $RPM_BUILD_ROOT%{_docdir}/%{name} html

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add %{name}
%service %{name} restart "Cherokee webserver"

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog TODO html
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cherokee.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icons.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/advanced.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mime.conf
%dir %{_sysconfdir}/mods-available
%dir %{_sysconfdir}/mods-enabled
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mods-available/admin
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mods-available/ssl
%dir %{_sysconfdir}/sites-available
%dir %{_sysconfdir}/sites-enabled
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sites-available/default
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sites-available/example.com
%attr(750,root,root) %dir %{_sysconfdir}/ssl

%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cherokee
%attr(754,root,root) /etc/rc.d/init.d/cherokee

%attr(755,root,root) %{_bindir}/cget
%attr(755,root,root) %{_bindir}/cherokee-panic
%attr(755,root,root) %{_bindir}/cherokee_logrotate
%attr(755,root,root) %{_sbindir}/cherokee

%dir %{_libdir}/cherokee
%attr(755,root,root) %{_libdir}/cherokee/libplugin_cgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_combined.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_common.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_dirlist.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_error_redir.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_fastcgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_file.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_gzip.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_htdigest.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_htpasswd.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_ncsa.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_nn.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_pam.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_phpcgi.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_plain.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_read_config.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_redir.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_server_info.so
%attr(755,root,root) %{_libdir}/cherokee/libplugin_w3c.so
%attr(755,root,root) %{_libdir}/libcherokee-base.so.*.*.*
%attr(755,root,root) %{_libdir}/libcherokee-client.so.*.*.*
%attr(755,root,root) %{_libdir}/libcherokee-config.so.*.*.*
%attr(755,root,root) %{_libdir}/libcherokee-server.so.*.*.*

%{_mandir}/man1/cherokee.1*
%{_mandir}/man1/cget.1*
%{_mandir}/man1/cherokee_logrotate.1*

%{_datadir}/cherokee

%dir %{_wwwhome}
%{_wwwroot}

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cherokee-config

%{_libdir}/libcherokee-base.la
%{_libdir}/libcherokee-client.la
%{_libdir}/libcherokee-config.la
%{_libdir}/libcherokee-server.la

%{_includedir}/cherokee
%{_pkgconfigdir}/cherokee.pc
%{_aclocaldir}/cherokee.m4
%{_mandir}/man1/cherokee-config.1*
