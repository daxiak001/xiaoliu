#!/bin/bash
# 小柳云端系统 - GitHub自动备份脚本

# 配置
REPO_DIR="/home/ubuntu/xiaoliu"
GITHUB_REPO="git@github.com:daxiak001/xiaoliu.git"
LOG_FILE="/home/ubuntu/xiaoliu/logs/github_backup.log"

# 进入仓库目录
cd "$REPO_DIR" || exit 1

# 记录日志函数
log() {
    echo "[$(date "+%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "开始GitHub备份任务"

# 确保有远程仓库
if ! git remote | grep -q "^origin$"; then
    log "添加远程仓库: $GITHUB_REPO"
    git remote add origin "$GITHUB_REPO"
fi

# 检查是否有变更
if [[ -z $(git status -s) ]]; then
    log "没有文件变更，跳过备份"
    exit 0
fi

# 添加所有变更
git add -A
log "已添加所有变更"

# 生成提交信息
CHANGED_FILES=$(git diff --cached --name-only | wc -l)
COMMIT_MSG="自动备份 $(date  +%Y-%m-%d %H:%M:%S)

变更文件数: $CHANGED_FILES
主机: $(hostname)
自动备份任务"

# 提交
git commit -m "$COMMIT_MSG"
log "已创建提交: $CHANGED_FILES 个文件变更"

# 推送到GitHub
if git push -u origin master 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ GitHub备份成功！"
    exit 0
else
    log "❌ GitHub备份失败，请检查网络和权限"
    exit 1
fi
