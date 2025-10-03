# 🔄 小柳云端Git提交指南

## 📍 Git仓库位置

**云端服务器路径**：
```
/home/ubuntu/xiaoliu/
```

**GitHub仓库地址**：
```
git@github.com:daxiak001/xiaoliu.git
```

---

## 🚀 快速提交（3种方式）

### 方式1: 通过SSH直接在服务器提交 ⭐ **推荐**

#### Windows PowerShell执行：

```powershell
# 连接到服务器并提交
ssh -i "f:\源码文档\设置\server_key" ubuntu@43.142.176.53 @"
cd /home/ubuntu/xiaoliu
git add .
git commit -m '更新小柳系统 - $(date +%Y-%m-%d)'
git push origin main
"@
```

#### 或者使用一键连接脚本：

```powershell
# 1. 先连接到服务器
f:\源码文档\设置\一键连接服务器.bat

# 2. 在SSH会话中执行
cd /home/ubuntu/xiaoliu
git add .
git commit -m "更新小柳系统 - $(date +%Y-%m-%d)"
git push origin main
```

---

### 方式2: 自动化提交脚本（已配置）

**服务器上已有自动备份**：
- 脚本位置：`/home/ubuntu/xiaoliu/backup_to_github.sh`
- 定时任务：每小时自动提交一次（Cron）

#### 手动触发立即备份：

```bash
# SSH连接后执行
ssh -i "f:\源码文档\设置\server_key" ubuntu@43.142.176.53

# 执行备份脚本
cd /home/ubuntu/xiaoliu
bash backup_to_github.sh
```

---

### 方式3: 本地克隆后提交（不推荐）

**为什么不推荐**：
- ❌ 容易造成版本冲突
- ❌ 需要手动同步
- ❌ 服务器和本地不一致

**如果确实需要**：

```bash
# 1. 克隆到本地
cd F:\源码文档\设置
git clone git@github.com:daxiak001/xiaoliu.git xiaoliu_local

# 2. 修改后提交
cd xiaoliu_local
git add .
git commit -m "本地修改"
git push origin main
```

---

## 📋 详细操作步骤

### 步骤1: 连接到服务器

**方法A: 使用一键连接脚本**
```
双击运行: f:\源码文档\设置\一键连接服务器.bat
```

**方法B: 手动SSH连接**
```powershell
ssh -i "f:\源码文档\设置\server_key" ubuntu@43.142.176.53
```

### 步骤2: 进入Git仓库目录

```bash
cd /home/ubuntu/xiaoliu
```

### 步骤3: 检查当前状态

```bash
# 查看修改的文件
git status

# 查看具体修改内容
git diff
```

### 步骤4: 添加文件到暂存区

```bash
# 添加所有修改的文件
git add .

# 或者只添加特定文件
git add skills/tools/xxx.py
git add memory/xxx.json
```

### 步骤5: 提交到本地仓库

```bash
# 提交并添加说明
git commit -m "更新说明"

# 示例：
git commit -m "添加新技能模块"
git commit -m "修复Bug: 修复XX问题"
git commit -m "优化性能: 提升XX性能"
```

### 步骤6: 推送到GitHub

```bash
git push origin main
```

---

## 🛠️ 常用Git命令

### 查看命令

```bash
# 查看提交历史
git log --oneline -10

# 查看远程仓库
git remote -v

# 查看分支
git branch -a

# 查看文件修改
git diff filename
```

### 撤销命令

```bash
# 撤销工作区修改（未add）
git checkout -- filename

# 撤销暂存区（已add，未commit）
git reset HEAD filename

# 撤销最后一次提交（保留修改）
git reset --soft HEAD^

# 撤销最后一次提交（不保留修改）
git reset --hard HEAD^
```

### 分支命令

```bash
# 创建新分支
git checkout -b new-feature

# 切换分支
git checkout main

# 合并分支
git merge new-feature
```

---

## 📝 提交信息规范

### 推荐格式

```
类型: 简短描述

详细描述（可选）
```

### 类型说明

```bash
# 新功能
git commit -m "feat: 添加用户认证模块"

# Bug修复
git commit -m "fix: 修复登录失败问题"

# 文档更新
git commit -m "docs: 更新API文档"

# 性能优化
git commit -m "perf: 优化数据库查询性能"

# 代码重构
git commit -m "refactor: 重构用户服务"

# 测试
git commit -m "test: 添加单元测试"

# 配置修改
git commit -m "chore: 更新配置文件"
```

---

## 🔧 一键提交脚本（Windows）

创建文件：`f:\源码文档\设置\提交小柳到GitHub.bat`

```batch
@echo off
echo ========================================
echo 小柳云端Git提交工具
echo ========================================
echo.

set /p commit_msg="请输入提交说明: "

echo.
echo 正在连接服务器并提交...
echo.

ssh -i "f:\源码文档\设置\server_key" ubuntu@43.142.176.53 "cd /home/ubuntu/xiaoliu && git add . && git commit -m '%commit_msg%' && git push origin main"

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo ✅ 提交成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ❌ 提交失败，请检查错误信息
    echo ========================================
)

echo.
pause
```

