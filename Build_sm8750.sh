#!/bin/bash

# 颜色定义
info() {
  tput setaf 3  
  echo "[INFO] $1"
  tput sgr0
}

error() {
  tput setaf 1
  echo "[ERROR] $1"
  tput sgr0
  exit 1
}


# 参数设置
ENABLE_KPM=true

# 分支选择
info "请选择要编译的分支："
info "1. ReSukiSU"
info "2. SukiSU-Ultra"
read -p "输入选择 [1-2]: " ksu_choice

# 根据选择设置分支名称
case $ksu_choice in
  1)
    KSU_TYPE="ReSukiSU"
    info "已选择：ReSukiSU"
    ;;
  2)
    KSU_TYPE="SukiSU-Ultra"
    info "已选择：SukiSU-Ultra"
    ;;
  *)
    error "无效的选择，请输入 1-2"
    ;;
esac


# 机型选择
info "请选择要编译的机型："
info "1. 一加 13"
info "2. 一加 Ace 5 Pro"
info "3.一加 Ace 6"
info "4.一加 13T"
info "5.一加 Pad 2 Pro"
info "6.一加 Ace5 至尊版"
info "7.真我 GT 7"
info "8.真我 GT 7 Pro"
info "9.真我 GT 7 Pro 竞速"
info "10.真我 GT 8"

read -p "输入选择 [1-10]: " device_choice

case $device_choice in
    1)
        DEVICE_NAME="oneplus_13"
        REPO_BRANCH="sm8750_b_16.0.0_oneplus_13"
        REPO_MANIFEST="sm8750_b_16.0.0_oneplus_13"
        KERNEL_TIME="Fri Sep 19 06:13:40 UTC 2025"
        KERNEL_SUFFIX="-android15-8-gf4dc45704e54-abogki446052083-4k"
        SCHED_FILE="oneplus_13_b"
        ;;
    2)
        DEVICE_NAME="oneplus_ace5_pro"
        REPO_BRANCH="sm8750_b_16.0.0_oneplus_ace5_pro"
        REPO_MANIFEST="sm8750_b_16.0.0_oneplus_ace5_pro"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace5_pro_b"
        ;;
    3)
        DEVICE_NAME="oneplus_ace5_pro"
        REPO_BRANCH="sm8750_b_16.0.0_oneplus_ace5_pro"
        REPO_MANIFEST="sm8750_b_16.0.0_oneplus_ace5_pro"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace5_pro_b"
        ;;
    4)
        DEVICE_NAME="oneplus_ace6"
        REPO_BRANCH="sm8750_b_16.0.0_ace_6"
        REPO_MANIFEST="sm8750_b_16.0.0_ace_6"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace_6"
        ;;
    5)
        DEVICE_NAME="oneplus_pad_2_pro"
        REPO_BRANCH="oneplus_pad_2_pro.xml"
        REPO_MANIFEST="oneplus_pad_2_pro"
        KERNEL_TIME="Fri Jul 11 22:46:09 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g5a0ffb447c1d-ab13771415-4k"   
        ;;
    6)
        DEVICE_NAME="oneplus_ace5_ultra"
        REPO_BRANCH="mt6991_v_15.0.2_ace5_ultra"
        REPO_MANIFEST="mt6991_v_15.0.2_ace5_ultra"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace5_ultra"
        ;;  
    7)
        DEVICE_NAME="realme_GT7"
        REPO_BRANCH="sm8750_b_16.0.0_oneplus_ace5_pro"
        REPO_MANIFEST="sm8750_b_16.0.0_oneplus_ace5_pro"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace5_pro_b"
        ;;
    8)
        DEVICE_NAME="realme_GT7pro"
        REPO_MANIFEST="master"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace_6"
        ;;
    9)
        DEVICE_NAME="realme_GT7pro_Speed"
        REPO_MANIFEST="master"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace_6"
        ;;
    10)
        DEVICE_NAME="realme_GT8"
        REPO_MANIFEST="master"
        KERNEL_TIME="Tue Jul  1 19:48:18 UTC 2025"
        KERNEL_SUFFIX="-android15-8-g29d86c5fc9dd-abogki428889875-4k"
        SCHED_FILE="oneplus_ace_6"
        ;;
    *)
        error "无效的选择，请输入1-10之间的数字"
        ;;
