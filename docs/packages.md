# 在装软件包中文说明（422 项）

本文件逐条说明 [`config/packages.txt`](../config/packages.txt) 里随固件打包的全部软件包。
这份清单来自现网路由器 `192.168.31.1` 的 `/etc/apk/world`，再追加了 4 个 Vantage 主题包。

> **怎么用**
>
> - 想删包：在 `config/packages.txt` 里把对应行前面加 `#` 注释掉，或直接删除该行。
> - 想加包：先去 [`packages-25.12.2-x86_64.tsv`](reference/packages-25.12.2-x86_64.tsv) 确认 25.12.2 官方源里确实有这个包（共 11 618 条），再写进 `config/packages.txt`。
> - 不确定某个包干什么用：先在路由器上 `apk info -a 包名` 看描述，再决定。
> - `kmod-*` 必须与内核版本严格匹配，**不要自己指定版本号**，源码构建会按当前内核自动编出对应模块（`=m`）。
> - `lib*` 基本都是依赖自动带入的，手工删容易把别的包弄坏。

## 分组统计

| 分类 | 数量 |
| --- | ---: |
| 包选择规则与默认包替换 | 2 |
| 系统基础 | 66 |
| 网络与防火墙 | 14 |
| 内核模块：有线网卡驱动 | 38 |
| 内核模块：网络与防火墙 | 47 |
| 内核模块：加密与校验 | 32 |
| 内核模块：文件系统、USB 与硬件 | 47 |
| 存储与文件系统工具 | 8 |
| 容器 | 6 |
| 共享与设备发现 | 5 |
| 下载 | 3 |
| 监控、日志与远程运维 | 13 |
| VPN、内网穿透与代理内核 | 3 |
| LuCI 框架与模块 | 17 |
| LuCI 应用 | 20 |
| LuCI 主题 | 5 |
| 简体中文语言包 | 20 |
| 运行库 | 72 |
| Vantage 主题（本仓库新增） | 4 |
| **合计** | **422** |

> 合计 = 421 个「安装」条目 + 1 个「移除」条目 `-dnsmasq`（不单独成包，仅用于替换默认精简版）。

## 零、包选择规则与默认包替换

这里放 `-包名` 这类“从默认包里移除”的条目（对应 `.config` 里的 `# CONFIG_PACKAGE_dnsmasq is not set`）。

| 包名 | 说明 |
| --- | --- |
| `-dnsmasq` | 从默认包中移除 busybox/dnsmasq 精简版，给 `dnsmasq-full` 让位。 |
| `dnsmasq-full` | 完整版 DNS 转发 + DHCP 服务器：支持 DNSSEC、ipset/nftset、DHCPv6、按域名分流，是各类代理插件的基础。 |

## 一、系统基础

OpenWrt/ImmortalWrt 运行必需：init、ubus、uci、ubox、rpcd、uhttpd、证书等。

