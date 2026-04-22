# Style Requirements Index

本页只维护 Phase 4 的需求索引、状态和依赖，不替代单需求卡片。

| Requirement | Summary | Status | Priority | Dependencies | Card |
| --- | --- | --- | --- | --- | --- |
| Style fingerprint | 形成可复用的风格基线与参考表达 | 待前置完成 | P1 | Phase 2 | [style-fingerprint](requirements/style-fingerprint.md) |
| Voice drift | 监测长篇生成过程中的风格漂移 | 待前置完成 | P1 | style-fingerprint | [voice-drift](requirements/voice-drift.md) |
| Anti-AI rules | 定义减少 AI 痕迹的约束与检查规则 | 待前置完成 | P1 | style-fingerprint | [anti-ai-rules](requirements/anti-ai-rules.md) |
| Style workbench | 提供查看、比较和调整风格能力的入口 | 待前置完成 | P2 | voice-drift, anti-ai-rules | [style-workbench](requirements/style-workbench.md) |
