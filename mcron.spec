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
PreReq:		rc-scripts
Requires:	/bin/run-parts
BuildRequires:	guile-devel
Provides:	crontabs
Provides:	crondaemon
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	crondaemon
Obsoletes:	vixie-cron
Obsoletes:	crontabs

%description

The GNU package mcron (Mellor's cron) is a 100% compatible replacement
for Vixie cron. It is written in pure Guile, and allows configuration
files to be written in scheme (as well as Vixie's original format) for
infinite flexibility in specifying when jobs should be run.

%prep
%setup  -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/var/{cron,run} \
	$RPM_BUILD_ROOT%{_datadir}/guile/site/mcron \
	$RPM_BUILD_ROOT%{_sbindir}

install mcron $RPM_BUILD_ROOT%{_sbindir}/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README
%attr(750,root,root) %{_sbindir}/*
%attr(1730,root,root) %dir /var/cron
%attr(755,root,root) %{_datadir}/guile/site/mcron