| 包名 | 说明 |
| --- | --- |
| `busybox` | 精简的 Unix 工具集合（sh、ls、cp、vi、ip 等），OpenWrt 的基础用户态。 |
| `procd` | OpenWrt 的 init 系统与进程管理（服务启动、热插拔、看门狗）。 |
| `procd-seccomp` | 给服务加 seccomp 系统调用过滤，降低被利用风险。 |
| `procd-ujail` | 用 namespace/资源限制把服务关进“监狱”，容器化系统服务。 |
| `ubus` | OpenWrt 的进程间通信总线（命令行客户端与库）。 |
| `ubusd` | ubus 总线守护进程，几乎所有 LuCI 操作都经过它。 |
| `ubox` | procd/ubox 的公共部分（日志、热插拔、kmodloader）。 |
| `uci` | 统一配置接口，`/etc/config/*` 的读写工具。 |
| `ucode` | ImmortalWrt 主推的轻量脚本语言，LuCI 新前端用它写。 |
| `ucode-mod-digest` | ucode 的哈希/摘要模块。 |
| `ucode-mod-fs` | ucode 的文件系统模块。 |
| `ucode-mod-html` | ucode 的 HTML 模板模块（LuCI 视图用）。 |
| `ucode-mod-log` | ucode 的日志模块。 |
| `ucode-mod-lua` | ucode 调用 Lua 代码的桥接模块。 |
| `ucode-mod-math` | ucode 的数学函数模块。 |
| `ucode-mod-ubus` | ucode 访问 ubus 的模块。 |
| `ucode-mod-uci` | ucode 读写 uci 配置的模块。 |
| `ucode-mod-uloop` | ucode 的事件循环（uloop）模块。 |
| `libubox` | OpenWrt 基础 C 库：链表、JSON、blob、uloop 事件循环。 |
| `libubus` | ubus 的 C 客户端库。 |
| `libubus-lua` | ubus 的 Lua 绑定。 |
| `libuci` | uci 的 C 库。 |
| `libucode` | ucode 解释器运行库。 |
| `libuclient` | OpenWrt 的 HTTP/FTP 下载客户端库。 |
| `libblobmsg-json` | blobmsg 与 JSON 互转库（ubus/LuCI 常用）。 |
| `libjson-script` | JSON 脚本解析库（jshn 的底层）。 |
| `jshn` | 在 shell 里读写 JSON 的工具库，OpenWrt 脚本大量使用。 |
| `jsonfilter` | 按路径提取 JSON 字段的小工具，init 脚本常用。 |
| `jansson` | Jansson JSON 库（aria2 等依赖）。 |
| `logd` | OpenWrt 的日志守护进程，收集内核与服务的日志。 |
| `netifd` | 网络配置守护进程，负责接口、路由、协议脚本。 |
| `fstools` | OpenWrt 的挂载/overlay 管理工具（`block`、`mount_root`）。 |
| `block-mount` | 块设备挂载与 fstab/overlay 配置支持。 |
| `fwtool` | 读写固件镜像元数据（sysupgrade 校验用）。 |
| `mtd` | MTD 闪存操作工具；x86 上基本用不到，随默认包带入。 |
| `rpcd` | LuCI 的 RPC 守护进程，Web 界面通过它与系统交互。 |
| `rpcd-mod-file` | rpcd 的文件浏览/上传插件。 |
| `rpcd-mod-iwinfo` | rpcd 的无线信息插件。 |
| `rpcd-mod-luci` | rpcd 的 LuCI 专用插件（会话、权限、菜单）。 |
| `rpcd-mod-rrdns` | rpcd 的反向 DNS 插件，用于在线主机名显示。 |
| `rpcd-mod-ucode` | 让 rpcd 能执行 ucode 插件。 |
| `uhttpd` | 轻量 HTTP 服务器，LuCI 的默认 Web 服务。 |
| `uhttpd-mod-ubus` | uhttpd 的 ubus 桥接，提供 LuCI 的 JSON-RPC 接口。 |
| `cgi-io` | LuCI 用的 CGI 上传/下载辅助程序。 |
| `dropbear` | 轻量 SSH 服务端（默认 22 端口）。 |
| `ca-bundle` | CA 根证书合集（curl/wget 校验 HTTPS 用）。 |
| `ca-certificates` | CA 证书管理工具与证书目录。 |
| `urandom-seed` | 启动时恢复/保存随机数种子，改善早期熵不足。 |
| `urngd` | 基于 jitter 的熵收集守护进程。 |
| `getrandom` | 早期启动阶段初始化内核熵池的辅助包。 |
| `usign` | OpenWrt 的签名/验签工具，用于软件源与镜像签名。 |
| `openwrt-keyring` | 内置官方软件源签名公钥。 |
| `terminfo` | 终端能力数据库，vim/tmux/htop 等全屏程序需要。 |
| `default-settings` | ImmortalWrt 定制包，写入一套默认 uci 配置（主机名、时区、国内优化等）。 |
| `bash` | GNU Bash，比 busybox ash 功能完整。 |
| `curl` | 命令行 HTTP/HTTPS/FTP 客户端。 |
| `jq` | 命令行 JSON 处理器，写脚本排障很方便。 |
| `attr` | 扩展属性工具（getfattr/setfattr），Samba ACL 场景会用到。 |
| `dbus` | D-Bus 消息总线守护进程，Avahi 等服务依赖。 |
| `grub2` | GRUB 引导器核心包，x86 启动全靠它。 |
| `grub2-bios-setup` | 把 GRUB 安装到磁盘 MBR，供 Legacy BIOS 启动。 |
| `grub2-efi` | GRUB 的 EFI 版本，供 UEFI 启动。 |
| `openssl-util` | `openssl` 命令行工具（生成证书/密钥/摘要）。 |
| `uclient-fetch` | 基于 libuclient 的轻量下载工具，常作为 wget 替代。 |
| `lua` | Lua 5.1 解释器，老版 LuCI 页面仍依赖。 |
| `zlib` | zlib 压缩库，大量程序的基础依赖。 |

## 二、网络与防火墙

网络配置、nftables/iptables 兼容层、PPPoE、DHCPv6、UPnP 等。

| 包名 | 说明 |
| --- | --- |
| `firewall4` | 基于 nftables 的防火墙服务（OpenWrt 22.03 起的默认实现）。 |
| `nftables-json` | nftables 的 JSON 输出支持，LuCI 防火墙页面读取规则用。 |
| `iptables-nft` | `iptables` 命令的 nftables 后端（兼容老脚本）。 |
| `ip6tables-nft` | `ip6tables` 命令的 nftables 后端。 |
| `xtables-nft` | xtables 与 nftables 的兼容工具集。 |
| `iptables-mod-extra` | iptables 额外匹配模块（按时间、长度、随机等）。 |
| `miniupnpd-nftables` | UPnP IGD 服务（nftables 版），给内网设备自动开端口。 |
| `odhcp6c` | DHCPv6 客户端，向运营商申请 IPv6 地址/前缀。 |
| `odhcpd-ipv6only` | 仅 IPv6 的 DHCPv6/RA 服务端，给下游发地址。 |
| `ppp` | PPP 协议守护进程，PPPoE 拨号的基础。 |
| `ppp-mod-pppoe` | PPP 的 PPPoE 插件（宽带拨号必需）。 |
| `iputils-arping` | arping 工具，检测 IP 冲突/邻居在线状态。 |
| `etherwake` | 发送 WOL 网络唤醒魔术包。 |
| `resolveip` | 把域名解析成 IP 的小工具（脚本常用）。 |

## 三、内核模块：有线网卡驱动

x86 软路由常见网卡。装多了不影响使用，但会增加镜像体积；实际只保留机器上用得到的即可。

