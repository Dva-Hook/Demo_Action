#!/usr/bin/env bash
set -euo pipefail

#######################################
# Build_oneplus_sm8750.sh
# 适用于本地 WSL / Ubuntu
#######################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"
WORKSPACE="$ROOT_DIR"
KERNEL_WORKSPACE="$ROOT_DIR/kernel_workspace"

#######################################
# 默认参数
#######################################
KSU_TYPE="ReSukiSU"
DEVICES_NAME="oneplus_ace5_pro"
CUSTOM_KERNEL_SUFFIX=""
CUSTOM_KERNEL_TIME=""
ENABLE_REKERNEL="false"
ENABLE_ADIOS="true"
ENABLE_SCX="true"
ENABLE_BBG="true"
ENABLE_SERIALID_CHECK="true"
ENABLE_SUSFS="true"

JOBS="$(nproc --all)"
CCACHE_DIR="${HOME}/.ccache_local_oneplus"
CCACHE_MAXSIZE="10G"

#######################################
# 帮助信息
#######################################
usage() {
  cat <<EOF
用法:
  $0 [选项]

选项:
  --device <name>                  机型
  --ksu <ReSukiSU|SukiSU-Ultra>    KSU类型
  --custom-kernel-suffix <suffix>  自定义内核后缀，建议以 - 开头
  --custom-kernel-time <time>      自定义构建时间
  --enable-rekernel <true|false>
  --enable-adios <true|false>
  --enable-scx <true|false>
  --enable-bbg <true|false>
  --enable-serialid-check <true|false>
  --enable-susfs <true|false>
  --jobs <N>                       编译线程数
  --ccache-dir <path>              ccache目录
  --help                           显示帮助

示例:
  $0 --device oneplus_ace5_pro --ksu ReSukiSU
  $0 --device oneplus_13 --ksu SukiSU-Ultra --enable-rekernel true
EOF
}

#######################################
# 参数解析
#######################################
while [[ $# -gt 0 ]]; do
  case "$1" in
    --device)
      DEVICES_NAME="$2"
      shift 2
      ;;
    --ksu)
      KSU_TYPE="$2"
      shift 2
      ;;
    --custom-kernel-suffix)
      CUSTOM_KERNEL_SUFFIX="$2"
      shift 2
      ;;
    --custom-kernel-time)
      CUSTOM_KERNEL_TIME="$2"
      shift 2
      ;;
    --enable-rekernel)
      ENABLE_REKERNEL="$2"
      shift 2
      ;;
    --enable-adios)
      ENABLE_ADIOS="$2"
      shift 2
      ;;
    --enable-scx)
      ENABLE_SCX="$2"
      shift 2
      ;;
    --enable-bbg)
      ENABLE_BBG="$2"
      shift 2
      ;;
    --enable-serialid-check)
      ENABLE_SERIALID_CHECK="$2"
      shift 2
      ;;
    --enable-susfs)
      ENABLE_SUSFS="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    --ccache-dir)
      CCACHE_DIR="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "未知参数: $1"
      usage
      exit 1
      ;;
  esac
done

#######################################
# 基础检查
#######################################
check_repo_files() {
  local missing=0

  for f in \
    "$ROOT_DIR/.github/workflows/tools/serialid_check.c" \
    "$ROOT_DIR/.github/workflows/tools/Re-Kernel_Support.patch" \
    "$ROOT_DIR/.github/workflows/tools/lz4armv8_support.patch" \
    "$ROOT_DIR/.github/workflows/tools/adios_ioscheduler.patch" \
    "$ROOT_DIR/.github/workflows/Bin/hmbird_patch.patch"; do
    if [[ ! -f "$f" ]]; then
      echo "缺少文件: $f"
      missing=1
    fi
  done

  if [[ "$missing" -ne 0 ]]; then
    echo "请在仓库根目录运行本脚本，且确保 .github/workflows 下的工具文件存在。"
    exit 1
  fi
}

