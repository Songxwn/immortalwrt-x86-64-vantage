#!/usr/bin/env python3
"""校验 `make defconfig` 之后的 .config 是否符合预期。

用法：verify-config.py <仓库根目录> <.config 路径> [tmp/.packageinfo 路径]

检查项：
  1. 目标平台 / profile / 分区表 / 镜像类型等关键开关
  2. config/packages.txt（含 `-包名`）+ 官方默认包是否都被解析进 .config
  3. 未解析的包：若它只是某个已选中包 PROVIDES 的「虚拟名」（如 nftables 由
     nftables-json 提供），视为正常；否则视为致命错误。
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


def read_provides(path):
    """从 tmp/.packageinfo 里读出「虚拟名 -> 提供者集合」的映射。"""
    provides = {}
    if not path or not os.path.exists(path):
        return provides
    cur = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if line.startswith("Package:"):
                cur = line.split(":", 1)[1].strip()
            elif line.startswith("Provides:") and cur:
                for name in line.split(":", 1)[1].split():
                    name = name.strip("+-")
                    if name:
                        provides.setdefault(name, set()).add(cur)
    return provides


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("用法: verify-config.py <仓库根目录> <.config 路径> [tmp/.packageinfo]")
    root, cfg_path = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    pkginfo = os.path.abspath(sys.argv[3]) if len(sys.argv) == 4 else None
    cfg, unset = read_config(cfg_path)

    errors = []

    def want(key, value):
        got = cfg.get(key)
        if got != value:
            errors.append("%s 应为 %s，实际为 %s" % (key, value, got if got is not None else "(未设置)"))

    # 1) 关键开关
    want("CONFIG_TARGET_x86", "y")
    want("CONFIG_TARGET_x86_64", "y")
    if not any(cfg.get(k) == "y" for k in ("CONFIG_TARGET_x86_64_DEVICE_generic", "CONFIG_TARGET_x86_64_Generic")):
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

    selected = {k[len("CONFIG_PACKAGE_"):] for k, v in cfg.items()
                if k.startswith("CONFIG_PACKAGE_") and v in ("y", "m")}
    provides = read_provides(pkginfo)

    missing, provided = [], []
    for name in sorted(set(keep) | set(defaults)):
        if name in selected:
            continue
        providers = provides.get(name, set()) & selected
        if providers:
            provided.append((name, sorted(providers)[0]))
        else:
            missing.append(name)

    total = len(set(keep) | set(defaults))
    print("期望包 %d 个；已直接选中 %d 个，由其他包提供 %d 个；.config 中共选中 %d 个包"
          % (total, total - len(missing) - len(provided), len(provided), len(selected)))
    for name, provider in provided:
        print("  · %s 由 %s 提供（虚拟名，无需单独包）" % (name, provider))

    if missing:
        print("\n以下包未解析成功（Kconfig 中不存在 / 依赖不满足 / 无提供者）：")
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
