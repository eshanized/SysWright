# OBS Build Engineering: Local Chroots, VM Workers, and Logs

Technical reference for debugging Open Build Service compilation failures and local mock builds.

---

## 1. Local Isolated Building with `osc build`

`osc build` reproduces the exact remote OBS build environment on your local workstation without requiring an internet connection during compilation:

```bash
# Build locally targeting openSUSE Leap 15.6 on x86_64
osc build openSUSE_Leap_15.6 x86_64 myapp.spec
```

### How `osc build` Works:
1. Downloads pristine RPM buildroot packages from the OBS repository cache into `/var/tmp/build-root/`.
2. Creates an isolated chroot / VM using `build` (`/usr/bin/build`).
3. Installs only declared `BuildRequires:`.
4. Executes the spec file `%prep`, `%build`, `%install`, and `%check` phases.
5. Saves resulting packages to `/var/tmp/build-root/.build.packages/`.

---

## 2. Diagnosing Build Failure States in OBS

When `osc results` reports a failure:
- **`failed`**: Compilation error, test suite failure in `%check`, or missing unpackaged files in `%install`. Inspect with `osc buildlog <repo> <arch>`.
- **`unresolvable`**: One or more `BuildRequires:` cannot be satisfied by the target repository.
- **`broken`**: Project repository configuration error or dependency cycle.
- **`blocked`**: Waiting for a prerequisite package in the same project to finish building.
