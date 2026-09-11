---
name: focus-task
description: Turn a vague or sprawling task into one focused execution card with a clear finish line, scope, exclusions, and check time. Use when the user invokes $focus-task or wants to reduce context switching and finish one task.
---

# Focus Task

Convert the user's request into this compact card:

```text
当前主任务：
完成条件：
本轮只改：
不顺手处理：
下次检查时间：
```

- Keep one main task. Allow at most one background task that does not require attention.
- Infer reasonable details from the request and current workspace; ask only when a missing choice would materially change the result.
- Make the finish line observable: a file, output, test, commit, or visible application state.
- Put unrelated discoveries in one `稍后：` line instead of switching tasks.
- For delegated work, add only `目标 / 范围 / 禁止 / 验收`.
- If the user asked to execute, continue with the work after showing the card. If they only asked to organize, stop after the card.
