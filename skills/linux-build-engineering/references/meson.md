# Meson Build Systems Engineering

## 1. Scope & The Meson Philosophy

Meson is a high-speed, user-friendly build system with a domain-specific, non-Turing-complete language. It is the official build system for the GNOME project, systemd, Wayland, and Mesa.
- **Fast Execution**: Meson parses configurations rapidly and generates optimized Ninja build graphs.
- **Out-of-Source by Default**: Meson strictly forbids in-source builds, keeping the source directory pristine.
- **First-Class Subprojects (Wrap)**: Automatic fallback from system dependencies to git/tarball subprojects.

---

## 2. Standard `meson.build` Architecture

```meson
project('myproject', 'c',
  version : '1.2.0',
  default_options : [
    'warning_level=2',
    'c_std=c11',
    'b_pie=true',
  ]
)

# 1. Dependency Resolution (uses pkg-config automatically)
gtk_dep = dependency('gtk4', version : '>= 4.10.0')
glib_dep = dependency('glib-2.0', version : '>= 2.76.0')
m_dep = meson.get_compiler('c').find_library('m', required : false)

# 2. Compile GResource XML
gnome = import('gnome')
resources = gnome.compile_resources('myproject-resources',
  'data/myproject.gresource.xml',
  source_dir : 'data'
)

# 3. Executable Target
executable('myproject',
  sources : [
    'src/main.c',
    'src/app.c',
    resources,
  ],
  dependencies : [
    gtk_dep,
    glib_dep,
    m_dep,
  ],
  install : true
)

# 4. Generate pkg-config metadata file
pkg = import('pkgconfig')
# (Optional: for shared libraries)
```

---

## 3. Invocation Commands

```bash
# Setup build directory
meson setup builddir --prefix=/usr --buildtype=release

# Compile with Ninja
meson compile -C builddir

# Run tests
meson test -C builddir

# Install to staging directory
DESTDIR=/tmp/staging meson install -C builddir
```
