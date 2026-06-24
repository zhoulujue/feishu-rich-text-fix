#!/usr/bin/env python3
"""
飞书富文本 Bug 一键修复脚本
通过上下文精确匹配 + 文本替换，兼容任意 Hermes 版本

修复:
  1. Markdown 表格 → Schema 2.0 interactive 卡片
  2. 合并转发消息解析 → 支持 forward_messages / merge_forward_content / 递归兜底
  3. user_status_change 事件 → 静默拦截，消除日志轰炸
"""

import glob
import os
import shutil
import sys

# ── 自动定位 feishu.py ──────────────────────────────────────────

def find_feishu_py():
    """在 Homebrew Cellar 中搜索 feishu.py，返回最新版本路径"""
    patterns = [
        "/opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py",
        "/usr/local/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py",
    ]
    for pat in patterns:
        matches = sorted(glob.glob(pat))
        if matches:
            return matches[-1]  # 最新版本
    return None


def backup(target):
    bak = target + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(target, bak)
        print(f"📦 已备份: {bak}")


# ── Fix 1: Markdown 表格 → Schema 2.0 卡片 ─────────────────────

def apply_fix1(content):
    """检测到 Markdown 表格时，路由到 interactive Schema 2.0 卡片"""
    old = '''        if _MARKDOWN_TABLE_RE.search(content):
            text_payload = {"text": content}
            return "text", json.dumps(text_payload, ensure_ascii=False)'''

    new = '''        if _MARKDOWN_TABLE_RE.search(content):
            card = {
                "schema": "2.0",
                "config": {"wide_screen_mode": True},
                "body": {
                    "elements": [
                        {"tag": "markdown", "content": content}
                    ]
                }
            }
            return "interactive", json.dumps(card, ensure_ascii=False)'''

    if old not in content:
        # 可能已经打过 patch，或者格式不同
        if "interactive" in content and "schema" in content and "2.0" in content:
            print("   Fix 1: 已打过 patch，跳过")
            return content, True
        print("   Fix 1: ⚠️ 未找到匹配的代码块（可能版本不同），跳过")
        return content, False

    content = content.replace(old, new)

    # 同时更新注释
    old_comment = '''        # Feishu post-type 'md' elements do not render markdown tables; sending
        # table content as post causes the message to appear blank on the client.
        # Force plain text for anything that looks like a markdown table.'''
    new_comment = '''        # Feishu post-type 'md' elements do not render markdown tables.
        # Route table-containing content to Schema 2.0 interactive card
        # whose 'tag: markdown' element supports CommonMark tables natively.
        # Patch: feishu-rich-text-fix skill'''

    if old_comment in content:
        content = content.replace(old_comment, new_comment)

    print("   ✅ Fix 1: Markdown 表格 → Schema 2.0 卡片")
    return content, True


# ── Fix 2: 合并转发解析 ─────────────────────────────────────────

def apply_fix2(content):
    """增强合并转发消息解析：支持 forward_messages + merge_forward_content + 递归兜底"""
    old = '''    for key in ("messages", "items", "message_list", "records", "content"):
        value = payload.get(key)
        if isinstance(value, list):
            candidates.extend(value)'''

    if old not in content:
        if "forward_messages" in content:
            print("   Fix 2: 已打过 patch，跳过")
            return content, True
        print("   Fix 2: ⚠️ 未找到匹配的代码块，跳过")
        return content, False

    new = '''    for key in ("messages", "items", "message_list", "records", "content", "forward_messages"):
        value = payload.get(key)
        if isinstance(value, list):
            candidates.extend(value)
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("messages", "items", "message_list", "records", "content", "forward_messages"):
            value = data.get(key)
            if isinstance(value, list):
                candidates.extend(value)
        mfc = data.get("merge_forward_content")
        if isinstance(mfc, dict):
            for key in ("messages", "items", "message_list", "records", "content", "forward_messages"):
                value = mfc.get(key)
                if isinstance(value, list):
                    candidates.extend(value)
    if not candidates:
        def find_lists_of_dicts(node: Any, seen=None) -> List[List[Any]]:
            if seen is None:
                seen = set()
            node_id = id(node)
            if node_id in seen:
                return []
            seen.add(node_id)
            found = []
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, list):
                        if v and any(isinstance(x, dict) and any(sk in x for sk in ("message_id", "msg_id", "sender_name", "user_name", "sender", "content", "body")) for x in v):
                            found.append(v)
                    elif isinstance(v, dict):
                        found.extend(find_lists_of_dicts(v, seen))
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, dict):
                        found.extend(find_lists_of_dicts(item, seen))
            return found
        lists = find_lists_of_dicts(payload)
        for lst in lists:
            candidates.extend(lst)'''

    content = content.replace(old, new)
    print("   ✅ Fix 2: 合并转发解析增强")
    return content, True


# ── Fix 3: user_status_change 静默拦截 ─────────────────────────

def apply_fix3(content):
    """为 user_status_change 注册空处理器，消除日志轰炸"""
    # 匹配 vc.bot.meeting_invited_v1 注册后的 .build() 调用
    old = '''            .register_p2_customized_event(
                "vc.bot.meeting_invited_v1",
                self._on_meeting_invited_event,
            )
            .build()'''

    if old not in content:
        if "user_status_change" in content and "lambda" in content:
            print("   Fix 3: 已打过 patch，跳过")
            return content, True
        print("   Fix 3: ⚠️ 未找到匹配的代码块，跳过")
        return content, False

    new = '''            .register_p2_customized_event(
                "vc.bot.meeting_invited_v1",
                self._on_meeting_invited_event,
            )
            .register_p1_customized_event(
                "user_status_change",
                lambda data: None,
            )
            .register_p2_customized_event(
                "user_status_change",
                lambda data: None,
            )
            .build()'''

    content = content.replace(old, new)
    print("   ✅ Fix 3: user_status_change 静默拦截")
    return content, True


# ── 验证 ─────────────────────────────────────────────────────────

def verify(content):
    ok = 0
    if "interactive" in content and '"schema": "2.0"' in content:
        ok += 1
    else:
        print("   ⚠️ Fix 1 验证失败")
    if "forward_messages" in content:
        ok += 1
    else:
        print("   ⚠️ Fix 2 验证失败")
    if "user_status_change" in content:
        ok += 1
    else:
        print("   ⚠️ Fix 3 验证失败")
    return ok


# ── Main ─────────────────────────────────────────────────────────

def main():
    target = find_feishu_py()
    if not target:
        print("❌ 找不到 feishu.py。请确认 Hermes Agent 已通过 Homebrew 安装。")
        print("   路径格式: /opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py")
        sys.exit(1)

    print(f"🔍 目标文件: {target}")
    backup(target)

    with open(target, "r") as f:
        content = f.read()

    print("\n── 应用修复 ──")
    content, _ = apply_fix1(content)
    content, _ = apply_fix2(content)
    content, _ = apply_fix3(content)

    print("\n── 验证 ──")
    ok = verify(content)

    with open(target, "w") as f:
        f.write(content)

    print(f"\n{'✅' if ok == 3 else '⚠️'} 修复完成 ({ok}/3 个生效)")
    print(f"📝 目标: {target}")
    print(f"🔄 下一步: 在 macOS 终端手动执行 hermes gateway restart")


if __name__ == "__main__":
    main()
