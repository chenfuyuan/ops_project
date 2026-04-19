---
name: codex-pre-design-review
description: "直接调用 codex runtime 审查 OpenSpec 的 pre_design，并判断它是否已准备好进入后续 proposal/design/tasks 生成"
---

# Codex Pre-Design Review

通过直接调用 Codex runtime，审查一个已有的 OpenSpec `pre_design`。

该 skill 用于完整流程：
- 定位目标 `pre_design.md`
- 读取 OpenSpec `pre_design` 的审查标准
- 将 prompt 与目标目录路径直接交给 Codex runtime
- 明确要求 Codex 自己从指定目录读取所需文件
- 明确要求发给 Codex 的请求全文使用中文
- 明确要求 Codex 的审查结论与输出全文使用中文
- 将 Codex stdout 原样返回给用户

**输入**：`/codex-pre-design-review` 后面的参数可以是：
- 一个直接指向 `pre_design.md` 的文件路径
- 一个 OpenSpec change 目录路径
- `openspec/changes/` 下的 change 名称

<HARD-GATE>
此 skill 仅用于审查。
- 不要生成 `proposal.md`、`design.md` 或 `tasks.md`
- 不要实现代码
- 不要通过重写 `pre_design` 来代替审查
- 不要为了让文档通过而臆造缺失的需求
- 不要仅因为文档写得好就放宽结论
</HARD-GATE>

## 目录约定

本 skill 的相关文件放在同一目录下：
- `SKILL.md`：skill 说明
- `PROMPT.md`：传给 Codex 的审查提示模板

执行时，应将以下信息提供给 Codex runtime：
- 本 skill 目录路径
- `PROMPT.md` 路径
- 目标 `pre_design.md` 路径
- 审查标准 `.claude/commands/opsx/pre-design.md` 路径

并明确要求 Codex：
- 先自行读取 `PROMPT.md`
- 再根据 prompt 自行读取目标文件与审查标准文件
- 不要假设调用方已经内联任何文件全文

## 步骤

1. **解析目标制品**

   只接受一个目标。

   - 如果输入是以 `pre_design.md` 结尾的文件路径，直接使用它
   - 如果输入是一个 change 目录，则使用 `<dir>/pre_design.md`
   - 如果输入看起来像一个 change 名称，则解析为 `openspec/changes/<name>/pre_design.md`
   - 如果没有提供输入，询问用户要审查哪个 `pre_design`
   - 如果存在多个可能候选，不要猜测，应先询问
   - 如果文件不存在，停止并报告缺失路径

2. **读取审查依据**

   读取：
   - 目标 `pre_design.md`
   - `.claude/commands/opsx/pre-design.md`
   - 本 skill 的 `PROMPT.md`

   将 `.claude/commands/opsx/pre-design.md` 作为合法 `pre_design` 的事实标准。

3. **直接调用 Codex runtime**

   使用一次 `Bash` 调用执行：

   ```bash
   node "$HOME/.claude/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs" task "<自包含的中文审查请求>"
   ```

   不要依赖 `CLAUDE_PLUGIN_ROOT` 之类未必会被运行时注入的环境变量；优先使用已确认可用的 Codex 插件路径，并优先选择像 `$HOME` 这样可由 shell 稳定展开的写法。

   传给 Codex 的审查请求中必须包括：
   - skill 目录路径
   - prompt 文件路径
   - 目标文件路径
   - 审查标准文件路径
   - 期望的输出格式

   必须明确要求 Codex：
   - 自己读取上述文件
   - 按 `PROMPT.md` 中的规则执行审查
   - 传给 Codex 的请求全文必须使用中文
   - Codex 的最终输出全文必须使用中文
   - 只报告审查发现，不给出超出文档修订范围的实现建议

4. **将 Codex 输出原样返回给用户**

   - 直接返回 `codex-companion.mjs task` 的 stdout
   - 不要对结果做规范化、摘要、重写或补充说明
   - 不要在前后添加额外标题、解释或结论
   - 如果 Codex 已按 `PROMPT.md` 输出固定结构，直接原样展示

5. **审查结束即停止**

   不要继续进入任何其他 OpenSpec 命令。
   不要创建或编辑任何制品。

## 必须覆盖的审查维度

审查必须覆盖以下问题：

### 1. 问题定义
- 是否解释了真实问题？
- 是否解释了背景、触发因素和当前不足？
- 是否解释了为什么这项工作现在要做？

### 2. Goals / Non-goals
- 目标是否明确？
- 非目标是否明确？
- 范围是否稳定，还是隐藏了扩张空间？

### 3. 需求理解
- 是否体现了对需求的深度理解？
- 成功标准是否清晰？
- 业务边界 / 系统边界是否清晰？
- 关键假设是否被写明？

### 4. Constraints / Invariants
- 是否记录了硬约束？
- 是否记录了不可协商的不变条件？
- 是否澄清了容易被误读的边界？

### 5. 架构方向
- 是否存在清晰的推荐方向？
- 模块边界与职责是否清晰？
- 必须保持稳定的边界是否明确？

### 6. 关键决策 / Trade-offs
- 重要决策是否明确？
- 决策理由是否明确？
- 是否点名了被否决的替代方案？
- 是否仍有关键决策未解决？

### 7. 关键流程
- 关键业务 / 数据 / 控制流程是否描述充分？
- 是否遗漏了重要失败路径或异常路径？
- 如果这里不需要流程说明，是否已明确写出？

### 8. OpenSpec 映射
- 是否说明了 `proposal.md` 应表达什么？
- 是否说明了 `design.md` 应展开什么？
- 是否说明了 `tasks.md` 应拆解什么？
- 是否说明了下游制品绝不能臆造什么？

### 9. 生成护栏
- 是否说明了下游制品必须遵守什么？
- 是否说明了哪些内容可以在后续补充？
- 是否说明了哪些内容绝不能猜？
- 是否解释了未决项应如何处理？

### 10. 下游就绪度
- 不同工程师或模型是否都能基于它稳定生成下游 OpenSpec 制品？
- 下游生成是否会被迫猜测？
- 该文档是否过于模糊、过于偏实现，或者没有起到“中间约束输入”的作用？

## 回退行为

如果无法直接调用 Codex runtime，不要静默失败。
应输出：
- 应发送给 Codex 的完整审查请求
- 解析后的目标文件路径
- prompt 文件路径
- 一段简短说明，解释为什么无法自动委托

## Guardrails

- 目标文件存在歧义时绝不能猜
- 绝不能因为文档写得流畅就直接通过
- 绝不能把审查变成 brainstorming 或实现规划
- 绝不能添加源文档中没有的需求
- 审查必须始终聚焦于“该文档是否足以支撑下游 OpenSpec 生成”
