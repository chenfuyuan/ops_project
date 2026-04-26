# 标准 Node 演进模式

在生成或重构 `app/business/<domain>/nodes/<unit>/` 时，使用这份模式判断 node 应保持轻量结构，还是演进为复杂 node 轻量 DDD 结构。

## 核心原则

node 的演进依据是业务/领域职责分化，而不是文件行数或技术实现细节。数字阈值只提示需要评估，不直接决定拆分方式。

## Level 1：轻量 node

适合：
- 1–2 个业务行为。
- 没有明确聚合根或复杂状态流转。
- 只依赖少量 port / repository。
- infrastructure 适配简单。

示例结构：

```text
nodes/<unit>/
├─ node.py
├─ service.py 或 facade.py
├─ dto.py
├─ entities.py
├─ rules.py
├─ ports.py
└─ infrastructure/
```

轻量 node 可以使用 `service.py`，但它只适合简单编排，不应持续吸收多个独立业务行为。

## Level 2：复杂 node 轻量 DDD

触发信号：
- 出现 3 个以上独立业务行为。
- 出现明确领域模型、聚合边界、状态流转或领域不变量。
- 出现多个 adapter 或外部协作。
- repository / port 开始围绕稳定领域资源展开。
- 多个方法堆在一个 service 中，且它们表达不同业务行为。

目标结构：

```text
nodes/<unit>/
├─ facade.py
├─ node.py
├─ application/
│  ├─ dto.py
│  └─ use_cases/
│     ├─ create_xxx.py
│     ├─ generate_xxx.py
│     └─ update_xxx.py
├─ domain/
│  ├─ models.py
│  ├─ rules.py
│  ├─ services.py
│  └─ repositories.py
└─ infrastructure/
   ├─ persistence/
   └─ <adapter-kind>/
```

职责：
- `facade.py`：稳定入口 + 横切协调，不写业务规则。
- `application/use_cases/`：一个业务行为一个 use case。
- `domain/`：模型、规则、领域服务、repository 抽象。
- `infrastructure/`：repository / AI / external adapter 实现。
- `node.py`：workflow state adapter，调用 facade。

## Level 3：domain-level bounded context

触发信号：
- 多个 node 共享同一批稳定领域模型。
- 多个 node 共享同一 repository 或领域服务。
- 某些规则不再属于单个 node，而属于整个业务域。

示例结构：

```text
business/<domain>/
├─ domain/
├─ application/
├─ nodes/
├─ infrastructure/
└─ workflow/
```

不要因为“未来可能复用”提前升级到 Level 3。只有共享概念已经稳定出现时才上移。

## 自检问题

- 我新增的是独立业务行为，还是已有行为的内部步骤？
- 当前 node 是否已经有明确聚合、状态流转或领域不变量？
- repository 表达的是领域资源/聚合，还是技术表/mapper？
- 如果继续写进原文件，未来读者是否还能按业务行为理解它？
- 如果多个 node 都需要这个模型或规则，它是否已经稳定到应上移到 domain-level？