esac

# 自定义补丁
# 函数：用于判断输入，确保无效输入返回默认值
prompt_boolean() {
    local prompt="$1"
    local default_value="$2"
    local result
    read -p "$prompt" result
    case "$result" in
        [nN]) echo false ;;
        [yY]) echo true ;;
        "") echo "$default_value" ;;
        *) echo "$default_value" ;;
    esac
}

# 自定义补丁设置

read -p "输入内核名称修改(带 - 开头，回车默认官方): " input_suffix
[ -n "$input_suffix" ] && KERNEL_SUFFIX="$input_suffix"

read -p "输入内核构建日期更改(回车默认官方): " input_time
[ -n "$input_time" ] && KERNEL_TIME="$input_time"

ENABLE_SCX=$(prompt_boolean "是否集成完美风驰补丁？(回车默认集成) [y/N]: " true)

ENABLE_BBG=$(prompt_boolean "是否启用BBG基带守护？(回车默认开启) [y/N]: " true)

# 选择的机型信息输出
info "选择的机型: $DEVICE_NAME"
info "内核名称: $KERNEL_SUFFIX"
info "内核时间: $KERNEL_TIME"
info "是否集成完美风驰：$ENABLE_SCX"
info "是否启用BBG: $ENABLE_BBG"

echo "请确认以上信息..."
echo "按任意键继续，按下 Ctrl+C 退出..."
read -n 1 -s


# 工作目录 - 按机型区分
WORKSPACE="$HOME/kernel_${DEVICE_NAME}"
mkdir -p "$WORKSPACE" || error "无法创建工作目录"
cd "$WORKSPACE" || error "无法进入工作目录"

# ==================== 源码管理 ====================
# 创建源码目录
KERNEL_WORKSPACE="$WORKSPACE/kernel_workspace"

mkdir -p "$KERNEL_WORKSPACE" || error "无法创建kernel_workspace目录"

cd "$KERNEL_WORKSPACE" || error "无法进入kernel_workspace目录"

sudo apt-mark hold firefox
sudo apt-mark hold libc-bin 
sudo apt purge man-db 
sudo rm -rf /var/lib/man-db/auto-update 
sudo apt update 
 sudo apt-get install -y --no-install-recommends binutils python-is-python3 libssl-dev libelf-dev dos2unix ccache p7zip-full aria2 unzip
info "正在克隆源码仓库..."
 if [ "${DEVICE_NAME}" = "realme_GT7pro" ] || [ "${DEVICE_NAME}" = "realme_GT7pro_Speed" ] || [ "${DEVICE_NAME}" = "realme_GT8" ]; then
  aria2c -s16 -x16 -k1M https://github.com/realme-kernel-opensource/realme_GT8pro-AndroidB-common-source/archive/refs/heads/master.zip -o common.zip
  unzip -q common.zip  
  mv "realme_GT7pro-AndroidB-common-source-master" common
 elif [ "${DEVICE_NAME}" = "oneplus_ace5_ultra" ] || [ "${DEVICE_NAME}" = "realme_GT7" ]; then
  aria2c -s16 -x16 -k1M https://github.com/OnePlusOSS/android_kernel_oneplus_mt6991/archive/refs/heads/oneplus/${REPO_MANIFEST}.zip -o common.zip
  unzip -q common.zip  
  mv "android_kernel_oneplus_mt6991-oneplus-${REPO_MANIFEST}" common
else
  aria2c -s16 -x16 -k1M https://github.com/OnePlusOSS/android_kernel_common_oneplus_sm8750/archive/refs/heads/oneplus/${REPO_MANIFEST}.zip -o common.zip
  unzip -q common.zip  
  mv "android_kernel_common_oneplus_sm8750-oneplus-${REPO_MANIFEST}" common
