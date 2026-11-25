#!/usr/bin/env python3
"""修补 ImmortalWrt 源码里的镜像生成脚本。

用法：patch-sparse.py <immortalwrt 源码目录>

20 GiB 的 rootfs 分区如果按老办法 `dd if=/dev/zero` 填零，会在 runner 上真实
占用 20 GiB 磁盘，并让后续 gzip 慢到不可接受。这里把「写零填充」改成
`truncate` 稀疏扩展（逻辑大小不变），并把 gzip 从 -9 降到 -1（内容本身已是
压缩过的 squashfs，产物大小几乎不变）。
"""
import sys

PATCHES = [
    (
        "scripts/gen_image_generic.sh",
        '[ -n "$PADDING" ] && dd if=/dev/zero of="$OUTPUT" bs=512 seek="$ROOTFSOFFSET" conv=notrunc count="$ROOTFSSIZE"',
        '[ -n "$PADDING" ] && truncate -s $(( (ROOTFSOFFSET + ROOTFSSIZE) * 512 )) "$OUTPUT"',
    ),
    (
        "include/image.mk",
        "\tdd if=$(1) of=$(1).new bs=$(2) conv=sync\n\tmv $(1).new $(1)",
        "\tsz=$$(stat -c %s $(1)); bs=$(2); \\\n"
        "\tn=$$(( (sz + bs - 1) / bs )); [ \"$$n\" -gt 0 ] || n=1; \\\n"
        "\ttruncate -s $$(( n * bs )) $(1)",
    ),
    (
        "include/image-commands.mk",
        "$(STAGING_DIR_HOST)/bin/gzip -f -9n -c $@ $(1) > $@.new",
        "$(STAGING_DIR_HOST)/bin/gzip -f -1n -c $@ $(1) > $@.new",
    ),
]


def main():
    if len(sys.argv) != 2:
        sys.exit("用法: patch-sparse.py <immortalwrt 源码目录>")
    top = sys.argv[1].rstrip("/")

    for rel, old, new in PATCHES:
        path = "%s/%s" % (top, rel)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        if new in src:
            print("已修补，跳过：%s" % rel)
            continue
        if old not in src:
            sys.exit("::error::在 %s 中找不到待替换的片段，源码版本可能已变化" % rel)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(src.replace(old, new, 1))
        print("已修补：%s" % rel)


if __name__ == "__main__":
    main()
