# Native Application Regressions: Behavior, Configuration, and Compatibility

Technical reference for investigating application-level behavioral regressions, configuration migrations, and state preservation.

---

## 1. Types of Application Regressions

| Regression Type | Mechanism | Diagnostic Strategy |
|---|---|---|
| **Silent Logic Bug** | Computation returns incorrect value without crashing | Unit test assertion against golden dataset |
| **CLI Argument Deprecation** | Existing CLI flags rejected with `unrecognized option` | Test CLI invocation scripts across versions |
| **Configuration Schema Break** | Upgraded binary cannot parse existing config file format in `~/.config/` | Schema validation and backward migration testing |
| **State / DB Schema Migration** | Database migration script corrupts or fails to upgrade existing SQLite db | Test migration against snapshot of old DB |
| **IPC Protocol Incompatibility** | Daemon upgraded, but older client binary cannot decode new D-Bus or socket format | Test client/server version cross-matrix |

---

## 2. Configuration Backward Compatibility Rules

When modifying application configuration formats (YAML, JSON, INI):

1. **Additive Changes Only**: New configuration options must have safe, backwards-compatible defaults if omitted from older configuration files.
2. **Deprecation Grace Period**: If an option is renamed, support both the legacy name and the new name for at least one major release, emitting a gentle warning on stderr.
3. **Atomic File Rewriting**: When saving state back to disk, always write to a temporary file (`config.yaml.tmp`) and atomically rename (`rename(2)`) over the original to prevent truncated configuration if the power cuts or process terminates mid-write.