| 包名 | 说明 |
| --- | --- |
| `kmod-8139cp` | Realtek RTL8139 百兆网卡（cp 变体）。 |
| `kmod-8139too` | Realtek RTL8139 百兆网卡（经典驱动）。 |
| `kmod-amazon-ena` | Amazon AWS ENA 虚拟网卡（云主机用）。 |
| `kmod-amd-xgbe` | AMD 10GbE 有线网卡。 |
| `kmod-bnx2` | Broadcom NetXtreme 千兆网卡，需要 `bnx2-firmware`。 |
| `bnx2-firmware` | Broadcom NetXtreme 网卡固件，`kmod-bnx2` 加载时需要。 |
| `i915-firmware-dmc` | Intel 核显 DMC 微码固件，影响显示输出与低功耗状态。 |
| `kmod-dwmac-intel` | Intel 平台集成的 Synopsys DWMAC 以太网。 |
| `kmod-e1000` | Intel 82540/82541/82544 等千兆网卡（老服务器常见）。 |
| `kmod-e1000e` | Intel I217/I218/I219 等 PCIe 千兆网卡。 |
| `kmod-forcedeth` | NVIDIA nForce 主板集成网卡。 |
| `kmod-i40e` | Intel X710/XL710 系列 10/40GbE 网卡。 |
| `kmod-igb` | Intel 82575/82576/82580/I350 千兆网卡。 |
| `kmod-igbvf` | Intel 82576 的 SR-IOV 虚拟功能。 |
| `kmod-igc` | Intel I225/I226 2.5GbE 网卡（N5105/J4125 软路由常见）。 |
| `kmod-ixgbe` | Intel 82598/82599/X540/X550 10GbE 网卡。 |
| `kmod-ixgbevf` | Intel 10GbE 网卡的 SR-IOV 虚拟功能。 |
| `kmod-pcnet32` | AMD PCnet32 网卡（老机器与部分虚拟机）。 |
| `kmod-r8101` | Realtek RTL810x 百兆网卡（厂商驱动）。 |
| `kmod-r8125` | Realtek RTL8125 2.5GbE 网卡（厂商驱动，性能更好）。 |
| `kmod-r8126` | Realtek RTL8126 5GbE 网卡（厂商驱动）。 |
| `kmod-r8168` | Realtek RTL8168/8111 千兆网卡（厂商驱动）。 |
| `kmod-tg3` | Broadcom Tigon3 千兆网卡。 |
| `kmod-tulip` | DEC Tulip 系列老网卡。 |
| `kmod-vmxnet3` | VMware vmxnet3 虚拟网卡（ESXi 虚拟机用）。 |
| `kmod-dummy` | 虚拟 dummy 网卡，常用于占位或测试路由。 |
| `kmod-phy-ax88796b` | ASIX AX88796B 以太网 PHY。 |
| `kmod-pcs-xpcs` | PCS/PMA 以太网子层，部分高速网卡依赖。 |
| `kmod-stmmac-core` | Synopsys DesignWare 以太网核心（多种嵌入式网卡共用）。 |
| `kmod-pps` | PPS 秒脉冲时间戳（高精度授时）。 |
| `kmod-ptp` | PTP 精确时间协议硬件时钟。 |
| `kmod-mdio` | MDIO 总线，网卡与 PHY 通信的基础。 |
| `kmod-mdio-devres` | MDIO 设备资源管理辅助。 |
| `kmod-mii` | MII 管理接口。 |
| `kmod-libphy` | 通用 PHY 设备库，多数网卡驱动依赖。 |
| `kmod-phylink` | PHY 链路状态管理框架。 |
| `kmod-libeth` | 内核以太网公共库。 |
| `kmod-libie` | 内核 IEEE 802.15.4 库。 |

## 四、内核模块：网络与防火墙

网桥、VLAN、隧道、netfilter/nftables、连接跟踪等。

