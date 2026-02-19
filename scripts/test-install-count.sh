#!/bin/bash
#
# 测试 skills.sh 安装量统计是否增长
# 每次安装前清理本地 skill 目录，确保触发全新安装 + 遥测上报
#
# 用法: bash scripts/test-install-count.sh [次数]  （默认 5 次）

set -e

COUNT=${1:-5}
REPO="hexiaochun/seedance2-api"
SKILL_NAME="seedance2-api"
WORK_DIR=$(mktemp -d)

echo "============================================"
echo " skills.sh 安装量测试"
echo " 仓库: $REPO"
echo " 计划安装: $COUNT 次"
echo " 临时目录: $WORK_DIR"
echo "============================================"
echo ""

for i in $(seq 1 $COUNT); do
    echo "--- [$i/$COUNT] 开始安装 ---"

    cd "$WORK_DIR"
    rm -rf .agents .cursor .claude .windsurf .trae .agent .iflow .kiro skills

    npx skills add "$REPO" --yes 2>&1 | tail -5

    echo "--- [$i/$COUNT] 完成 ---"
    echo ""
    sleep 2
done

rm -rf "$WORK_DIR"

echo "============================================"
echo " 全部完成！共安装 $COUNT 次"
echo ""
echo " 验证方法："
echo "   agentskill.sh: https://agentskill.sh/q/seedance2-api"
echo "   skills.sh:     https://skills.sh/?q=seedance2-api"
echo "============================================"
