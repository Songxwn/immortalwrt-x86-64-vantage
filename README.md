# ImmortalWrt x86/64 + Vantage 自动构建

用 GitHub Actions 调用 **ImmortalWrt 官方 ImageBuilder** 生成可直接刷机的固件，全部编译在云端完成，本地不需要任何环境。

- 目标平台：`x86/64`，profile `generic`（适配 CncTion J4125-4L 等 x86 软路由）
- 基础版本：ImmortalWrt **25.12.x**（默认 25.12.2，apk 包管理）
- 主题：[Vantage](https://github.com/anothaDev/luci-theme-vantage) 1.2.x + 中文语言包，已写入固件并设为默认主题
- 包清单：来自现网路由 `/etc/apk/world`（423 项），见 [`config/packages.txt`](config/packages.txt)
- 产物：
  - `*combined-efi.img.gz` —— UEFI 启动，**推荐**
  - `*combined.img.gz` —— Legacy BIOS 启动
  - `SHA256SUMS.images` —— 校验值

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

## 自定义

- 增删软件包：编辑 `config/packages.txt`，一行一个；`-包名` 表示从默认包里移除（如 `-dnsmasq` 换成 `dnsmasq-full`）。
- 覆盖文件：放进 `files/`，会原样合并进固件（如 `files/etc/uci-defaults/`）。
- 换主题版本：修改 workflow 中 `VANTAGE_FEED` 指向的目录即可，包版本随主题源 `SHA256SUMS` 自动取最新。

## 说明

- 若某些包在 25.12 中不存在（如部分仅存在于 snapshot 的插件），构建脚本会自动剔除并在日志中列出，不会导致整体失败。
- Vantage 的签名公钥会装进固件 `/etc/apk/keys/`，并把主题源写入 `/etc/apk/repositories.d/99-vantage.list`，之后可在路由上 `apk update && apk upgrade` 单独升级主题。
- 首次启动由 `files/etc/uci-defaults/zzzz-vantage-theme` 强制选中 Vantage 主题。