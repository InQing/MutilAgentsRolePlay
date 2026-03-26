# 项目背景与详细架构文档

## 1. 文档用途

本文件是项目的长期主架构文档，目标是让后续接手本项目的人在阅读完本文件后，可以立即理解以下内容：

- 这个项目要解决什么问题
- 当前代码已经做到哪一步
- 系统按什么方式运行
- 每个模块的职责边界是什么
- 哪些能力已经实现，哪些能力只是预留
- 现在继续开发时应该从哪里下手

阅读顺序建议：

1. 先读本文件
2. 再读 `docs/project-progress.md`
3. 最后读 `docs/upcoming-work-plan.md`

如果要理解最早期的产品设计背景，再补读 `docs/v1-solution-and-blueprint.md`。

## 2. 项目定位

### 2.1 项目名称

- MutilAgentsRolePlay

### 2.2 产品目标

项目目标是开发一个“多 AI 角色扮演与社交模拟”产品。

核心体验不是单个 AI 与用户对话，而是：

- 多个 AI 角色生活在同一个世界中
- 它们会按自己的计划、社交倾向和当前状态自主行动
- 它们可以群聊、私聊、发朋友圈
- 用户既是世界成员，也具备导演视角
- 用户可以参与互动，也可以观察 AI 世界的演化

### 2.3 V1 产品范围

V1 明确限定为：

- Web 端
- 单用户单世界
- 6-10 个 AI 角色
- 核心玩法聚焦群像社交模拟
- AI 行动机制采用“定时计划 + 事件驱动”
- 导演模式采用“延迟全可见”

V1 暂不包含：

- 多真人共享世界
- 复杂商业化后台
- LangChain / LangGraph 深度接入
- 完整剧情系统
- 原始 chain-of-thought 对外暴露

## 3. 当前实现状态总览

截至当前阶段，项目已从“纯方案阶段”进入“后端核心闭环可运行、可测试”的状态。

### 3.1 已完成的内容

- Monorepo 结构已建立
- 前端基础页面已可运行
- 后端 FastAPI 基础服务已可运行
- world runtime 已具备基本时钟、调度、事件记录与状态持久化
- social 已具备群聊、私聊、朋友圈的基础消息落库能力
- 角色自治链路已打通：
  - 调度器触发任务
  - ThinkingEngine 做动作决策
  - 自治执行器执行动作
  - 动作写入会话与消息表
  - follow-up task 自动续排
- SQLite 轻量本地模式已跑通
- 后端本地测试已通过 17 项

### 3.2 尚未完成的内容

- 角色表达仍是模板化，不是真正的角色语言生成
- relationship 已具备最小持久化与行动驱动更新能力，但 relationship / plan / moment interaction 仍未完整成型
- director 面板已接入真实 API 数据，但延迟可见细则与导演控制仍未完整实现
- Redis 尚未进入真实调度链路
- WebSocket 实时广播尚未实现
- Docker/PostgreSQL/Redis 一致性联调尚未完成

### 3.3 当前阶段判断

当前阶段可以定义为：

- 本地核心闭环可运行
- 基础自治能力已可验证
- 可以继续进入功能增强
- 但在进入大规模功能扩展前，架构边界和测试基线必须继续保持

## 4. 技术栈与理由

### 4.1 前端

- Next.js
- TypeScript
- React
- Tailwind CSS

选择原因：

- 适合快速搭建 Web 产品原型
- 方便后续接入实时数据流和导演面板
- TypeScript 便于共享契约和稳定前后端接口

### 4.2 后端

- Python
- FastAPI
- Pydantic
- SQLAlchemy

选择原因：

- Python 更适合 Agent 运行逻辑与未来 LLM 集成
- FastAPI 适合快速实现结构化 API
- Pydantic 适合清晰建模 runtime、消息和决策结构
- SQLAlchemy 支撑后续从 SQLite 平滑过渡到 PostgreSQL

### 4.3 数据与基础设施

- SQLite：当前轻量本地测试模式
- PostgreSQL：目标主数据库
- Redis：目标事件队列 / 调度协作层
- Docker Compose：目标本地 / 服务器统一基础设施入口

### 4.4 当前环境策略

当前为了降低私人电脑资源占用，项目支持两种模式：

1. 轻量本地模式
- Python 3.12 + venv
- SQLite
- 本地启动 API
- 不依赖 Docker

2. 标准部署模式
- Docker Compose
- Web + API + PostgreSQL + Redis 容器化运行
- PostgreSQL
- Redis
- 对外主要暴露 Web，API 默认仅绑定服务器本机回环地址

目前真正跑通并经过测试的是轻量本地模式；云端 Docker Compose 已补齐 `web` 服务与服务间内网配置，但仍待真实服务器联调验证。

## 5. 仓库结构

### 5.1 顶层目录

