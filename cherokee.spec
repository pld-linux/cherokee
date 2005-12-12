Summary:	Cherokee webserver
Summary(pl):	Cherokee - serwer WWW
Name:		cherokee
Version:	0.4.6
%define		pre	20031225
Release:	0.%{pre}.1
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://alobbs.com/cherokee/%{version}/%{name}-%{version}-%{pre}.tar.gz
# Source0-md5:	c3987a0abe0cbbab54d939a2fcc046ba
URL:		http://alobbs.com/cherokee/
BuildRequires:	fcgi-devel
BuildRequires:	gnome-vfs2-devel >= 2.0
# "TLS under construction"
#BuildRequires:	gnutls-devel >= 0.9.99
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	zlib-devel
Provides:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Cherokee is a webserwer:
- FAST and tiny
- Embedable
- Extensible with plug-ins
- Handler-to-path support
- Virtual servers support
- FastCGI support
- Encoders support, including GZip
- Loggers support, including NCSA
- Dynamic / Static plug-in compilation
- Streaming support
- Common tasks: Work as a daemon, MIME types, Log via syslog,
  Keep-alive connections, Runs under a chroot enviroment
- Clean code ;-)
- It's free software

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
	--disable-static \
	--enable-gnomevfs \
	--enable-tls
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# modules dlopened by *.so
rm -f $RPM_BUILD_ROOT%{_libdir}/cherokee/lib*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cherokee
%dir %{_sysconfdir}/cherokee
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cherokee/cherokee.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cherokee/icons.conf
%attr(755,root,root) %{_libdir}/libcherokee.so.*.*.*
%dir %{_libdir}/cherokee
%attr(755,root,root) %{_libdir}/cherokee/libcherokee_*.so*
%{_datadir}/cherokee
%{_mandir}/man1/cherokee.1*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cherokee-config
%attr(755,root,root) %{_libdir}/libcherokee.so
%{_libdir}/libcherokee.la
%{_includedir}/cherokee
%{_pkgconfigdir}/cherokee.pc
%{_aclocaldir}/cherokee.m4
%{_mandir}/man1/cherokee-config.1*
