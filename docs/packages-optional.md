# 常用可选软件包中文说明

本文件列出 25.12.2 x86-64 官方源里**存在、但当前没有装进固件**的常用包，方便按需增补。

- 当前在装的 423 项见 [`packages.md`](packages.md)。
- 全部 11 618 个包名（含版本、来源 feed）见 [`reference/packages-25.12.2-x86_64.tsv`](reference/packages-25.12.2-x86_64.tsv)。
- 添加方式：把包名写进 [`config/packages.txt`](../config/packages.txt)，一行一个，然后 push 触发构建。
- 下表里标 **（已装）** 的表示清单里已经有了，不用重复添加。

> **加包前先想清楚三件事**
>
> 1. **空间**：rootfs 分区 20 GiB，但 squashfs 镜像越大，刷机写入越慢；代理/媒体类插件动辄几十 MB。
> 2. **冲突**：同一功能只装一个（例如 `dnsmasq-full` 与 `dnsmasq`、`luci-app-samba4` 与 `luci-app-ksmbd` 可以共存，但 `luci-app-passwall`/`homeproxy`/`openclash` 同时开会抢 DNS 和防火墙规则）。
> 3. **依赖**：`luci-app-*` 一般会自动带上后台程序和中文语言包；如果只想装后台程序，直接装同名非 `luci-` 包即可。

---

## 一、代理与分流

| 包名 | 说明 |
| --- | --- |
| `luci-app-homeproxy` **（已装）** | 基于 sing-box 的代理界面，支持订阅、规则分流、TUN 模式，配置最简单。TUN 依赖 `ip-full` 与 `kmod-tun`，本固件已预装，开箱即可启用 |
| `sing-box` **（已装）** | HomeProxy 的后端代理内核 |
| `luci-app-passwall` | 老牌全能代理插件，支持 SS/SSR/VMess/VLESS/Trojan/Hysteria 等，功能多、配置项也多 |
| `luci-app-openclash` | Clash 内核 + 图形界面，适合直接用 Clash 订阅 |
| `luci-app-dae` | 基于 eBPF 的透明代理（dae），性能好，需要较新内核特性 |
| `luci-app-daed` | dae 的守护进程/配置前端 |
| `luci-app-v2raya` | V2RayA 的 LuCI 前端，多协议、带订阅 |
| `luci-app-tinyproxy` | 最轻量的 HTTP 正向代理，适合内网共享上网 |

> 代理插件会修改 `dnsmasq`、`nftables` 规则并常驻内存；建议一次只启用一个。切换前先备份 `/etc/config/`。

## 二、DNS 与广告过滤

| 包名 | 说明 |
| --- | --- |
| `luci-app-adguardhome` + `adguardhome` | AdGuard Home：DNS 广告过滤 + 家长控制 + 统计面板 |
| `luci-app-smartdns` + `smartdns` | 多上游并发 DNS、按域名/IP 分流，常配合代理使用 |
| `mosdns` | 高性能 DNS 分流器（当前无 LuCI 应用，需手写配置） |
| `luci-app-adblock` | 用 dnsmasq 的 adblock 规则做广告过滤，轻量、无额外守护进程 |
| `luci-app-https-dns-proxy` | 把普通 DNS 转发到 DoH/DoT 上游（Cloudflare/Google 等） |
| `luci-app-unblockneteasemusic` | 解锁网易云音乐灰色歌曲（外部音源替换） |

> AdGuard Home、smartdns 都要接管 53 端口，和 `dnsmasq-full` 二选一或做上下游串联，别同时监听。

## 三、下载与网盘

| 包名 | 说明 |
| --- | --- |
| `luci-app-qbittorrent` + `qbittorrent` | qBittorrent BT/PT 下载，带 Web UI |
| `luci-app-transmission` + `transmission-daemon` | Transmission BT 下载，资源占用低 |
| `luci-app-aria2` + `aria2` **（已装）** | HTTP/FTP/BT 多线程下载，配 `ariang` 前端 |
| `luci-app-filebrowser` + `filebrowser` | 网页文件管理器，可当轻量网盘 |
| `luci-app-rclone` + `rclone` | 挂载/同步 OneDrive、Google Drive、阿里云盘等 |
| `luci-app-syncthing` + `syncthing` | 多设备文件同步（去中心化） |

> 下载类应用建议把数据目录放到独立磁盘或大分区，并注意 BT 连接数对内存的占用。

## 四、NAS 与共享