| 包名 | 说明 |
| --- | --- |
| `kmod-br-netfilter` | 让网桥流量经过 netfilter；Docker、透明网桥防火墙必需。 |
| `kmod-veth` | 虚拟以太网对，容器网络的基础。 |
| `kmod-macvlan` | MACVLAN 虚拟接口，容器/多网段场景用。 |
| `kmod-tun` | TUN/TAP 虚拟网卡，VPN 与代理工具依赖。 |
| `kmod-wireguard` | WireGuard VPN 内核模块。 |
| `kmod-udptunnel4` | IPv4 UDP 隧道封装（L2TP、VXLAN 等依赖）。 |
| `kmod-udptunnel6` | IPv6 UDP 隧道封装。 |
| `kmod-nfnetlink` | netfilter 与用户态通信的 netlink 通道。 |
| `kmod-nf-conntrack` | 连接跟踪核心，NAT/防火墙状态检测的基础。 |
| `kmod-nf-conntrack6` | IPv6 连接跟踪。 |
| `kmod-nf-conntrack-netlink` | 连接跟踪 netlink 接口，`conntrack` 命令用。 |
| `kmod-nf-nat` | netfilter NAT 核心。 |
| `kmod-nf-nat6` | netfilter IPv6 NAT。 |
| `kmod-nf-flow` | 网络流表，软件加速转发（flowtable）。 |
| `kmod-nf-ipt` | netfilter 的 IPv4 iptables 兼容层。 |
| `kmod-nf-ipt6` | netfilter 的 IPv6 iptables 兼容层。 |
| `kmod-nf-log` | netfilter 日志目标（IPv4）。 |
| `kmod-nf-log6` | netfilter 日志目标（IPv6）。 |
| `kmod-nf-reject` | netfilter REJECT 动作（IPv4），拒绝时回 ICMP。 |
| `kmod-nf-reject6` | netfilter REJECT 动作（IPv6）。 |
| `kmod-nf-ipvs` | IPVS 四层负载均衡。 |
| `kmod-nf-tproxy` | netfilter 透明代理（IPv4），代理插件重定向流量用。 |
| `kmod-nft-core` | nftables 核心。 |
| `kmod-nft-nat` | nftables NAT。 |
| `kmod-nft-fib` | nftables FIB 表达式（反向路径/路由信息匹配）。 |
| `kmod-nft-fullcone` | fullcone NAT，改善 P2P、游戏联机的连通性。 |
| `kmod-nft-offload` | 流表卸载加速（软件/硬件 offload）。 |
| `kmod-nft-compat` | nftables 与 xtables 的兼容层。 |
| `kmod-nft-tproxy` | nftables 透明代理。 |
| `kmod-ipt-core` | iptables 核心表（filter/nat/mangle）。 |
| `kmod-ipt-conntrack` | iptables 连接跟踪匹配（`-m conntrack`）。 |
| `kmod-ipt-nat` | iptables IPv4 NAT。 |
| `kmod-ipt-nat6` | iptables IPv6 NAT。 |
| `kmod-ipt-extra` | iptables 额外匹配模块。 |
| `kmod-ipt-physdev` | 按入站物理设备匹配，多拨/策略路由常用。 |
| `kmod-ip6tables` | IPv6 iptables 的内核部分。 |
| `kmod-netlink-diag` | netlink 诊断协议，`ss` 等工具依赖。 |
| `kmod-inet-diag` | INET socket 诊断，`ss` 查看连接用。 |
| `kmod-net-selftests` | 内核网络子系统自测模块，正常使用不需要。 |
| `kmod-ppp` | PPP 协议内核支持。 |
| `kmod-pppoe` | PPPoE 内核加速，宽带拨号用。 |
| `kmod-pppox` | PPPoX 通用框架。 |
| `kmod-slhc` | PPP 的 TCP 头压缩（Van Jacobson）。 |
| `kmod-mppe` | Microsoft MPPE 加密，PPTP VPN 用。 |
| `kmod-button-hotplug` | 把按键事件转成 hotplug 事件（复位键等）。 |
| `kmod-tcp-bbr` | Google BBR 拥塞控制内核模块。本固件为**源码构建**，内核已打入 BBRv3 补丁，因此这里提供的是 **BBRv3**，并由 `files/etc/sysctl.d/99-bbr.conf` 设为默认拥塞控制。 |
| `kmod-sched` | 额外的流量调度器集合，包含 BBR 推荐的 `fq` 队列（另有 codel、sfq 等）。 |

## 五、内核模块：加密与校验

WireGuard、OpenSSL、IPsec、磁盘加密、哈希/校验算法依赖。

| 包名 | 说明 |
| --- | --- |
| `kmod-crypto-manager` | 加密算法管理框架，自动加载所需算法模块。 |
| `kmod-crypto-hash` | 哈希算法框架（SHA/MD5 等）。 |
| `kmod-crypto-acompress` | 压缩算法框架（IPComp 等）。 |
| `kmod-crypto-aead` | AEAD 认证加密框架（GCM/CCM）。 |
| `kmod-crypto-null` | 空加密算法，测试用。 |
| `kmod-crypto-arc4` | ARC4 流加密（老式 WEP/PPTP）。 |
| `kmod-crypto-ecb` | ECB 分组加密模式。 |
| `kmod-crypto-hmac` | HMAC 消息认证码。 |
| `kmod-crypto-kpp` | 密钥协商原语框架（DH/ECDH）。 |
| `kmod-crypto-rng` | 随机数生成器框架。 |
| `kmod-crypto-user` | 用户态加密接口（AF_ALG），cryptsetup 等用。 |
| `kmod-crypto-sha1` | SHA-1 哈希。 |
| `kmod-crypto-sha3` | SHA-3 哈希。 |
| `kmod-crypto-sha512` | SHA-512 哈希。 |
| `kmod-crypto-blake2b` | BLAKE2b 高速哈希。 |
| `kmod-crypto-xxhash` | xxHash 高速哈希。 |
| `kmod-crypto-crc32` | CRC32 校验。 |
| `kmod-crypto-crc32c` | CRC32C 校验（iSCSI/btrfs 等）。 |
| `kmod-crypto-lib-chacha20` | ChaCha20 流加密。 |
| `kmod-crypto-lib-chacha20poly1305` | ChaCha20-Poly1305，WireGuard/TLS 1.3 使用。 |
| `kmod-crypto-lib-curve25519` | Curve25519 密钥交换。 |
| `kmod-crypto-lib-poly1305` | Poly1305 消息认证。 |
| `kmod-lib-crc16` | CRC16 计算库。 |
| `kmod-lib-crc32c` | CRC32C 计算库。 |
| `kmod-lib-crc-ccitt` | CRC-CCITT 计算库。 |
| `kmod-lib-xxhash` | xxHash 内核库。 |
| `kmod-lib-zlib-deflate` | 内核 zlib 压缩。 |
| `kmod-lib-zlib-inflate` | 内核 zlib 解压。 |
| `kmod-lib-zstd` | 内核 Zstandard 压缩。 |
| `kmod-lib-lzo` | 内核 LZO 压缩。 |
| `kmod-lib-xor` | XOR 加速库（RAID/校验）。 |
| `kmod-lib-raid6` | RAID6 校验计算库。 |

