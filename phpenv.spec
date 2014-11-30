# NOTE:
# - use similar recipe as done by CHH (https://github.com/CHH/phpenv)
#   however, make it more rbenv compatible: code in /usr/share, env files in ~/.phpenv
# - actually don't need code from CHH/phpenv as all is inlined in this .spec
Summary:	Thin Wrapper around rbenv for PHP version managment
Name:		phpenv
Version:	0.4.0
Release:	1
License:	MIT
Group:		Development/Languages/PHP
Source0:	https://github.com/sstephenson/rbenv/archive/v%{version}/rbenv-%{version}.tar.gz
# Source0-md5:	c4a15a4dccf3dc1d28d08e87fb7c7789
URL:		https://github.com/CHH/phpenv
Requires:	bash
BuildArch:	noarch
# https://github.com/CHH/php-build
Suggests:	php-build
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir			%{_datadir}/%{name}

%description
Sets up a separate rbenv environment for PHP

This environment is stored in the $HOME/.phpenv directory and contains
a phpenv executable which sets the PHPENV_ROOT environment variable to
$HOME/.phpenv.

To install PHP versions, just put them to the $HOME/.phpenv/versions
directory.

%prep
%setup -qc
mv rbenv-%{version}/* .

# deprecated as of rbenv 0.4.0, pointless in phpenv
rm bin/ruby-local-exec

# fully replace to rbenv -> phpenv
# https://github.com/CHH/phpenv/pull/30
# Create file phpenv prefixed copies of the original rbenv files
for f in bin/rbenv* completions/rbenv* libexec/rbenv*; do
	mv "$f" "${f/rbenv/phpenv}"
done

# Remove all rbenv/Ruby from phpenv prefixed files
sed -i \
	-e 's/rbenv/phpenv/g' \
	-e 's/RBENV/PHPENV/g' \
	-e 's/Ruby/PHP/g' \
	-e 's/ruby/php/g' \
	completions/phpenv* libexec/phpenv*

# Fix the version
cat <<'SH' > libexec/phpenv---version
#!/bin/sh
echo "phpenv %{version} - based on rbenv %{version}"
SH
chmod a+x libexec/phpenv---version

# Fix link in help text:
RBENV_REPO="https://github.com/sstephenson/rbenv"
PHPENV_REPO="https://github.com/chh/phpenv"
sed -i -e "s|^.*For full documentation.*\$|  echo \"For full documentation, see:\"\n  echo \" rbenv: ${RBENV_REPO}#readme\"\n  echo \" phpenv: ${PHPENV_REPO}#readme\"|" libexec/phpenv-help

# use pld (not debian) version of hooks dir
sed -i -e 's#/usr/lib/phpenv/hooks#%{_appdir}/hooks#' libexec/phpenv

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_appdir}/hooks}
cp -a libexec completions $RPM_BUILD_ROOT%{_appdir}

ln -s %{_appdir}/libexec/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%attr(755,root,root) %{_bindir}/phpenv
%dir %{_appdir}
%dir %{_appdir}/libexec
%attr(755,root,root) %{_appdir}/libexec/%{name}*
%{_appdir}/completions
%dir %{_appdir}/hooks
