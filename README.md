# 🔧 Hermes Agent 飞书富文本 Bug 修复

> 一键修复 Hermes Agent 的三个飞书富文本 Bug。独立 Skill，复制即用。

[![Skill Type](https://img.shields.io/badge/Hermes-Skill-8A2BE2)](https://hermes-agent.nousresearch.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)

---

## 🐛 修复的 Bug

| # | Bug | 现象 | 上游 PR |
|---|-----|------|---------|
| 1 | **Markdown 表格乱码** | Agent 回复中的表格在飞书显示为 `\| --- \|` 源码，完全不可读 | [#35781](https://github.com/NousResearch/hermes-agent/pull/35781) |
| 2 | **合并转发解析失败** | 飞书合并转发消息退化显示为 `[Merged forward message]` 占位符 | - |
| 3 | **user_status_change 日志轰炸** | Gateway 日志被 `processor not found` 错误刷爆 | - |

---

## 🚀 快速安装与使用

### 方式一：克隆到 skills 目录（推荐）

```bash
# 1. 克隆
cd ~/.hermes/skills
git clone https://github.com/YOUR_USERNAME/feishu-rich-text-fix.git

# 2. 一键应用修复
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/apply.py

# 3. 重启 Gateway（⚠️ 必须在 macOS 终端手动执行，不能通过 Hermes Agent 进程内操作）
hermes gateway restart
```

### 方式二：手动下载

```bash
# 下载 ZIP 解压到 ~/.hermes/skills/feishu-rich-text-fix/
# 然后执行：
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/apply.py
hermes gateway restart
```

### 方式三：Hermes Agent 自动加载

把 `SKILL.md` 所在目录放到 `~/.hermes/skills/` 下，Hermes Agent 启动时自动识别。之后只需告诉 Agent：

> "加载 feishu-rich-text-fix skill 然后应用修复"

---

## ✅ 验证修复

```bash
TARGET=$(ls -d /opt/homebrew/Cellar/hermes-agent/*/libexec/lib/python*/site-packages/gateway/platforms/feishu.py | tail -1)

# Fix 1: 表格是否走 interactive 卡片
grep -A3 "MARKDOWN_TABLE_RE" "$TARGET" | grep -q "interactive" && echo "✅ Fix 1" || echo "❌ Fix 1"

# Fix 2: 合并转发解析
grep -q "forward_messages" "$TARGET" && echo "✅ Fix 2" || echo "❌ Fix 2"

# Fix 3: user_status_change 拦截
grep -q "user_status_change" "$TARGET" && echo "✅ Fix 3" || echo "❌ Fix 3"
```

---

## 🔄 回滚

```bash
python3 ~/.hermes/skills/feishu-rich-text-fix/scripts/rollback.py
hermes gateway restart
```

每次 `apply.py` 运行都会自动创建 `.bak` 备份，回滚从备份恢复。

---

## ⚙️ 工作原理

**不做脆弱的行号 patch**。所有修复通过 **上下文精确匹配 + 文本替换** 实现，兼容 Hermes Agent v0.15 ~ v0.17+ 任意版本：

| Fix | 实施方式 |
|-----|---------|
| **#1 表格** | 检测到 Markdown 表格时，将 `msg_type` 从 `"text"` 改为 `"interactive"`，构造 Schema 2.0 卡片（`tag:markdown` 原生支持 CommonMark 表格） |
| **#2 转发** | 在 `_collect_forward_entries` 中增加 `forward_messages` 键名、`data.merge_forward_content` 嵌套路径解包、递归字典遍历兜底 |
| **#3 日志** | 在事件分发器 `build()` 链中为 `user_status_change` 注册空处理器（`lambda data: None`），静默丢弃无 UUID 的事件 |

---

## ⚠️ 注意事项

- **`brew upgrade hermes-agent` 会覆盖修复**，升级后需重新运行 `apply.py`
- **幂等安全**：重复运行不会出错，已打过的 patch 自动跳过
- 上游 PR 合并后此仓库可归档

---

## 📂 文件结构

```
feishu-rich-text-fix/
├── README.md           # 本文件
├── SKILL.md            # Hermes Skill 定义（Agent 可读取）
└── scripts/
    ├── apply.py        # 一键修复脚本
    └── rollback.py     # 回滚脚本
```

---

## 📄 License

MIT — 随意使用、修改、分发。