## 六、内核模块：文件系统、USB 与硬件

ext4/f2fs/NTFS/exFAT、USB 存储、显示与输入、传感器等。

| 包名 | 说明 |
| --- | --- |
| `kmod-fs-ext4` | ext4 文件系统。 |
| `kmod-fs-f2fs` | F2FS 文件系统（overlay 分区默认格式）。 |
| `kmod-fs-btrfs` | Btrfs 文件系统（快照、压缩）。 |
| `kmod-fs-ntfs3` | NTFS3 读写驱动（Paragon 内核驱动）。 |
| `kmod-fs-exfat` | exFAT 文件系统，U 盘/移动硬盘常用。 |
| `kmod-fs-vfat` | FAT16/32 文件系统。 |
| `kmod-nls-base` | 文件名编码转换核心。 |
| `kmod-nls-utf8` | UTF-8 文件名编码，U 盘中文文件名必需。 |
| `kmod-nls-cp437` | DOS CP437 编码，FAT 长文件名用。 |
| `kmod-nls-iso8859-1` | Latin-1 编码。 |
| `kmod-scsi-core` | SCSI 核心，USB 存储/UAS 依赖。 |
| `kmod-usb-core` | USB 核心。 |
| `kmod-usb-common` | USB 公共库。 |
| `kmod-usb-storage` | USB 大容量存储（U 盘/移动硬盘）。 |
| `kmod-usb-storage-extras` | 特殊 USB 存储设备支持。 |
| `kmod-usb-storage-uas` | USB Attached SCSI，UASP 设备加速。 |
| `kmod-usb-hid` | USB 键盘/鼠标。 |
| `kmod-usb-net` | USB 网卡框架。 |
| `kmod-usb-net-asix` | ASIX AX88xxx USB 网卡。 |
| `kmod-usb-net-asix-ax88179` | ASIX AX88179 USB3 千兆网卡。 |
| `kmod-usb-net-rtl8150` | Realtek RTL8150 USB 网卡。 |
| `kmod-usb-net-rtl8152-vendor` | Realtek RTL8152/8153/8156 USB 网卡（厂商驱动，2.5G 常用）。 |
| `kmod-hid` | HID 输入设备核心。 |
| `kmod-hid-generic` | 通用 HID 驱动（USB 键鼠）。 |
| `kmod-input-core` | 输入子系统核心。 |
| `kmod-input-evdev` | evdev 输入事件接口。 |
| `kmod-hwmon-core` | 硬件监控核心（温度/电压/风扇）。 |
| `kmod-i2c-core` | I2C 总线核心。 |
| `kmod-i2c-algo-bit` | 软件模拟 I2C（GPIO bit-banging）。 |
| `kmod-dma-buf` | DMA 缓冲区共享框架。 |
| `kmod-drm` | 直接渲染管理器核心（核显）。 |
| `kmod-drm-i915` | Intel 核显驱动（J4125 的 UHD 600 等）。 |
| `kmod-drm-buddy` | DRM 显存伙伴分配器。 |
| `kmod-drm-display-helper` | DRM 显示模式辅助库。 |
| `kmod-drm-exec` | DRM 执行/提交辅助。 |
| `kmod-drm-kms-helper` | DRM KMS 辅助库。 |
| `kmod-drm-suballoc-helper` | DRM 子分配辅助库。 |
| `kmod-drm-ttm` | DRM 显存管理（TTM）。 |
| `kmod-drm-ttm-helper` | TTM 辅助库。 |
| `kmod-fb` | framebuffer 控制台核心（本地显示输出）。 |
| `kmod-fb-cfb-copyarea` | framebuffer 位块拷贝。 |
| `kmod-fb-cfb-fillrect` | framebuffer 矩形填充。 |
| `kmod-fb-cfb-imgblt` | framebuffer 图像位块传输。 |
| `kmod-fb-sys-fops` | framebuffer 文件操作。 |
| `kmod-fb-sys-ram` | framebuffer 内存映射。 |
| `kmod-acpi-video` | ACPI 视频扩展（亮度/背光热键）。 |
| `kmod-backlight` | 背光控制子系统。 |

## 七、存储与文件系统工具

分区、格式化、挂载、SMART 检测。

| 包名 | 说明 |
| --- | --- |
| `e2fsprogs` | ext2/3/4 工具：mkfs.ext4、e2fsck、resize2fs、tune2fs。 |
| `btrfs-progs` | Btrfs 管理工具：mkfs.btrfs、btrfs subvolume、scrub。 |
| `fdisk` | MBR/GPT 分区工具（util-linux 版）。 |
| `lsblk` | 列出块设备与分区。 |
| `partx-utils` | 解析内核分区表、通知内核重读分区。 |
| `mkf2fs` | 创建 F2FS 文件系统的工具。 |
| `ntfs3-mount` | 用内核 ntfs3 驱动挂载 NTFS 的辅助脚本与 hotplug 规则。 |
| `automount` | U 盘/移动硬盘插入后自动挂载到 `/mnt/` 下。 |

## 八、容器

Docker 与 OCI 运行时。