#######################################
# 设置机型变量
#######################################
set_repo_manifest() {
  case "${DEVICES_NAME}" in
    oneplus_ace5_pro)
      REPO_MANIFEST="sm8750_b_16.0.0_oneplus_ace5_pro"
      IMAGENAME="Image_Op_Ace_5_Pro"
      SCHED_FILE="oneplus_ace5_pro_b"
      ;;
    oneplus_13)
      REPO_MANIFEST="sm8750_b_16.0.0_oneplus_13"
      IMAGENAME="Image_Op_13"
      SCHED_FILE="oneplus_13_b"
      ;;
    oneplus_ace_6)
      REPO_MANIFEST="sm8750_b_16.0.0_ace_6"
      IMAGENAME="Image_Op_Ace_6"
      SCHED_FILE="oneplus_ace_6"
      ;;
    oneplus_13t)
      REPO_MANIFEST="sm8750_b_16.0.0_oneplus_13t"
      IMAGENAME="Image_Op_13_T"
      SCHED_FILE="oneplus_13t_b"
      ;;
    oneplus_pad_2_pro)
      REPO_MANIFEST="sm8750_b_16.0.0_pad_2_pro"
      IMAGENAME="Image_Op_Pad_2_Pro_New"
      SCHED_FILE="oneplus_pad_2_pro_b"
      ;;
    oneplus_ace5_ultra)
      REPO_MANIFEST="mt6991_b_16.0.0_oneplus_ace5_ultra"
      IMAGENAME="Image_Op_Ace_5_Ultra"
      SCHED_FILE="oneplus_ace5_ultra_b"
      ;;
    realme_GT7)
      REPO_MANIFEST="mt6991_b_16.0.0_oneplus_ace5_ultra"
      IMAGENAME="Image_Rm_GT_7"
      SCHED_FILE="oneplus_ace5_ultra_b"
      ;;
    realme_GT7pro)
      REPO_MANIFEST=""
      IMAGENAME="Image_Rm_GT_7_Pro"
      SCHED_FILE="oneplus_ace_6"
      ;;
    realme_GT7pro_Speed)
      REPO_MANIFEST=""
      IMAGENAME="Image_Rm_GT_7_Pro_Speed"
      SCHED_FILE="oneplus_ace_6"
      ;;
    realme_GT8)
      REPO_MANIFEST=""
      IMAGENAME="Image_Rm_GT_8"
      SCHED_FILE="oneplus_ace_6"
      ;;
    *)
      echo "不支持的机型: ${DEVICES_NAME}"
      exit 1
      ;;
  esac

  if [[ -z "${CUSTOM_KERNEL_SUFFIX}" ]]; then
    case "${DEVICES_NAME}" in
      oneplus_pad_2_pro)
        DEFAULT_SUFFIX='-android15-8-g096cdb6ecefc-ab14358676-4k'
        ;;
      oneplus_ace5_ultra)
        DEFAULT_SUFFIX='-android15-8-ge6068c2aa11d-abogki454747580-4k'
        ;;
      oneplus_13|oneplus_13t|oneplus_ace5_pro|oneplus_ace_6|realme_GT7|realme_GT7pro_Speed|realme_GT8)
        DEFAULT_SUFFIX='-android15-8-g7e1f3c083cc6-abogki467167594-4k'
        ;;
      realme_GT7pro)
        DEFAULT_SUFFIX='-android15-8-gf4dc45704e54-abogki446052083-4k'
        ;;
    esac
    echo "使用原官核名称：$DEFAULT_SUFFIX"
  else
    if [[ "${CUSTOM_KERNEL_SUFFIX}" != -* ]]; then
      echo "警告: 自定义内核名称建议以 - 开头"
    fi
    DEFAULT_SUFFIX="${CUSTOM_KERNEL_SUFFIX}"
    echo "使用自定义名称: ${DEFAULT_SUFFIX}"
  fi

  if [[ -z "${CUSTOM_KERNEL_TIME}" ]]; then
    case "${DEVICES_NAME}" in
      oneplus_pad_2_pro)
        KERNEL_TIME='Tue Oct 28 09:04:21 UTC 2025'
        ;;
      oneplus_ace5_ultra)
        KERNEL_TIME='Tue Jul  1 19:48:18 UTC 2025'
        ;;
      oneplus_13|oneplus_13t|oneplus_ace5_pro|oneplus_ace_6|realme_GT7|realme_GT7pro_Speed|realme_GT8)
        KERNEL_TIME='Mon Dec  8 04:00:43 UTC 2025'
        ;;
      realme_GT7pro)
        KERNEL_TIME='Fri Sep 19 06:13:40 UTC 2025'
        ;;
    esac
    echo "使用官核时间：$KERNEL_TIME"
  else
    KERNEL_TIME="${CUSTOM_KERNEL_TIME}"
    echo "使用自定义构建时间: ${KERNEL_TIME}"
  fi
}