fi
rm -rf common.zip 
info "正在克隆llvm-clang18工具链..."
mkdir -p clang18 
aria2c -s16 -x16 -k1M https://github.com/cctv18/oneplus_sm8650_toolchain/releases/download/LLVM-Clang18-r510928/clang-r510928.zip -o clang.zip 
unzip -q clang.zip -d clang18 
rm -rf clang.zip 
info "正在克隆构建工具..." 
aria2c -s16 -x16 -k1M https://github.com/cctv18/oneplus_sm8650_toolchain/releases/download/LLVM-Clang18-r510928/build-tools.zip -o build-tools.zip 
unzip -q build-tools.zip 
rm -rf build-tools.zip 
wait
info "所有源码及llvm-Clang18工具链初始化完成！"
info "正在去除 ABI 保护 & 去除 dirty 后缀..."
rm common/android/abi_gki_protected_exports_* || true
for f in common/scripts/setlocalversion; do
  sed -i 's/ -dirty//g' "$f"
  sed -i '$i res=$(info "$res" | sed '\''s/-dirty//g'\'')' "$f"
done
cd "$KERNEL_WORKSPACE" || error "无法进入kernel_workspace目录"

# 环境变量 - 按机型区分ccache目录
export CCACHE_COMPILERCHECK="%compiler% -dumpmachine; %compiler% -dumpversion"
export CCACHE_NOHASHDIR="true"
export CCACHE_HARDLINK="true"
# 按 KSU_TYPE 和 DEVICE_NAME 区分缓存目录（替换特殊字符为下划线）
KSU_TYPE_SAFE=$(echo "${KSU_TYPE}" | tr '-' '_')
export CCACHE_DIR="$HOME/.ccache_${KSU_TYPE_SAFE}_${DEVICE_NAME}"
export CCACHE_MAXSIZE="8G"
cd "$KERNEL_WORKSPACE" || error "无法进入kernel_workspace目录"

# ccache 初始化标志文件也按机型区分
CCACHE_INIT_FLAG="$CCACHE_DIR/.ccache_initialized"

# 初始化 ccache（仅第一次）
if command -v ccache >/dev/null 2>&1; then
    if [ ! -f "$CCACHE_INIT_FLAG" ]; then
        info "第一次为${KSU_TYPE}/${DEVICE_NAME}初始化ccache..."
        mkdir -p "$CCACHE_DIR" || error "无法创建ccache目录"
        ccache -M "$CCACHE_MAXSIZE"
        touch "$CCACHE_INIT_FLAG"
    else
        info "ccache (${KSU_TYPE}/${DEVICE_NAME}) 已初始化，跳过..."
    fi
else
    info "未安装 ccache，跳过初始化"
fi
cd "$KERNEL_WORKSPACE" || error "无法进入kernel_workspace目录"

#添加lz4 1.10.0 & zstd 1.5.7补丁
info "正在添加lz4 1.10.0 & zstd 1.5.7补丁…"
curl -LSs https://raw.githubusercontent.com/cctv18/oppo_oplus_realme_sm8750/main/zram_patch/001-lz4.patch -o ./common/001-lz4.patch
curl -LSs https://raw.githubusercontent.com/cctv18/oppo_oplus_realme_sm8750/main/zram_patch/lz4armv8.S -o ./common/lib/lz4armv8.S
curl -LSs https://raw.githubusercontent.com/cctv18/oppo_oplus_realme_sm8750/main/zram_patch/002-zstd.patch -o ./common/002-zstd.patch
cd ./common
git apply -p1 < 001-lz4.patch || true
patch -p1 < 002-zstd.patch || true

#开启BBG基带守护
if [ "$ENABLE_BBG" = true ]; then
  cd $KERNEL_WORKSPACE/common
  echo "正在启用BBG基带守护…"
  curl -LSs https://raw.githubusercontent.com/vc-teahouse/Baseband-guard/main/setup.sh | bash
  sed -i '/^config LSM$/,/^help$/{ /^[[:space:]]*default/ { /baseband_guard/! s/lockdown/lockdown,baseband_guard/ } }' ./security/Kconfig
