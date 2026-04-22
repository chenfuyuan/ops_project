---
name: business-workflow-node-centered-architecture
created: 2026-04-20
status: draft
---

# 业务线 + Workflow + Node-Centered DDD 架构设计

## 文档角色

本文档属于**总纲专题**，用于补充业务线 / workflow / node-centered 的架构组织方向。

使用方式：
- 从总纲入口页按需进入
- 作为系统结构演进的补充架构参考
- 不替代 phase overview、总纲入口或单个专题文档的职责

## 1. 背景

当前项目最初采用的是“模块化单体 + 模块内分层”的思路：`novel / outline / blueprint / chapter / memory / llm` 等模块各自拆分 `api / application / domain / infrastructure`。

随着主流程设计逐渐清晰，系统的核心不再只是“有哪些模块”，而是：

- 业务线有自己的主流程
- 主流程由多个流程节点组成
- 每个流程节点内部会协同多个组件
- 共享能力不应绑定在某个业务线或某个节点下

因此，架构需要从“模块视角”进一步演进为“业务线主流程 + 节点执行 + 共享能力”的组织方式。

## 2. 设计目标

本次架构调整的目标是：

1. 让**业务线主流程**成为一等公民，而不是分散在多个 service 中
2. 让 **LangGraph** 只负责主流程节点编排，不吞掉业务实现
3. 让每个流程节点成为可独立理解、测试、演化的业务单元
4. 让共享能力（如 AI 网关、知识库、爬虫）从业务节点中抽离出来，形成横向复用能力
5. 保持 DDD 分层边界，避免流程编排、业务规则、基础设施混杂

## 3. 顶层设计原则

### 3.1 顶层按“业务线 + 能力域”组织

顶层不再以通用 `modules/` 作为唯一组织方式，而是拆成两类：

- `business/`：业务线，如小说、漫剧、未来其他内容产品线
- `capabilities/`：横向共享能力，如 AI 网关、知识库、爬虫

这样可以清晰区分：

- 哪些目录代表面向用户的业务线
- 哪些目录代表多个业务线共享的支撑能力

### 3.2 流程优先，模块次之

在小说业务线内，系统的核心组织对象不是单纯的 CRUD 模块，而是：

- 主流程状态机
- 主流程中的节点
- 节点所调用的组件与共享能力

因此，小说业务线内部采用：

- `workflow/`：主流程图与状态管理
- `nodes/`：每个节点一个独立包

### 3.3 Node 是 Graph Runtime 的适配入口，不是业务本体

LangGraph 中的 node 不等于整个 application 层。

更准确地说：

- `workflow/graph.py` 决定“下一步去哪个节点”
- `nodes/<node>/presentation/node.py` 负责接 Graph state、调用应用服务、写回结果
- `nodes/<node>/application/` 负责真正的用例编排
- `nodes/<node>/domain/` 负责规则和模型
- `nodes/<node>/infrastructure/` 负责持久化和外部适配

因此，node 更接近 **Presentation / Interface Adapter** 层中的“图节点适配器”，而不是整个应用层本身。

### 3.4 共享能力不挂在业务线名下

如果一个能力会被多个业务线、多个节点、多个入口复用，就不应放在某个业务线目录下。

例如：

- `ai_gateway`：统一模型路由与提供商适配
- `knowledge`：检索、召回、上下文构建、知识组织
- `crawl`：外部内容采集

这些都应放在 `capabilities/` 下。

## 4. 三层执行模型

本架构把系统执行拆成三层：

### 第一层：业务线主流程状态机

单位是**流程节点**。

负责：

- 定义业务线主流程阶段
- 控制节点流转
- 校验节点准入条件
- 管理全局状态与进度
- 处理回退、重试、挂起等流程控制

例如小说业务线主流程：

- 立项
- 世界观构建
- 角色设定
- 宏观规划
- 蓝图生成
- 章节生成
- 审计

这一层建议使用 **LangGraph** 实现。

### 第二层：流程内部编排

单位是**组件**。

负责：

- 定义某个节点内部如何协同多个组件完成任务
- 把节点级输入拆给各组件
- 聚合组件输出，形成节点结果

