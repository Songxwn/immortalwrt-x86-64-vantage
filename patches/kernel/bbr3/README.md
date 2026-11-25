# BBRv3 内核补丁（来自 OpenWrt PR #16414）

- 来源：<https://github.com/openwrt/openwrt/pull/16414>（作者 nasbdh9，Draft）
- 抓取时的 PR head commit：`94d8192c17b99ff5bc3975c00e2ed7079f6e5b89`
- 原路径：`target/linux/generic/hack-6.12/601-*.patch`
- 本仓库改名为 `900-*.patch`，确保在 ImmortalWrt 自带的 hack-6.12 补丁（最大编号 661）之后应用，编号顺序与原 PR 一致。

补丁顺序不可乱，`900-01` ~ `900-15` 是 BBRv3 依赖的 TCP CC API / rate_sample 前置改动，`900-16` 才是 `tcp_bbr.c` 升级到 v3，`900-17` ~ `900-19` 是后续小修。

上游内核（含 6.12.103）自带的 BBR 是 **BBRv1**；BBRv3 只有这套 out-of-tree 补丁，主线尚未合并。