else
  info "未启用BBG基带守护，跳过步骤...."
fi

# 设置KSU
info "设置${KSU_TYPE}..."
cd $KERNEL_WORKSPACE
if [ "${KSU_TYPE}" = "ReSukiSU" ]; then
  curl -LSs "https://raw.githubusercontent.com/ReSukiSU/ReSukiSU/refs/heads/main/kernel/setup.sh" | bash -s main
  cd ./KernelSU 
  KSU_VERSION=$(expr $(git rev-list --count main) + 30700 2>/dev/null || echo 114514)
else
  curl -LSs "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/refs/heads/main/kernel/setup.sh" | bash -s builtin
  cd ./KernelSU
  GIT_COMMIT_HASH=$(git rev-parse --short=8 HEAD)
  echo "当前提交哈希: $GIT_COMMIT_HASH"
  export KSU_VERSION=$KSU_VERSION
  for i in {1..3}; do
    KSU_API_VERSION=$(curl -s "https://raw.githubusercontent.com/SukiSU-Ultra/SukiSU-Ultra/builtin/kernel/Kbuild" | 
      grep -m1 "KSU_VERSION_API :=" | 
      awk -F'= ' '{print $2}' | 
      tr -d '[:space:]')
    [ -n "$KSU_API_VERSION" ] && break
    [ $i -lt 3 ] && sleep 1
  done
  [ -z "$KSU_API_VERSION" ] && KSU_API_VERSION="4.1.0"
  echo "KSU_API_VERSION=$KSU_API_VERSION"
  VERSION_DEFINITIONS=$'define get_ksu_version_full\nv\\$1-'"$GIT_COMMIT_HASH"$'-TG@qdykernel\nendef\n\nKSU_VERSION_API := '"$KSU_API_VERSION"$'\nKSU_VERSION_FULL := v'"$KSU_API_VERSION"$'-'"$GIT_COMMIT_HASH"$'-TG@qdykernel'

  sed -i '/define get_ksu_version_full/,/endef/d' kernel/Kbuild
  sed -i '/KSU_VERSION_API :=/d' kernel/Kbuild
  sed -i '/KSU_VERSION_FULL :=/d' kernel/Kbuild
  awk -v def="$VERSION_DEFINITIONS" '
    /REPO_OWNER :=/ {print; print def; inserted=1; next}
    1
    END {if (!inserted) print def}
  ' kernel/Kbuild > kernel/Kbuild.tmp && mv kernel/Kbuild.tmp kernel/Kbuild
  KSU_VERSION=$(expr $(git rev-list --count main) + 37185 2>/dev/null || echo 114514)
  grep -A10 "REPO_OWNER" kernel/Kbuild
  grep "KSU_VERSION_FULL" kernel/Kbuild
  echo "SukiSU版本号: v${KSU_API_VERSION}-${GIT_COMMIT_HASH}-TG@qdykernel"
fi


