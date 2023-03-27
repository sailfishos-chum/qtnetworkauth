%global qt_version 5.15.8

Summary: Qt5 - NetworkAuth component
Name:    opt-qt5-qtnetworkauth
Version: 5.15.8
Release: 1%{?dist}

# See LGPL_EXCEPTIONS.txt, LICENSE.GPL3, respectively, for exception details
License: LGPL-3.0-only OR GPL-3.0-only WITH Qt-GPL-exception-1.0
Url:     http://www.qt.io
%global majmin %(echo %{version} | cut -d. -f1-2)
Source0: %{name}-%{version}.tar.bz2

# filter plugin/qml provides
%global __provides_exclude_from ^(%{_opt_qt5_archdatadir}/qml/.*\\.so|%{_opt_qt5_plugindir}/.*\\.so)$
%{?opt_qt5_default_filter}

BuildRequires: make
BuildRequires: opt-qt5-qtbase-devel >= %{qt_version}
BuildRequires: opt-qt5-qtbase-private-devel
%{?_opt_qt5:Requires: %{_opt_qt5}%{?_isa} = %{_opt_qt5_version}}

%description
%{summary}

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: opt-qt5-qtbase-devel%{?_isa}
%description devel
%{summary}.

%prep
%autosetup -n %{name}-%{version}/upstream


%build
# no shadow builds until fixed: https://bugreports.qt.io/browse/QTBUG-37417
export QTDIR=%{_opt_qt5_prefix}
touch .git
%{opt_qmake_qt5}

# have to restart build several times due to bug in sb2
%make_build -k || chmod -R ugo+r . || true
%make_build
chmod -R ugo+r .

%install
make install INSTALL_ROOT=%{buildroot}

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_opt_qt5_libdir}
for prl_file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.GPL*
%{_opt_qt5_libdir}/libQt5NetworkAuth.so.5*

%files devel
%{_opt_qt5_headerdir}/QtNetworkAuth/
%{_opt_qt5_libdir}/libQt5NetworkAuth.so
%{_opt_qt5_libdir}/libQt5NetworkAuth.prl
%{_opt_qt5_libdir}/pkgconfig/Qt5NetworkAuth.pc
%{_opt_qt5_libdir}/cmake/Qt5NetworkAuth/
%{_opt_qt5_archdatadir}/mkspecs/modules/qt_lib_networkauth*.pri

