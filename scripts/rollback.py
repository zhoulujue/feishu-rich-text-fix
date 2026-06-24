#!/usr/bin/env python3
"""回滚 feishu-rich-text-fix 的所有修复，从 .bak 备份恢复"""

import glob
import os
import sys


def find_feishu_py():
    patterns = [
        "/opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py",
        "/usr/local/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py",
    ]
    for pat in patterns:
        matches = sorted(glob.glob(pat))
        if matches:
            return matches[-1]
    return None


def main():
    target = find_feishu_py()
    if not target:
        print("❌ 找不到 feishu.py")
        sys.exit(1)

    bak = target + ".bak"
    if not os.path.exists(bak):
        print("❌ 找不到备份文件: " + bak)
        print("   可能修复尚未应用，或备份已被删除。")
        sys.exit(1)

    print(f"🔍 目标: {target}")
    print(f"📦 从备份恢复: {bak}")

    with open(bak, "r") as f:
        content = f.read()

    with open(target, "w") as f:
        f.write(content)

    # 检查是否回滚成功（应该不再包含我们的修改）
    has_fix1 = "interactive" in content and '"schema": "2.0"' in content
    has_fix2 = "forward_messages" in content
    has_fix3 = "user_status_change" in content and "lambda" in content

    rolled_back = not has_fix1 or not has_fix2 or not has_fix3
    if rolled_back:
        print("✅ 已回滚到原始版本")
    else:
        print("⚠️ 备份文件似乎也包含了修复，回滚可能无效")

    print(f"🔄 下一步: 在 macOS 终端手动执行 hermes gateway restart")


if __name__ == "__main__":
    main()
