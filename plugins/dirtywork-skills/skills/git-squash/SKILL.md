---
name: git-squash
description: 当用户说「squash 提交」「把这些提交合成一个」「合并成一个提交」「整理当前分支的提交」「当前分支有哪些单独提交」「rebase 主分支」时调用。将当前分支（典型是 AI 任务生成的占位提交）相对基准分支的独立提交压缩为一个提交，用中文 message 写清楚实际改动，再 rebase 到最新主分支。不推送远端。
---

# `git-squash` Skill

把当前分支相对基准分支的多个提交（典型是 AI 任务生成的 `chore(agent)` 占位提交）压缩成一个，提交信息用中文写明白改动内容，并 rebase 到最新主分支。不推送远端。

## 工作流程

1. **确定基准分支**：默认用 `main`。若不存在或用 `master`，用 `git symbolic-ref refs/remotes/origin/HEAD`（去掉 `refs/remotes/origin/` 前缀）获取远端默认分支。用户指定了基准（如 `origin/main`、某个 commit）则照用。记作 `<base>`。

2. **查看独立提交**：运行 `git log <base>..HEAD --oneline`，列出当前分支单独有的提交。同时 `git status --short` 确认工作区是干净的——若有未提交改动，先停下告知用户（squash 前必须 `git commit`/`git stash` 处理，否则 `reset --soft` 会把它们混进暂存区）。

3. **读懂改动内容（写 message 的前提，不可跳过）**：
   - `git diff <base>...HEAD --stat` 看涉及文件与规模
   - 分目录看实际 diff（如 `-- src/`、`-- docs/`、`-- tests/`），理解这些改动在做什么、为什么改
   - 不要只看提交标题就写 message——已提交里常有没意义的占位信息（如 `chore(agent): uncommitted changes from task`），必须从 diff 还原真实改动。命名改动的场景，注意代码、文档、测试里同步的命名是否一致，message 要覆盖全链路。

4. **压缩提交**：`git reset --soft <base>`。所有分支独立提交合并为暂存改动，内容完全保留，只丢失提交历史。随后在暂存区用一次 `git commit` 创建新提交。多个提交里若包含空提交（无改动），`reset --soft` 只保留实际改动。

5. **写中文 message**：
   - 首行 `[<type>][<scope>] 中文简短说明`，type 用 fix/feat/refactor/docs/test 等，scope 用改动集中模块的中文短词（如 `[fix][cc]`）
   - 空一行，之后用 `- ` 开头的无序列表逐项列改动点：改了什么 + 为什么改，至少 2 条，不超过 5 条
   - 全部中文（代码符号、专有名词除外）；不要复述「合并了 N 个提交」这类过程话
   - 末尾追加当前会话要求的 `Co-Authored-By` 署名行

6. **验证**：
   - `git log <base>..HEAD --oneline`：应只剩 1 个新提交
   - `git status --short`：工作区干净
   - `git diff <base>...HEAD --stat`：统计应与第 3 步合并前一致（证明内容无损）

7. **Rebase 主分支**：
   - `git fetch origin` 拉取远端更新
   - 比较 `<base>` 与 `origin/<主分支>`：若远端有更新，先将本地主分支快进到最新（`git checkout <base> && git merge --ff-only origin/<主分支> && git checkout -`），再 `git rebase <base>`
   - 主分支无更新时直接说明「已基于最新主分支，无需 rebase」，不执行任何操作
   - 冲突：rebase 停下时向用户报告冲突文件清单，确认解决方式后再继续（`git add <file> && git rebase --continue`），不要擅自选择保留哪边

8. **汇报**：说明新提交 hash、message 首行、改动了什么、是否已 rebase 到最新主分支。检查 `git branch -vv`：
   - 分支无远端跟踪：告知用户未推送，是否推送由用户决定
   - 分支有远端跟踪：推送需要 `--force`，必须等用户明确确认后再执行

## 注意

- 不要用 `git rebase -i`：交互式编辑在自动化环境不可用，`reset --soft` + 一次 commit 等效且可预测
- 用户要求「只合并后 N 个提交」时，用 `git reset --soft HEAD~N` 代替 `<base>`，并在 commit 前确认前一个提交仍在
- 压缩前如果中间某几个提交想保留，先停下来问用户，不要擅自选择