#######################################
# 安装依赖
#######################################
install_deps() {
  echo "==> 安装依赖"
  sudo apt update
  sudo apt install -y \
    binutils \
    python-is-python3 \
    libssl-dev \
    libelf-dev \
    dos2unix \
    ccache \
    p7zip-full \
    zstd \
    aria2 \
    unzip \
    wget \
    curl \
    git \
    patch \
    build-essential \
    flex \
    bison \
    bc \
    rsync \
    libncurses-dev
}

#######################################
# 初始化源码和工具链
#######################################
init_workspace() {
  echo "==> 初始化工作区"
  rm -rf "$KERNEL_WORKSPACE"
  mkdir -p "$KERNEL_WORKSPACE"
  cd "$KERNEL_WORKSPACE"

  echo "==> 克隆源码仓库..."
  if [[ "${DEVICES_NAME}" == "realme_GT7pro" || "${DEVICES_NAME}" == "realme_GT7pro_Speed" || "${DEVICES_NAME}" == "realme_GT8" ]]; then
    aria2c -s16 -x16 -k1M \
      https://github.com/realme-kernel-opensource/realme_GT8-AndroidB-common-source/archive/refs/heads/master.zip \
      -o common.zip
    unzip -q common.zip
    mv "realme_GT8-AndroidB-common-source-master" common
  elif [[ "${DEVICES_NAME}" == "oneplus_ace5_ultra" || "${DEVICES_NAME}" == "realme_GT7" ]]; then
    aria2c -s16 -x16 -k1M \
      "https://github.com/OnePlusOSS/android_kernel_oneplus_mt6991/archive/refs/heads/oneplus/${REPO_MANIFEST}.zip" \
      -o common.zip
    unzip -q common.zip
    mv "android_kernel_oneplus_mt6991-oneplus-${REPO_MANIFEST}" common
  else
    aria2c -s16 -x16 -k1M \
      "https://github.com/OnePlusOSS/android_kernel_common_oneplus_sm8750/archive/refs/heads/oneplus/${REPO_MANIFEST}.zip" \
      -o common.zip
    unzip -q common.zip
    mv "android_kernel_common_oneplus_sm8750-oneplus-${REPO_MANIFEST}" common
  fi
  rm -f common.zip

  echo "==> 下载 clang18 工具链..."
  mkdir -p clang18
  aria2c -s16 -x16 -k1M \
    https://github.com/cctv18/oneplus_sm8650_toolchain/releases/download/LLVM-Clang18-r510928/clang-r510928.zip \
    -o clang.zip
  unzip -q clang.zip -d clang18
  rm -f clang.zip

  echo "==> 下载 build-tools..."
  aria2c -s16 -x16 -k1M \
    https://github.com/cctv18/oneplus_sm8650_toolchain/releases/download/LLVM-Clang18-r510928/build-tools.zip \
    -o build-tools.zip
  unzip -q build-tools.zip
  rm -f build-tools.zip

  echo "==> 去除 ABI 保护 & dirty 后缀..."
  rm -f common/android/abi_gki_protected_exports_* || true
  sed -i 's/ -dirty//g' common/scripts/setlocalversion || true
  sed -i '$i res=$(echo "$res" | sed '\''s/-dirty//g'\'')' common/scripts/setlocalversion || true
}

#######################################
# 初始化 ccache
#######################################
init_ccache() {
  echo "==> 初始化 ccache"
  mkdir -p "$CCACHE_DIR"

  export CCACHE_COMPILERCHECK="none"
  export CCACHE_BASEDIR="$WORKSPACE"
  export CCACHE_NOHASHDIR="true"
  export CCACHE_HARDLINK="true"
  export CCACHE_DIR="$CCACHE_DIR"
  export CCACHE_MAXSIZE="$CCACHE_MAXSIZE"

  ccache -M "$CCACHE_MAXSIZE"
  ccache -o compression=true

  echo "ccache 状态:"
  ccache -s || true
}

