%define pre 20031225

Summary:	Cherokee webserver
Name:		cherokee
Version:	0.4.6
Release:	0.%{pre}.1
License:	GPL
Group:	Networking/Daemons
URL:		http://alobbs.com/cherokee
Source0:	ftp://alobbs.com/cherokee/%{version}/%{name}-%{version}-%{pre}.tar.gz
# Source0-md5:	c3987a0abe0cbbab54d939a2fcc046ba
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildRequires:	fcgi-devel
BuildRequires:	gnome-vfs2-devel

%description
- FAST and tiny
- Embedable
- Extensible with plug-ins
- Handler-to-path support
- Virtual servers support
- FastCGI support
- Encoders support: o GZip
- Loggers support: o NCSA
- Dynamic / Static plug-in compilation
- Streaming support
- Common tasks: o Work as a daemon o Mime types o Log via syslog o
  Keep-alive connections o Runs under a chroot enviroment
- Clean code ;-)
- It's free software

%package devel
Summary: headers for cherokee web server
Group: Development/Libraries

%description devel
headers for cherokee web server

%prep
%setup -q

%build
%configure \
	--enable-gnomevfs \
	--enable-tls
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/cherokee
%{_sysconfdir}/cherokee
%{_sysconfdir}/cherokee/cherokee.conf
%dir %{_includedir}/cherokee
%dir %{_libdir}/cherokee
%{_libdir}/cherokee/libcherokee_*
%{_libdir}/libcherokee.*
%{_datadir}/cherokee
%{_mandir}/man1/cherokee.1.gz

%files devel
%attr(755,root,root) %{_bindir}/cherokee-config
%{_includedir}/cherokee/*.h
%{_libdir}/pkgconfig/cherokee.pc
%{_datadir}/aclocal/cherokee.m4
%{_mandir}/man1/cherokee-config.1.gz




%clean
rm -rf $RPM_BUILD_ROOT