| 包名 | 说明 |
| --- | --- |
| `docker` | Docker CLI 元包。 |
| `dockerd` | Docker 守护进程。 |
| `containerd` | 符合 OCI 标准的容器运行时，Docker 底层依赖。 |
| `runc` | OCI 容器创建与运行工具。 |
| `tini` | 极简 init，容器里回收僵尸进程。 |
| `docker-compose` | 用 YAML 编排多个容器（v2 插件）。 |

## 九、共享与设备发现

SMB 共享、Windows 网络发现、mDNS/Avahi。

| 包名 | 说明 |
| --- | --- |
| `samba4-server` | SMB/CIFS 文件共享服务端（Windows 网络邻居）。 |
| `samba4-libs` | Samba4 运行库。 |
| `autosamba` | 自动为已挂载磁盘生成 Samba 共享配置的辅助包。 |
| `wsdd2` | WS-Discovery 服务，让 Windows 10/11 能在“网络”里发现本机。 |
| `avahi-dbus-daemon` | mDNS/DNS-SD 服务（Avahi），局域网设备自动发现。 |

## 十、下载

aria2 及其 Web 前端。

| 包名 | 说明 |
| --- | --- |
| `aria2` | 多协议多线程下载器（HTTP/FTP/BT/磁力）。 |
| `aria2-openssl` | 让 aria2 使用 OpenSSL 而非内置 TLS 实现。 |
| `ariang` | Aria2 的现代 Web 前端（纯静态页面）。 |

## 十一、监控、日志与远程运维

流量统计、SNMP、LLDP、终端、时间同步、KMS 等。

| 包名 | 说明 |
| --- | --- |
| `netdata` | 实时性能监控面板（CPU/内存/磁盘/网络/进程）。 |
| `vnstat2` | 按接口统计流量（日/月/年），数据持久化。 |
| `vnstati2` | vnstat 的图片输出工具（PNG 图表）。 |
| `snmpd-nossl` | Net-SNMP 服务端（不带 TLS），供 Zabbix/PRTG 等采集。 |
| `lldpd` | LLDP 邻居发现服务，交换机拓扑里能看到本机。 |
| `ttyd` | 把终端搬到浏览器（Web SSH），方便手机排障。 |
| `openssh-client` | OpenSSH 客户端（ssh/scp/sftp），比 dropbear 兼容性好。 |
| `openssh-keygen` | OpenSSH 密钥生成工具。 |
| `chrony` | 高精度 NTP 客户端/服务端，比 busybox ntpd 稳。 |
| `smartmontools` | 硬盘 SMART 检测（smartctl），可看健康度/温度。 |
| `smartmontools-drivedb` | smartctl 的硬盘型号数据库。 |
| `vlmcsd` | KMS 服务器模拟器，用于激活 Windows/Office（自用场景）。 |
| `shellsync` | 同步多个 shell 脚本并行执行的小工具（多核编译/批处理）。 |

## 十二、VPN、内网穿透与代理内核

WireGuard 工具、ZeroTier、sing-box 等。

| 包名 | 说明 |
| --- | --- |
| `wireguard-tools` | WireGuard 配置工具（wg、wg-quick）。 |
| `zerotier` | ZeroTier 虚拟局域网客户端，免公网 IP 组网。 |
| `sing-box` | 通用代理内核（Shadowsocks/VMess/VLESS/Trojan/Hysteria 等），HomeProxy 的后端。 |

## 十三、LuCI 框架与模块

Web 管理界面的基础组件。这些是 LuCI 正常工作的骨架，不建议删除。

| 包名 | 说明 |
| --- | --- |
| `luci` | LuCI 元包，安装 Web 管理界面所需的全部基础组件。 |
| `luci-base` | LuCI 核心：MVC 框架、会话、菜单、主题框架。 |
| `luci-light` | 精简 LuCI：base + 完整管理模块 + bootstrap 主题。 |
| `luci-compat` | 兼容旧 Lua 控制器/视图的兼容层，很多第三方插件需要。 |
| `luci-lua-runtime` | LuCI 的 Lua 运行时支持包。 |
| `luci-mod-admin-full` | 完整管理模块（系统、网络、状态菜单合集）。 |
| `luci-mod-network` | 网络配置模块（接口、DHCP、防火墙入口）。 |
| `luci-mod-status` | 状态模块（概览、路由、日志、实时流量）。 |
| `luci-mod-system` | 系统模块（管理权、软件包、备份、重启）。 |
| `luci-lib-base` | LuCI 基础 Lua 库。 |
| `luci-lib-ip` | LuCI 的 IP 地址处理库。 |
| `luci-lib-jsonc` | LuCI 的 JSON-C 封装。 |
| `luci-lib-nixio` | LuCI 的 socket/文件系统库。 |
| `luci-lib-uqr` | 二维码生成库（分享 Wi-Fi 密码用）。 |
| `luci-proto-ipv6` | LuCI 的 IPv6 协议配置支持。 |
| `luci-proto-ppp` | LuCI 的 PPP/PPPoE 配置支持。 |
| `luci-proto-wireguard` | LuCI 的 WireGuard 配置支持。 |

## 十四、LuCI 应用

各功能对应的 Web 配置页面。