#######################################
# 添加 SerialID 校验
#######################################
apply_serialid_check() {
  if [[ "$ENABLE_SERIALID_CHECK" != "true" ]]; then
    return
  fi

  echo "==> 添加 SerialID 校验"
  cd "$KERNEL_WORKSPACE/common"

  if grep -q 'SOC_SN_CHECK' init/main.c; then
    echo "main.c 已包含 SerialID 逻辑，跳过"
    return
  fi

  cp "$ROOT_DIR/.github/workflows/tools/serialid_check.c" ./
  LINE=$(grep -n '^#include' init/main.c | tail -n 1 | cut -d: -f1)
  head -n "$LINE" init/main.c > init/main.c.patched
  cat serialid_check.c >> init/main.c.patched
  tail -n +$((LINE+1)) init/main.c >> init/main.c.patched
  mv init/main.c.patched init/main.c
  echo "已自动插入 serialid_check.c 到 main.c"
}

#######################################
# 添加 Re-Kernel
#######################################
apply_rekernel() {
  if [[ "$ENABLE_REKERNEL" != "true" ]]; then
    return
  fi

  echo "==> 添加 Re-Kernel 支持"
  cd "$KERNEL_WORKSPACE/common"

  local patch_file="$ROOT_DIR/.github/workflows/tools/Re-Kernel_Support.patch"
  [[ -f "$patch_file" ]] || { echo "未找到补丁: $patch_file"; exit 1; }

  if grep -q "Re-Kernel" init/main.c 2>/dev/null || grep -q "re_kernel" init/main.c 2>/dev/null; then
    echo "Re-Kernel 已存在，跳过补丁"
  else
    cp "$patch_file" ./Re-Kernel_Support.patch
    if patch -p1 -N --ignore-whitespace -F 3 < Re-Kernel_Support.patch 2>&1 | tee /tmp/patch.log; then
      echo "Re-Kernel 补丁应用成功"
    else
      if grep -q "malformed patch" /tmp/patch.log; then
        patch -p1 -N --force --ignore-whitespace < Re-Kernel_Support.patch || true
      else
        cat /tmp/patch.log
        exit 1
      fi
    fi
    rm -f Re-Kernel_Support.patch
  fi

  echo "CONFIG_REKERNEL=y" >> arch/arm64/configs/gki_defconfig
}

#######################################
# 添加 lz4armv8
#######################################
apply_lz4armv8() {
  echo "==> 添加 LZ4 ARM64 硬件加速支持"
  cd "$KERNEL_WORKSPACE/common"

  local patch_file="$ROOT_DIR/.github/workflows/tools/lz4armv8_support.patch"
  [[ -f "$patch_file" ]] || { echo "未找到补丁: $patch_file"; exit 1; }

  if [[ -f "fs/f2fs/lz4armv8/lz4accel.c" ]]; then
    echo "LZ4 ARM64 加速文件已存在，跳过"
  else
    cp "$patch_file" ./lz4armv8_support.patch
    if patch -p1 --ignore-whitespace -F 3 < lz4armv8_support.patch 2>&1 | tee /tmp/lz4_patch.log; then
      echo "LZ4 ARM64 补丁应用成功"
    else
      if grep -q "malformed patch\|patch failed" /tmp/lz4_patch.log; then
        patch -p1 --force --ignore-whitespace < lz4armv8_support.patch || true
      else
        cat /tmp/lz4_patch.log
        exit 1
      fi
    fi
    rm -f lz4armv8_support.patch
  fi

  grep -q "CONFIG_F2FS_COMPRESSION=y" arch/arm64/configs/gki_defconfig || echo "CONFIG_F2FS_COMPRESSION=y" >> arch/arm64/configs/gki_defconfig
  grep -q "CONFIG_KERNEL_MODE_NEON=y" arch/arm64/configs/gki_defconfig || echo "CONFIG_KERNEL_MODE_NEON=y" >> arch/arm64/configs/gki_defconfig
}

