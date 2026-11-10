# RPM Scriptlets, Transactions, and File Triggers

Technical reference for package installation scriptlets, transaction semantics, and modern RPM file triggers.

---

## 1. Scriptlet Execution Phases

Scriptlets run shell commands during package transactions:

| Scriptlet | Execution Trigger | Argument `$1` |
|---|---|---|
| `%pre` | Before files from the package are written to disk. | 1 (initial install), 2+ (upgrade) |
| `%post` | After files from the package are written to disk. | 1 (initial install), 2+ (upgrade) |
| `%preun` | Before an existing package version is removed. | 0 (complete uninstall), 1+ (upgrade) |
| `%postun` | After an existing package version is removed. | 0 (complete uninstall), 1+ (upgrade) |
| `%pretrans` | Before the entire transaction begins. | 0 |
| `%posttrans` | After the entire multi-package transaction finishes. | 0 |

### Critical Scriptlet Argument Invariant:
When upgrading a package from version 1 to version 2, RPM executes:
1. `%pre` of version 2 (`$1 = 2`)
2. Unpack files of version 2 (overwrites version 1 files)
3. `%post` of version 2 (`$1 = 2`)
4. `%preun` of version 1 (`$1 = 1`)
5. Delete old files unique to version 1
6. `%postun` of version 1 (`$1 = 1`)

> [!WARNING]
> In `%postun`, you must check `$1 == 0` before stopping a service or deleting user state!
> If you execute `systemctl stop mydaemon` unconditionally in `%postun`, upgrading the package will immediately kill the daemon that was just updated in step 3!

---

## 2. Declarative Systemd Scriptlet Macros

Never write raw `systemctl` commands in scriptlets. Always use distribution systemd macros:

```spec
%post
%systemd_post myapp.service

%preun
%systemd_preun myapp.service

%postun
%systemd_postun_with_restart myapp.service
```

---

## 3. Modern RPM File Triggers

Instead of having hundreds of packages run `ldconfig` or `gtk-update-icon-cache` in `%post`, modern RPM uses **File Triggers**:
- The `glibc` package registers a file trigger monitoring `/usr/lib64/`.
- Whenever *any* package writes a file into `/usr/lib64/`, RPM runs `ldconfig` once at the end of the entire transaction.
- Do NOT write `%post -p /sbin/ldconfig` in modern RPM packages.
