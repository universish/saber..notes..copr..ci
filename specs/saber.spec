%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs /bin/true
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip_static_archive %{nil}

# Flutter'ın iç kütüphanelerinin sistem geneline sahte Provide/Require üretmesini engelle
%global __provides_exclude_from ^%{_libdir}/%{name}/lib/.*$
%global __requires_exclude_from ^%{_libdir}/%{name}/lib/.*$

Name:           saber
# Eğer dışarıdan _version tanımlanmadıysa varsayılan sürümü ata
%{!?_version: %global _version 1.36.1}
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
# Yeniden derleme adımı yoktur; AppImage içindeki ikili dosyalar doğrudan kullanılır.

%install
rm -rf %{buildroot}

# Gerekli dizin yapısını oluştur
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_metainfodir}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps

# Ana uygulama dosyalarını ve bağımlılıklarını yerleştir
cp -a saber %{buildroot}%{_libdir}/%{name}/
cp -a data %{buildroot}%{_libdir}/%{name}/
cp -a lib %{buildroot}%{_libdir}/%{name}/

# /usr/bin altına çalıştırılabilir sembolik bağ oluştur
ln -sf %{_libdir}/%{name}/saber %{buildroot}%{_bindir}/%{name}

# Masaüstü giriş dosyasını bul ve yerleştir
DESKTOP_SRC=$(find . -maxdepth 1 -name "*.desktop" | head -n 1)
if [ -n "$DESKTOP_SRC" ]; then
    install -m 0644 "$DESKTOP_SRC" %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
fi

# Masaüstü dosyasındaki Exec ve Icon yollarını standartlaştır
sed -i 's|^Exec=.*|Exec=%{_bindir}/saber %U|' %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop
sed -i 's|^Icon=.*|Icon=com.saber-notes.saber|' %{buildroot}%{_datadir}/applications/com.saber-notes.saber.desktop

# İkonları kopyala
if [ -f com.saber-notes.saber.svg ]; then
    install -m 0644 com.saber-notes.saber.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.saber-notes.saber.svg
elif [ -f saber.svg ]; then
    install -m 0644 saber.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.saber-notes.saber.svg
fi

PNG_ICON=$(find . -maxdepth 1 -name "*.png" | head -n 1)
if [ -n "$PNG_ICON" ]; then
    install -m 0644 "$PNG_ICON" %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/com.saber-notes.saber.png
fi

# AppStream Metainfo dosyasını kur
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
* Sun Oct 04 2026 Universish Automation <contact@universish.org> - %{version}-1
- Otomatik AppImage repackage sürümü (x86_64 ve aarch64).