#######################################
# 添加 ADIOS
#######################################
apply_adios() {
  if [[ "$ENABLE_ADIOS" != "true" ]]; then
    return
  fi

  echo "==> 添加 ADIOS I/O 调度器支持"
  cd "$KERNEL_WORKSPACE/common"

  local patch_file="$ROOT_DIR/.github/workflows/tools/adios_ioscheduler.patch"
  [[ -f "$patch_file" ]] || { echo "未找到补丁: $patch_file"; exit 1; }

  if [[ -f "block/adios.c" ]]; then
    echo "ADIOS 文件已存在，跳过"
  else
    cp "$patch_file" ./adios_ioscheduler.patch
    if patch -p1 --ignore-whitespace -F 3 < adios_ioscheduler.patch 2>&1 | tee /tmp/adios_patch.log; then
      echo "ADIOS 补丁应用成功"
    else
      if grep -q "malformed patch" /tmp/adios_patch.log; then
        patch -p1 --force --ignore-whitespace < adios_ioscheduler.patch || true
      fi
    fi
    rm -f adios_ioscheduler.patch
  fi

  if ! grep -q "CONFIG_MQ_IOSCHED_ADIOS" arch/arm64/configs/gki_defconfig; then
    echo "CONFIG_MQ_IOSCHED_ADIOS=y" >> arch/arm64/configs/gki_defconfig
    echo "CONFIG_MQ_IOSCHED_DEFAULT_ADIOS=y" >> arch/arm64/configs/gki_defconfig
  fi
}

#######################################
# 应用 zram 补丁
#######################################
apply_zram_patches() {
  echo "==> 应用 lz4 1.10.0 & zstd 1.5.7 补丁"
  cd "$KERNEL_WORKSPACE"

  rm -rf oppo_oplus_realme_sm8750
  git clone --depth=1 https://github.com/cctv18/oppo_oplus_realme_sm8750.git

  cp ./oppo_oplus_realme_sm8750/zram_patch/001-lz4.patch ./common/
  cp ./oppo_oplus_realme_sm8750/zram_patch/lz4armv8.S ./common/lib/
  cp ./oppo_oplus_realme_sm8750/zram_patch/002-zstd.patch ./common/

  cd ./common
  git apply -p1 < 001-lz4.patch || true
  patch -p1 < 002-zstd.patch || true
}

#######################################
# Baseband-guard
#######################################
apply_bbg() {
  if [[ "$ENABLE_BBG" != "true" ]]; then
    return
  fi

  echo "==> 启用 Baseband-guard"
  cd "$KERNEL_WORKSPACE"
  wget -O- https://github.com/vc-teahouse/Baseband-guard/raw/main/setup.sh | bash
  echo "CONFIG_BBG=y" >> ./common/arch/arm64/configs/gki_defconfig
  sed -i '/^config LSM$/,/^help$/{ /^[[:space:]]*default/ { /baseband_guard/! s/lockdown/lockdown,baseband_guard/ } }' ./common/security/Kconfig
}

#######################################
# 设置 KSU
#######################################
setup_ksu() {
  echo "==> 配置 ${KSU_TYPE}"
  cd "$KERNEL_WORKSPACE"

  if [[ "${KSU_TYPE}" == "ReSukiSU" ]]; then
    curl -LSs "https://raw.githubusercontent.com/ReSukiSU/ReSukiSU/refs/heads/main/kernel/setup.sh" | bash -s main
    cd ./KernelSU
    KSUVER=$(expr "$(git rev-list --count main)" + 30700 2>/dev/null || echo 114514)
    echo "KSUVER=${KSUVER}"
  else
    curl -LSs "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/refs/heads/main/kernel/setup.sh" | bash -s builtin
    cd ./KernelSU
    local GIT_COMMIT_HASH
    GIT_COMMIT_HASH=$(git rev-parse --short=8 HEAD)
    echo "当前提交哈希: $GIT_COMMIT_HASH"

    local KSU_API_VERSION=""
    for i in {1..3}; do
      KSU_API_VERSION=$(curl -s "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/builtin/kernel/Kbuild" | \
        grep -m1 "KSU_VERSION_API :=" | \
        awk -F'= ' '{print $2}' | tr -d '[:space:]')
      [[ -n "$KSU_API_VERSION" ]] && break || sleep 1
    done
    [[ -z "$KSU_API_VERSION" ]] && KSU_API_VERSION="4.1.0"

    local VERSION_DEFINITIONS
    VERSION_DEFINITIONS=$'define get_ksu_version_full\nv\\$1-'"$GIT_COMMIT_HASH"$'-TG@qdykernel\nendef\n\nKSU_VERSION_API := '"$KSU_API_VERSION"$'\nKSU_VERSION_FULL := v'"$KSU_API_VERSION"$'-'"$GIT_COMMIT_HASH"$'-TG@qdykernel'

    sed -i '/define get_ksu_version_full/,/endef/d' kernel/Kbuild
    sed -i '/KSU_VERSION_API :=/d' kernel/Kbuild
    sed -i '/KSU_VERSION_FULL :=/d' kernel/Kbuild
    awk -v def="$VERSION_DEFINITIONS" '
      /REPO_OWNER :=/ {print; print def; inserted=1; next}
      1
      END {if (!inserted) print def}
    ' kernel/Kbuild > kernel/Kbuild.tmp && mv kernel/Kbuild.tmp kernel/Kbuild

    KSUVER=$(expr "$(git rev-list --count main)" + 37185 2>/dev/null || echo 114514)
    echo "KSUVER=${KSUVER}"
    echo "SukiSU版本号: v${KSU_API_VERSION}-${GIT_COMMIT_HASH}-TG@qdykernel"
  fi
}