```text
MutilAgentsRolePlay/
  apps/
    web/
  services/
    api/
  packages/
    shared-contracts/
  docs/
  scripts/
    local/
    integration/
```

### 5.2 目录职责

- `apps/web`
  - 前端 Web 应用
  - 当前包含首页和导演页的基础壳子
  - 暂未接入真实后端数据

- `services/api`
  - 后端主服务
  - 当前的主要开发重心
  - world runtime、social、agent runtime、持久化和 API 都在这里

- `packages/shared-contracts`
  - 前后端共享的 TypeScript 契约
  - 当前规模较小，未来可放公共 DTO / event contract

- `docs`
  - 产品、架构、进度、计划文档

- `scripts/local`
  - 低资源本地开发与测试脚本

- `scripts/integration`
  - 环境联调脚本

## 6. 后端模块架构

后端按领域拆分，不按技术杂糅拆分。

### 6.1 模块总览

- `api`
- `agent_runtime`
- `character`
- `director`
- `infra`
- `llm`
- `plan`
- `relationship`
- `social`
- `workflow`
- `world`

### 6.2 模块职责

#### `api`

职责：

- 对外暴露 HTTP 接口
- 做最薄的一层路由转发
- 不承载复杂业务

当前已实现路由：

- `/api/health`
- `/api/world/state`
- `/api/world/advance`
- `/api/director/panel`
- `/api/social/conversations`
- `/api/social/conversations/{id}/messages`
- `/api/social/private-messages`
- `/api/social/moments`

#### `world`

职责：

- 管理世界时钟
- 管理事件总线
- 管理调度器
- 管理世界状态快照
- 管理恢复和推进的基础行为

关键文件：

- `clock.py`
- `event_bus.py`
- `events.py`
- `scheduler.py`
- `service.py`
- `persistence.py`
- `models.py`

#### `agent_runtime`

职责：

- 定义角色动作决策结构
- 定义 ThinkingEngine 接口
- 执行自治动作
- 将角色决策与 social 写入连接起来

关键文件：

- `types.py`
- `executor.py`
- `thinking/base.py`
- `thinking/state_driven.py`

#### `social`

职责：

- 维护 conversation / message 的业务入口
- 提供群聊、私聊、朋友圈消息写入
- 负责私聊自动建会话、默认会话初始化
- 作为自治执行器的 social gateway

关键文件：

- `models.py`
- `service.py`
- `interfaces.py`

#### `director`

职责：

- 承载导演模式的数据结构与权限策略
- 聚合世界时钟、角色状态、关系快照、最近事件与会话预览，供导演面板读取
- 当前已接入真实面板数据读取，但延迟可见细则与导演控制仍未完整落地

关键文件：

- `models.py`
- `service.py`
- `policies/base.py`
- `policies/member_director_hybrid.py`

#### `infra`

职责：

- 数据库连接
- ORM 模型
- 初始化逻辑
- 仓储层
- Redis 接入位

关键文件：

- `db/session.py`
- `db/models.py`
- `db/repositories.py`
- `db/initializer.py`
- `cache/redis_client.py`

#### `llm`

职责：

- 定义模型客户端抽象
- 当前只有接口，尚未接真实供应商

#### `workflow`

职责：

- 预留复杂工作流编排接口
- 当前只有接口，尚未接真实实现

#### `character` / `plan` / `relationship`

职责：

- 提供核心领域模型
- `relationship` 已补齐最小服务层与数据库持久化闭环
- `plan` 当前主要用于数据结构与未来扩展
- 这些领域仍未形成完整规则系统

## 7. 运行时架构

### 7.1 核心对象

当前运行时最关键的对象有：

- `RuntimeRegistry`
- `WorldRuntimeService`
- `WorldPersistenceService`
- `SocialService`
- `AutonomousActionExecutor`
- `ThinkingEngine`

### 7.2 RuntimeRegistry

位置：

- `services/api/app/bootstrap.py`

职责：

- 统一创建后端运行所需的单例对象
- 管理设置、数据库、redis、world runtime、social service、autonomous executor

当前包含：

- `settings`
- `thinking_engine`
- `permission_policy`
- `database`
- `redis`
- `world_runtime`
- `world_persistence`
- `social_service`
- `autonomous_executor`

注意事项：

- 当前是全局单例
- 测试中通过 `reset_runtime_registry()` 做隔离
- 后续如果引入更复杂的生命周期控制，需要继续保持测试可重置性

### 7.3 WorldRuntimeService

职责：

- 保存当前世界的内存执行态
- 推进世界时间
- 取出到期任务
- 生成世界事件
- 提供角色与事件的访问入口
- 安排 follow-up task

当前仍是“内存执行 + 数据库存档”混合模式：

- 真正推进世界的是内存态 runtime
- 数据库用于初始化恢复和状态持久化

