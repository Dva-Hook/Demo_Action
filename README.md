# OnePlus / Realme / Lenovo SM8750 内核构建项目

**`简体中文`** | [English](README-en.md)

[![GitHub](https://img.shields.io/badge/-GitHub|@showdo-181717?logo=github&logoColor=white&style=flat-square)](https://github.com/showdo/Build_Oneplus_Realme_Action)
[![Telegram](https://img.shields.io/badge/Telegram-频道-blue.svg?logo=telegram)](https://t.me/qdykernel)
[![酷安|主页](https://img.shields.io/badge/酷安|主页-3DDC84?style=flat-square&logo=android&logoColor=white)](http://www.coolapk.com/u/1624571)
[![Workflow Status](https://img.shields.io/github/actions/workflow/status/showdo/Build_Oneplus_Realme_Action/Build_all_devices_sm8750.yml?label=SM8750&logo=github-actions&style=flat-square)](https://github.com/showdo/Build_Oneplus_Realme_Action/actions)

---

## 📖 项目简介

本项目提供基于 **GitHub Actions** 的自动化内核编译工作流，支持 **OnePlus**、**Realme** 及**联想**多款搭载 **SM8750 / MT6991** 平台的设备。通过高度集成的脚本，实现一键编译包含 **ReSukiSU**、**SUSFS**、**完美风驰 (SCX)**、**ADIOS I/O 调度器** 等功能的定制内核。

---

## ✨ 主要特性

| 功能 | 说明 |
|------|------|
| 🚀 **全自动化编译** | 基于 GitHub Actions，无需本地环境 |
| 🔐 **ReSukiSU 集成** | 内核级 Root 方案，可选启用 |
| 🛡 **SUSFS 支持** | 完整 Magic Mount 挂载隐藏支持 |
| ⚡ **完美风驰 (SCX)** | 集成 SCX 调度器补丁，显著提升流畅度 |
| 📡 **ADIOS I/O 调度器** | 优化存储 I/O 性能 |
| 🔒 **BBG 基带守护** | 内核级基带保护 |
| 📱 **Re-Kernel 支持** | 增强后台冻结能力（需配合 NoActive） |
| 🐳 **Droidspaces** | Linux 容器支持（ntsync + SYSVIPC 等） |
| 🆔 **SerialID 校验** | 防止内核被移植到不支持的设备 |
| 📦 **lz4 1.10.0 + zstd 1.5.7** | 更新 ZRAM 压缩算法，提升内存压缩效率 |
| 💾 **ccache 智能缓存** | 自动匹配公共缓存，首次构建加速约 50%，二次构建加速约 80% |
| 🔑 **KPM 支持** | 内核补丁模块支持（联想设备） |
| 📦 **AnyKernel3 / Boot 签名** | 自动打包刷入包或签名 boot 镜像 |

---

## 📱 支持的设备

### OnePlus / Realme (SM8750 / MT6991)

> 工作流：`Build_All_Devices_SM8750`

| 序号 | 设备名称 | 代号 | 平台 |
|------|---------|------|------|
| 1 | 一加 13 | `oneplus_13` | SM8750 |
| 2 | 一加 Ace 5 Pro | `oneplus_ace5_pro` | SM8750 |
| 3 | 一加 Ace 6 | `oneplus_ace_6` | SM8750 |
| 4 | 一加 13T | `oneplus_13t` | SM8750 |
| 5 | 一加 Pad 2 | `oneplus_pad_2` | MT6991 |
| 6 | 一加 Pad 2 Pro | `oneplus_pad_2_pro` | SM8750 |
| 7 | 一加 Ace5 至尊版 | `oneplus_ace5_ultra` | MT6991 |
| 8 | 真我 GT 7 | `realme_GT7` | MT6991 |
| 9 | 真我 GT 7 Pro | `realme_GT7pro` | SM8750 |
| 10 | 真我 GT 7 Pro 竞速 | `realme_GT7pro_Speed` | SM8750 |
| 11 | 真我 GT 8 | `realme_GT8` | SM8750 |

### 联想 (Lenovo) SM8750

> 工作流：`Build_All_Lenovo_sm8750`

| 内核版本 | 安全补丁级别 | 对应固件 |
|---------|------------|---------|
| 6.6.56 | 2024-11 | TB322FC 1.1.11.120 |
| 6.6.89 | 2025-06 | ColorOS 16 400 |
| 6.6.102 | 2025-10 | TB322FC 1.5.10.096 |
| 6.6.118 | 2026-01 | ZUXOS 1.5.10.183 |

---

## 🎯 快速开始

### 步骤 1：Fork 本仓库

点击仓库右上角的 **Fork** 按钮，将本仓库复制到你自己的 GitHub 账户。

### 步骤 2：运行工作流

1. 进入你 Fork 的仓库，点击 **Actions** 标签页
2. 根据你的设备选择对应工作流：
   - OnePlus / Realme：选择 **`Build_All_Devices_SM8750`**
   - 联想平板：选择 **`Build_All_Lenovo_sm8750`**
3. 点击 **Run workflow**，按需勾选功能选项
4. 等待构建完成（首次约 12 分钟，二次约 3~5 分钟）
5. 在 **Actions → 对应运行记录 → Artifacts** 中下载构建产物，或在 **Releases** 页面获取自动发布的版本

---

## ⚙️ 构建参数说明

### OnePlus / Realme 工作流参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 一键编译所有机型 | `false` | 同时编译所有支持的设备 |
| 选择机型 | `oneplus_13` | 单独编译指定机型 |
| 自定义内核名称 | 空（使用官方） | 以 `-` 开头 |
| 自定义构建时间 | 空（使用官方） | 英文时间字符串格式 |
| Re-Kernel 支持 | `false` | 增强后台冻结 |
| ADIOS I/O 调度器 | `true` | 优化存储性能 |
| 完美风驰 (SCX) | `true` | SCX 调度器补丁 |
| BBG 基带守护 | `true` | 内核级基带保护 |
| Droidspaces | `false` | Linux 容器支持 |
| SerialID 校验 | `true` | 序列号绑定验证 |
| KernelSU (ReSukiSU) | `true` | Root 支持 |
| SUSFS | `true` | 挂载隐藏支持 |

### 联想工作流参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 一键编译所有版本 | `false` | 同时编译所有内核版本 |
| 内核版本 | `6.6.89` | 选择目标内核版本 |
| BBG 基带守护 | `false` | 内核级基带保护 |
| KernelSU (ReSukiSU) | `true` | Root 支持 |
| Re-Kernel 支持 | `true` | 增强后台冻结 |
| ADIOS I/O 调度器 | `true` | 优化存储性能 |
| Droidspaces | `false` | Linux 容器支持 |
| KPM | `true` | 内核补丁模块 |
| SUSFS | `true` | 挂载隐藏支持 |
| AOSP 密钥签名 boot | `true` | 使用 AOSP 测试密钥签名 |

---

## 📥 安装方法

### AnyKernel3 刷入包（OnePlus / Realme）

1. 若已使用 ReSukiSU 内核，且管理器已更新至最新版本，可在管理器中直接刷入 AnyKernel3 刷机包并重启
2. 由于 KernelSU 上游更新了元模块功能，最新版管理器需配合元模块才能正常挂载模块。可用的元模块包括：
   - [meta overlayfs](https://github.com/KernelSU-Modules-Repo/meta-overlayfs)
   - [mountify](https://github.com/backslashxx/mountify)
   - [meta magic_mount](https://github.com/7a72/meta-magic_mount/)
3. 若启用了 Re-Kernel，需刷入配套 Re-Kernel 模块并配合 NoActive 软件使用

### Boot 镜像（联想设备）

直接使用 `fastboot flash boot boot.img` 刷入已签名的 boot 镜像

> ※※※ 刷写内核有风险，刷入前请务必用 [KernelFlasher](https://github.com/capntrips/KernelFlasher) 备份 boot 等关键启动分区！※※※

---

## 🔧 高级功能

### ccache 缓存说明

- **私有缓存**：每台设备/版本独立维护缓存，构建时间超过 8 分钟自动更新
- **公共缓存**：当私有缓存未命中时，自动从公共仓库拉取，加速首次构建
- **Droidspaces 变体**：启用 Droidspaces 时使用独立缓存键（`-ds` 后缀），避免污染标准缓存
- **缓存仓库**：可通过仓库变量 `PUBLIC_CACHE_REPO` 和 `PUBLIC_CACHE_TAG` 自定义

### 功能依赖关系

- 启用 **Droidspaces** 时会自动强制启用 **完美风驰 (SCX)**（因为 Droidspaces 依赖 SCX）
- 启用 **SUSFS** 需同时启用 **KernelSU**
- **Re-Kernel** 独立于 KSU，可单独启用

### 日志标记

```
[INFO]    - 一般信息
[SUCCESS] - 成功完成
[ERROR]   - 错误（需立即处理）
```

---

## 🔗 相关资源

### 上游项目

- [OnePlus 内核开源](https://github.com/OnePlusOSS/kernel_manifest)
- [Realme 内核开源](https://github.com/realme-kernel-opensource)
- [ReSukiSU](https://github.com/ReSukiSU/ReSukiSU)
- [SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)
- [SUSFS4OKI](https://github.com/cctv18/susfs4oki)
- [完美风驰补丁 (SCHED_PATCH)](https://github.com/Numbersf/SCHED_PATCH)
- [Re-Kernel](https://github.com/Sakion-Team/Re-Kernel)
- [Baseband-guard](https://github.com/vc-teahouse/Baseband-guard)
- [Droidspaces](https://github.com/Droidspaces)

### KSU 管理器

- [ReSukiSU CI](https://github.com/cctv18/ReSukiSU_CI/releases)
- [SukiSU-Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra/releases)
- [KernelSU-Next](https://github.com/KernelSU-Next/KernelSU-Next/releases)
- [KernelSU 原版](https://github.com/tiann/KernelSU/releases)

### 社区支持

- **Telegram 频道**: [@qdykernel](https://t.me/qdykernel)
- **酷安主页**: [@showdo](http://www.coolapk.com/u/1624571)
- **GitHub Issues**: [提交问题](https://github.com/showdo/Build_Oneplus_Realme_Action/issues)

### 致谢

- [HanKuCha](https://github.com/HanKuCha/oneplus13_a5p_sukisu) — 早期参考实现
- [cctv18](https://github.com/cctv18) — 工具链、补丁及公共缓存支持

---

## 📜 许可证

本项目采用 **GPL-3.0** 许可证。详见 [LICENSE](LICENSE) 或 [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/)。

---

## 📈 项目统计

[![Star History Chart](https://api.star-history.com/svg?repos=showdo/Build_Oneplus_Realme_Action&type=Date)](https://star-history.com/#showdo/Build_Oneplus_Realme_Action&Date)

---

**维护状态**: 🟢 活跃维护中
