%{!?_version: %global _version 1.36.1}

%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_static_archive %{nil}

# Flutter iç kütüphanelerinin sistem geneline sahte Provide/Require üretmesini engelle
%global __provides_exclude_from ^%{_libdir}/%{name}/lib/.*$
%global __requires_exclude_from ^%{_libdir}/%{name}/lib/.*$

Name:           saber
Version:        %{_version}
Release:        1%{?dist}
Summary:        El yazısı ve dijital not alma uygulaması
License:        GPL-3.0-or-later
URL:            https://github.com/saber-notes/saber

Source0:        saber-%{version}-x86_64.tar.gz
Source1:        saber-%{version}-aarch64.tar.gz
Source2:        com.saber-notes.saber.metainfo.xml

ExclusiveArch:  x86_64 aarch64

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  tar

# Flutter Linux çalışma zamanı temel bağımlılıkları
Requires:       gtk3
Requires:       glib2
Requires:       cairo
Requires:       pango
Requires:       libepoxy
Requires:       hicolor-icon-theme

%description
Saber; dokunmatik ekranlar ve grafik tabletler için optimize edilmiş,
Nextcloud/WebDAV senkronizasyonunu destekleyen, açık kaynaklı ve gizlilik
odaklı bir el yazısı not alma uygulamasıdır.

%prep
%setup -q -c -n %{name}-%{version} -T
%ifarch x86_64
tar -xzf %{SOURCE0} -C .
%endif
%ifarch aarch64
tar -xzf %{SOURCE1} -C .
%endif

%build
# Yeniden derleme adımı yoktur; AppImage içindeki hazır ELF ikilileri kullanılır.

%install
rm -rf %{buildroot}

# Gerekli hedef dizinleri oluştur
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_metainfodir}

# İkili dosyayı (Saber / saber) tespit et ve /usr/lib64/saber/saber olarak kur
BIN_SRC=""
if [ -f "Saber" ]; then
    BIN_SRC="Saber"
elif [ -f "saber" ]; then
    BIN_SRC="saber"
else
    BIN_SRC=$(find . -maxdepth 3 -type f \( -name "Saber" -o -name "saber" \) | head -n 1)
fi

if [ -n "$BIN_SRC" ]; then
    install -m 0755 "$BIN_SRC" %{buildroot}%{_libdir}/%{name}/saber
    ln -sf saber %{buildroot}%{_libdir}/%{name}/Saber
else
    echo "HATA: Saber ikili dosyasi bulunamadi!"
    exit 1
fi

# /usr/bin/saber sembolik bağını oluştur
ln -sf %{_libdir}/%{name}/saber %{buildroot}%{_bindir}/%{name}

# Flutter varlıklarını (data ve lib) kopyala
if [ -d "data" ]; then
    cp -a data %{buildroot}%{_libdir}/%{name}/
else
    DATA_SRC=$(find . -maxdepth 3 -type d -name "data" | head -n 1)
    [ -n "$DATA_SRC" ] && cp -a "$DATA_SRC" %{buildroot}%{_libdir}/%{name}/
fi

if [ -d "lib" ]; then
    cp -a lib %{buildroot}%{_libdir}/%{name}/
else
    LIB_SRC=$(find . -maxdepth 3 -type d -name "lib" | head -n 1)
    [ -n "$LIB_SRC" ] && cp -a "$LIB_SRC" %{buildroot}%{_libdir}/%{name}/
fi

# Masaüstü giriş dosyasını bul ve yerleştir
DESKTOP_SRC=$(find . -maxdepth 2 -name "*.desktop" | head -n 1)
if [ -n "$DESKTOP_SRC" ]; then
    install -m 0644 "$DESKTOP_SRC" %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
    sed -i 's|^Exec=.*|Exec=%{_bindir}/saber %U|' %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
    sed -i 's|^Icon=.*|Icon=com.saber-notes.saber|' %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
fi

# Varsa SVG ikonunu kur
ICON_SVG=$(find . -maxdepth 3 -type f -name "*.svg" | head -n 1)
if [ -n "$ICON_SVG" ]; then
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
    install -m 0644 "$ICON_SVG" %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.saber-notes.saber.svg
fi

# Varsa PNG ikonunu kur
ICON_PNG=$(find . -maxdepth 3 -type f -name "*.png" | head -n 1)
if [ -n "$ICON_PNG" ]; then
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps
    install -m 0644 "$ICON_PNG" %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/com.saber-notes.saber.png
fi

# AppStream Metainfo kurulumu
install -m 0644 %{SOURCE2} %{buildroot}%{_metainfodir}/com.saber-notes.saber.metainfo.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/com.saber-notes.saber.metainfo.xml

%files
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/com.saber-notes.saber.desktop
%{_metainfodir}/com.saber-notes.saber.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/*

%changelog
* Sun Oct 04 2026 Saffet Yavuz - Universish Automation <universish@tutamail.com> - %{version}-1
- Otomatik AppImage repackage sürümü.