这是当前架构最重要的现实特征，后续开发必须理解这一点。

### 7.4 世界主链路

当前 `/api/world/advance` 的真实执行流为：

1. 读取 runtime registry
2. `world_runtime.advance(seconds=...)`
3. 时钟推进
4. 取出到期任务
5. 为到期任务写入 `schedule_triggered` event
6. `autonomous_executor.execute_due_tasks(...)`
7. ThinkingEngine 基于 `VisibleContext` 做决策
8. social service 执行群聊 / 私聊 / 朋友圈写入
9. runtime 写入 `action_executed` 或 `action_skipped` event
10. runtime 生成 follow-up task
11. `world_persistence.persist_runtime(...)`
12. 返回最新 world state

### 7.5 当前世界状态来源

`/api/world/state` 当前返回的数据来自：

- `clock`：runtime 内存态
- `active_characters`：runtime 内存态
- `recent_events`：runtime 事件仓储
- `pending_tasks`：runtime 调度器快照

所以它当前是“运行态视图”，不是数据库实时查询视图。

## 8. 数据模型与持久化

### 8.1 当前 ORM 表

当前已落地的数据库表包括：

- `worlds`
- `characters`
- `world_events`
- `scheduled_tasks`
- `conversations`
- `chat_messages`
- `relationships`

### 8.2 表职责

#### `worlds`

保存：

- 当前世界时间
- 世界速度
- 是否暂停

#### `characters`

保存：

- 角色 ID
- 展示名
- 当前计划摘要
- 当前情绪
- 社交欲望
- 打断阈值

#### `world_events`

保存：

- event id
- sequence_number
- world id
- kind
- summary
- created_at
- payload

说明：

- `sequence_number` 是为了解决恢复后事件顺序不稳定的问题
- 后续新增 event 时必须继续走统一 `record_event()` 入口

#### `scheduled_tasks`

保存：

- task id
- world id
- task type
- character id
- run_at
- payload
- priority

#### `conversations`

保存：

- 会话 id
- world id
- title
- conversation type
- participant_ids 等 meta

#### `chat_messages`

保存：

- message id
- world id
- conversation id
- conversation type
- sender id
- content
- created_at
- target id
- mentions

#### `relationships`

保存：

- relationship id
- world id
- source_character_id
- target_character_id
- affinity
- labels
- updated_at

### 8.3 当前持久化模式

当前数据库主要承担：

- 冷启动恢复
- 状态持久化
- 消息与会话存储

当前数据库尚未承担：

- 全部运行态实时计算
- 复杂查询
- 关系与计划系统存储

### 8.4 当前恢复机制

启动时：

1. 初始化数据库 schema
2. 查询 `worlds`
3. 如果不存在 world 记录：
   - 使用 sample world 初始化
   - 立刻持久化初始状态
4. 如果存在 world 记录：
   - 恢复 clock
   - 恢复角色
   - 恢复调度任务
   - 恢复最近事件
   - 确保默认 conversation 存在

## 9. 社交系统设计

### 9.1 当前支持的会话类型

- `group`
- `private`
- `moment`

### 9.2 默认会话

当前系统会自动确保两个默认会话存在：

- `conv-general`
- `conv-moments`

### 9.3 私聊会话

私聊会话不是预先写死，而是按参与者动态创建和复用。

规则：

- 同一世界下
- 同一组参与者
- 应复用同一个 private conversation

### 9.4 当前已实现的 social API

- `GET /api/social/conversations`
- `GET /api/social/conversations/{id}/messages`
- `POST /api/social/conversations/{id}/messages`
- `POST /api/social/private-messages`
- `POST /api/social/moments`

### 9.5 当前 social 限制

- 还没有评论 / 点赞
- 没有朋友圈可见性层次
- 没有消息已读/未读
- 没有更复杂的用户身份系统

## 10. 自治系统设计

### 10.1 当前 ThinkingEngine

当前默认实现是：

- `StateDrivenThinkingEngine`

它目前基于：

- `task_intent`
- 最近可见事件
- 角色 `social_drive`
- 角色 `interrupt_threshold`

做出以下动作之一：

- 群聊发言
- 私聊发言
- 朋友圈发言
- 忽略

### 10.2 当前自治执行器

`AutonomousActionExecutor` 的职责是：

- 接收到期任务
- 找到目标角色
- 构建可见上下文
- 调用 ThinkingEngine
- 调用 social gateway 执行动作
- 写入 action event
- 安排下一次 follow-up task

### 10.3 当前消息生成方式

当前消息文本不是 LLM 生成，而是模板化生成。

原因：

- 先打通闭环
- 先保证测试可预测
- 先验证架构稳定性

这意味着后续如果要接入真正角色表达生成，不应该直接改 runtime 主骨架，而应该替换或扩展表达生成层。