例如“章节生成”节点内部：

- 读取蓝图
- 获取知识上下文
- 调用 AI 网关生成正文
- 保存章节
- 触发状态提取与审计

### 第三层：组件内部编排

单位是**组件内部步骤 / 子能力**。

负责：

- 组织某个组件自己的内部实现顺序
- 调用子组件或外部系统
- 返回稳定的组件输出

例如：

- `knowledge`：检索 → 去重 → 裁剪 → 组装上下文
- `ai_gateway`：选 profile → 选 provider → 调用 → 统一解析

## 5. 推荐目录结构

```text
app/
  business/
    novel/
      workflow/
        graph.py
        state.py
        registry.py
        edges.py

      nodes/
        project_init/
          presentation/
            node.py
            dto.py
          application/
            service.py
            orchestrator.py
          domain/
            entities.py
            value_objects.py
            rules.py
          infrastructure/
            repository.py
            persistence.py

        world_building/
          presentation/
          application/
          domain/
          infrastructure/

        character_design/
          presentation/
          application/
          domain/
          infrastructure/

        macro_planning/
          presentation/
          application/
          domain/
          infrastructure/

        blueprint_generation/
          presentation/
          application/
          domain/
          infrastructure/

        chapter_generation/
          presentation/
            node.py
          application/
            service.py
            orchestrator.py
          domain/
            entities.py
            rules.py
          infrastructure/
            repository.py

        audit/
          presentation/
          application/
          domain/
          infrastructure/

    video/
      workflow/
      nodes/

  capabilities/
    ai_gateway/
      api/
      application/
      domain/
      infrastructure/

    knowledge/
      api/
      application/
      domain/
      infrastructure/

    crawl/
      api/
      application/
      domain/
      infrastructure/

  interfaces/
    http/

  shared/
    kernel/
    infra/
    events/

  bootstrap/
```

## 6. 各层职责说明

### 6.1 `business/<line>/workflow/`

职责：

- 定义 LangGraph graph
- 定义 graph state
- 注册 node
- 定义 edge 和路由规则

约束：

- 不直接拼 prompt
- 不直接查数据库
- 不直接调用 provider SDK
- 不承载业务实现细节

一句话：**这里只管流程图，不管业务细节。**

### 6.2 `business/<line>/nodes/<node>/presentation/`

职责：

- 作为 graph node 入口
- 从 graph state 读取输入
- 调用 application service
- 处理节点级输入输出转换
- 把结果写回 graph state

约束：

- 不承载核心业务规则
- 不承载复杂组件协同

一句话：**这是 Graph Runtime 的适配层。**

### 6.3 `business/<line>/nodes/<node>/application/`

职责：

- 实现节点用例
- 协调本节点依赖的业务组件与共享能力
- 组织节点内部执行顺序
- 聚合节点输出

约束：

- 不写底层 SDK 调用细节
- 不把规则全塞进 service

一句话：**这里是节点内部真正的流程编排层。**

### 6.4 `business/<line>/nodes/<node>/domain/`

职责：

- 定义本节点相关的实体、值对象、业务规则
- 表达哪些状态流转合法、哪些约束必须满足

例如：

- 是否允许从当前阶段进入章节生成
- 蓝图是否满足生成条件
- 审计结果是否允许流转到下一个节点

一句话：**这里回答“什么是合法的业务行为”。**

### 6.5 `business/<line>/nodes/<node>/infrastructure/`

职责：

- 持久化实现
- 外部系统适配
- ORM / Repository / 文件存储等实现细节

一句话：**这里放技术细节，不放业务决策。**

### 6.6 `capabilities/<capability>/`

职责：

- 提供跨业务线复用的横向能力
- 向业务节点暴露稳定接口
- 自己内部保持分层

例如：

#### `ai_gateway`
- 模型 profile 管理
- provider 路由
- 流式调用统一封装
- 结构化输出解析

#### `knowledge`
- 检索与召回
- 上下文构建
- 知识组织
- 未来可扩展到知识图谱

#### `crawl`
- 采集外部文本/站点内容
- 清洗与导入知识系统

## 7. 典型调用链示例