**使用方法**：
1. 双击运行脚本
2. 输入提交说明
3. 自动提交到GitHub

---

## 🔍 常见问题解决

### 问题1: Permission denied (publickey)

**原因**: SSH密钥认证失败

**解决**:
```bash
# 确认密钥文件权限
chmod 600 /path/to/server_key

# 或在Windows上
icacls "f:\源码文档\设置\server_key" /inheritance:r /grant:r "%USERNAME%:R"
```

### 问题2: 找不到Git仓库

**检查**:
```bash
# SSH连接后
cd /home/ubuntu/xiaoliu
ls -la .git
```

**如果没有.git目录**:
```bash
# 重新初始化
cd /home/ubuntu/xiaoliu
git init
git remote add origin git@github.com:daxiak001/xiaoliu.git
git branch -M main
git pull origin main
```

### 问题3: 推送被拒绝 (rejected)

**原因**: 远程仓库有新提交

**解决**:
```bash
# 先拉取远程更新
git pull origin main --rebase

# 解决冲突后
git add .
git rebase --continue

# 推送
git push origin main
```

### 问题4: 提交冲突

**解决**:
```bash
# 查看冲突文件
git status

# 编辑冲突文件，解决冲突标记
# <<<<<<< HEAD
# 你的修改
# =======
# 远程修改
# >>>>>>> origin/main

# 解决后
git add 冲突文件
git commit -m "解决冲突"
git push origin main
```

### 问题5: 密码过期

**GitHub已不支持密码认证**，必须使用SSH密钥

**检查SSH密钥**:
```bash
# 在服务器上
ssh -T git@github.com

# 应该看到:
# Hi daxiak001! You've successfully authenticated...
```

---

## 📊 Git仓库结构

```
/home/ubuntu/xiaoliu/
├─ .git/                    # Git仓库信息
├─ skills/                  # 技能模块
│   ├─ vision/             # 视觉能力
│   ├─ action/             # 执行能力
│   └─ tools/              # 工具集（你的升级模块在这里）
├─ memory/                  # 记忆系统
│   ├─ permanent_iron_rules.json
│   └─ pre_check_lists.json
├─ config/                  # 配置文件
│   └─ xiaoliu_config.json
├─ user_rules/             # 用户规则
│   └─ CURSOR_RULES.md
├─ www/                    # Web界面
│   └─ api/
│       └─ rules/
├─ backup_to_github.sh     # 自动备份脚本
└─ README.md               # 项目说明
```

**你的升级模块位置**:
```
/home/ubuntu/xiaoliu/skills/tools/
├─ code_deep_analyzer.py
├─ error_prevention_system.py
├─ cursor_token_optimizer.py
└─ ... (其他30个模块)
```

---

## 🔄 自动备份状态

### 查看自动备份配置

```bash
# SSH连接后
crontab -l

# 应该看到:
# 0 * * * * cd /home/ubuntu/xiaoliu && bash backup_to_github.sh >> /home/ubuntu/xiaoliu/backup.log 2>&1
```

### 查看备份日志

```bash
tail -f /home/ubuntu/xiaoliu/backup.log
```

### 手动触发备份

```bash
cd /home/ubuntu/xiaoliu
bash backup_to_github.sh
```

---

## 📞 快速联系方式

**在另一个Cursor窗口告诉对方**:

```markdown
嘿！需要提交小柳云端的Git？

【快速方法】
1. 打开: f:\源码文档\设置\一键连接服务器.bat
2. 登录后执行:
   cd /home/ubuntu/xiaoliu
   git add .
   git commit -m "你的提交说明"
   git push origin main

【详细文档】
查看: f:\源码文档\设置\小柳云端Git提交指南.md

【服务器信息】
- 地址: 43.142.176.53
- 用户: ubuntu
- 密钥: f:\源码文档\设置\server_key
- 仓库: /home/ubuntu/xiaoliu/

【自动备份】
每小时自动提交，也可以手动:
bash /home/ubuntu/xiaoliu/backup_to_github.sh
```

---

## ✅ 检查清单

提交前检查：
- [ ] 已连接到服务器
- [ ] 在正确目录 `/home/ubuntu/xiaoliu/`
- [ ] 检查了修改的文件 `git status`
- [ ] 添加了文件 `git add .`
- [ ] 写了清晰的提交说明
- [ ] 成功推送 `git push origin main`

---

## 🎯 总结

**最简单的方法**:
```bash
# 1. 连接服务器
ssh -i "f:\源码文档\设置\server_key" ubuntu@43.142.176.53

# 2. 一键提交
cd /home/ubuntu/xiaoliu && git add . && git commit -m "更新" && git push
```

**完整流程**:
1. SSH连接
2. `cd /home/ubuntu/xiaoliu`
3. `git status` (查看)
4. `git add .` (添加)
5. `git commit -m "说明"` (提交)
6. `git push origin main` (推送)

**记住**: Git仓库在**服务器上**，不在本地！

---

**如有问题，随时问我！** 🚀