| 包名 | 说明 |
| --- | --- |
| `luci-app-samba4` + `samba4-server` **（已装）** | SMB/CIFS 共享，Windows 直接访问 |
| `luci-app-ksmbd` + `ksmbd-server` | 内核态 SMB 服务，性能比 Samba 好，配置项略少 |
| `luci-app-nfs` + `nfs-kernel-server` | NFS 共享，Linux/ESXi 场景常用 |
| `luci-app-minidlna` + `minidlna` | DLNA 媒体服务器，电视/盒子可直接播放 |
| `luci-app-airplay2` | AirPlay 2 音频接收，把路由变成无线音箱节点 |
| `wsdd2` **（已装）** | 让 Windows 10/11 的“网络”里能发现本机 |

> Samba 与 ksmbd 都监听 445，只能启用一个。用 Samba 的 ACL/回收站功能选 samba4，追求速度选 ksmbd。

## 五、媒体与投屏

| 包名 | 说明 |
| --- | --- |
| `xupnpd` | 把 IPTV 播放列表发布成 DLNA/UPnP 资源 |
| `luci-app-udpxy` + `udpxy` | 把运营商组播 IPTV 转成单播 HTTP，内网任意设备可看 |
| `luci-app-airplay2` | AirPlay 2 接收端 |

> udpxy 需要 `kmod-ipt-*` 与 IGMP 代理配合；本清单已含 `kmod-ip6tables`、`kmod-nf-*`，但未装 `igmpproxy`。

## 六、容器与虚拟化

| 包名 | 说明 |
| --- | --- |
| `luci-app-dockerman` + `docker`/`dockerd`/`containerd`/`runc`/`tini` **（已装）** | Docker 全套 + 图形管理 |
| `luci-app-lxc` + `lxc` | LXC 系统容器，比 Docker 更接近轻量虚拟机 |
| `podman` | 无守护进程的 OCI 容器工具（无 LuCI 界面） |
| `docker-compose` **（已装）** | 多容器编排 |

> 跑容器建议 rootfs ≥ 8 GiB 并开启 `kmod-veth`、`kmod-br-netfilter`（本清单已含）。J4125 只有 4 核，别一次跑太多容器。

## 七、远程访问与组网

| 包名 | 说明 |
| --- | --- |
| `luci-app-tailscale-community` + `tailscale` | Tailscale 组网（基于 WireGuard，免公网 IP） |
| `luci-app-zerotier` + `zerotier` **（已装）** | ZeroTier 虚拟局域网 |
| `luci-app-frpc` | frp 客户端，把内网服务映射到公网服务器 |
| `luci-app-frps` | frp 服务端，需要公网 IP |
| `luci-app-nps` | NPS 内网穿透客户端 |
| `luci-app-rustdesk-server` | 自建 RustDesk 远程桌面中继（hbb_rs） |
| `luci-app-softethervpn` | SoftEther VPN 服务端（L2TP/SSTP/OpenVPN 多协议） |
| `luci-app-openvpn-server` | OpenVPN 服务端一键配置 |

> 公网暴露管理端口风险很高，优先用 Tailscale/ZeroTier 这类点对点组网，别直接映射 22/80/443。

## 八、网络优化与多线

| 包名 | 说明 |
| --- | --- |
| `luci-app-mwan3` | 多 WAN 负载均衡与故障切换（多条宽带叠加） |
| `luci-app-sqm` | 智能队列管理（SQM），降低 bufferbloat、改善游戏延迟 |
| `luci-app-syncdial` | 多拨（同一账号多次拨号）辅助 |
| `luci-app-eqos` | 按 IP 限速（基于 tc） |
| `luci-app-ddns` | 动态域名（DDNS），支持几十家服务商 |
| `luci-app-ddns-go` | DDNS-GO 的界面，自动获取公网 IP 并更新域名 |
| `luci-app-watchcat` | 断网自动重启（看门狗） |
| `luci-app-wifischedule` | 按时间开关 Wi-Fi |
| `luci-app-upnp` + `miniupnpd-nftables` **（已装）** | UPnP 自动端口映射 |

> mwan3 与代理插件、IPv6 同时使用时规则容易冲突，建议先在测试环境验证。

## 九、系统与硬件

| 包名 | 说明 |
| --- | --- |
| `luci-app-diskman` | 图形化分区/格式化/挂载（比命令行安全） |
| `luci-app-hd-idle` | 硬盘空闲自动休眠，延长机械盘寿命 |
| `luci-app-nut` + `nut` | UPS 监控，断电自动关机 |
| `luci-app-p910nd` + `p910nd` | USB 打印机共享（RAW 端口） |
| `luci-app-usb-printer` | USB 打印机共享（带驱动/队列） |
| `luci-app-wol` **（已装）** | 网络唤醒内网设备 |
| `luci-app-advanced-reboot` | 重启到另一个系统/分区（双系统切换） |
| `luci-app-commands` | 自定义常用命令按钮，省得每次 SSH |
| `luci-app-attendedsysupgrade` | 在线保留配置升级固件（需固件支持） |

