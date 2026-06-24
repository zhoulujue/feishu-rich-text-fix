#!/bin/bash
# 飞书富文本修复 — 一键安装脚本
# curl -sSL https://raw.githubusercontent.com/zhoulujue/feishu-rich-text-fix/main/setup.sh | bash

set -e

SKILL_DIR="$HOME/.hermes/skills/feishu-rich-text-fix"
REPO="https://github.com/zhoulujue/feishu-rich-text-fix.git"

echo "🔧 飞书富文本修复 — 一键安装"
echo ""

# 克隆/更新
if [ -d "$SKILL_DIR/.git" ]; then
    echo "📦 更新已有仓库..."
    cd "$SKILL_DIR" && git pull
else
    echo "📦 克隆仓库..."
    rm -rf "$SKILL_DIR"
    git clone "$REPO" "$SKILL_DIR"
fi

# 应用修复
echo ""
python3 "$SKILL_DIR/scripts/apply.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  最后一步：重启 Gateway（手动在终端执行）"
echo ""
echo "   hermes gateway restart"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
