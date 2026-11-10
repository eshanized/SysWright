# Open Build Service (OBS) Project Architecture & Metadata

Technical reference for OBS project hierarchies, meta configurations, and repository definitions.

---

## 1. OBS Project Hierarchy

In OBS, every package lives inside a Project:
- `openSUSE:Factory`: The main development trunk for openSUSE Tumbleweed.
- `openSUSE:Leap:15.6`: The maintenance project for Leap 15.6.
- `home:<username>`: Personal user workspace projects for experimental packages and development.
- `home:<username>:branches:<project>`: Branched package workspaces.

---

## 2. Project Meta Configuration (`osc meta prj`)

A project's target distributions and architectures are configured via an XML file:

```xml
<project name="home:myuser:networking">
  <title>Networking Utilities Project</title>
  <description>High performance networking tools built for openSUSE and Fedora</description>
  <person userid="myuser" role="maintainer"/>
  <repository name="openSUSE_Tumbleweed">
    <path project="openSUSE:Factory" repository="snapshot"/>
    <arch>x86_64</arch>
    <arch>aarch64</arch>
  </repository>
  <repository name="openSUSE_Leap_15.6">
    <path project="openSUSE:Leap:15.6" repository="standard"/>
    <arch>x86_64</arch>
  </repository>
  <repository name="Fedora_40">
    <path project="Fedora:40" repository="standard"/>
    <arch>x86_64</arch>
  </repository>
</project>
```

Edit via CLI:
```bash
osc meta prj -e home:myuser:networking
```
