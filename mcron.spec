Summary:	Cron daemon
Summary(fr):	Démon cron
Summary(pl):	Demon cron
Name:		mcron
Version:	1.0.1
Release:	0.1
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.gnu.org/pub/gnu/mcron/%{name}-%{version}.tar.gz
# Source0-md5:	975eba069a1aa2fdaef4029752d78100
Source1:        %{name}.init
Source2:        cron.logrotate
Source3:        cron.sysconfig
Source4:        %{name}.crontab
URL:		http://www.gnu.org/software/mcron/
BuildRequires:	guile-devel
BuildRequires:	sed >= 4.0
BuildRequires:	texinfo
PreReq:		rc-scripts
Requires:	/bin/run-parts
Provides:	crondaemon
Provides:	crontabs
Obsoletes:	crondaemon
Obsoletes:	vixie-cron
Obsoletes:	crontabs
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The GNU package mcron (Mellor's cron) is a 100% compatible replacement
for Vixie cron. It is written in pure Guile, and allows configuration
files to be written in scheme (as well as Vixie's original format) for
infinite flexibility in specifying when jobs should be run.

%description -l pl
Pakiet GNU mcron (Mellor's cron) jest w 100% kompatybilnym
zamiennikiem Vixie crona. Jest napisany w czystym Guile i pozwala na
pisanie plików konfiguracyjnych w scheme (a tak¿e w oryginalnym
formacie Vixie) dla nieskoñczonej elastyczno¶ci w podawaniu zadañ do
uruchomienia.

%prep
%setup -q
sed -i -e 's#/etc/crontab#/etc/cron.d/system#g' *

%build
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

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/crond
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/cron
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/cron
install %{SOURCE4} $RPM_BUILD_ROOT/etc/cron.d/crontab

install mcron $RPM_BUILD_ROOT%{_sbindir}
ln -s mcron $RPM_BUILD_ROOT%{_sbindir}/crond
ln -s ../sbin/mcron $RPM_BUILD_ROOT%{_bindir}/crontab

install mcron.info $RPM_BUILD_ROOT%{_infodir}/%{name}.info

cat > $RPM_BUILD_ROOT%{_sysconfdir}/cron/cron.allow << EOF
# cron.allow   This file describes the names of the users which are
#               allowed to use the local cron daemon
root
EOF

cat > $RPM_BUILD_ROOT%{_sysconfdir}/cron/cron.deny << EOF2
# cron.deny    This file describes the names of the users which are
#               NOT allowed to use the local cron daemon
EOF2

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid crontab`" ]; then
        if [ "`/usr/bin/getgid crontab`" != "117" ]; then
                echo "Error: group crontab doesn't have gid=117. Correct this before installing cron." 1>&2
                exit 1
        fi
else
        echo "Adding group crontab GID=117."
        /usr/sbin/groupadd -g 117 -r -f crontab
fi

%post
/sbin/chkconfig --add crond
if [ -f /var/lock/subsys/crond ]; then
        /etc/rc.d/init.d/crond restart >&2
else
        echo "Run \"/etc/rc.d/init.d/crond start\" to start cron daemon."
fi
umask 027
touch /var/log/cron
chgrp crontab /var/log/cron
chmod 660 /var/log/cron
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/crond ]; then
                /etc/rc.d/init.d/crond stop >&2
        fi
        /sbin/chkconfig --del crond
fi

%postun
if [ "$1" = "0" ]; then
        echo "Removing group crontab."
        /usr/sbin/groupdel crontab
fi
[ ! -x /usr/sbin/fix-info-dir ] || /usr/sbin/fix-info-dir -c %{_infodir} >/dev/null 2>&1

%files
%defattr(644,root,root,755)
%doc AUTHORS NEWS ChangeLog README TODO
%attr(755,root,root) %{_bindir}
%attr(755,root,root) %{_sbindir}/*
%attr(1730,root,root) /var/spool/cron
%{_infodir}/m*
