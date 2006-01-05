#
# Conditional build:
%bcond_without	php		# adds PHP support
%bcond_with	mono		# adds ASPX support
%bcond_with	gnomevfs	# compile the gnomevfs handler (broken)
%bcond_without	gnutls		# build with tls=gnutls
%bcond_with	openssl		# build with tls=openssl
#
%if %{with gnutls} || %{with openssl}
%define	with_tls 1
%endif
Summary:	Fast, Flexible and Lightweight Web server
Summary(pl):	Cherokee - serwer WWW
Name:		cherokee
Version:	0.4.29
Release:	0.15
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.0x50.org/download/0.4/0.4.29/%{name}-%{version}.tar.gz
# Source0-md5:	854e6e61a69781746496012658d8ef98
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-config.patch
Patch1:		%{name}-php-path.patch
URL:		http://www.0x50.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	fcgi-devel
%{?with_gnomevfs:BuildRequires:	gnome-vfs2-devel >= 2.0}
%{?with_gnutls:BuildRequires:	gnutls-devel >= 0.9.99}
%{?with_openssl:BuildRequires:	openssl-devel}
BuildRequires:	pam-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun):	rc-scripts
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
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

%description -l pl
Cherokee to elastyczny, bardzo szybki i lekki serwer WWW. Jest
zaimplementowany ca³kowicie w C i nie ma zale¿no¶ci poza standardow±
bibliotek± C. Jest osadzalny i rozbudowywalny poprzez wtyczki.
Obs³uguje konfiguracjê w locie poprzez odczyt plików lub ³añcuchów
znaków, TLS/SSL (poprzez GNUTLS lub OpenSSL), hosty wirtualne,
uwierzytelnianie, opcje zwi±zane z pamiêci± podrêczn±, PHP, w³asne
zarz±dzanie b³êdami i wiele wiêcej.

%package devel
Summary:	Header files for Cherokee web server
Summary(pl):	Pliki nag³ówkowe dla serwera WWW Cherokee
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for Cherokee web server.

%description devel -l pl
Pliki nag³ówkowe dla serwera WWW Cherokee.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--sysconfdir=/etc \
	--enable-os-string="PLD Linux" \
	--with-wwwroot=%{_wwwroot} \
	--disable-static \
	%{?with_gnomevfs:--enable-gnomevfs} \
	%{?with_tls:--enable-tls=%{?with_gnutls:gnutls}%{?with_openssl:openssl}} \
	--enable-pthreads \
	%{?with_php:--with-php=%{_prefix}} \
	%{?with_mono:--with-mono=DIR}

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
mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/cherokee_logrotate

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
/sbin/ldconfig
/sbin/chkconfig --add %{name}
%service %{name} restart "Cherokee webserver"
exit 0

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove cherokee
	%groupremove cherokee
	%groupremove http
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog TODO html
%dir %attr(750,root,root) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cherokee.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/icons.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/advanced.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mime.conf
%dir %attr(750,root,root) %{_sysconfdir}/mods-available
%dir %attr(750,root,root) %{_sysconfdir}/mods-enabled
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mods-available/admin
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mods-available/ssl
%dir %attr(750,root,root) %{_sysconfdir}/sites-available
%dir %attr(750,root,root) %{_sysconfdir}/sites-enabled
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sites-available/default
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sites-available/example.com
%config(missingok) %{_sysconfdir}/sites-enabled/default
%dir %attr(750,root,root) %{_sysconfdir}/ssl

%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/cherokee
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cherokee
%attr(754,root,root) /etc/rc.d/init.d/cherokee

%attr(755,root,root) %{_bindir}/cget
%attr(755,root,root) %{_sbindir}/cherokee
%attr(755,root,root) %{_sbindir}/cherokee-panic
%attr(755,root,root) %{_sbindir}/cherokee_logrotate

%dir %{_libdir}/cherokee
%attr(755,root,root) %{_libdir}/cherokee/libplugin_admin.so
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
%dir %{_wwwroot}
%config(missingok) %{_wwwroot}/*

%dir %attr(750,root,logs) /var/log/%{name}

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
