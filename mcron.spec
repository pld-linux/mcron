# TODO
# - teach mcron to use /etc/cron.d
# - mcron.{init,crontab} not in git
Summary:	Cron daemon
Summary(fr.UTF-8):	Démon cron
Summary(pl.UTF-8):	Demon cron
Name:		mcron
Version:	1.1.3
Release:	0.1
License:	GPL v3+
Group:		Daemons
Source0:	https://ftp.gnu.org/gnu/mcron/%{name}-%{version}.tar.gz
# Source0-md5:	53d138f8569bc8c6269791aeb5fa3789
#Source1:	%{name}.init
Source2:	cron.logrotate
Source3:	cron.sysconfig
#Source4:	%{name}.crontab
Patch0:		%{name}-guile.patch
Patch1:		%{name}-info.patch
URL:		http://www.gnu.org/software/mcron/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake >= 1:1.11
BuildRequires:	guile-devel >= 5:2.0
BuildRequires:	help2man
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
BuildRequires:	texinfo
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	/bin/run-parts
Requires:	rc-scripts
Provides:	crondaemon
Provides:	crontabs = 1.7
Provides:	group(crontab)
Obsoletes:	crondaemon
Obsoletes:	crontabs
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The GNU package mcron (Mellor's cron) is a 100% compatible replacement
for Vixie cron. It is written in pure Guile, and allows configuration
files to be written in scheme (as well as Vixie's original format) for
infinite flexibility in specifying when jobs should be run.

%description -l pl.UTF-8
Pakiet GNU mcron (Mellor's cron) jest w 100% kompatybilnym
zamiennikiem Vixie crona. Jest napisany w czystym Guile i pozwala na
pisanie plików konfiguracyjnych w scheme (a także w oryginalnym
formacie Vixie), co daje nieskończoną elastyczność w określaniu zadań
do uruchomienia.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

# XXX: this is wrong, /etc/cron.d _directory_ should be processed instead of single file!
%{__sed} -i -e 's#/etc/crontab#/etc/cron.d/crontab#g' \
	src/mcron/scripts/cron.scm \
	src/mcron/utils.scm \
	src/mcron/vixie-specification.scm \
	doc/cron.8 \
	doc/mcron.texi

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-silent-rules \
	--with-allow-file=/etc/cron/cron.allow \
	--with-deny-file=/etc/cron/cron.deny \
	--with-sendmail="/usr/lib/sendmail -t" \
	--with-socket-file=/var/run/mcron.sock \
	--with-spool-dir=/var/spool/cron
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/{log,spool/cron} \
	$RPM_BUILD_ROOT/etc/{cron,cron.{d,hourly,daily,weekly,monthly},rc.d/init.d,logrotate.d,sysconfig} \

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/crond
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/cron
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/cron
#install %{SOURCE4} $RPM_BUILD_ROOT/etc/cron.d/crontab

cat > $RPM_BUILD_ROOT/etc/cron/cron.allow << 'EOF'
# cron.allow	This file describes the names of the users which are
#		allowed to use the local cron daemon
root
EOF

cat > $RPM_BUILD_ROOT/etc/cron/cron.deny << 'EOF'
# cron.deny	This file describes the names of the users which are
#		NOT allowed to use the local cron daemon
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 117 -r -f crontab

%post
/sbin/chkconfig --add crond
%service crond restart "cron daemon"
umask 027
touch /var/log/cron
chgrp crontab /var/log/cron
chmod 660 /var/log/cron
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%preun
if [ "$1" = "0" ]; then
	%service crond stop
	/sbin/chkconfig --del crond
fi

%postun
if [ "$1" = "0" ]; then
	%groupremove crontab
fi
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README TODO
%dir /etc/cron
%attr(640,root,crontab) %config(noreplace,missingok) %verify(not md5 mtime size) /etc/cron/cron.allow
%attr(640,root,crontab) %config(noreplace,missingok) %verify(not md5 mtime size) /etc/cron/cron.deny
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/cron
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cron
%attr(755,root,root) %{_bindir}/crontab
%attr(755,root,root) %{_bindir}/mcron
%attr(755,root,root) %{_sbindir}/cron
%{_libdir}/guile/2.*/site-ccache/mcron
%{_datadir}/guile/site/2.*/mcron
%dir %attr(1730,root,root) /var/spool/cron
%{_mandir}/man1/crontab.1*
%{_mandir}/man1/mcron.1*
%{_mandir}/man8/cron.8*
%{_infodir}/mcron.info*
