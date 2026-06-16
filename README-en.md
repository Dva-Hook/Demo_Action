# OnePlus / Realme / Lenovo SM8750 Kernel Build Project

**[简体中文](README.md)** | `English`

[![GitHub](https://img.shields.io/badge/-GitHub|@showdo-181717?logo=github&logoColor=white&style=flat-square)](https://github.com/showdo/Build_Oneplus_Realme_Action)
[![Telegram](https://img.shields.io/badge/Telegram-Channel-blue.svg?logo=telegram)](https://t.me/qdykernel)
[![CoolAPK|Profile](https://img.shields.io/badge/CoolAPK%7CProfile-3DDC84?style=flat-square&logo=android&logoColor=white)](http://www.coolapk.com/u/1624571)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/showdo/Build_Oneplus_Realme_Action/Build_all_devices_sm8750.yml?label=SM8750&logo=github-actions&style=flat-square)](https://github.com/showdo/Build_Oneplus_Realme_Action/actions)

---

## 📖 Introduction

This project provides automated kernel compilation workflows based on **GitHub Actions**, supporting **OnePlus**, **Realme**, and **Lenovo** devices powered by **SM8750 / MT6991** platforms. Through highly integrated scripts, it enables one-click compilation of custom kernels featuring **ReSukiSU**, **SUSFS**, **Fengchi Scheduler (SCX)**, **ADIOS I/O Scheduler**, and more.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🚀 **Fully Automated** | GitHub Actions based, no local environment required |
| 🔐 **ReSukiSU Integration** | Kernel-level root solution, optional |
| 🛡 **SUSFS Support** | Full Magic Mount hiding support |
| ⚡ **Fengchi Scheduler (SCX)** | SCX scheduler patch for improved smoothness |
| 📡 **ADIOS I/O Scheduler** | Optimized storage I/O performance |
| 🔒 **BBG Baseband Guard** | Kernel-level baseband protection |
| 📱 **Re-Kernel Support** | Enhanced background freeze (requires NoActive) |
| 🐳 **Droidspaces** | Linux container support (ntsync + SYSVIPC, etc.) |
| 🆔 **SerialID Check** | Prevents kernel from being ported to unsupported devices |
| 📦 **lz4 1.10.0 + zstd 1.5.7** | Updated ZRAM compression algorithms |
| 💾 **Smart ccache** | Auto-matches public cache; ~50% faster first build, ~80% faster rebuilds |
| 🔑 **KPM Support** | Kernel Patch Module support (Lenovo devices) |
| 📦 **AnyKernel3 / Boot Signing** | Auto-packages flashable zip or signs boot image |

---

## 📱 Supported Devices

### OnePlus / Realme (SM8750 / MT6991)

> Workflow: `Build_All_Devices_SM8750`

| # | Device Name | Codename | Platform |
|---|-------------|----------|----------|
| 1 | OnePlus 13 | `oneplus_13` | SM8750 |
| 2 | OnePlus Ace 5 Pro | `oneplus_ace5_pro` | SM8750 |
| 3 | OnePlus Ace 6 | `oneplus_ace_6` | SM8750 |
| 4 | OnePlus 13T | `oneplus_13t` | SM8750 |
| 5 | OnePlus Pad 2 | `oneplus_pad_2` | MT6991 |
| 6 | OnePlus Pad 2 Pro | `oneplus_pad_2_pro` | SM8750 |
| 7 | OnePlus Ace5 Ultra | `oneplus_ace5_ultra` | MT6991 |
| 8 | Realme GT 7 | `realme_GT7` | MT6991 |
| 9 | Realme GT 7 Pro | `realme_GT7pro` | SM8750 |
| 10 | Realme GT 7 Pro Speed | `realme_GT7pro_Speed` | SM8750 |
| 11 | Realme GT 8 | `realme_GT8` | SM8750 |

### Lenovo SM8750

> Workflow: `Build_All_Lenovo_sm8750`

| Kernel Version | Security Patch Level | Corresponding Firmware |
|----------------|---------------------|----------------------|
| 6.6.56 | 2024-11 | TB322FC 1.1.11.120 |
| 6.6.89 | 2025-06 | ColorOS 16 400 |
| 6.6.102 | 2025-10 | TB322FC 1.5.10.096 |
| 6.6.118 | 2026-01 | ZUXOS 1.5.10.183 |

---

## 🎯 Quick Start

### Step 1: Fork This Repository

Click the **Fork** button in the upper right corner to copy this repository to your own GitHub account.

### Step 2: Run the Workflow

1. Go to your forked repository and click the **Actions** tab
2. Select the workflow for your device:
   - OnePlus / Realme: **`Build_All_Devices_SM8750`**
   - Lenovo tablets: **`Build_All_Lenovo_sm8750`**
3. Click **Run workflow** and configure the feature options as needed
4. Wait for the build to complete (first build ~12 min, subsequent builds ~3-5 min)
5. Download build artifacts from **Actions → Run record → Artifacts**, or get auto-published releases from the **Releases** page

---

## ⚙️ Build Parameters

### OnePlus / Realme Workflow

| Parameter | Default | Description |
|-----------|---------|-------------|
| Build all devices | `false` | Build all supported devices simultaneously |
| Device selection | `oneplus_13` | Build a specific device |
| Custom kernel name | Empty (use official) | Must start with `-` |
| Custom build time | Empty (use official) | English time string format |
| Re-Kernel support | `false` | Enhanced background freeze |
| ADIOS I/O Scheduler | `true` | Optimized storage I/O |
| Fengchi SCX | `true` | SCX scheduler patch |
| BBG Baseband Guard | `true` | Kernel-level baseband protection |
| Droidspaces | `false` | Linux container support |
| SerialID Check | `true` | Serial number binding |
| KernelSU (ReSukiSU) | `true` | Root support |
| SUSFS | `true` | Mount hiding support |

### Lenovo Workflow

| Parameter | Default | Description |
|-----------|---------|-------------|
| Build all versions | `false` | Build all kernel versions simultaneously |
| Kernel version | `6.6.89` | Target kernel version |
| BBG Baseband Guard | `false` | Kernel-level baseband protection |
| KernelSU (ReSukiSU) | `true` | Root support |
| Re-Kernel support | `true` | Enhanced background freeze |
| ADIOS I/O Scheduler | `true` | Optimized storage I/O |
| Droidspaces | `false` | Linux container support |
| KPM | `true` | Kernel Patch Module |
| SUSFS | `true` | Mount hiding support |
| AOSP key boot signing | `true` | Sign boot with AOSP test key |

---

## 📥 Installation

### AnyKernel3 Flashable Zip (OnePlus / Realme)

1. If you already have a ReSukiSU kernel and the manager is up to date, you can flash the AnyKernel3 zip directly from the manager and reboot
2. The latest KSU manager requires a **meta module** to mount modules properly. Available meta modules:
   - [meta overlayfs](https://github.com/KernelSU-Modules-Repo/meta-overlayfs)
   - [mountify](https://github.com/backslashxx/mountify)
   - [meta magic_mount](https://github.com/7a72/meta-magic_mount/)
3. If Re-Kernel is enabled, flash the Re-Kernel module and use it with NoActive for better background freeze

### Boot Image (Lenovo Devices)

Flash the signed boot image directly using `fastboot flash boot boot.img`

> ⚠️ Flashing kernels carries risks. Always back up your `boot` partition using [KernelFlasher](https://github.com/capntrips/KernelFlasher) before proceeding!

---

## 🔧 Advanced Details

### ccache Caching

- **Private cache**: Each device/version maintains independent cache; auto-updated when build exceeds 8 minutes
- **Public cache**: Automatically pulled from the public repository when private cache misses, accelerating first builds
- **Droidspaces variant**: Uses a separate cache key (`-ds` suffix) when Droidspaces is enabled to avoid cache contamination
- **Custom cache repo**: Configurable via repository variables `PUBLIC_CACHE_REPO` and `PUBLIC_CACHE_TAG`

### Feature Dependencies

- Enabling **Droidspaces** automatically forces **Fengchi SCX** (Droidspaces depends on SCX)
- Enabling **SUSFS** requires **KernelSU** to also be enabled
- **Re-Kernel** is independent of KSU and can be enabled separately

### Log Markers

```
[INFO]    - General information
[SUCCESS] - Successfully completed
[ERROR]   - Error (requires immediate attention)
```

---

## 🔗 Related Resources

### Upstream Projects

- [OnePlus Kernel Open Source](https://github.com/OnePlusOSS/kernel_manifest)
- [Realme Kernel Open Source](https://github.com/realme-kernel-opensource)
- [ReSukiSU](https://github.com/ReSukiSU/ReSukiSU)
- [SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)
- [SUSFS4OKI](https://github.com/cctv18/susfs4oki)
- [Fengchi Scheduler Patch (SCHED_PATCH)](https://github.com/Numbersf/SCHED_PATCH)
- [Re-Kernel](https://github.com/Sakion-Team/Re-Kernel)
- [Baseband-guard](https://github.com/vc-teahouse/Baseband-guard)
- [Droidspaces](https://github.com/Droidspaces)

### KSU Managers

- [ReSukiSU CI](https://github.com/cctv18/ReSukiSU_CI/releases)
- [SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra/releases)
- [KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next/releases)
- [KernelSU](https://github.com/tiann/KernelSU/releases)

### Community

- **Telegram Channel**: [@qdykernel](https://t.me/qdykernel)
- **CoolAPK Profile**: [@showdo](http://www.coolapk.com/u/1624571)
- **GitHub Issues**: [Submit Issue](https://github.com/showdo/Build_Oneplus_Realme_Action/issues)

### Credits

- [HanKuCha](https://github.com/HanKuCha/oneplus13_a5p_sukisu) — Early reference implementation
- [cctv18](https://github.com/cctv18) — Toolchain, patches, and public cache support

---

## 📜 License

This project is licensed under **GPL-3.0**. See [LICENSE](LICENSE) or [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/).

---

## 📈 Project Statistics

[![Star History Chart](https://api.star-history.com/svg?repos=showdo/Build_Oneplus_Realme_Action&type=Date)](https://star-history.com/#showdo/Build_Oneplus_Realme_Action&Date)

---

**Maintenance Status**: 🟢 Actively Maintained