#######################################
# 设置 SUSFS
#######################################
setup_susfs() {
  if [[ "$ENABLE_SUSFS" != "true" ]]; then
    return
  fi

  echo "==> 配置 SUSFS"
  cd "$KERNEL_WORKSPACE"
  rm -rf susfs4ksu
  git clone --depth=1 https://github.com/cctv18/susfs4oki.git susfs4ksu -b oki-android15-6.6
  wget https://raw.githubusercontent.com/cctv18/oppo_oplus_realme_sm8750/main/other_patch/69_hide_stuff.patch -O ./common/69_hide_stuff.patch
  cp ./susfs4ksu/kernel_patches/50_add_susfs_in_gki-android15-6.6.patch ./common/
  cp ./susfs4ksu/kernel_patches/fs/* ./common/fs/
  cp ./susfs4ksu/kernel_patches/include/linux/* ./common/include/linux/
  cd ./common
  patch -p1 < 50_add_susfs_in_gki-android15-6.6.patch || true
  patch -p1 -N -F 3 < 69_hide_stuff.patch || true
  echo "[OK] SUSFS 补丁处理流程全部完成"
}

#######################################
# 设置 defconfig
#######################################
set_gki_defconfig() {
  echo "==> 设置 gki_defconfig"
  cd "$KERNEL_WORKSPACE"

  echo "CONFIG_KSU=y" >> ./common/arch/arm64/configs/gki_defconfig
  echo "CONFIG_KPM=y" >> ./common/arch/arm64/configs/gki_defconfig

  if [[ "${KSU_TYPE}" == "ReSukiSU" ]]; then
    echo 'CONFIG_KSU_FULL_NAME_FORMAT="%TAG_NAME%-%COMMIT_SHA%-Re-TG@qdykernel"' >> ./common/arch/arm64/configs/gki_defconfig
  fi

  if [[ "${ENABLE_SUSFS}" == "true" ]]; then
    cat >> ./common/arch/arm64/configs/gki_defconfig <<EOF
CONFIG_KSU_SUSFS=y
CONFIG_KSU_SUSFS_HAS_MAGIC_MOUNT=y
CONFIG_KSU_SUSFS_SUS_PATH=y
CONFIG_KSU_SUSFS_SUS_MOUNT=y
CONFIG_KSU_SUSFS_AUTO_ADD_SUS_KSU_DEFAULT_MOUNT=y
CONFIG_KSU_SUSFS_AUTO_ADD_SUS_BIND_MOUNT=y
CONFIG_KSU_SUSFS_SUS_KSTAT=y
CONFIG_KSU_SUSFS_TRY_UMOUNT=y
CONFIG_KSU_SUSFS_AUTO_ADD_TRY_UMOUNT_FOR_BIND_MOUNT=y
CONFIG_KSU_SUSFS_SPOOF_UNAME=y
CONFIG_KSU_SUSFS_ENABLE_LOG=y
CONFIG_KSU_SUSFS_HIDE_KSU_SUSFS_SYMBOLS=y
CONFIG_KSU_SUSFS_SPOOF_CMDLINE_OR_BOOTCONFIG=y
CONFIG_KSU_SUSFS_OPEN_REDIRECT=y
CONFIG_KSU_SUSFS_SUS_MAP=y
EOF
  else
    echo "未启用 SUSFS，跳过"
  fi

  echo "CONFIG_TMPFS_XATTR=y" >> ./common/arch/arm64/configs/gki_defconfig
  echo "CONFIG_TMPFS_POSIX_ACL=y" >> ./common/arch/arm64/configs/gki_defconfig
  echo "CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE=y" >> ./common/arch/arm64/configs/gki_defconfig

  sed -i 's/check_defconfig//' ./common/build.config.gki
}

#######################################
# 设置内核名称
#######################################
set_kernel_name() {
  echo "==> 设置内核名称"
  cd "$KERNEL_WORKSPACE"
  echo "内核后缀: $DEFAULT_SUFFIX"
  ESCAPED_SUFFIX=$(printf '%s\n' "$DEFAULT_SUFFIX" | sed 's:[\/&]:\\&:g')
  sed -i "s/-4k/$ESCAPED_SUFFIX/g" ./common/arch/arm64/configs/gki_defconfig
  sed -i 's/${scm_version}//' ./common/scripts/setlocalversion
}

#######################################
# 应用风驰补丁
#######################################
apply_sched_patch() {
  echo "==> 应用调度补丁"
  cd "$KERNEL_WORKSPACE/common"

  if [[ "${ENABLE_SCX}" == "true" ]]; then
    if [[ "$SCHED_FILE" == "none" ]]; then
      echo "该机型自带风驰，跳过"
    else
      rm -rf SCHED_PATCH
      if [[ "${DEVICES_NAME}" == "oneplus_ace5_ultra" || "${DEVICES_NAME}" == "realme_GT7" ]]; then
        git clone --depth=1 https://github.com/Numbersf/SCHED_PATCH.git -b "mt6991"
      else
        git clone --depth=1 https://github.com/Numbersf/SCHED_PATCH.git -b "sm8750"
      fi

      cp "./SCHED_PATCH/fengchi_${SCHED_FILE}.patch" ./
      if [[ -f "fengchi_${SCHED_FILE}.patch" ]]; then
        dos2unix "fengchi_${SCHED_FILE}.patch"
        patch -p1 -F 3 < "fengchi_${SCHED_FILE}.patch"
        echo "完美风驰补丁应用完成"
      else
        echo "未匹配到风驰补丁"
        exit 11
      fi
    fi
  else
    echo "未启用风驰，应用 OGKI 转 GKI 补丁"
    sed -i '1iobj-y += hmbird_patch.o' drivers/Makefile
    cp "$ROOT_DIR/.github/workflows/Bin/hmbird_patch.patch" ./hmbird_patch.patch
    patch -p1 -F 3 < hmbird_patch.patch
    echo "OGKI 转 GKI patch 完成"
  fi
}

#######################################
# 编译内核
#######################################
build_kernel() {
  echo "==> 开始构建"
  local BUILD_START
  BUILD_START=$(date +%s)

  export PATH="/usr/lib/ccache:$PATH"
  export PATH="$KERNEL_WORKSPACE/clang18/bin:$PATH"
  export PATH="$KERNEL_WORKSPACE/build-tools/bin:$PATH"

  local CLANG_DIR="$KERNEL_WORKSPACE/clang18/bin"
  echo "clang版本: $("$CLANG_DIR/clang" --version | head -n 1)"
  echo "ld.lld版本: $("$CLANG_DIR/ld.lld" --version | head -n 1)"

  export CCACHE_LOGFILE="${KERNEL_WORKSPACE}/ccache.log"
  export CCACHE_COMPILERCHECK="none"
  export CCACHE_BASEDIR="${WORKSPACE}"
  export CCACHE_NOHASHDIR="true"
  export CCACHE_HARDLINK="true"
  export CCACHE_DIR="${CCACHE_DIR}"
  export CCACHE_MAXSIZE="3G"

  mkdir -p "$CCACHE_DIR"
  echo "sloppiness = file_stat_matches,include_file_ctime,include_file_mtime,pch_defines,file_macro,time_macros" >> "$CCACHE_DIR/ccache.conf"

  cd "$KERNEL_WORKSPACE/common"

  wget -q https://github.com/cctv18/oppo_oplus_realme_sm8750/raw/refs/heads/main/lib/libfakestat.so
  wget -q https://github.com/cctv18/oppo_oplus_realme_sm8750/raw/refs/heads/main/lib/libfaketimeMT.so
  chmod 777 ./*.so

  export FAKESTAT="2025-05-25 12:00:00"
  export FAKETIME="@2025-05-25 13:00:00"
  export KBUILD_BUILD_TIMESTAMP="${KERNEL_TIME}"

  local SO_DIR
  SO_DIR=$(pwd)
  export PRELOAD_LIBS="$SO_DIR/libfakestat.so $SO_DIR/libfaketimeMT.so"

  cat > cc-wrapper <<EOF
#!/bin/bash
export LD_PRELOAD="$PRELOAD_LIBS"
export FAKESTAT="$FAKESTAT"
export FAKETIME="$FAKETIME"
ccache clang "\$@"
EOF

  cat > ld-wrapper <<EOF
#!/bin/bash
export LD_PRELOAD="$PRELOAD_LIBS"
export FAKESTAT="$FAKESTAT"
export FAKETIME="$FAKETIME"
ld.lld "\$@"
EOF

  chmod +x cc-wrapper ld-wrapper

  make -j"${JOBS}" LLVM=1 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
    CC="ccache clang" LD="ld.lld" HOSTLD=ld.lld O=out KCFLAGS+=-O2 KCFLAGS+=-Wno-error gki_defconfig

  make -j"${JOBS}" LLVM=1 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
    CC="$(pwd)/cc-wrapper" LD="$(pwd)/ld-wrapper" HOSTLD=ld.lld O=out KCFLAGS+=-O2 KCFLAGS+=-Wno-error Image

  echo "ccache 状态:"
  ccache -s || true

  local BUILD_END BUILD_TIME
  BUILD_END=$(date +%s)
  BUILD_TIME=$((BUILD_END - BUILD_START))
  echo "构建耗时: ${BUILD_TIME} 秒"
}

#######################################
# 输出产物
#######################################
package_output() {
  echo "==> 处理构建产物"
  cd "$KERNEL_WORKSPACE/common/out/arch/arm64/boot"

  [[ -f Image ]] || { echo "未找到 Image，构建可能失败"; exit 1; }

  cp ./Image "./${IMAGENAME}"
  echo "镜像输出: $KERNEL_WORKSPACE/common/out/arch/arm64/boot/${IMAGENAME}"

  cd "$ROOT_DIR"
  rm -rf ./AnyKernel3
  git clone https://github.com/showdo/AnyKernel3.git --depth=1
  rm -rf ./AnyKernel3/.git
  rm -rf ./AnyKernel3/push.sh
  cp "$KERNEL_WORKSPACE/common/out/arch/arm64/boot/Image" ./AnyKernel3/
  7z a -t7z -p'501b10728d2cb08abe16eb8b0bdee33c9d2382e1' -mhe=on "./AnyKernel3/TG频道@qdykernel.7z" ./AnyKernel3/Image >/dev/null
  rm -f ./AnyKernel3/Image

  echo
  echo "================ 构建完成 ================"
  echo "Image:     $KERNEL_WORKSPACE/common/out/arch/arm64/boot/${IMAGENAME}"
  echo "AnyKernel: $ROOT_DIR/AnyKernel3/TG频道@qdykernel.7z"
  echo "KSUVER:    ${KSUVER:-unknown}"
  echo "========================================="
}

#######################################
# 主流程
#######################################
main() {
  check_repo_files
  set_repo_manifest

  echo "========================================="
  echo "设备:               $DEVICES_NAME"
  echo "KSU:                $KSU_TYPE"
  echo "ReKernel:           $ENABLE_REKERNEL"
  echo "ADIOS:              $ENABLE_ADIOS"
  echo "SCX:                $ENABLE_SCX"
  echo "BBG:                $ENABLE_BBG"
  echo "SerialID Check:     $ENABLE_SERIALID_CHECK"
  echo "SUSFS:              $ENABLE_SUSFS"
  echo "JOBS:               $JOBS"
  echo "CCACHE_DIR:         $CCACHE_DIR"
  echo "========================================="

  install_deps
  init_workspace
  init_ccache

  apply_serialid_check
  apply_rekernel
  apply_lz4armv8
  apply_adios
  apply_zram_patches
  apply_bbg
  setup_ksu
  setup_susfs
  set_gki_defconfig
  set_kernel_name
  apply_sched_patch
  build_kernel
  package_output
}

main "$@"