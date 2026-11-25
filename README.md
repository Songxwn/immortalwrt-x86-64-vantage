# ImmortalWrt x86/64 + Vantage 自动构建

用 GitHub Actions 调用 **ImmortalWrt 官方 ImageBuilder** 生成可直接刷机的固件，全部编译在云端完成，本地不需要任何环境。

- 目标平台：`x86/64`，profile `generic`（适配 CncTion J4125-4L 等 x86 软路由）
- 基础版本：ImmortalWrt **25.12.x**（默认 25.12.2，apk 包管理）
- 主题：[Vantage](https://github.com/anothaDev/luci-theme-vantage) 1.2.x + 中文语言包，已写入固件并设为默认主题
- 拥塞控制：默认启用 **BBR**（`kmod-tcp-bbr` + `fq` 队列），开机自动生效。注意这是**主线内核的 BBRv1**，BBRv3 未进入主线，ImageBuilder 无法启用
- 包清单：来自现网路由 `/etc/apk/world`（423 项），见 [`config/packages.txt`](config/packages.txt)
- 分区表：与现网设备 `/dev/sda` 完全一致（16 MiB kernel + 20 GiB rootfs），见[下方说明](#分区布局)
- 产物：
  - `*combined-efi.img.gz` —— UEFI 启动，**推荐**
  - `*combined.img.gz` —— Legacy BIOS 启动
  - `*rootfs.img.gz` —— 仅 rootfs（供手工组装）
  - `SHA256SUMS.images` —— 校验值

## 定制化文档

| 文档 | 内容 |
| --- | --- |
| [`docs/build-options.md`](docs/build-options.md) | 编译选项中文说明：镜像类型、文件系统、分区、GRUB、全局开关、内核选项、软件源、常用配方 |
| [`docs/packages.md`](docs/packages.md) | 当前 423 个在装包逐条中文说明（按类别分组） |
| [`docs/packages-optional.md`](docs/packages-optional.md) | 常用可选包：代理、DNS 过滤、下载、NAS、容器、组网、监控、命令行工具 |
| [`docs/reference/`](docs/reference/) | 官方原始数据：11 618 个包名/版本、428 条 Kconfig 选项、官方 `.config`/feeds/profile |

文档总入口：[`docs/README.md`](docs/README.md)。

## 触发构建

| 方式 | 说明 |
| --- | --- |
| Push 到 `main` | 自动构建并更新 `latest` Release |
| Actions → Build → Run workflow | 手动构建，可填其他 25.12.x 版本 |
| 推送 `v*` tag | 额外生成带版本的 Release |

构建完成后在 **Releases → Latest build** 直接下载，或在对应 Actions 运行的 **Artifacts** 里下载。

## 刷机

1. 下载 `*-combined-efi.img.gz`（UEFI）或 `*-combined.img.gz`（Legacy BIOS）。
2. LuCI → 系统 → 备份/刷机 → 刷写新固件，上传该文件。
3. 或 SSH：

```sh
sysupgrade -n /tmp/immortalwrt-x86-64-generic-squashfs-combined-efi.img.gz
```

> 当前路由器是 ImmortalWrt SNAPSHOT（main 分支），本仓库基于 25.12 稳定分支，属于跨分支刷机，**建议不保留配置**（`-n`）。
>
> 镜像的 rootfs 分区是 20 GiB，sysupgrade 会按分区表整盘写入，写入量约 20 GiB（SSD 上通常 1~3 分钟），期间不要断电。

## 分区布局

现网设备（192.168.31.1，32 GB SSD）的实际分区：

```text
Device     Boot Start      End  Sectors Size Type
/dev/sda1  *      512    33279    32768  16M 83 Linux   # /boot（kernel + grub）
/dev/sda2       33792 41976831 41943040  20G 83 Linux   # squashfs rootfs + f2fs overlay
```

构建时通过 ImageBuilder 变量固定为同一布局：

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `CONFIG_TARGET_KERNEL_PARTSIZE` | `16` | MiB，对应 sda1 |
| `CONFIG_TARGET_ROOTFS_PARTSIZE` | `20480` | MiB（20 GiB），对应 sda2 |
| `CONFIG_QCOW2_IMAGES` | `n` | 不需要虚拟机镜像，省时间和磁盘 |

由于 20 GiB 的镜像在 CI 上不可能真实写满，workflow 会把 `gen_image_generic.sh` 和 `Image/pad-to` 的“写零填充”改成 `truncate` 稀疏扩展：文件逻辑大小仍是 20 GiB，磁盘占用只有实际内容（几百 MB），gzip 后的产物约 150 MB。构建结束前会解析 MBR，校验两个分区确实是 16 MiB / 20480 MiB。

## 自定义

- 增删软件包：编辑 `config/packages.txt`，一行一个；`-包名` 表示从默认包里移除（如 `-dnsmasq` 换成 `dnsmasq-full`）。
- 覆盖文件：放进 `files/`，会原样合并进固件（如 `files/etc/uci-defaults/`）。
- 换主题版本：修改 workflow 中 `VANTAGE_FEED` 指向的目录即可，包版本随主题源 `SHA256SUMS` 自动取最新。

## 说明

- 若某些包在 25.12 中不存在（如部分仅存在于 snapshot 的插件），构建脚本会自动剔除并在日志中列出，不会导致整体失败。
- Vantage 的签名公钥会装进固件 `/etc/apk/keys/`，并把主题源写入 `/etc/apk/repositories.d/99-vantage.list`，之后可在路由上 `apk update && apk upgrade` 单独升级主题。
- 首次启动由 `files/etc/uci-defaults/zzzz-vantage-theme` 强制选中 Vantage 主题。

## 构建时做的自动修补

ImageBuilder 25.12.2 装 400+ 包并按现网分区出镜像，会遇到几个坑，workflow 里已自动处理：

1. **`include/rootfs.mk` 空命令 bug**：ImageBuilder 模式下 `$(if $(IB),,awk ...)` 展开为空，生成 `then  ;` 造成 `syntax error near unexpected token ';'`。补丁把空分支改成 `:`。
2. **rootfs 分区默认只有 300 MB**：未压缩 rootfs 约 436 MB，`make_ext4fs` 报 `failed to allocate ... out of space`。现已改为 20480 MiB。
3. **20 GiB 分区写零会打满 runner**：`scripts/gen_image_generic.sh` 用 `dd if=/dev/zero` 填满整个分区，`include/image.mk` 的 `pad-to` 同样。两处都改为 `truncate` 稀疏扩展，逻辑大小不变、真实占用很小。
4. **gzip -9 压缩 20 GiB 太慢**：镜像内容是已压缩的 xz squashfs，改为 `gzip -1`，产物大小基本不变。
5. **默认开着 qcow2 / VDI / VMDK / VHDX / ISO 镜像和 ext4 变体**：每种格式都会把 20 GiB 分区再完整复制一遍（每份 1~5 分钟），ISO 还需要 `mkisofs`，对刷机毫无用处。现在统一关掉，只保留 squashfs 的 `combined.img.gz`（BIOS）、`combined-efi.img.gz`（UEFI）和 `rootfs.img.gz`。

## 常见问题

- **构建卡在下载**：ImmortalWrt 镜像站偶尔限速，重跑即可；脚本带 `--retry`。
- **刷完没有 Vantage**：确认刷的是本仓库产物，并在刷机时清除浏览器缓存后重新登录 LuCI。
- **想换 24.10**：本仓库只针对 25.12（apk 体系、主题 25.12 包）。24.10 需要改用 `.ipk` 主题包，不属于当前流程。