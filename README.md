# ImmortalWrt x86/64 + Vantage + BBRv3 自动构建

用 **GitHub Actions 从 ImmortalWrt 源码全量编译** 固件，全部在云端完成，本地不需要任何环境。内核额外打入 **BBRv3** 补丁（主线内核只有 BBRv1）。

| 版本 | 构建方式 | 拥塞控制 | 触发方式 |
| --- | --- | --- | --- |
| **正式固件** | 源码全量编译（[`build.yml`](.github/workflows/build.yml)） | **BBRv3** | push `main` / tag / 手动 |
| 备用快速验证 | ImageBuilder 组装（[`build-imagebuilder.yml`](.github/workflows/build-imagebuilder.yml)） | BBRv1 | **仅手动** |

- 目标平台：`x86/64`，profile `generic`（适配 CncTion J4125-4L 等 x86 软路由）
- 基础版本：ImmortalWrt **25.12.x**（默认 25.12.2，apk 包管理；源码用同名 git tag）
- 内核：Linux **6.12.103** + BBRv3 补丁（[OpenWrt PR #16414](https://github.com/openwrt/openwrt/pull/16414)，19 个补丁，见 [`patches/kernel/bbr3/`](patches/kernel/bbr3/)）
- 拥塞控制：默认 `bbr` + `fq`，由 `files/etc/sysctl.d/99-bbr.conf` 生效，`kmod-tcp-bbr` / `kmod-sched` 随固件安装
- 主题：[Vantage](https://github.com/anothaDev/luci-theme-vantage) 1.2.x（feed 方式编译）+ 中文语言包，已设为默认主题
- 包清单：来自现网路由 `/etc/apk/world`（421 个包 + 移除 `dnsmasq`），见 [`config/packages.txt`](config/packages.txt)
- 分区表：与现网设备 `/dev/sda` 完全一致（16 MiB kernel + 20 GiB rootfs），见[下方说明](#分区布局)
- 产物：
  - `*combined-efi.img.gz` —— UEFI 启动，**推荐**
  - `*combined.img.gz` —— Legacy BIOS 启动
  - `*rootfs.img.gz` —— 仅 rootfs（供手工组装）
  - `*.manifest` —— 固件内全部包与版本清单
  - `SHA256SUMS.images` —— 校验值

## 定制化文档

| 文档 | 内容 |
| --- | --- |
| [`docs/build-options.md`](docs/build-options.md) | 编译选项中文说明：镜像类型、文件系统、分区、GRUB、全局开关、内核选项、软件源、常用配方 |
| [`docs/packages.md`](docs/packages.md) | 当前在装包逐条中文说明（按类别分组） |
| [`docs/packages-optional.md`](docs/packages-optional.md) | 常用可选包：代理、DNS 过滤、下载、NAS、容器、组网、监控、命令行工具 |
| [`docs/reference/`](docs/reference/) | 官方原始数据：11 618 个包名/版本、Kconfig 选项、官方 `.config`/feeds/profile |

文档总入口：[`docs/README.md`](docs/README.md)。

## 触发构建

| 方式 | 说明 |
| --- | --- |
| Push 到 `main`（非 `*.md` / `docs/**`） | 自动构建并更新 `latest` Release |
| Actions → 源码构建 → Run workflow | 手动构建，可填其他 25.12.x 版本 |
| 推送 `v*` tag | 额外生成带版本的 Release |

构建完成后在 **Releases → Latest build** 直接下载，或在对应 Actions 运行的 **Artifacts** 里下载。

> 源码全量构建首次约 **2~2.5 小时**（实测 148~151 分钟）；workflow 会缓存 `.ccache` 和 `dl/`，后续构建通常 **1.5~2 小时**（实测 100~133 分钟）。单 job 上限 6 小时，workflow 设为 350 分钟。

## 刷机

1. 下载 `*-combined-efi.img.gz`（UEFI）或 `*-combined.img.gz`（Legacy BIOS）。
2. LuCI → 系统 → 备份/刷机 → 刷写新固件，上传该文件。
3. 或 SSH：

```sh
sysupgrade -n /tmp/immortalwrt-25.12.2-x86-64-generic-squashfs-combined-efi.img.gz
```

> 当前路由器是 ImmortalWrt SNAPSHOT（main 分支），本仓库基于 25.12 稳定分支，属于跨分支刷机，**建议不保留配置**（`-n`）。
>
> 镜像的 rootfs 分区是 20 GiB，sysupgrade 会按分区表整盘写入，写入量约 20 GiB（SSD 上通常 1~3 分钟），期间不要断电。

## BBRv3

主线 Linux 只带 **BBRv1**（`net/ipv4/tcp_bbr.c`），BBRv3 需要打补丁。本仓库的做法：

- 补丁源：[OpenWrt PR #16414](https://github.com/openwrt/openwrt/pull/16414) 的 19 个 `601-*.patch`（针对 6.12），落在 `target/linux/generic/hack-6.12/`，本仓库重命名为 `900-01..900-19`。
- 版本固定：抓取自 PR head 提交 `94d8192c17b99ff5bc3975c00e2ed7079f6e5b89`，见 [`patches/kernel/bbr3/README.md`](patches/kernel/bbr3/README.md)。
- 应用顺序由 `include/quilt.mk` 决定：backport → pending → **hack** → platform，`scripts/patch-kernel.sh` 用 `patch -f -p1`（默认 fuzz=2）。
- 补丁只改内核，不产生额外软件包；`CONFIG_PACKAGE_kmod-tcp-bbr` 与 `kmod-sched` 提供模块与 `fq` 队列。
- 构建时会**自动校验**：内核源码 `net/ipv4/tcp_bbr.c` 里必须出现 `BBR_VERSION 3`，否则构建失败，避免“以为刷了 BBRv3 实际还是 BBRv1”。
- 想单独验证补丁能否干净应用，可手动运行 [`bbr3-validate.yml`](.github/workflows/bbr3-validate.yml)（只打补丁不编译，几分钟出结果）。

> 为什么不用 ImageBuilder：ImageBuilder 只组装官方**预编译内核**，无法改内核源码，因此拿不到 BBRv3（只有 BBRv1）。备用流程 `build-imagebuilder.yml` 仍保留，适合改包清单后二十分钟快速验证。

## 分区布局

现网设备（192.168.31.1，32 GB SSD）的实际分区：

```text
Device     Boot Start      End  Sectors Size Type
/dev/sda1  *      512    33279    32768  16M 83 Linux   # /boot（kernel + grub）
/dev/sda2       33792 41976831 41943040  20G 83 Linux   # squashfs rootfs + f2fs overlay
```

构建时通过以下开关固定为同一布局：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `CONFIG_TARGET_KERNEL_PARTSIZE` | `16` | MiB，对应 sda1 |
| `CONFIG_TARGET_ROOTFS_PARTSIZE` | `20480` | MiB（20 GiB），对应 sda2 |
| `CONFIG_ISO_IMAGES` / `CONFIG_QCOW2_IMAGES` / `CONFIG_VDI/VMDK/VHDX_IMAGES` | `n` | 不需要虚拟机/光盘镜像，省时间和磁盘 |

由于 20 GiB 的镜像在 CI 上不可能真实写满，workflow 会把 `scripts/gen_image_generic.sh` 和 `Image/pad-to` 的“写零填充”改成 `truncate` 稀疏扩展：文件逻辑大小仍是 20 GiB，磁盘占用只有实际内容（几百 MB），gzip 后的产物约 **210 MB**。构建结束前会解析 MBR，校验两个分区确实是 16 MiB / 20480 MiB。

## 自定义

- 增删软件包：编辑 [`config/packages.txt`](config/packages.txt)，一行一个；`-包名` 表示从默认包里移除（如 `-dnsmasq` 换成 `dnsmasq-full`）。
  - 软件包统一写成 `=y`。内核模块在内核里依旧是独立 `.ko`：OpenWrt 的包 Kconfig 里 `=m` 只会「编出来但不装进 rootfs」（`package/Makefile` 的安装清单只取 `CONFIG_PACKAGE_x=y`），而内核符号本身由构建系统统一按 `=m` 生成，所以 `=y` 也不会把驱动编进内核、不影响 16 MiB 内核分区。
  - `.config` 由 [`ci/gen-config.py`](ci/gen-config.py) 根据 `packages.txt` + 官方默认包自动生成，**不必手写 Kconfig**。
  - 若某个包名不存在或依赖不满足，[`ci/verify-config.py`](ci/verify-config.py) 会在编译前直接报错（虚拟名如 `nftables` 由 `nftables-json` 提供会自动识别）。
- 覆盖文件：放进 [`files/`](files/)，会原样合并进固件（如 `files/etc/uci-defaults/`）。
- 换主题版本：修改 workflow 中 `VANTAGE_REF`（默认 `v1.2.0`）。
- 换 BBRv3 补丁：替换 [`patches/kernel/bbr3/900-*.patch`](patches/kernel/bbr3/)，用 `bbr3-validate.yml` 先验证。

## 说明

- 内核模块编译失败时会自动禁用该包并重试（最多 6 轮），日志里会列出失败的包和错误摘要。
- 首次启动由 `files/etc/uci-defaults/zzzz-vantage-theme` 强制选中 Vantage 主题。
- 需在 GitHub Actions 的 **Releases → Latest build** 下载正式产物；ImageBuilder 备用产物在 **Releases → imagebuilder**。

## 构建时做的自动修补

源码构建在 20 GiB 分区 + 400 多个包的实际场景下会遇到几个坑，workflow / `ci/` 脚本已自动处理：

1. **rootfs 分区写零会打满 runner**：`scripts/gen_image_generic.sh` 用 `dd if=/dev/zero` 填满整个分区，`include/image.mk` 的 `pad-to` 同样。两处改为 `truncate` 稀疏扩展，逻辑大小不变、真实占用很小（[`ci/patch-sparse.py`](ci/patch-sparse.py)）。
2. **gzip -9 压缩 20 GiB 太慢**：镜像内容是已压缩的 xz squashfs，改为 `gzip -1`，产物大小基本不变。
3. **默认开着 qcow2 / VDI / VMDK / VHDX / ISO 镜像和 ext4 变体**：每种格式都会把 20 GiB 分区再完整复制一遍，对刷机毫无用处。现在统一关掉，只保留 squashfs 的 `combined.img.gz`（BIOS）、`combined-efi.img.gz`（UEFI）和 `rootfs.img.gz`。
4. **部分软件包在 25.12 里会编译失败**：编译失败时脚本自动定位 `ERROR: package/... failed to build`，在 `.config` 里禁用该包并重试。
5. **ccache 缓存“恢复了却不生效”**：OpenWrt 只导出 `CCACHE_DIR`/`CCACHE_BASEDIR`/`CCACHE_NOCOMPRESS`，没有设 `CCACHE_COMPILERCHECK`，于是 ccache 默认按编译器的 **mtime** 判断缓存是否有效。CI 每次都重新编译工具链，mtime 每次都变，缓存条目全部作废。workflow 里显式设 `CCACHE_COMPILERCHECK=content`（按编译器内容判断）后才真正命中，并把 `CCACHE_MAXSIZE` 提到 5G。

## 常见问题

- **构建卡在下载 / 下载失败**：ImmortalWrt 镜像站偶尔限速，重跑即可；`make download` 阶段允许部分失败，编译阶段会重试。
- **首次构建很慢**：源码全量编译正常需要 2~2.5 小时；之后有 ccache 缓存通常会快一些（实测 1.5~2 小时）。ccache 的缓存目录是源码树的 `.ccache/`，缓存命中情况会在编译日志的 “ccache 编译前/后状态” 里打印。
- **刷完没有 Vantage**：确认刷的是本仓库产物，并在刷机时清除浏览器缓存后重新登录 LuCI。
- **想确认是不是 BBRv3**：看构建日志里 “校验 BBRv3 已进入 target 内核” 与 “校验内核模块与 packages.txt 已装进固件” 这两步；或 SSH 上路由后 `sysctl net.ipv4.tcp_congestion_control`（应为 `bbr`）、`lsmod | grep tcp_bbr`，再 `dmesg | grep -i bbr` 看版本。
- **想换 24.10**：本仓库只针对 25.12（apk 体系、主题 25.12 包）。24.10 需要改用 `.ipk` 主题包，且 BBRv3 补丁要换 6.6 版本，不属于当前流程。
