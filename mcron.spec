# TODO
# - mcron.{init,crontab} not in CVS
Summary:	Cron daemon
Summary(fr.UTF-8):	Démon cron
Summary(pl.UTF-8):	Demon cron
Name:		mcron
Version:	1.0.6
Release:	1
License:	GPL
Group:		Daemons
Source0:	http://ftp.gnu.org/gnu/mcron/%{name}-%{version}.tar.gz
# Source0-md5:	c228b01d14673e8d181376b9549eb1f8
#Source1:	%{name}.init
Source2:	cron.logrotate
Source3:	cron.sysconfig
#Source4:	%{name}.crontab
URL:		http://www.gnu.org/software/mcron/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	guile-devel
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
formacie Vixie) dla nieskończonej elastyczności w podawaniu zadań do
uruchomienia.

%prep
%setup -q
sed -i -e 's#/etc/crontab#/etc/cron.d/system#g' *

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-spool-dir=/var/spool/cron \
	--with-socket-file=/var/run/mcron.sock \
	--with-allow-file=/etc/cron/cron.allow \
	--with-deny-file=/etc/cron/cron.deny
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/{log,spool/cron} \
	$RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_infodir}} \
	$RPM_BUILD_ROOT/etc/{rc.d/init.d,logrotate.d,sysconfig} \
	$RPM_BUILD_ROOT%{_sysconfdir}/{cron,cron.{d,hourly,daily,weekly,monthly}}

#install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/crond
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/cron
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/cron
#install %{SOURCE4} $RPM_BUILD_ROOT/etc/cron.d/crontab

install mcron $RPM_BUILD_ROOT%{_sbindir}
ln -s mcron $RPM_BUILD_ROOT%{_sbindir}/crond
ln -s ../sbin/mcron $RPM_BUILD_ROOT%{_bindir}/crontab

install mcron.info $RPM_BUILD_ROOT%{_infodir}/%{name}.info

cat > $RPM_BUILD_ROOT%{_sysconfdir}/cron/cron.allow << 'EOF'
# cron.allow	This file describes the names of the users which are
#		allowed to use the local cron daemon
root
EOF

cat > $RPM_BUILD_ROOT%{_sysconfdir}/cron/cron.deny << 'EOF'
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
%doc AUTHORS NEWS ChangeLog README TODO
%attr(640,root,crontab) %config(noreplace,missingok) %verify(not md5 mtime size) %{_sysconfdir}/cron/cron.allow
%attr(640,root,crontab) %config(noreplace,missingok) %verify(not md5 mtime size) %{_sysconfdir}/cron/cron.deny
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/cron
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cron
%attr(755,root,root) %{_bindir}/crontab
%attr(755,root,root) %{_sbindir}/crond
%attr(755,root,root) %{_sbindir}/mcron
%dir %attr(1730,root,root) /var/spool/cron
%{_infodir}/mcron.info*
