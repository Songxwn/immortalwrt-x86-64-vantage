#!/usr/bin/env python3
"""校验 `make defconfig` 之后的 .config 是否符合预期。

用法：verify-config.py <仓库根目录> <.config 路径>

检查项：
  1. 目标平台 / profile / 分区表 / 镜像类型等关键开关
  2. config/packages.txt（含 `-包名`）+ 官方默认包是否都被解析进 .config
  3. 逐个列出被 Kconfig 丢弃（不存在 / 依赖不满足）的包
"""
import json
import os
import sys


def read_config(path):
    cfg, unset = {}, set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("# ") and line.endswith(" is not set"):
                unset.add(line[2:].split(" is not set")[0])
            elif "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip().strip('"')
    return cfg, unset


def main():
    if len(sys.argv) != 3:
        sys.exit("用法: verify-config.py <仓库根目录> <.config 路径>")
    root, cfg_path = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    cfg, unset = read_config(cfg_path)

    errors = []

    def want(key, value):
        got = cfg.get(key)
        if got != value:
            errors.append("%s 应为 %s，实际为 %s" % (key, value, got if got is not None else "(未设置)"))

    # 1) 关键开关
    want("CONFIG_TARGET_x86", "y")
    want("CONFIG_TARGET_x86_64", "y")
    for key in ("CONFIG_TARGET_x86_64_DEVICE_generic", "CONFIG_TARGET_x86_64_Generic"):
        if cfg.get(key) == "y":
            break
    else:
        errors.append("未选中 x86/64 generic profile（TARGET_x86_64_DEVICE_generic / TARGET_x86_64_Generic 均为空）")
    want("CONFIG_TARGET_KERNEL_PARTSIZE", "16")
    want("CONFIG_TARGET_ROOTFS_PARTSIZE", "20480")
    want("CONFIG_TARGET_ROOTFS_SQUASHFS", "y")
    for key, label in [
        ("CONFIG_TARGET_ROOTFS_EXT4FS", "ext4 rootfs"),
        ("CONFIG_ISO_IMAGES", "ISO"),
        ("CONFIG_QCOW2_IMAGES", "QCOW2"),
        ("CONFIG_VDI_IMAGES", "VDI"),
        ("CONFIG_VMDK_IMAGES", "VMDK"),
        ("CONFIG_VHDX_IMAGES", "VHDX"),
    ]:
        if cfg.get(key) == "y":
            errors.append("%s 不应开启（%s）" % (key, label))

    # 2) 包
    with open(os.path.join(root, "config", "packages.txt"), encoding="utf-8") as fh:
        keep, drop = [], []
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            (drop if line.startswith("-") else keep).append(line.lstrip("-").strip())
    with open(os.path.join(root, "docs", "reference", "profiles.json"), encoding="utf-8") as fh:
        prof = json.load(fh)
    defaults = list(prof["default_packages"])
    for p in prof["profiles"].values():
        defaults += list(p.get("device_packages", []))

    missing = []
    for name in sorted(set(keep) | set(defaults)):
        if cfg.get("CONFIG_PACKAGE_%s" % name) not in ("y", "m"):
            missing.append(name)

    total = len(set(keep) | set(defaults))
    selected = sum(1 for k, v in cfg.items() if k.startswith("CONFIG_PACKAGE_") and v in ("y", "m"))
    print("期望包 %d 个，已解析 %d 个；.config 中共选中 %d 个包" % (total, total - len(missing), selected))

    if missing:
        print("\n以下包未解析成功（Kconfig 中不存在或依赖不满足）：")
        for name in missing:
            print("  - %s" % name)
        errors.append("有 %d 个包未解析成功：%s" % (len(missing), ", ".join(missing)))

    if errors:
        print("\n::error::配置校验未通过：")
        for e in errors:
            print("  - %s" % e)
        sys.exit(1)
    print("配置校验通过")


if __name__ == "__main__":
    main()
