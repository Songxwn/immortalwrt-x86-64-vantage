# 定制化文档

这里放的是这个仓库的“说明书”：怎么改包、怎么改分区、每个包是干什么的、25.12 有哪些编译选项。

| 文档 | 内容 | 适合谁 |
| --- | --- | --- |
| [build-options.md](build-options.md) | 编译选项逐项中文说明：镜像类型、文件系统、分区、GRUB、全局编译开关、内核选项、软件源、常用定制配方 | 想改镜像结构 / 换文件系统 / 调分区的人 |
| [packages.md](packages.md) | 当前固件里 **422 个包**逐条中文说明，按系统基础、网络、kmod、存储、容器、LuCI、运行库等分组 | 想删包瘦身 / 搞清楚某个包干什么的人 |
| [packages-optional.md](packages-optional.md) | 25.12 官方源里**可用但未安装**的常用包：代理、DNS 过滤、下载、NAS、容器、组网、监控、命令行工具 | 想加功能的人 |
| [reference/build-options-25.12.2.tsv](reference/build-options-25.12.2.tsv) | 从官方源码提取的 397 条 Kconfig 选项原始数据（符号、类型、英文提示、默认值、依赖） | 想精确查某个 `CONFIG_*` 的人 |
| [reference/packages-25.12.2-x86_64.tsv](reference/packages-25.12.2-x86_64.tsv) | 25.12.2 x86-64 全部 **11 618 个包**（包名、版本、来源 feed），含 kmods | 查包名 / 确认版本的人 |
| [reference/config.buildinfo](reference/config.buildinfo) | 官方 25.12.2 x86/64 发布构建的完整 `.config` 原文 | 想对照官方配置的人 |
| [reference/feeds.buildinfo](reference/feeds.buildinfo) | 官方发布时各 feed 的 git 提交与地址 | 想复现官方源的人 |
| [reference/profiles.json](reference/profiles.json) | 官方 x86/64 的 profile 与默认包清单（机器可读） | 写脚本 / 查默认包的人 |

## 三分钟上手

### 只想换几个软件包

1. 打开 [`../config/packages.txt`](../config/packages.txt)。
2. 删包：把该行注释掉（行首加 `#`）或整行删除。
3. 加包：先在本目录的 `reference/packages-25.12.2-x86_64.tsv` 里搜一下包名，确认存在，再写一行。
4. 提交并 push 到 `main`，GitHub Actions 会自动重编。

```text
# 例：去掉 material 主题，加上 htop 和 tmux
- luci-theme-material
+ htop
+ tmux
```

### 想改分区大小

在 [`.github/workflows/build.yml`](../.github/workflows/build.yml) 里同时改这三处的值（它们必须一致）：

- `CONFIG_TARGET_KERNEL_PARTSIZE`（默认 `16`，单位 MiB）
- `CONFIG_TARGET_ROOTFS_PARTSIZE`（默认 `20480`，单位 MiB）
- 末尾“校验分区表”步骤中的断言值

改完 push，构建结束时会自动解析 MBR 校验；不一致会直接失败，不会产出有问题的镜像。

### 想预置配置

把文件放进 [`../files/`](../files/)：

- `files/etc/config/network` → 覆盖默认网络配置
- `files/etc/uci-defaults/xxx` → 首次启动执行一次，成功后自动删除
- `files/etc/init.d/xxx` → 每次启动执行（记得 `chmod +x`）

### 想看构建产物

- Actions 运行页的 **Artifacts**：保留 90 天
- **Releases → Latest build**：长期保存，含 `SHA256SUMS.images`

## 关于本仓库的构建方式

用的是 **ImmortalWrt 官方 ImageBuilder**，只做“组装”：下载官方预编译的内核和软件包，按清单拼成镜像。

这意味着：

- ✅ 能改：包选择、分区大小、镜像类型、GRUB 参数、rootfs 文件系统参数、`files/` 覆盖文件。
- ❌ 不能改：内核编译选项、软件包编译参数（LTO、musl/glibc、SELinux 策略等）。
- 想改后者只能做完整源码编译，耗时几小时，本仓库不涉及。

## 数据是怎么来的

| 文件 | 来源 |
| --- | --- |
| `packages.txt` | 现网路由器 `/etc/apk/world` 原样导出 + 4 个 Vantage 包 |
| `packages-25.12.2-x86_64.tsv` | `downloads.immortalwrt.org/releases/25.12.2/` 下各 feed 的 `index.json` + `kmods/<内核>/index.json` 合并 |
| `build-options-25.12.2.tsv` | 从 `immortalwrt/immortalwrt` 的 `config/Config-images.in`、`Config-build.in`、`Config-kernel.in`、`target/Config.in` 解析 |
| `config.buildinfo` / `feeds.buildinfo` / `profiles.json` | 官方 25.12.2 x86/64 发布目录 |

各 feed 的 `index.json` **只有包名和版本，没有描述**，所以 `packages.md` 里的中文说明是人工撰写的，按包的实际用途整理；发现不准确的欢迎提 issue 修正。

## 更新这些文档

升级到 25.12.x 新版本时，重新抓一遍数据即可：

```powershell
$base = 'https://downloads.immortalwrt.org/releases/25.12.3'
# 1) 抓各 feed 的 index.json，合并成 tsv
# 2) 抓 targets/x86/64/config.buildinfo、feeds.buildinfo、profiles.json
# 3) 从 GitHub 拉最新的 Config-*.in，重新解析 build-options tsv
```

具体命令可参考仓库提交历史里的脚本片段，或直接问维护者。