| 包名 | 说明 |
| --- | --- |
| `luci-app-firewall` | 防火墙规则与端口转发界面。 |
| `luci-app-package-manager` | apk 软件包管理界面（安装/卸载/升级）。 |
| `luci-app-argon-config` | Argon 主题的设置页面（配色、模糊、登录背景）。 |
| `luci-app-aria2` | aria2 下载器的 Web 配置页面。 |
| `luci-app-chrony` | chrony 时间同步的配置页面。 |
| `luci-app-dockerman` | Docker 管理界面（容器、镜像、网络、卷）。 |
| `luci-app-filebrowser` | FileBrowser 网盘界面配置（多用户文件管理）。 |
| `luci-app-homeproxy` | 基于 sing-box 的代理/分流界面，支持订阅与规则。 |
| `luci-app-lldpd` | LLDP 邻居发现配置。 |
| `luci-app-netdata` | netdata 监控面板入口与配置。 |
| `luci-app-openvpn` | OpenVPN 客户端/服务端配置。 |
| `luci-app-samba4` | Samba 共享目录与用户配置。 |
| `luci-app-snmpd` | SNMP 服务端配置。 |
| `luci-app-ttyd` | Web 终端配置。 |
| `luci-app-upnp` | UPnP/NAT-PMP 端口自动映射配置。 |
| `luci-app-vlmcsd` | vlmcsd KMS 服务配置。 |
| `luci-app-vnstat2` | 流量统计与图表页面。 |
| `luci-app-wechatpush` | 把路由事件/状态推送到微信（Server 酱类接口）。 |
| `luci-app-wol` | 网络唤醒（WOL）界面。 |
| `luci-app-zerotier` | ZeroTier 组网配置。 |

## 十五、LuCI 主题

默认会同时装多个主题，可在“系统 → 系统 → 语言和界面”里切换。

| 包名 | 说明 |
| --- | --- |
| `luci-theme-argon` | Argon 主题（社区最流行，支持深浅色与自定义配色）。 |
| `luci-theme-bootstrap` | LuCI 默认主题，轻量、兼容性最好。 |
| `luci-theme-material` | Material Design 风格主题。 |
| `luci-theme-openwrt` | OpenWrt 经典主题。 |
| `luci-theme-openwrt-2020` | OpenWrt 2020 版经典主题。 |

## 十六、简体中文语言包

`luci-i18n-*-zh-cn` 只包含翻译，不含功能；删掉后对应页面变英文。

| 包名 | 说明 |
| --- | --- |
| `luci-i18n-base-zh-cn` | LuCI 基础界面的简体中文。 |
| `luci-i18n-firewall-zh-cn` | 防火墙页面简体中文。 |
| `luci-i18n-package-manager-zh-cn` | 软件包管理页面简体中文。 |
| `luci-i18n-argon-config-zh-cn` | Argon 主题设置简体中文。 |
| `luci-i18n-aria2-zh-cn` | aria2 页面简体中文。 |
| `luci-i18n-dockerman-zh-cn` | Docker 管理页面简体中文。 |
| `luci-i18n-docker-zh-cn` | Docker 相关页面简体中文。 |
| `luci-i18n-filebrowser-zh-cn` | FileBrowser 页面简体中文。 |
| `luci-i18n-homeproxy-zh-cn` | HomeProxy 页面简体中文。 |
| `luci-i18n-lldpd-zh-cn` | LLDP 页面简体中文。 |
| `luci-i18n-netdata-zh-cn` | netdata 页面简体中文。 |
| `luci-i18n-openvpn-zh-cn` | OpenVPN 页面简体中文。 |
| `luci-i18n-samba4-zh-cn` | Samba 页面简体中文。 |
| `luci-i18n-snmpd-zh-cn` | SNMP 页面简体中文。 |
| `luci-i18n-ttyd-zh-cn` | Web 终端页面简体中文。 |
| `luci-i18n-upnp-zh-cn` | UPnP 页面简体中文。 |
| `luci-i18n-vlmcsd-zh-cn` | vlmcsd 页面简体中文。 |
| `luci-i18n-vnstat2-zh-cn` | 流量统计页面简体中文。 |
| `luci-i18n-wechatpush-zh-cn` | 微信推送页面简体中文。 |
| `luci-i18n-wol-zh-cn` | 网络唤醒页面简体中文。 |
| `luci-i18n-zerotier-zh-cn` | ZeroTier 页面简体中文。 |

## 十七、运行库

绝大多数由依赖自动带入。手工删除容易造成包损坏，除非确认没有包依赖它。

