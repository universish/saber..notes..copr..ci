# Saber Notes Copr Packaging CI (`saber..notes..copr..ci`)

Automated continuous integration pipeline to repackage upstream [Saber](https://github.com/saber-notes/saber) AppImage releases into native RPM packages for Fedora Linux, built and hosted on [Fedora Copr](https://copr.fedorainfracloud.org/coprs/universish/saber..notes/).

---

## Overview

[Saber](https://github.com/saber-notes/saber) is a privacy-focused handwritten note-taking application written in Flutter. Upstream distributes pre-compiled Linux binaries exclusively as standalone AppImages (`x86_64` and `arm64`).

Building Flutter desktop applications directly inside isolated build environments like Fedora Mock or Copr is frequently impeded by offline environment constraints and intricate Dart/Flutter toolchain dependencies. This repository solves that problem by implementing an automated **AppImage-to-RPM repackaging pipeline**:

* Extracts upstream pre-compiled AppImages for both `x86_64` and `arm64` architectures.
* Strips AppImage runtime wrappers (`AppRun`, squashfs headers) and packages payload contents into architecture-specific source tarballs.
* Generates a unified Source RPM (`.src.rpm`).
* Dispatches automated build tasks to the `universish/saber..notes` Copr repository across `fedora-44` and `fedora-rawhide` chroots.

---

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── saber_ci.yml                   # Automated release detector and Copr trigger
├── sources/
│   └── com.saber-notes.saber.metainfo.xml # AppStream catalog metadata
├── specs/
│   └── saber.spec                         # RPM packaging specification
└── README.md

```

---

## Component Deep Dive

### 1. GitHub Actions Workflow (`.github/workflows/saber_ci.yml`)

The workflow runs on a scheduled cron trigger (daily at 04:00 UTC) and can also be dispatched manually (`workflow_dispatch`) with an optional `force_version` input.

#### Operational Sequence:

1. **Upstream Release Resolution**: Queries the GitHub REST API for `saber-notes/saber` releases, strips any leading `v` prefixes, and identifies direct download URLs matching `(?i)saber-.*-x86_64.appimage` and `(?i)saber-.*-arm64.appimage`.
2. **QEMU Multi-Arch Emulation (`docker/setup-qemu-action`)**: GitHub Actions `ubuntu-latest` runners are natively `x86_64`. To extract an ARM64 AppImage via `./saber-arm64.AppImage --appimage-extract`, user-space QEMU emulation is initialized to enable transparent `binfmt_misc` execution of foreign ARM64 binaries.
3. **AppImage Extraction & Sanitization**:
* Executes `--appimage-extract` for both architectures, producing `squashfs-root-x86_64` and `squashfs-root-arm64`.
* Purges AppImage runtime shims (`AppRun`, `.DirIcon`).
* Compresses sanitized payloads into individual archives:
* `saber-<VERSION>-x86_64.tar.gz`
* `saber-<VERSION>-aarch64.tar.gz`




4. **Isolated SRPM Generation (`addnab/docker-run-action`)**: Mounts the workspace inside an official `fedora:latest` container containing `rpmdevtools` and `rpm-build`. Runs `rpmbuild -bs` using `specs/saber.spec` to output a clean, verifiable `.src.rpm`.
5. **Copr Dispatch (`copr-cli`)**: Mounts credentials from the `COPR_CONFIG` secret into `~/.config/copr` and triggers non-blocking builds (`copr-cli build --nowait`) targeting four chroots:
* `fedora-44-x86_64`
* `fedora-44-aarch64`
* `fedora-rawhide-x86_64`
* `fedora-rawhide-aarch64`



---

### 2. RPM Specification (`specs/saber.spec`)

The RPM spec file handles binary payload placement, library conflict prevention, and desktop integration.

#### Key Architectural Highlights:

* **Binary Integrity Preservation**:
```spec
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs /bin/true
%global __brp_strip %{nil}

```


Disables standard RPM build-root stripping and debuginfo extraction routines. Flutter engine ELF binaries (`libflutter_linux_gtk.so` and `saber`) contain embedded metadata and symbols that can be corrupted if altered by standard Red Hat stripping macros.
* **Dependency Isolation & Symbol Filtering**:
```spec
%global __provides_exclude_from ^%{_libdir}/%{name}/lib/.*$
%global __requires_exclude_from ^%{_libdir}/%{name}/lib/.*$

```


Prevents `rpmbuild`'s internal dependency generator from exposing internal bundled Flutter libraries as system-wide RPM provides or generating conflicting system library requirements.
* **Multi-Architecture Source Unpacking**:
```spec
%prep
%setup -q -c -n %{name}-%{version} -T
%ifarch x86_64
tar -xzf %{SOURCE0} -C .
%endif
%ifarch aarch64
tar -xzf %{SOURCE1} -C .
%endif

```


Conditionally extracts the appropriate pre-compiled architecture tarball based on the build target architecture inside Fedora Mock/Copr.
* **FHS Compliance & System Integration**:
* Installs the application payload into `/usr/lib64/saber/`.
* Creates a symlink `/usr/bin/saber -> /usr/lib64/saber/saber`.
* Validates and installs the `.desktop` file to `/usr/share/applications/`.
* Registers HiDPI and vector icons under `/usr/share/icons/hicolor/`.
* Installs AppStream metadata to `/usr/share/metainfo/`.



---

### 3. AppStream Metadata (`sources/com.saber-notes.saber.metainfo.xml`)

Ensures the package integrates natively with graphical package management frontends (GNOME Software, KDE Discover) across Fedora installations:

* Validated during the RPM `%check` phase using `appstream-util validate-relax --nonet`.
* Connects desktop launch definitions (`com.saber-notes.saber.desktop`) with upstream project URLs, license declarations (`GPL-3.0-or-later`), and OARS content ratings.

---

## Configuration & Deployment

### 1. Copr Project Settings

Ensure the destination project exists on Fedora Copr:

* **Project URL**: `[https://copr.fedorainfracloud.org/coprs/universish/saber..notes/](https://copr.fedorainfracloud.org/coprs/universish/saber..notes/)`
* Navigate to **Settings -> Chroots** and enable:
* `fedora-44-x86_64`
* `fedora-44-aarch64`
* `fedora-rawhide-x86_64`
* `fedora-rawhide-aarch64`



### 2. GitHub Secrets Setup
## Badges

[![Copr build status](https://copr.fedorainfracloud.org/coprs/universish/saber..notes/package/saber/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/universish/saber..notes/package/saber/)
[![Saber Fedora COPR CI](https://github.com/universish/saber..ci/actions/workflows/saber_ci.yml/badge.svg)](https://github.com/universish/saber..ci/actions/workflows/saber_ci.yml)
[![Saber latest release](https://img.shields.io/github/v/release/saber-notes/saber)](https://github.com/saber-notes/saber/releases)

---

## Packaging compliance

This package is distributed via COPR only. It unpacks and rewraps the upstream prebuilt
AppImage binaries (`Saber-X.Y.Z-x86_64.AppImage` and `Saber-X.Y.Z-arm64.AppImage`), so it is
**not eligible for the official Fedora repositories**: the Fedora Packaging Guidelines
require all binaries to be built from source within the Fedora build system, and this
repository intentionally ships the upstream Flutter engine and application payloads as-is (see `specs/saber.spec`).

Everything else adheres strictly to Fedora packaging standards:

- `ExclusiveArch: x86_64 aarch64` — matches the tested upstream prebuilt AppImage artifacts.
- `%build` section is present (empty — nothing to recompile) ensuring standard RPM macro build hooks run.
- `%check` executes `desktop-file-validate` and `appstream-util validate-relax --nonet` against packaged artifacts during the build phase.
- `rpmlint` validation is filtered via `rpmlintrc` with explicit rationales: all warnings/errors inherent to packaging prebuilt Flutter blobs (unstripped binaries, private dynamic libraries with $ORIGIN runpaths, lack of manual pages for GUI applications) are documented and scoped.
- Standard path macros (`%{_bindir}`, `%{_libdir}`, `%{_datadir}`, `%{_metainfodir}`) are used throughout `%files`.
- License provenance: the underlying Saber application is released under GPL-3.0-or-later (`License: GPL-3.0-or-later`).
- `%global debug_package %{nil}` is specified with an explicit rationale: foreign prebuilt binaries cannot produce standard DWARF debuginfo. Disabling debuginfo avoids invalid debug package extraction. Furthermore, Fedora's automatic `%__os_install_post` hooks (`brp-strip`, `brp-strip-comment-note`, `brp-strip-lto`) are bypassed or normalized in the spec to guarantee the Flutter engine ELF binary and Dart AOT snapshots remain byte-identical to upstream releases.
- The bundled Flutter libraries under `%{_libdir}/saber/lib` contain private SONAMEs (such as `libflutter_linux_gtk.so`). To prevent private symbols from leaking into system-wide RPM dependency registries, `%__provides_exclude_from` and `%__requires_exclude_from` isolate the internal library paths.
- Symbolic linking: `/usr/bin/saber -> %{_libdir}/saber/saber` is declared directly in `%install`. RPM owns this symlink natively, eliminating the need for post-installation (`%post`) shell scriptlets.
- Curated AppStream metadata: upstream ships no standalone AppStream catalog metadata file, so this repository provides `com.saber-notes.saber.metainfo.xml` mapping directly to the desktop entry and upstream issue tracker.
- System dependencies: standard Flutter Linux dependencies (`gtk3`, `glib2`, `cairo`, `pango`, `libepoxy`, `hicolor-icon-theme`) are explicitly declared. Network access is completely disabled within the build environment.

---

## Installation Instructions (Client-Side)

To install Saber on Fedora using the Copr repository:

```bash
# 1. Enable the Copr repository
sudo dnf copr enable universish/saber..notes

# 2. Install Saber
sudo dnf install saber

# 3. Launch from terminal or application launcher
saber

```

---

## License

* Packaging definitions, CI automation, and spec files in this repository are licensed under the [MIT License](https://www.google.com/search?q=LICENSE).
* The underlying Saber application is licensed under [GPL-3.0-or-later](https://www.google.com/search?q=https://github.com/saber-notes/saber/blob/main/LICENSE).