# 添加susfs补丁
info "设置susfs..."
cd $KERNEL_WORKSPACE
git clone --depth=1 https://github.com/cctv18/susfs4oki.git susfs4ksu -b oki-android15-6.6
wget https://raw.githubusercontent.com/cctv18/oppo_oplus_realme_sm8750/main/other_patch/69_hide_stuff.patch -O ./common/69_hide_stuff.patch
cp ./susfs4ksu/kernel_patches/50_add_susfs_in_gki-android15-6.6.patch ./common/
cp ./susfs4ksu/kernel_patches/fs/* ./common/fs/
cp ./susfs4ksu/kernel_patches/include/linux/* ./common/include/linux/
cd ./common
patch -p1 < 50_add_susfs_in_gki-android15-6.6.patch || true
patch -p1 -N -F 3 < 69_hide_stuff.patch || true
echo "[OK] SUSFS 补丁处理流程全部完成"

#设置config
cd $KERNEL_WORKSPACE/common/arch/arm64/configs || error "进入configs目录失败"
info "设置内核Config..."
# KSU 基础配置
echo "CONFIG_KSU=y" >> gki_defconfig
echo "CONFIG_KPM=y" >> gki_defconfig

# ReSukiSU 特有配置
if [ "${KSU_TYPE}" = "ReSukiSU" ]; then
  echo "CONFIG_KSU_MULTI_MANAGER_SUPPORT=y" >> gki_defconfig
  echo 'CONFIG_KSU_FULL_NAME_FORMAT="%TAG_NAME%-%COMMIT_SHA%-Re-TG@qdykernel"' >> gki_defconfig
fi

# 加密和压缩支持
echo "CONFIG_CRYPTO_LZ4=y" >> gki_defconfig
echo "CONFIG_CRYPTO_LZ4HC=y" >> gki_defconfig
echo "CONFIG_CRYPTO_LZ4KD=y" >> gki_defconfig
echo "CONFIG_CRYPTO_ZSTD=y" >> gki_defconfig
echo "CONFIG_F2FS_FS_COMPRESSION=y" >> gki_defconfig
echo "CONFIG_F2FS_FS_LZ4=y" >> gki_defconfig
echo "CONFIG_F2FS_FS_LZ4HC=y" >> gki_defconfig
echo "CONFIG_F2FS_FS_ZSTD=y" >> gki_defconfig

# 内存管理
echo "CONFIG_ZSMALLOC=y" >> gki_defconfig
echo "CONFIG_ZRAM=y" >> gki_defconfig
echo "CONFIG_ZRAM_WRITEBACK=y" >> gki_defconfig
echo "CONFIG_SWAP=y" >> gki_defconfig

# 网络调度器
echo "CONFIG_NET_SCH_FQ_CODEL=y" >> gki_defconfig
echo "CONFIG_NET_SCH_FQ=y" >> gki_defconfig
echo "CONFIG_NET_SCH_SFQ=y" >> gki_defconfig
echo "CONFIG_NET_SCH_HTB=y" >> gki_defconfig
echo "CONFIG_NET_SCH_TBF=y" >> gki_defconfig
echo "CONFIG_NET_SCH_SFB=y" >> gki_defconfig
echo "CONFIG_NET_SCH_RED=y" >> gki_defconfig
echo "CONFIG_NET_SCH_INGRESS=y" >> gki_defconfig
echo "CONFIG_DEFAULT_FQ_CODEL=y" >> gki_defconfig
echo 'CONFIG_DEFAULT_NET_SCH="fq_codel"' >> gki_defconfig

# ECN 支持
echo "CONFIG_IP_ECN=y" >> gki_defconfig
echo "CONFIG_TCP_ECN=y" >> gki_defconfig
echo "CONFIG_IPV6_ECN=y" >> gki_defconfig
echo "CONFIG_IP_NF_TARGET_ECN=y" >> gki_defconfig

# SUSFS 配置
echo "CONFIG_KSU_SUSFS=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_HAS_MAGIC_MOUNT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_SUS_PATH=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_SUS_MOUNT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_AUTO_ADD_SUS_KSU_DEFAULT_MOUNT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_AUTO_ADD_SUS_BIND_MOUNT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_SUS_KSTAT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_TRY_UMOUNT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_AUTO_ADD_TRY_UMOUNT_FOR_BIND_MOUNT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_SPOOF_UNAME=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_ENABLE_LOG=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_HIDE_KSU_SUSFS_SYMBOLS=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_SPOOF_CMDLINE_OR_BOOTCONFIG=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_OPEN_REDIRECT=y" >> gki_defconfig
echo "CONFIG_KSU_SUSFS_SUS_MAP=y" >> gki_defconfig

# TMPFS 支持
echo "CONFIG_TMPFS_XATTR=y" >> gki_defconfig
echo "CONFIG_TMPFS_POSIX_ACL=y" >> gki_defconfig
echo "CONFIG_TMPFS=y" >> gki_defconfig
echo "CONFIG_HEADERS_INSTALL=n" >> gki_defconfig

# 返回主目录
cd $KERNEL_WORKSPACE || error "返回主目录失败"
# 移除check_defconfig
sudo sed -i 's/check_defconfig//' ./common/build.config.gki || error "修改build.config.gki失败"

info "内核Config设置成功"

# 修改内核名称
info "修改内核名称..."
sed -i 's/${scm_version}//' ./common/scripts/setlocalversion || error "修改setlocalversion失败"
sudo sed -i "s/-4k/${KERNEL_SUFFIX}/g" ./common/arch/arm64/configs/gki_defconfig || error "修改gki_defconfig失败"

# 应用完美风驰补丁
cd $KERNEL_WORKSPACE/common
if [ "$ENABLE_SCX" = "true" ]; then
  if [ "$SCHED_FILE" = "none" ]; then
    echo "该机型自带风驰，跳过应用补丁"
  else
    case "${DEVICE_NAME}" in
      oneplus_ace5_ultra|realme_GT7)
        SCHED_BRANCH="mt6991"
        ;;
      *)
        SCHED_BRANCH="sm8750"
        ;;
    esac
    echo "正在拉取风驰补丁"
    git clone https://github.com/Numbersf/SCHED_PATCH.git -b "$SCHED_BRANCH"
    cp ./SCHED_PATCH/fengchi_${{env.SCHED_FILE}}.patch ./
    if [[ -f "fengchi_${{env.SCHED_FILE}}.patch" ]]; then
      echo "开始应用风驰补丁"
      dos2unix "fengchi_${{env.SCHED_FILE}}.patch"
      patch -p1 -F 3 < "fengchi_${{env.SCHED_FILE}}.patch"
      echo "完美风驰补丁应用完成"
    else
      echo "❌ 未匹配到补丁，风驰补丁暂未支持该机型"
      exit 11
    fi
  fi
else
  echo "未启用风驰，则需应用OGKI转换GKI补丁"
  sed -i '1iobj-y += hmbird_patch.o' drivers/Makefile
  curl -L "https://raw.githubusercontent.com/showdo/Build_oneplus_sm8750/main/.github/workflows/Bin/hmbird_patch.patch" -o hmbird_patch.patch
  echo "正在打OGKI转换GKI补丁"
  patch -p1 -F 3 < hmbird_patch.patch
  echo "OGKI转换GKI_patch完成"
fi
cd $KERNEL_WORKSPACE || error "返回主目录失败"
# 构建内核
info "开始构建内核..."
WORKDIR="$(pwd)"
export PATH="/usr/lib/ccache:$PATH"
export PATH="$KERNEL_WORKSPACE/clang18/bin:$PATH"
export PATH="$KERNEL_WORKSPACE/build-tools/bin:$PATH"
CLANG_DIR="$KERNEL_WORKSPACE/clang18/bin"
CLANG_VERSION="$($CLANG_DIR/clang --version | head -n 1)"
LLD_VERSION="$($CLANG_DIR/ld.lld --version | head -n 1)"
pahole_version=$(pahole --version 2>/dev/null | head -n1); [ -z "$pahole_version" ] && echo "pahole版本：未安装" || echo "pahole版本：$pahole_version"
export CCACHE_LOGFILE="$KERNEL_WORKSPACE/ccache.log"
echo "sloppiness = file_stat_matches,include_file_ctime,include_file_mtime,pch_defines,file_macro,time_macros" >> "$CCACHE_DIR/ccache.conf"
cd $KERNEL_WORKSPACE/common
wget https://github.com/cctv18/oppo_oplus_realme_sm8750/raw/refs/heads/main/lib/libfakestat.so
wget https://github.com/cctv18/oppo_oplus_realme_sm8750/raw/refs/heads/main/lib/libfaketimeMT.so
chmod 777 ./*.so
FAKESTAT="2025-05-25 12:00:00"
FAKETIME="@2025-05-25 13:00:00"
SO_DIR=$KERNEL_WORKSPACE/common
export PRELOAD_LIBS="$SO_DIR/libfakestat.so $SO_DIR/libfaketimeMT.so"
echo '#!/bin/bash' > cc-wrapper
echo 'export LD_PRELOAD="'$PRELOAD_LIBS'"' >> cc-wrapper
echo 'export FAKESTAT="'$FAKESTAT'"' >> cc-wrapper
echo 'export FAKETIME="'$FAKETIME'"' >> cc-wrapper
echo 'ccache clang "$@"' >> cc-wrapper
echo '#!/bin/bash' > ld-wrapper
echo 'export LD_PRELOAD="'$PRELOAD_LIBS'"' >> ld-wrapper
echo 'export FAKESTAT="'$FAKESTAT'"' >> ld-wrapper
echo 'export FAKETIME="'$FAKETIME'"' >> ld-wrapper
echo 'ld.lld "$@"' >> ld-wrapper
echo '#!/bin/bash' > test-wrapper.sh
echo 'export LD_PRELOAD="'$PRELOAD_LIBS'"' >> test-wrapper.sh
echo 'export FAKESTAT="'$FAKESTAT'"' >> test-wrapper.sh
echo 'export FAKETIME="'$FAKETIME'"' >> test-wrapper.sh
echo 'echo ">>> Wrapper 内部环境检查完毕."' >> test-wrapper.sh
echo 'exec "$@"' >> test-wrapper.sh
chmod +x test-wrapper.sh
./test-wrapper.sh date
./test-wrapper.sh stat ./Makefile
chmod +x cc-wrapper ld-wrapper
LD_PRELOAD=$PRELOAD_LIBS stat ./Makefile
export KBUILD_BUILD_TIMESTAMP="${KERNEL_TIME}"
sudo rm -rf /usr/share/dotnet &
sudo rm -rf /usr/local/lib/android &
sudo rm -rf /opt/ghc &
sudo rm -rf /opt/hostedtoolcache/CodeQL &
make -j$(nproc --all) LLVM=1 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC="ccache clang" LD="ld.lld" HOSTLD=ld.lld O=out KCFLAGS+=-O2 KCFLAGS+=-Wno-error gki_defconfig &&
make -j$(nproc --all) LLVM=1 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC="$SO_DIR/cc-wrapper" LD="$SO_DIR/ld-wrapper" HOSTLD=ld.lld O=out KCFLAGS+=-O2 KCFLAGS+=-Wno-error Image
LD_PRELOAD=$PRELOAD_LIBS stat ./Makefile
echo "ccache状态："
ccache -s

# 创建AnyKernel3包
info "创建AnyKernel3包..."
cd "$WORKSPACE" || error "返回工作目录失败"
git clone -q https://github.com/showdo/AnyKernel3.git --depth=1 || info "AnyKernel3已存在"
rm -rf ./AnyKernel3/.git
rm -f ./AnyKernel3/push.sh
7z a -t7z -p'501b10728d2cb08abe16eb8b0bdee33c9d2382e1' -mhe=on ./AnyKernel3/TG频道@qdykernel.7z ./AnyKernel3/Image
rm -rf ./AnyKernel3/Image
cp "$KERNEL_WORKSPACE//common/out/arch/arm64/boot/Image" ./AnyKernel3/ || error "复制Image失败"

# 打包
cd AnyKernel3 || error "进入AnyKernel3目录失败"
zip -r "AnyKernel3_${KSU_VERSION}_${DEVICE_NAME}_SukiSU.zip" ./* || error "打包失败"

# 创建C盘输出目录（通过WSL访问Windows的C盘）
WIN_OUTPUT_DIR="/mnt/c/Kernel_Build/${DEVICE_NAME}/"
mkdir -p "$WIN_OUTPUT_DIR" || error "无法创建Windows目录，可能未挂载C盘，将保存到Linux目录:$WORKSPACE/AnyKernel3/AnyKernel3_${KSU_VERSION}_${DEVICE_NAME}_SukiSU.zip"