### 10.4 当前 follow-up task 策略

当前续排逻辑由上一次动作决定下一次意图和延迟时间。

示例：

- 群聊发言后，后续更倾向继续分享更新
- 朋友圈发言后，后续可能重新看群聊
- 私聊后，后续更倾向回到原计划

这是一套非常初级但可持续的自治节奏骨架。

## 11. 扩展点设计

### 11.1 ThinkingEngine

目标：

- 未来替换当前状态机驱动决策方式

可扩展方向：

- ReActThinkingEngine
- PlannerExecutorThinkingEngine
- MultiAgentThinkingEngine
- LangGraphThinkingEngine

替换原则：

- 业务层只依赖 `ActionDecision` 和 `DirectorExplanation`
- 不要让具体思维方式渗透进 route / social / world 模块

### 11.2 PermissionPolicy

目标：

- 未来扩展导演权限和用户角色体系

当前默认实现：

- `MemberDirectorHybridPolicy`

后续可扩展：

- 成员模式
- 导演模式
- 多级导演权限
- 多用户共享世界权限模型

### 11.3 WorkflowRunner

目标：

- 为未来复杂编排预留统一入口

当前状态：

- 只有接口
- 尚无实现

### 11.4 LLMClient

目标：

- 隔离具体模型供应商

当前状态：

- 只有接口
- 尚未接真实模型

## 12. 前端状态

### 12.1 当前页面

- 首页
- 群聊页
- 朋友圈页
- 导演页

### 12.2 当前能力

- 能运行
- 能展示项目方向和当前骨架
- 首页已可读取真实 world state，并提供前端“推进世界”入口
- 群聊页已可读取真实会话与消息，并支持向默认群聊发送消息
- 朋友圈页已可读取真实 moment 流，并支持发布新动态
- 导演页已可读取真实 director panel API，并展示角色快照、关系快照、事件日志与会话预览

### 12.3 当前限制

- 没有世界状态实时推送
- 还没有私聊可视化页面

## 13. 当前测试基线

### 13.1 当前已通过

轻量本地模式下已通过 17 项测试。

覆盖范围包括：

- health
- world runtime
- ThinkingEngine
- PermissionPolicy
- social model
- social service
- world API
- social API
- world 持久化恢复
- world 重启后一致性
- 多次 advance 稳定性

### 13.2 当前未完成

- Docker/PostgreSQL/Redis 联调
- follow-up task 更深层落库恢复一致性
- 自治消息产生后 API 可见性在更长时间运行中的稳定性
- WebSocket / director / relationship / plan / moment interaction 相关测试

### 13.3 当前测试结论

可以认为：

- SQLite 轻量模式下的核心闭环已基本稳定
- 当前架构可继续开发
- 但在进入生产化或服务器验证前，必须完成 Docker/PostgreSQL/Redis 联调

## 14. 已知架构风险

### 14.1 runtime 与数据库双态风险

当前运行态由内存驱动，数据库负责恢复与持久化。

风险：

- 如果后续某些写入只写数据库、不写 runtime
- 或只写 runtime、不写数据库
- 就会出现状态分叉

要求：

- 所有世界事件和调度更新必须明确经过统一入口

### 14.2 事件顺序风险

之前已经暴露过“created_at 相同导致恢复后顺序不稳定”的问题。

当前解决方案：

- 引入 `sequence_number`

要求：

- 以后新增 event 持久化逻辑时必须保持 sequence 正常递增

### 14.3 单例生命周期风险

当前 runtime registry 是全局单例。

风险：

- 测试状态串扰
- 长生命周期资源释放问题

当前解决方式：

- 测试中显式 reset + dispose

后续如引入更复杂后台任务，需要重新审视生命周期管理。

## 15. 新开发者接手建议

如果后续有人接手本项目，建议按以下顺序理解和进入开发：

1. 读本文件第 6 到第 10 节
2. 跑一遍 `scripts/local/run-backend-tests.ps1`
3. 看 `services/api/app/world/service.py`
4. 看 `services/api/app/agent_runtime/executor.py`
5. 看 `services/api/app/social/service.py`
6. 再看 `docs/upcoming-work-plan.md`

如果要继续后端功能，最优先不要随便改动：

- `WorldRuntimeService` 的主推进链路
- `record_event()` 的顺序语义
- `AutonomousActionExecutor` 的职责边界
- `SocialService` 作为自治动作网关的角色

## 16. 协作约定

- 任何影响架构边界、数据流或扩展点设计的改动，都必须同步更新本文件
- 任何进入新阶段的工作，都应同步更新 `docs/project-progress.md`
- 具体执行顺序和下一阶段任务，统一参考 `docs/upcoming-work-plan.md`
- 如果只是做一次性方案讨论，优先更新 `docs/v1-solution-and-blueprint.md`
