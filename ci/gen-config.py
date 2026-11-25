#!/usr/bin/env python3
"""生成 ImmortalWrt 源码构建用的 .config 种子。

用法：gen-config.py <仓库根目录>

数据来源：
  * config/packages.txt        —— 现网设备 /etc/apk/world 的包清单（`-包名` 表示显式移除）
  * docs/reference/profiles.json —— 官方 25.12.2 x86/64 的默认包与设备包（会一并纳入）

x86/64 的内核模块一律按 `=m`（独立 .ko）处理，其余包按 `=y`，
这样内核镜像不会因为把驱动编进内核而撑爆 16 MiB 的 kernel 分区，
也与现网设备（模块按需加载）保持一致。
"""
import json
import os
import sys


def load_packages(path):
    keep, drop = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-"):
                drop.append(line[1:].strip())
            else:
                keep.append(line)
    return keep, drop


def main():
    if len(sys.argv) != 2:
        sys.exit("用法: gen-config.py <仓库根目录>")
    root = os.path.abspath(sys.argv[1])

    keep, drop = load_packages(os.path.join(root, "config", "packages.txt"))
    with open(os.path.join(root, "docs", "reference", "profiles.json"), encoding="utf-8") as fh:
        prof = json.load(fh)
    defaults = list(prof["default_packages"])
    for p in prof["profiles"].values():
        defaults += list(p.get("device_packages", []))

    all_pkgs = sorted(set(keep) | set(defaults))

    out = [
        "# 由 ci/gen-config.py 生成，请勿手工修改（改 config/packages.txt 即可）",
        "",
        "# ---- 目标平台与 profile ----",
        "CONFIG_TARGET_x86=y",
        "CONFIG_TARGET_x86_64=y",
        "# CONFIG_TARGET_MULTI_PROFILE is not set",
        "CONFIG_TARGET_x86_64_DEVICE_generic=y",
        "",
        "# ---- 分区表：与现网设备一致（16 MiB kernel + 20 GiB rootfs）----",
        "CONFIG_TARGET_KERNEL_PARTSIZE=16",
        "CONFIG_TARGET_ROOTFS_PARTSIZE=20480",
        "",
        "# ---- 文件系统与镜像类型 ----",
        "CONFIG_TARGET_ROOTFS_SQUASHFS=y",
        "# CONFIG_TARGET_ROOTFS_EXT4FS is not set",
        "# CONFIG_ISO_IMAGES is not set",
        "# CONFIG_QCOW2_IMAGES is not set",
        "# CONFIG_VDI_IMAGES is not set",
        "# CONFIG_VMDK_IMAGES is not set",
        "# CONFIG_VHDX_IMAGES is not set",
        "",
        "# ---- 开发者选项：ccache + 包级构建日志（失败时用于定位）----",
        "CONFIG_DEVEL=y",
        "CONFIG_CCACHE=y",
        "CONFIG_BUILD_LOG=y",
        "",
        "# ---- 软件包（来自 config/packages.txt + 官方默认包）----",
    ]

    for name in all_pkgs:
        out.append("CONFIG_PACKAGE_%s=%s" % (name, "m" if name.startswith("kmod-") else "y"))
    for name in drop:
        out.append("# CONFIG_PACKAGE_%s is not set" % name)

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
