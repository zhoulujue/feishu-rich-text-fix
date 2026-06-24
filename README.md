# 🔧 Hermes Agent 飞书富文本 Bug 修复

> 一键修复 Hermes Agent 的三个飞书富文本 Bug。独立 Skill，复制即用。

[![Skill Type](https://img.shields.io/badge/Hermes-Skill-8A2BE2)](https://hermes-agent.nousresearch.com)

---

## 🐛 修复的 Bug

| # | Bug | 现象 | 上游 PR |
|---|-----|------|---------|
| 1 | **Markdown 表格乱码** | Agent 回复中的表格在飞书显示为 `\| --- \|` 源码，完全不可读 | [#35781](https://github.com/NousResearch/hermes-agent/pull/35781) |
| 2 | **合并转发解析失败** | 飞书合并转发消息退化显示为 `[Merged forward message]` 占位符 | - |
| 3 | **user_status_change 日志轰炸** | Gateway 日志被 `processor not found` 错误刷爆 | - |

---

## 🚀 安装方式

### 方式一：贴给 Hermes Agent（最省事 🤖）

**直接把下面这段话发给你的 Hermes Agent（飞书私聊 / 终端均可）：**

> 请帮我安装并应用飞书富文本修复 skill：
>
> 1. 克隆 https://github.com/zhoulujue/feishu-rich-text-fix.git 到 ~/.hermes/skills/feishu-rich-text-fix
> 2. 执行 python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/apply.py
> 3. 完成后提醒我在终端手动执行 **hermes gateway restart**

Agent 会自动完成克隆、打补丁，你只需要最后手动重启 Gateway（这一步 Agent 不能在进程内完成）。

### 方式二：Shell 一行命令（最快 ⚡）

```bash
curl -sSL https://raw.githubusercontent.com/zhoulujue/feishu-rich-text-fix/main/setup.sh | bash
```

然后手动执行：

```bash
hermes gateway restart
```

### 方式三：手动克隆

```bash
cd ~/.hermes/skills
git clone https://github.com/zhoulujue/feishu-rich-text-fix.git
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/apply.py
hermes gateway restart
```

---

## ✅ 验证修复

```bash
TARGET=$(ls -d /opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py | tail -1)

grep -A3 "MARKDOWN_TABLE_RE" "$TARGET" | grep -q "interactive" && echo "✅ Fix 1 表格" || echo "❌ Fix 1"
grep -q "forward_messages" "$TARGET" && echo "✅ Fix 2 转发" || echo "❌ Fix 2"
grep -q "user_status_change" "$TARGET" && echo "✅ Fix 3 日志" || echo "❌ Fix 3"
```

---

## 🔄 回滚

```bash
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/rollback.py
hermes gateway restart
```

每次 apply 自动创建 `.bak` 备份，回滚从备份恢复。

---

## ⚙️ 工作原理

**不做脆弱的行号 patch**。所有修复通过 **上下文精确匹配 + 文本替换** 实现，兼容 Hermes Agent v0.15 ~ v0.17+ 任意版本：

| Fix | 实施方式 |
|-----|---------|
| **#1 表格** | 检测到 Markdown 表格时，将 `msg_type` 从 `"text"` 路由到 `"interactive"` Schema 2.0 卡片 |
| **#2 转发** | 增加 `forward_messages` / `data.merge_forward_content` 嵌套解包 + 递归字典遍历兜底 |
| **#3 日志** | 为 `user_status_change` 注册空处理器，静默丢弃无 UUID 的事件 |

---

## ⚠️ 注意事项

- **`brew upgrade hermes-agent` 会覆盖修复**，升级后需重新运行 `apply.py`
- **幂等安全**：重复运行不会出错，已打过自动跳过
- 上游 PR 合并后此仓库可归档

---

## 📂 文件结构

```
feishu-rich-text-fix/
├── README.md           # 本文件
├── setup.sh            # Shell 一键安装
├── SKILL.md            # Hermes Skill 定义
└── scripts/
    ├── apply.py        # 修复脚本
    └── rollback.py     # 回滚脚本
```

---

## 📄 License

MIT — 随意使用、修改、分发。