> J4125 软路由常见搭配：`luci-app-diskman` + `luci-app-hd-idle` + `smartmontools`（已装）。

## 十、监控

| 包名 | 说明 |
| --- | --- |
| `luci-app-netdata` + `netdata` **（已装）** | 实时性能面板 |
| `luci-app-vnstat2` + `vnstat2` **（已装）** | 流量统计 |
| `luci-app-snmpd` + `snmpd-nossl` **（已装）** | SNMP 采集，接 Zabbix/PRTG |
| `luci-app-lldpd` + `lldpd` **（已装）** | LLDP 拓扑发现 |
| `prometheus-node-exporter-lua` | Prometheus 指标导出（HTTP 拉取） |

> netdata 默认占内存较多，4 GB 内存的机器建议在配置里关掉不用的插件（`/etc/netdata/netdata.conf`）。

## 十一、主题

| 包名 | 说明 |
| --- | --- |
| `luci-theme-argon` + `luci-app-argon-config` **（已装）** | 社区最流行主题，支持自定义配色/背景 |
| `luci-theme-footstrap` | 基于 Bootstrap 的现代主题 |
| `luci-theme-material` **（已装）** | Material Design 风格 |
| `luci-theme-openwrt` / `luci-theme-openwrt-2020` **（已装）** | OpenWrt 经典主题 |
| `luci-theme-bootstrap` **（已装）** | 默认主题，最轻量 |

> 本仓库默认主题是 Vantage（第三方源）。多装主题只影响体积，可在“系统 → 系统 → 语言和界面”随时切换。

## 十二、命令行工具

路由器上排障基本靠这些，装上后 SSH 体验接近普通 Linux：

| 包名 | 说明 |
| --- | --- |
| `htop` | 交互式进程/资源查看 |
| `tmux` / `screen` | 会话保持，SSH 断了任务不中断 |
| `nano` / `vim-full` | 顺手的编辑器（busybox vi 功能有限） |
| `git` | 拉取配置仓库、脚本 |
| `rsync` | 增量同步/备份 |
| `unzip` / `tar` | 解压 |
| `tree` / `ncdu` | 目录树 / 磁盘占用分析 |
| `lsof` / `strace` | 查看占用文件 / 跟踪系统调用 |
| `iperf3` | 打流测速 |
| `tcpdump` | 抓包 |
| `nmap` | 端口扫描（自查暴露面） |
| `ethtool` | 网卡速率/协商/驱动信息 |
| `bind-dig` | DNS 查询诊断 |
| `psmisc` / `procps-ng-top` / `procps-ng-ps` | `killall`、`top`、`ps` 的完整版 |
| `coreutils` / `findutils` | GNU 版基础命令 |
| `zsh` / `fish` | 更好用的 shell |
| `python3` / `python3-pip` | 跑脚本 |
| `sqlite3-cli` | 查 AdGuard Home 等应用的数据库 |
| `openssh-sftp-server` | 让 WinSCP/FileZilla 能用 SFTP |
| `jq` **（已装）** | JSON 处理 |
| `bash` **（已装）** | Bash |

> 这些包单个都很小，全装大约 60–100 MB（解压后）。`vim-full`、`python3` 相对大一些。

---

## 附：不建议在 25.12 上找的包

下面这些在社区教程里很常见，但 **25.12.2 官方源里没有**，写进 `config/packages.txt` 会被构建脚本自动剔除：

- `luci-app-ssr-plus`、`luci-app-passwall2`、`luci-app-bypass`、`luci-app-clash`
- `luci-app-alist`、`alist`、`luci-app-jellyfin`、`jellyfin`、`luci-app-plex`
- `luci-app-mosdns`（只有后台 `mosdns`）
- `luci-app-turboacc`、`luci-app-nft-qos`、`luci-app-dnsfilter`
- `luci-app-cpufreq`、`luci-app-temp-status`
- `luci-theme-vantage` 的官方源版本（本仓库用的是第三方签名源，见 [`build-options.md`](build-options.md) 5.4）
- `7zip`、`zip`、`mtr`、`dnsutils`、`bash-completion`

需要这类插件时有三条路：换用 snapshot 源、自己编译 ipk/apk、或改用第三方 feed（风险自负）。