以“生成章节”为例：

```text
business/novel/workflow/graph.py
  -> business/novel/nodes/chapter_generation/presentation/node.py
    -> business/novel/nodes/chapter_generation/application/service.py
      -> capabilities/knowledge/application/...
      -> capabilities/ai_gateway/application/...
      -> business/novel/nodes/chapter_generation/domain/...
      -> business/novel/nodes/chapter_generation/infrastructure/...
```

职责分解：

1. `graph.py` 决定流程进入 `chapter_generation` 节点
2. `presentation/node.py` 从 graph state 读取 `novel_id`、`chapter_num` 等输入
3. `application/service.py` 协调蓝图、知识上下文、AI 生成、章节保存
4. `domain/` 负责章节生成相关约束与规则
5. `infrastructure/` 负责持久化与外部依赖调用

## 8. 与旧的 modules 思路如何衔接

旧结构中，`outline / blueprint / chapter / memory / llm` 都被视为同层模块。

新结构下，建议这样重组：

### 8.1 业务节点侧

原本的：

- `outline`
- `blueprint`
- `chapter`

如果它们体现的是小说主流程中的阶段或节点，则优先体现在：

- `business/novel/nodes/world_building/`
- `business/novel/nodes/macro_planning/`
- `business/novel/nodes/blueprint_generation/`
- `business/novel/nodes/chapter_generation/`
- `business/novel/nodes/audit/`

### 8.2 横向能力侧

原本的：

- `llm`
- `memory`

如果它们会被多个节点乃至多个业务线复用，则应抽成：

- `capabilities/ai_gateway/`
- `capabilities/knowledge/`

其中：

- `llm` 更适合重命名为 `ai_gateway`
- `memory` 若未来承担检索、召回、知识组织、知识图谱等职责，更适合收敛到 `knowledge`

### 8.3 shared 仍保持克制

`shared/` 只放真正无业务语义的能力，例如：

- `kernel`
- `infra`
- `events`

不要把业务能力误塞进 `shared/`。

## 9. 命名约定

推荐命名原则：

- `business/`：业务线
- `workflow/`：LangGraph 主流程编排
- `nodes/`：流程节点实现
- `presentation/`：graph runtime 适配入口
- `application/`：节点用例编排
- `domain/`：业务规则与模型
- `infrastructure/`：技术实现
- `capabilities/`：横向共享能力

避免：

- 把所有东西都叫 `service`
- 把所有流程都叫 `engine`
- 把共享能力挂在某个业务线名下

## 10. 落地建议

### 10.1 第一阶段先只落最小骨架

不需要一次性把所有 node 都拆满 4 层。

建议优先实现：

- `business/novel/workflow/`
- `business/novel/nodes/project_init/`
- `business/novel/nodes/macro_planning/`
- `business/novel/nodes/chapter_generation/`
- `capabilities/ai_gateway/`
- `capabilities/knowledge/`

### 10.2 简单节点不要过度分层

如果某个节点逻辑简单，可以先只保留：

```text
<pnode>/
  presentation/
    node.py
  application/
    service.py
```

只有复杂度上来后，再补 `domain/` 与 `infrastructure/`。

### 10.3 先把边界定清，再逐步迁移

本次架构设计更适合作为**目标架构**。

如果当前已有基于 `modules/` 的实现，可以逐步迁移：

1. 先引入 `business/novel/workflow/` 和少量关键 node
2. 把最核心的共享能力抽到 `capabilities/`
3. 旧模块保留一段时间作为过渡
4. 最终让主流程驱动业务，而不是模块之间松散调用

## 11. 最终结论

本项目推荐采用：

**业务线（business） + 主流程工作流（workflow） + 节点中心实现（node-centered DDD） + 横向共享能力（capabilities）**

其核心分工是：

- `workflow` 管**节点流转**
- `node` 管**节点执行入口**
- `application` 管**节点内部编排**
- `domain` 管**业务规则**
- `infrastructure` 管**技术实现**
- `capabilities` 管**横向共享能力**

一句话总结：

**让业务线主流程成为骨架，让节点成为业务单元，让共享能力成为横向底座。**