| 包名 | 说明 |
| --- | --- |
| `libatomic` | GCC 原子操作运行库。 |
| `libattr` | 扩展属性（xattr）运行库。 |
| `libavahi-client` | Avahi 客户端库。 |
| `libavahi-dbus-support` | Avahi 的 D-Bus 支持。 |
| `libblkid` | 块设备标识库（lsblk/blkid 用）。 |
| `libcap` | POSIX capabilities 库。 |
| `libcap-ng` | 简化版 capabilities 库。 |
| `libcomerr` | ext2fs 错误码库。 |
| `libcurl` | libcurl HTTP 传输库。 |
| `libdaemon` | 守护进程化辅助库。 |
| `libdbus` | D-Bus 消息总线库。 |
| `libe2p` | e2fsprogs 的参数解析库。 |
| `libevent2` | 事件循环库（ttyd 等依赖）。 |
| `libexpat` | XML 解析库。 |
| `libext2fs` | ext2/3/4 文件系统操作库。 |
| `libf2fs` | F2FS 文件系统操作库。 |
| `libfdisk` | util-linux 分区表操作库。 |
| `libgcc` | GCC 运行时库。 |
| `libgd` | 图形绘制库（流量图、验证码等）。 |
| `libgmp` | 大数运算库（加密算法依赖）。 |
| `libgnutls` | GnuTLS TLS 实现库。 |
| `libiptext` | iptables IPv4 扩展库。 |
| `libiptext6` | iptables IPv6 扩展库。 |
| `libiptext-nft` | iptables 的 nftables 兼容扩展库。 |
| `libiwinfo` | 无线信息查询库（信号、速率、信道）。 |
| `libiwinfo-data` | iwinfo 的硬件能力数据。 |
| `libjpeg-turbo` | JPEG 编解码库。 |
| `libjson-c` | JSON-C 库。 |
| `liblua` | Lua 5.1 运行库。 |
| `liblucihttp` | LuCI 的 HTTP 解析库。 |
| `liblucihttp-lua` | liblucihttp 的 Lua 绑定。 |
| `liblucihttp-ucode` | liblucihttp 的 ucode 绑定。 |
| `liblzo` | LZO 压缩库。 |
| `libminiupnpc` | UPnP 客户端库。 |
| `libmnl` | Netlink 最小封装库。 |
| `libmount` | 挂载操作库（util-linux）。 |
| `libnatpmp` | NAT-PMP 客户端库。 |
| `libncurses` | 终端界面（TUI）库。 |
| `libnetfilter-conntrack` | 连接跟踪用户态库。 |
| `libnetsnmp-nossl` | Net-SNMP 库（不带 TLS）。 |
| `libnettle` | Nettle 加密库。 |
| `libnfnetlink` | netfilter netlink 库。 |
| `libnftnl` | nftables 用户态库。 |
| `libnghttp2` | HTTP/2 库（curl 依赖）。 |
| `libnl-tiny` | 精简版 netlink 库（OpenWrt 专用）。 |
| `libopenssl` | OpenSSL 3 主库。 |
| `libopenssl-conf` | OpenSSL 配置文件支持。 |
| `libopenssl-legacy` | OpenSSL 旧算法提供者（MD4/RC4 等）。 |
| `libpci` | PCI 设备访问库（lspci）。 |
| `libpcre2` | Perl 兼容正则库。 |
| `libpng` | PNG 图像库。 |
| `libpopt` | 命令行选项解析库。 |
| `libpthread` | POSIX 线程库（musl 下为空壳）。 |
| `libreadline` | 命令行行编辑库（bash 用）。 |
| `librt` | POSIX 实时扩展库（musl 下为空壳）。 |
| `libseccomp` | seccomp 用户态库。 |
| `libsmartcols` | 表格输出库（lsblk/fdisk）。 |
| `libsqlite3` | SQLite 数据库库。 |
| `libss` | ext2fs 的子系统库。 |
| `libstdcpp` | GNU C++ 标准库。 |
| `libtasn1` | ASN.1 编解码库（GnuTLS 依赖）。 |
| `libtirpc` | TI-RPC 库（NFS 等依赖）。 |
| `libudebug` | OpenWrt 用户态调试库。 |
| `liburing` | io_uring 用户态库。 |
| `libustream-openssl` | ustream 的 OpenSSL 实现（HTTPS 下载）。 |
| `libuuid` | UUID 生成库。 |
| `libuv` | 异步 IO 事件库。 |
| `libwebp` | WebP 图像库。 |
| `libwebsockets-full` | 完整版 libwebsockets（WebSocket 服务）。 |
| `libxtables` | xtables 扩展库。 |
| `protobuf` | Google Protocol Buffers 运行库（netdata 等用）。 |
| `protobuf-lite` | 精简版 Protocol Buffers 运行库。 |

## 十八、Vantage 主题（本仓库新增）

来自第三方签名 apk 源，不在 ImmortalWrt 官方源里。

| 包名 | 说明 |
| --- | --- |
| `luci-theme-vantage` | Vantage 主题本体（本仓库默认主题）。 |
| `luci-app-vantage` | Vantage 主题的配套设置应用（状态卡片、快捷入口等）。 |
| `luci-i18n-vantage-theme-zh-cn` | Vantage 主题界面的简体中文。 |
| `luci-i18n-vantage-zh-cn` | Vantage 应用的简体中文。 |

## 附：维护建议

1. **先减后加**：这份清单是把现网 `/etc/apk/world` 原样搬过来的，里面有不少“当年装上但未必在用”的包（例如 `luci-theme-material`、`luci-theme-openwrt`、`kmod-tulip`、`kmod-pcnet32`、`kmod-net-selftests`）。删掉能明显缩小镜像、减少攻击面。
2. **别删基础包**：`busybox`、`procd`、`ubus`、`ubox`、`uci`、`netifd`、`fstools`、`firewall4`、`rpcd`、`uhttpd`、`dropbear`、`ca-bundle` 这些删了会直接起不来或进不去 LuCI。
3. **主题只留一个**：`luci-theme-*` 每多一个就多几 MB。当前默认 Vantage，其他四个主题可以按需注释。
4. **语言包按需**：`luci-i18n-*-zh-cn` 每个只有几十 KB，但 20 多个加起来也有 1 MB 左右；不用英文界面的话可以全留。
5. **改完一定看构建日志**：workflow 会把 25.12 里不存在的包自动剔除并打印 `Dropping missing package: xxx`，按提示清理 `config/packages.txt` 即可。
