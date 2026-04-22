# 去 AI 化规则

## Goal

建立减少 AI 痕迹的规则边界，让系统在生成过程中更主动地避免疲劳表达、套路句式和明显机器感。

## User Value

作品输出更接近作者希望的文学表达，减少读者一眼就能看出的“AI 味”。

## Success Criteria

- 需求明确表达需要被约束的表达风险类型。
- 后续流程可以把这些规则作为持续可用的质量要求。
- 卡片不提前定义规则库格式、评分实现或重写算法。

## Scope

- 疲劳词、禁用句式和明显 AI 痕迹的约束需求
- 规则对生成结果的约束和反馈边界
- 与风格检测和工作台的协同关系

## Non-goals

- 具体词表内容
- 规则执行引擎实现
- 模型后处理算法

## Dependencies / Prerequisites

- [style-fingerprint](style-fingerprint.md)

## Notes

- 这张卡片聚焦约束边界，不承担完整风格系统设计。
- 历史参考：[`phase4-style/03-anti-ai-rules.md`](../../../../archive/project_plan-pre-phase-first/phase4-style/03-anti-ai-rules.md)
