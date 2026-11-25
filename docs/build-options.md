# 编译选项中文说明（ImmortalWrt 25.12 / x86-64）

本文把 ImmortalWrt 25.12.2 中和固件定制相关的编译选项逐项翻译说明，配合本仓库的 GitHub Actions 使用。

- 镜像、文件系统、分区、GRUB：来自 [`config/Config-images.in`](https://github.com/immortalwrt/immortalwrt/blob/openwrt-25.12/config/Config-images.in)
- 全局编译/包管理/加固：来自 [`config/Config-build.in`](https://github.com/immortalwrt/immortalwrt/blob/openwrt-25.12/config/Config-build.in)
- 内核：来自 [`config/Config-kernel.in`](https://github.com/immortalwrt/immortalwrt/blob/openwrt-25.12/config/Config-kernel.in)
- 平台特性：来自 [`target/Config.in`](https://github.com/immortalwrt/immortalwrt/blob/openwrt-25.12/target/Config.in)
- 全部 397 个符号（含英文提示、默认值、依赖）见 [`reference/build-options-25.12.2.tsv`](reference/build-options-25.12.2.tsv)

> **重要前提：ImageBuilder 能改什么**
>
> 本仓库用的是官方 **ImageBuilder**（只组装镜像，不重新编译内核和软件包）。
>
> - ✅ 能用：分区大小、镜像类型、GRUB 菜单、rootfs 文件系统参数、`PACKAGES` 包选择、`FILES` 覆盖文件、`DISABLED_SERVICES`。
> - ❌ 不能用：`CONFIG_KERNEL_*`（内核已编译好）、`CONFIG_PACKAGE_*`（用 `PACKAGES` 代替）、`USE_LTO`/`USE_MKLIBS`/`SELINUX` 等需要重编软件包的选项。要改这些必须做完整源码编译（`make menuconfig` + `make`），耗时以小时计。

---

## 一、构建命令与变量

### 1.1 本仓库用到的参数

| 名称 | 含义 | 本仓库取值 |
| --- | --- | --- |
| `IB_VERSION` | ImmortalWrt 版本号（workflow 输入） | `25.12.2` |
| `PROFILE` | 设备 profile，`make info` 可列出 | `generic` |
| `PACKAGES` | 空格分隔的软件包列表 | [`config/packages.txt`](../config/packages.txt) |
| `FILES` | 覆盖文件目录，原样合并进 rootfs | `files/` |
| `CONFIG_TARGET_KERNEL_PARTSIZE` | kernel 分区大小（MiB） | `16` |
| `CONFIG_TARGET_ROOTFS_PARTSIZE` | rootfs 分区大小（MiB） | `20480` |
| `CONFIG_QCOW2_IMAGES` | 是否生成 PVE/KVM 镜像 | `n` |
| `VANTAGE_FEED` | Vantage 主题 apk 源 | `.../luci-theme-vantage/25.12` |

### 1.2 ImageBuilder 通用命令

```sh
make info                    # 列出 profile / 默认包
make image PROFILE=generic PACKAGES="..." FILES=./files
make manifest                # 只生成 .manifest（包清单）
make help                    # 全部可用变量
```

常用变量：

| 变量 | 说明 |
| --- | --- |
| `PROFILE` | 目标设备，x86 软路由一般是 `generic`（另有 `generic-efi` 之类由镜像类型决定，不在此列） |
| `PACKAGES` | 追加/删除软件包，见 1.3 |
| `FILES` | 覆盖目录，里面的 `etc/`、`root/` 等会覆盖到固件；`etc/uci-defaults/` 脚本首次启动执行后自动删除 |
| `DISABLED_SERVICES` | 空格分隔的 init.d 服务名，安装后默认禁用（如 `dnsmasq`） |
| `EXTRA_IMAGE_NAME` | 镜像文件名附加后缀，便于区分自编译版本 |
| `BIN_DIR` | 输出目录，默认 `bin/targets/<target>/<subtarget>` |
| `CONFIG_*` | 以 make 变量形式覆盖 ImageBuilder 的 `.config`，只对镜像组装阶段生效 |

### 1.3 软件包选择语法（`PACKAGES`）

```sh
# 追加
PACKAGES="luci-app-dockerman luci-i18n-dockerman-zh-cn"

# 用 - 前缀移除默认包（默认包里已选中的）
PACKAGES="-dnsmasq dnsmasq-full"

# 混用
PACKAGES="-dnsmasq dnsmasq-full luci-app-samba4 luci-i18n-samba4-zh-cn"
```

规则：

- 空格分隔，不要加引号包裹单个包名。
- `-包名` 表示从默认包集合中删除；如果不加 `-` 直接写，则是追加。
- 依赖会自动解析，无需手写 `lib*`；写 `kmod-*` 时注意 25.12 的 kmod 必须和内核版本匹配（ImageBuilder 内置的仓库就是匹配的）。
- 包不存在时，本仓库 workflow 会自动把它从列表剔除并重试，日志里会列出被剔除的包。

---

## 二、镜像类型与文件系统

### 2.1 镜像类型（`Config-images.in`）

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_GRUB_IMAGES` | `y` | 生成 BIOS/传统启动镜像（`combined.img`），本仓库的 `combined.img.gz` |
| `CONFIG_GRUB_EFI_IMAGES` | `y` | 生成 UEFI 启动镜像（`combined-efi.img`），本仓库的 `combined-efi.img.gz` |
| `CONFIG_ISO_IMAGES` | Buildbot 构建时 `y` | 生成 LiveCD ISO，可用于体验/救援，不适合长期运行 |
| `CONFIG_QCOW2_IMAGES` | Buildbot 构建时 `y` | 生成 PVE/KVM 用的 qcow2 镜像（需要 `qemu-img`），本仓库关闭 |
| `CONFIG_VDI_IMAGES` | Buildbot 构建时 `y` | 生成 VirtualBox VDI 镜像 |
| `CONFIG_VMDK_IMAGES` | Buildbot 构建时 `y` | 生成 VMware VMDK 镜像 |
| `CONFIG_VHDX_IMAGES` | Buildbot 构建时 `y` | 生成 Hyper-V VHDX 镜像 |
| `CONFIG_TARGET_IMAGES_GZIP` | `y` | 镜像额外做 gzip 压缩（`*.img.gz`） |
| `CONFIG_TARGET_SERIAL` | `ttyS0` | 串口控制台设备名（x86/armsr/loongarch64） |

### 2.2 rootfs 文件系统

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_TARGET_ROOTFS_SQUASHFS` | 视平台，x86 为 `y` | 只读 squashfs 根文件系统，配合 overlay 可恢复出厂 |
| `CONFIG_TARGET_SQUASHFS_BLOCK_SIZE` | `256`（KiB） | squashfs 块大小，可选 4/8/16/32/64/128/256/512/1024；越大压缩率越高、随机读放大越明显 |
| `CONFIG_TARGET_SQUASHFS_BLOCK_READERS` | `4` | mksquashfs 大文件并行读取线程数（构建速度） |
| `CONFIG_TARGET_SQUASHFS_SMALL_READERS` | `4` | mksquashfs 小文件并行读取线程数 |
| `CONFIG_TARGET_ROOTFS_EXT4FS` | 视平台 | 生成 ext4 根文件系统（可读写，无回滚） |
| `CONFIG_TARGET_EXT4_RESERVED_PCT` | `0` | ext4 保留块百分比 |
| `CONFIG_TARGET_EXT4_BLOCKSIZE` | `4096` | ext4 块大小，可选 4k/2k/1k |
| `CONFIG_TARGET_EXT4_JOURNAL` | `y` | ext4 是否带日志（掉电更安全，略慢） |
| `CONFIG_TARGET_ROOTFS_EROFS` | 视平台 | 只读 EROFS 根文件系统 |
| `CONFIG_TARGET_EROFS_PCLUSTER_SIZE` | `256`（KiB） | EROFS 物理簇大小 |
| `CONFIG_TARGET_ROOTFS_JFFS2` | 视平台 | JFFS2（NOR flash 设备用，x86 不用） |
| `CONFIG_TARGET_ROOTFS_JFFS2_NAND` | 视平台 | NAND 版 JFFS2 |
| `CONFIG_TARGET_ROOTFS_UBIFS` | 视平台 | UBIFS（NAND 设备用） |
| `CONFIG_TARGET_UBIFS_COMPRESSION_*` | `ZLIB` | UBIFS 压缩算法：none / lzo / zlib |
| `CONFIG_TARGET_UBIFS_FREE_SPACE_FIXUP` | `y` | 首次挂载时修空闲空间（UBIFS 必需） |
| `CONFIG_TARGET_UBIFS_JOURNAL_SIZE` | 空 | UBIFS 日志大小 |
| `CONFIG_TARGET_ROOTFS_CPIOGZ` | 视平台 | 额外生成 `rootfs.cpio.gz` |
| `CONFIG_TARGET_ROOTFS_TARGZ` | 视平台 | 额外生成 `rootfs.tar.gz`（容器/手工部署常用） |
| `CONFIG_TARGET_ROOTFS_PERSIST_VAR` | `n` | 让 `/var` 持久化（默认 `/var` 链接到 `/tmp`，重启丢失） |
| `CONFIG_TARGET_ROOTFS_SECURITY_LABELS` | `n` | 给 rootfs 打 SELinux 安全标签（配合 `SELINUX`） |

### 2.3 initramfs（内存根文件系统）

一般 x86 软路由不需要，除非要做无盘/救援镜像。

| 选项 | 中文说明 |
| --- | --- |
| `CONFIG_TARGET_ROOTFS_INITRAMFS` | 把 rootfs 打进内核（initramfs） |
| `CONFIG_TARGET_INITRAMFS_COMPRESSION_NONE/GZIP/BZIP2/LZMA/LZO/LZ4/XZ/ZSTD` | initramfs 压缩算法 |
| `CONFIG_EXTERNAL_CPIO` | 使用外部 cpio 作为 initramfs 源 |
| `CONFIG_TARGET_INITRAMFS_FORCE` | 忽略 bootloader 传入的 initramfs |
| `CONFIG_TARGET_ROOTFS_INITRAMFS_SEPARATE` | 生成独立的 `initrd.cpio` 而不是内嵌 |

### 2.4 分区与 GRUB

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_TARGET_KERNEL_PARTSIZE` | `32`（MiB） | kernel + GRUB 所在分区大小。**本仓库设为 16**，与现网设备一致 |
| `CONFIG_TARGET_ROOTFS_PARTSIZE` | `300`（Buildbot）/`160` | rootfs 分区大小（MiB）。**本仓库设为 20480（20 GiB）** |
| `CONFIG_TARGET_ROOTFS_PARTNAME` | 空 → `PARTUUID=...-02` | 内核根分区定位方式，留空即按 PARTUUID 自动找 |
| `CONFIG_GRUB_TIMEOUT` | `"0"` | GRUB 菜单等待秒数，0 表示不停留 |
| `CONFIG_GRUB_TITLE` | `"ImmortalWrt"` | GRUB 菜单显示名称 |
| `CONFIG_GRUB_BOOTOPTS` | 空 | 额外内核启动参数（如 `console=ttyS0,115200`） |
| `CONFIG_GRUB_CONSOLE` | `y` | 除串口外同时启用本地控制台 |
| `CONFIG_GRUB_BAUDRATE` | `38400`（x86_generic）/`115200` | 串口波特率 |
| `CONFIG_GRUB_FLOWCONTROL` | `n` | 串口硬件流控 RTS/CTS |

**改分区大小的后果**：x86 的 sysupgrade 会按镜像里的分区表整盘写入，rootfs 分区变小会直接截掉现有 overlay（数据丢失）。跨大小刷机请务必 `-n` 不保留配置，并确认目标磁盘容量足够。

---

## 三、全局编译选项

### 3.1 构建行为

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_EXPERIMENTAL` | `n` | 启用实验性功能，可能不稳定，生产环境不要开 |
| `CONFIG_TESTING_KERNEL` | 跟随 `EXPERIMENTAL` | 使用平台提供的新版测试内核 |
| `CONFIG_BUILDBOT` | `n` | 自动构建模式：删构建目录、开 per-device rootfs、默认产物更全（官方 release 用它） |
| `CONFIG_JSON_OVERVIEW_IMAGE_INFO` | `y` | 生成 `profiles.json`（镜像/设备信息，机器可读） |
| `CONFIG_JSON_CYCLONEDX_SBOM` | Buildbot 时 `y` | 生成 CycloneDX 格式 SBOM（软件物料清单） |
| `CONFIG_INCLUDE_CONFIG` | `n` | 把构建配置写进固件 `/etc/build.*`，方便排障（需 `DEVEL`） |
| `CONFIG_COLLECT_KERNEL_DEBUG` | Buildbot 时 `y` | 收集内核调试符号，便于离线分析 panic |
| `CONFIG_REPRODUCIBLE_DEBUG_INFO` | Buildbot 时 `y` | 去掉调试信息里的本机路径，构建可复现 |

### 3.2 软件包选择

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_ALL` | `n` | 选中所有用户态软件包（镜像巨大，仅调试用） |
| `CONFIG_ALL_KMODS` | `n` | 选中所有内核模块 |
| `CONFIG_ALL_NONSHARED` | `n` | 选中所有目标平台专属包（会连带 `ALL_KMODS`） |

> 本仓库不使用这三个选项，而是在 `config/packages.txt` 里精确列出需要的包。

### 3.3 包管理与签名

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_USE_APK` | `y` | 使用 apk 包管理器（25.12 默认；关闭则回到 opkg） |
| `CONFIG_SIGNED_PACKAGES` | `y` | 生成签名后的包索引 |
| `CONFIG_SIGNATURE_CHECK` | 跟随上一项 | 安装包时校验签名；关闭后 ImageBuilder 加 `--allow-untrusted` |
| `CONFIG_DOWNLOAD_CHECK_CERTIFICATE` | `y` | 下载源码/包时校验 TLS 证书 |
| `CONFIG_CLEAN_IPKG` | 无提示（仅 opkg） | 从镜像里删除 opkg 状态文件 |
| `CONFIG_IPK_FILES_CHECKSUMS` | 无提示（仅 opkg） | 在包元数据里记录文件校验和 |

### 3.4 功能与安全开关

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_DISPLAY_SUPPORT` | `n` | 在 menuconfig 里显示需要图形支持的包 |
| `CONFIG_BUILD_PATENTED` | `n` | 允许编译专利功能（如部分编解码器） |
| `CONFIG_BUILD_NLS` | `n` | 完整语言/国际化支持（体积大） |
| `CONFIG_SHADOW_PASSWORDS` | `y` | 使用 shadow 密码文件（无提示项） |
| `CONFIG_IPV6` | `y` | 启用 IPv6 支持（无提示项） |
| `CONFIG_USE_SECCOMP` | `y` | 启用 seccomp，并选用 `procd-seccomp` |
| `CONFIG_SELINUX` | `n` | 启用 SELinux（额外约 0.5 MiB） |
| `CONFIG_SELINUXTYPE_targeted` | 二选一 | 使用 refpolicy 参考策略 |
| `CONFIG_SELINUXTYPE_dssp` | 默认 | 使用 dssp 策略（Defensec OpenWrt 版） |

### 3.5 优化与调试

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_DEBUG` | `n` | 包带 `-g3` 调试信息（体积暴涨） |
| `CONFIG_USE_GC_SECTIONS` | `n` | 函数/数据分段 + 链接期垃圾回收（实验性） |
| `CONFIG_USE_LTO` | `n` | 全局链接时优化（实验性，编译慢、部分包需 opt-out） |
| `CONFIG_USE_MOLD` | `n` | 使用 mold 链接器（需宿主支持） |
| `CONFIG_NO_STRIP` | 三选一 | 不裁剪二进制 |
| `CONFIG_USE_STRIP` | glibc 时默认 | 用 binutils `strip` 裁剪 |
| `CONFIG_USE_SSTRIP` | musl 时默认 | 用 `sstrip` 进一步裁剪 |
| `CONFIG_STRIP_ARGS` | `--strip-all` | strip 参数 |
| `CONFIG_SSTRIP_DISCARD_TRAILING_ZEROES` | `y` | sstrip 丢弃尾部零字节 |
| `CONFIG_STRIP_KERNEL_EXPORTS` | `n` | 裁剪内核未使用的导出符号（可能影响外部模块） |
| `CONFIG_USE_MKLIBS` | `n` | 只保留被选中包用到的库函数（会破坏未选包） |
| `CONFIG_PKG_FANALYZER` | `n` | GCC `-fanalyzer` 静态分析 |

### 3.6 加固选项

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_PKG_CHECK_FORMAT_SECURITY` | `y` | 编译加 `-Wformat -Werror=format-security` |
| `CONFIG_PKG_ASLR_PIE_NONE/REGULAR/ALL` | `REGULAR` | 用户态 PIE/ASLR 强度 |
| `CONFIG_PKG_CC_STACKPROTECTOR_NONE/REGULAR/STRONG/ALL` | `REGULAR` | 用户态栈保护 |
| `CONFIG_KERNEL_CC_STACKPROTECTOR_NONE/REGULAR/STRONG` | `REGULAR` | 内核栈保护 |
| `CONFIG_PKG_FORTIFY_SOURCE_NONE/1/2/3` | `1` | `_FORTIFY_SOURCE` 缓冲区溢出检查强度 |
| `CONFIG_PKG_RELRO_NONE/PARTIAL/FULL` | `FULL` | RELRO 保护 |
| `CONFIG_PKG_DT_RELR` | `y` | 使用 RELR 相对重定位，减小体积 |

### 3.7 开发者选项（`Config-devel.in`）

| 选项 | 中文说明 |
| --- | --- |
| `CONFIG_DEVEL` | 打开“高级配置选项”菜单 |
| `CONFIG_BROKEN` | 显示标记为 broken 的平台/包/设备 |
| `CONFIG_BINARY_FOLDER` | 自定义镜像输出目录（默认 `./bin/<board>`） |
| `CONFIG_DOWNLOAD_TOOL_CUSTOM` | 自定义下载工具（aria2c/curl/wget 或任意命令） |
| `CONFIG_DOWNLOAD_FOLDER` | 源码下载缓存目录（默认 `./dl`） |
| `CONFIG_LOCALMIRROR` | 源码包本地镜像地址 |
| `CONFIG_AUTOREBUILD` | 源文件变化时自动重编（默认 `y`） |
| `CONFIG_AUTOREMOVE` | 目标完成后删除 build_dir（省空间） |
| `CONFIG_BUILD_ALL_HOST_TOOLS` | 编译全部宿主工具（做通用工具链包时用） |
| `CONFIG_OPTIMIZE_HOST_TOOLS` | 宿主工具编译优化菜单 |
| `CONFIG_HOST_FLAGS_OPT` | 宿主工具优化参数，默认 `-O2` |
| `CONFIG_HOST_TOOLS_STRIP` | 裁剪宿主工具 |
| `CONFIG_HOST_FLAGS_STRIP` | 宿主工具裁剪参数，默认 `-Wl,-s` |
| `CONFIG_HOST_EXTRA_CFLAGS/CXXFLAGS/CPPFLAGS/LDFLAGS` | 宿主工具额外编译/链接参数 |
| `CONFIG_BUILD_SUFFIX` | 给 build_dir 加后缀，方便多套配置并存 |
| `CONFIG_TARGET_ROOTFS_DIR` | 自定义目标 rootfs 目录 |
| `CONFIG_CCACHE` / `CONFIG_CCACHE_DIR` | 启用 ccache 及其目录 |
| `CONFIG_KERNEL_CFLAGS` | 内核额外 CFLAGS |
| `CONFIG_EXTERNAL_KERNEL_TREE` | 使用外部内核源码树 |
| `CONFIG_KERNEL_GIT_CLONE_URI` / `_LOCAL_REPOSITORY` / `_REF` / `_MIRROR_HASH` | 从 git 克隆内核及参考仓库/分支/校验 |
| `CONFIG_BUILD_LOG` / `CONFIG_BUILD_LOG_DIR` | 保存构建日志及目录 |
| `CONFIG_SRC_TREE_OVERRIDE` | 允许用本地 git 树覆盖包源码 |
| `CONFIG_EXTRA_OPTIMIZATION` | 额外优化参数（默认 `-fno-caller-saves -fno-plt`） |

---

## 四、内核选项（摘要）

`Config-kernel.in` 共 216 项，完整清单见 [`reference/build-options-25.12.2.tsv`](reference/build-options-25.12.2.tsv)。**ImageBuilder 无法修改这些**，只有完整源码编译（`make menuconfig` + `make`）才生效。

> 注意：网卡驱动、nftables、WireGuard、overlayfs、TUN 等“看起来像内核选项”的东西，在 25.12 里是以 `kmod-*` 包的形式提供的，请通过 `PACKAGES` 选择，不要在这里找。

### 4.1 日志与基础功能

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_KERNEL_PRINTK` | `y` | 内核日志输出，关掉省空间但无法排障 |
| `CONFIG_KERNEL_PRINTK_TIME` | `y` | 日志带时间戳 |
| `CONFIG_KERNEL_SWAP` | `y`（非小闪存） | 支持 swap 交换分区 |
| `CONFIG_KERNEL_DEBUG_FS` | `y` | debugfs 文件系统（调试工具、部分驱动依赖） |
| `CONFIG_KERNEL_MAGIC_SYSRQ` | `y` | SysRq 组合键救援（卡死时能安全重启/卸载） |
| `CONFIG_KERNEL_KALLSYMS` | `y`（非小闪存） | 保留内核符号表，便于看 oops 栈 |
| `CONFIG_KERNEL_ELF_CORE` | `y`（非小闪存） | 允许进程 core dump |
| `CONFIG_KERNEL_PROC_STRIPPED` | 仅小闪存 | 裁剪非必要 `/proc` 节点以省空间 |
| `CONFIG_KERNEL_X86_VSYSCALL_EMULATION` | 空 | 兼容依赖旧 vsyscall 的老二进制 |

### 4.2 调试 / 追踪 / eBPF

| 选项 | 中文说明 |
| --- | --- |
| `CONFIG_KERNEL_PERF_EVENTS` / `KERNEL_PROFILING` | 性能事件与性能剖析 |
| `CONFIG_KERNEL_FTRACE` | ftrace 函数跟踪框架 |
| `CONFIG_KERNEL_FTRACE_SYSCALLS` | 跟踪系统调用 |
| `CONFIG_KERNEL_FUNCTION_TRACER` / `FUNCTION_GRAPH_TRACER` | 函数调用/调用图跟踪 |
| `CONFIG_KERNEL_DYNAMIC_FTRACE` | 运行时开关函数跟踪 |
| `CONFIG_KERNEL_FUNCTION_PROFILER` | 函数级耗时统计 |
| `CONFIG_KERNEL_IRQSOFF_TRACER` / `PREEMPT_TRACER` | 中断/抢占延迟测量 |
| `CONFIG_KERNEL_HIST_TRIGGERS` | 跟踪事件直方图触发器 |
| `CONFIG_KERNEL_KPROBES` / `KPROBE_EVENTS` | 内核探针与探针事件 |
| `CONFIG_KERNEL_BPF_EVENTS` / `KERNEL_BPF_STREAM_PARSER` | eBPF 事件与 TCP 流解析 |
| `CONFIG_KERNEL_DEBUG_INFO_BTF` | 生成 BTF 类型信息（bpftrace、Cilium、XDP 工具需要） |
| `CONFIG_KERNEL_NETKIT` | BPF 可编程网络设备（Netkit） |
| `CONFIG_KERNEL_XDP_SOCKETS` | XDP socket（高性能收发） |
| `CONFIG_KERNEL_UBSAN` / `KASAN` / `KCOV` | 未定义行为检查 / 内存越界检查 / 模糊测试覆盖率，仅开发用，开销极大 |
| `CONFIG_KERNEL_DEBUG_KERNEL` | 打开内核调试总开关（连带一堆自检项） |

### 4.3 容器与隔离（Docker / LXC 相关）

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_KERNEL_CGROUPS` | `y`（非小闪存） | cgroups 资源分组，容器必需 |
| `CONFIG_KERNEL_MEMCG` / `MEMCG_KMEM` | `y` | 内存/内核内存限额 |
| `CONFIG_KERNEL_CGROUP_SCHED` / `CFS_BANDWIDTH` | `y` | CPU 配额与带宽限制 |
| `CONFIG_KERNEL_BLK_CGROUP` / `BLK_DEV_THROTTLING` | `y` | 块设备 IO 限额 |
| `CONFIG_KERNEL_CGROUP_PIDS` | `y` | 进程数限制（防 fork 炸弹） |
| `CONFIG_KERNEL_CGROUP_BPF` / `CGROUP_DEVICE` | `y` / 空 | 在 cgroup 上挂 eBPF / 设备白名单 |
| `CONFIG_KERNEL_NAMESPACES` | `y`（非小闪存） | 命名空间总开关 |
| `CONFIG_KERNEL_{UTS,IPC,USER,PID,NET}_NS` | `y` | 各类命名空间隔离 |
| `CONFIG_KERNEL_SECCOMP` / `SECCOMP_FILTER` | `y`（非小闪存） | 系统调用过滤（容器安全） |
| `CONFIG_KERNEL_POSIX_MQUEUE` | `y`（非小闪存） | POSIX 消息队列 |

### 4.4 网络

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_KERNEL_IP_MROUTE` | `y` | IPv4 组播路由（IPTV/udpxy 需要） |
| `CONFIG_KERNEL_IPV6_MROUTE` | `y` | IPv6 组播路由 |
| `CONFIG_KERNEL_IPV6_SEG6_LWTUNNEL` | `y`（非小闪存） | IPv6 Segment Routing 轻量隧道 |
| `CONFIG_KERNEL_MPTCP` / `MPTCP_IPV6` | `y`（非小闪存） | 多路径 TCP |
| `CONFIG_KERNEL_NF_CONNTRACK_TIMEOUT` | `y`（非小闪存） | 每条连接可单独设置超时 |
| `CONFIG_KERNEL_NET_L3_MASTER_DEV` | `y`（非小闪存） | L3 master 设备（VRF 等） |
| `CONFIG_KERNEL_IP_PNP` + `_DHCP/_BOOTP/_RARP` | 空 | 从网络挂载根文件系统（无盘启动） |
| `CONFIG_KERNEL_DCB` | 仅 armsr | 数据中心桥接 |

### 4.5 文件系统

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_KERNEL_BTRFS_FS` | 空 | 内建 Btrfs 支持（快照/压缩，内存占用较高） |
| `CONFIG_KERNEL_EROFS_FS` + `_ZIP` / `_ZIP_LZMA` | 空 | EROFS 只读压缩文件系统 |
| `CONFIG_KERNEL_FS_POSIX_ACL` | `y`（非小闪存） | 通用 POSIX ACL |
| `CONFIG_KERNEL_{EXT4,F2FS,BTRFS,EROFS,JFFS2,TMPFS}_FS_POSIX_ACL` | 跟随上一项 | 各文件系统的 ACL 支持 |
| `CONFIG_KERNEL_NFS_FS` / `NFS_V2` / `NFS_V3` / `ROOT_NFS` | 空 | NFS 客户端与网络根 |
| `CONFIG_KERNEL_CIFS_ACL` / `NFS_ACL_SUPPORT` | 跟随 ACL | CIFS/NFS 的 ACL 支持 |
| `CONFIG_KERNEL_SQUASHFS_XATTR` | 视配置 | squashfs 扩展属性（SELinux/ACL 用） |
| `CONFIG_KERNEL_SQUASHFS_FRAGMENT_CACHE_SIZE` | `2`（小闪存） | squashfs 片段缓存数量 |
| `CONFIG_KERNEL_AIO` / `IO_URING` | `y`（非小闪存 / x86_64+aarch64） | 异步 IO，数据库与高并发下载依赖 |
| `CONFIG_KERNEL_FANOTIFY` / `FHANDLE` | `y`（非小闪存） | 文件变更通知 / 文件句柄系统调用（Samba、备份工具用） |
| `CONFIG_KERNEL_TRANSPARENT_HUGEPAGE_*` | `ALWAYS` | 透明大页策略：always / madvise / never |

### 4.6 安全与加固

| 选项 | 默认 | 中文说明 |
| --- | --- | --- |
| `CONFIG_KERNEL_SECURITY` | 空 | 安全模型框架总开关 |
| `CONFIG_KERNEL_SECURITY_SELINUX` | 空 | SELinux 支持（配套 `CONFIG_SELINUX`） |
| `CONFIG_KERNEL_LSM` | `lockdown,yama,...` | 启用哪些 LSM 模块及顺序 |
| `CONFIG_KERNEL_KEYS` / `PERSISTENT_KEYRINGS` / `BIG_KEYS` | 非小闪存 | 内核密钥环（加密盘、Kerberos） |
| `CONFIG_KERNEL_AUDIT` | 空 | 审计子系统 |
| `CONFIG_KERNEL_WERROR` | 空 | 编译警告当错误（开发用） |
| `CONFIG_KERNEL_DEVMEM` | 空 | `/dev/mem` 直接物理内存访问（有风险，一般关） |
| `CONFIG_KERNEL_DEVTMPFS` / `DEVTMPFS_MOUNT` | 空 | devtmpfs 及自动挂载（嵌入式常开） |

### 4.7 性能与体积

| 选项 | 中文说明 |
| --- | --- |
| `CONFIG_KERNEL_CC_OPTIMIZE_FOR_PERFORMANCE` | 按性能优化（与下一项二选一） |
| `CONFIG_KERNEL_CC_OPTIMIZE_FOR_SIZE` | 按体积优化，小闪存设备默认 |
| `CONFIG_KERNEL_DEBUG_INFO` / `DEBUG_INFO_REDUCED` | 生成/精简调试信息 |
| `CONFIG_KERNEL_KEXEC` / `CRASH_DUMP` / `PROC_VMCORE` | kexec 快速重启与崩溃转储 |
| `CONFIG_KERNEL_TASKSTATS` / `PSI` | 进程资源统计 / 压力失速信息（监控工具用） |
| `CONFIG_USE_RFKILL` | 无线射频开关支持 |

---

## 五、软件包与软件源

### 5.1 官方软件源

25.12.2 x86/64 的 apk 源（`feeds.buildinfo` 里的固定提交）：

| feed | 内容 |
| --- | --- |
| `targets/x86/64/packages` | 目标平台专属包（网卡固件、平台工具） |
| `targets/x86/64/kmods/<内核版本>` | 与内核严格匹配的 kmod |
| `packages/x86_64/base` | 基础系统包（busybox、libc、dropbear、防火墙…） |
| `packages/x86_64/packages` | 通用软件包（下载、NAS、容器、工具…） |
| `packages/x86_64/luci` | LuCI 界面、应用、主题、语言包 |
| `packages/x86_64/routing` | 路由协议（babeld、batman、olsr…） |
| `packages/x86_64/telephony` | 电话/VoIP（asterisk、kamailio…） |

完整包名清单（11 618 条，含版本与来源 feed）见 [`reference/packages-25.12.2-x86_64.tsv`](reference/packages-25.12.2-x86_64.tsv)。

### 5.2 查包

```sh
# 在仓库里查（Windows PowerShell 也可用）
Select-String -Path docs\reference\packages-25.12.2-x86_64.tsv -Pattern 'docker'

# 在路由器上查（apk 体系）
apk search docker
apk info -a luci-app-dockerman

# ImageBuilder 里看默认包
make info
```

### 5.3 命名约定

| 前缀/后缀 | 含义 |
| --- | --- |
| `luci-app-*` | LuCI 里的应用页面（一般同时需要对应的后台包） |
| `luci-i18n-*-zh-cn` | 对应应用的简体中文语言包 |
| `luci-theme-*` | 主题，配合 `luci-app-*-config` 做设置 |
| `kmod-*` | 内核模块，必须与内核版本匹配 |
| `lib*` | 运行库，通常由依赖自动带入，不必手写 |
| `-openssl` / `-mbedtls` / `-nossl` | 同一软件的不同 TLS 实现变体，只能选一个 |

### 5.4 安装第三方 apk / 自定义源

ImageBuilder 支持两种方式：

```sh
# 方式 1：把 apk 文件放进 ImageBuilder 的 packages/ 目录
cp luci-theme-vantage-*.apk "$IB/packages/"

# 方式 2：加一个带签名的 feed（本仓库给 Vantage 就是这么做的）
echo 'https://anothadev.github.io/luci-theme-vantage/25.12/packages.adb' \
  > files/etc/apk/repositories.d/99-vantage.list
# 同时把对应公钥放进 files/etc/apk/keys/ 和 $IB/keys/
```

没有签名密钥时，需要 `CONFIG_SIGNATURE_CHECK=n`（ImageBuilder 会加 `--allow-untrusted`）；生产环境不建议关闭校验。

---

## 六、常用定制配方

### 6.1 只换主题

编辑 `config/packages.txt`：

```text
luci-theme-vantage
luci-app-vantage
luci-i18n-vantage-theme-zh-cn
luci-i18n-vantage-zh-cn
```

并在 `config/packages.txt` 里用 `-` 去掉不想要的主题（如 `-luci-theme-material`）。

### 6.2 加 Docker

```text
docker
dockerd
containerd
runc
tini
docker-compose
luci-app-dockerman
luci-i18n-dockerman-zh-cn
kmod-br-netfilter
kmod-veth
kmod-macvlan
```

> rootfs 分区至少 2 GiB 才有实用价值，本仓库默认 20 GiB。Docker 数据建议放独立磁盘或 overlay。

### 6.3 加代理/分流

25.12 官方源里可用：

```text
luci-app-homeproxy          # sing-box 内核，界面友好
luci-app-passwall           # 功能全，需自行配置节点
luci-app-openclash          # Clash 内核
luci-app-dae / luci-app-daed
luci-app-v2raya
luci-app-smartdns           # 配合 DNS 分流
```

注意：这些包体积大，且部分会修改防火墙/DNS 默认行为，建议单独做一版镜像验证。

### 6.4 改分区大小

workflow 里改这两个值（同时改 `.config` 与 `make` 参数）：

```yaml
CONFIG_TARGET_KERNEL_PARTSIZE=16
CONFIG_TARGET_ROOTFS_PARTSIZE=20480
```

改大：需要确认目标磁盘剩余空间足够；改小：sysupgrade 会截断现有 overlay，先备份。

### 6.5 预置配置 / 首次启动脚本

- 静态文件放 `files/`，例如 `files/etc/config/network` 会覆盖默认网络配置。
- 首次启动执行的脚本放 `files/etc/uci-defaults/`，执行成功后被自动删除；适合改主题、设主机名、开服务。
- 需要每次启动都执行的脚本放 `files/etc/init.d/` 并 `chmod +x`。

### 6.6 裁剪体积

- 去掉用不到的主题、语言包、kmod（网卡驱动只留实际使用的）。
- 用 `-luci-app-*` 去掉默认应用。
- 不建议用 `CONFIG_USE_MKLIBS`/`CONFIG_ALL_KMODS` 这类会破坏依赖的选项。

### 6.7 换 ImmortalWrt 版本

workflow 的 `IB_VERSION` 支持任意 `25.12.x`；主题源目录固定为 `25.12`（`${IB_VERSION%.*}`）。升级到 25.12.3 只需改默认值或手动触发时填版本号。