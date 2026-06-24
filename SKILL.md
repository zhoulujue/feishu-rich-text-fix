---
name: feishu-rich-text-fix
version: 1.0.0
description: "一键修复 Hermes Agent 飞书三大富文本 Bug：Markdown表格乱码、合并转发解析失败、user_status_change 日志轰炸。独立可分发，张奇等同事可直接安装使用。"
metadata:
  requires:
    bins: ["python3"]
---

# 飞书富文本 Bug 一键修复 🔧

> **适用对象**：任何使用 Hermes Agent + 飞书的人。独立 skill，复制即用。

---

## 修复的 3 个 Bug

| # | Bug | 现象 |
|---|-----|------|
| 1 | **Markdown 表格乱码** | Agent 回复中的表格在飞书显示为 `| --- |` 源码，不可读 |
| 2 | **合并转发解析失败** | 转发消息退化显示为 `[Merged forward message]` 占位符 |
| 3 | **user_status_change 日志轰炸** | Gateway 日志被 `processor not found` 错误刷爆 |

---

## 快速开始（给使用者的指令）

```bash
# 1. 如果还没安装这个 skill，先加载
#    （在 Hermes 对话中让 Agent 执行即可）

# 2. 一键应用修复
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/apply.py

# 3. 重启 Gateway（必须！在 macOS 终端手动执行）
hermes gateway restart
```

---

## 工作原理

所有修复都通过 **上下文匹配 + 精确文本替换**（而非脆弱的行号 patch），兼容任意 Hermes 版本和 Python 版本：

- **Fix 1**：检测到 Markdown 表格 → 路由到 Schema 2.0 `interactive` 卡片，其 `tag:markdown` 原生支持 CommonMark 表格
- **Fix 2**：在合并转发解析函数中增加 `data.merge_forward_content` 嵌套路径提取 + 递归兜底探测
- **Fix 3**：在事件分发器中为 `user_status_change` 注册空处理器，静默拦截无 uuid 的事件

---

## 回滚

```bash
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/rollback.py
hermes gateway restart
```

每次运行 apply 都会自动备份原文件（`.bak`），回滚会从备份恢复。

---

## 验证修复是否生效

```bash
# Fix 1: 检查表格是否走 interactive 卡片
grep -A 3 "MARKDOWN_TABLE_RE" $(ls -d /opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py | tail -1) | grep -q "interactive" && echo "✅ Fix 1 OK" || echo "❌ Fix 1 MISSING"

# Fix 2: 检查合并转发解析
grep -q "forward_messages" $(ls -d /opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py | tail -1) && echo "✅ Fix 2 OK" || echo "❌ Fix 2 MISSING"

# Fix 3: 检查 user_status_change 拦截
grep -q "user_status_change" $(ls -d /opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py | tail -1) && echo "✅ Fix 3 OK" || echo "❌ Fix 3 MISSING"
```

---

## ⚠️ 注意事项

- **brew upgrade hermes-agent 后会覆盖修复**，升级后需重新运行 `apply.py`
- **每次 apply 都会自动备份**，回滚脚本从 `.bak` 恢复
- 上游 PR [#35781](https://github.com/NousResearch/hermes-agent/pull/35781) 和 [#18155](https://github.com/NousResearch/hermes-agent/pull/18155) 仍 Open，合并后此 skill 可废弃

---

## 给 Agent 的指令

当用户说"修复飞书bug"、"飞书表格乱码"、"打feishu patch"时：

1. 运行 `scripts/apply.py`
2. 告诉用户手动执行 `hermes gateway restart`
3. 不要尝试在进程内重启 gateway（会被防循环机制拦截）
