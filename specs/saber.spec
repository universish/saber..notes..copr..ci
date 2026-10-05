%{!?_version: %global _version 1.36.1}

%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_static_archive %{nil}

# Flutter dahili kütüphanelerinin ve bundled PDFium'un sistem genelinde aranmasını engelle
%global __provides_exclude_from ^%{_libdir}/%{name}/lib/.*$
%global __requires_exclude ^(lib.*_plugin\\.so|libflutter_linux_gtk\\.so|libpdfium\\.so)

Name:           saber
Version:        %{_version}
Release:        3%{?dist}
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

# Flutter Linux çalışma zamanı için sistem kütüphaneleri
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
# Yeniden derleme adımı yoktur; açılan ELF ikilileri doğrudan kullanılır.

%install
export QA_RPATHS=0x0003

rm -rf %{buildroot}

mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_metainfodir}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor

# 1. Ana ikili dosyayı kur
BIN_SRC=$(find . -type f \( -name "saber" -o -name "Saber" \) ! -name "*.desktop" ! -name "*.spec" | head -n 1)

if [ -n "$BIN_SRC" ]; then
    install -m 0755 "$BIN_SRC" %{buildroot}%{_libdir}/%{name}/saber
else
    echo "HATA: Saber ikili dosyası bulunamadı!"
    exit 1
fi

# 2. Asıl data ve lib dizinlerini kopyala
BUNDLE_DIR=$(dirname "$BIN_SRC")

if [ -d "$BUNDLE_DIR/data" ]; then
    cp -a "$BUNDLE_DIR/data" %{buildroot}%{_libdir}/%{name}/
fi

if [ -d "$BUNDLE_DIR/lib" ]; then
    cp -a "$BUNDLE_DIR/lib" %{buildroot}%{_libdir}/%{name}/
    chmod 0755 %{buildroot}%{_libdir}/%{name}/lib/*.so* 2>/dev/null || true
fi

# 3. Kütüphane yolunu yükleyen başlatıcı betik (/usr/bin/saber)
cat << 'EOF' > %{buildroot}%{_bindir}/%{name}
#!/bin/sh
export LD_LIBRARY_PATH="%{_libdir}/%{name}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec %{_libdir}/%{name}/saber "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

# 4. Masaüstü giriş dosyasını yapılandır
DESKTOP_SRC=$(find . -name "*.desktop" | head -n 1)
if [ -n "$DESKTOP_SRC" ]; then
    install -m 0644 "$DESKTOP_SRC" %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
    sed -i 's|^Exec=.*|Exec=%{_bindir}/saber %U|' %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
    sed -i 's|^Icon=.*|Icon=com.saber-notes.saber|' %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
fi

# 5. İkonları yerleştir
if [ -d "usr/share/icons/hicolor" ]; then
    cp -a usr/share/icons/hicolor/* %{buildroot}%{_datadir}/icons/hicolor/
fi

find %{buildroot}%{_datadir}/icons/hicolor/ -type f -name "*saber*" | while read -r icon; do
    dir=$(dirname "$icon")
    ext="${icon##*.}"
    cp -a "$icon" "$dir/com.saber-notes.saber.$ext" 2>/dev/null || true
done

# 6. AppStream Metainfo kurulumu
install -m 0644 %{SOURCE2} %{buildroot}%{_metainfodir}/com.saber-notes.saber.metainfo.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/com.saber-notes.saber.metainfo.xml

%files
%{_bindir}/%{name}
%{_libdir}/%{name}/
%{_datadir}/applications/com.saber-notes.saber.desktop
%{_metainfodir}/com.saber-notes.saber.metainfo.xml
%{_datadir}/icons/hicolor/*/*/*

%changelog
* Mon Oct 05 2026 Saffet Yavuz - Universish Automation <universish@tutamail.com> - %{version}-3
- libpdfium sahte bagimliligi filtrelendi (jellyfin cakismasi giderildi).
