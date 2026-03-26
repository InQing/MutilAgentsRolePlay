# V1 方案与开发蓝图

## 1. 产品目标

V1 的目标是构建一个 Web 端多 AI 角色扮演与社交模拟产品。世界中有 6-10 个 AI 角色，它们拥有各自人设、关系、计划、情绪和记忆，能够在群聊、私聊、朋友圈中持续互动。用户既是世界中的普通成员，也拥有增强版导演权限，可以观察、查看记录并做轻度干预。

V1 首先验证的是“AI 能否像一群正在生活的人一样持续互动，并且用户能自然参与其中”，不追求一次性做成完整商业化产品。

## 2. V1 产品范围

### 2.1 核心能力

- AI 角色按计划行动，并根据事件做出响应
- AI 可发群聊、私聊、朋友圈，可点赞与评论
- AI 可根据互动结果调整情绪、关系和计划
- 用户可参与聊天、私聊和朋友圈互动
- 用户可通过导演模式查看世界状态与历史记录
- 用户可注入轻量事件，并控制世界节奏

### 2.2 导演模式

导演模式采用“延迟全可见”设计。

- 群聊与朋友圈默认实时可见
- 私聊、计划细节、关系变化与内部状态默认延迟可见
- 用户可以查看 AI 聊天记录
- 系统提供导演可读解释，说明 AI 为什么做出某个动作
- 不展示模型原始思维链

### 2.3 V1 不做

- 多真人共享世界
- 复杂账号体系
- LangChain / LangGraph 深度接入
- 向量数据库作为必选依赖
- 完整剧情系统与任务系统
- 对用户开放原始 chain-of-thought

## 3. 技术栈

- 前端：Next.js + TypeScript + React + Tailwind CSS
- 后端：Python + FastAPI
- 实时通信：WebSocket
- 数据库：PostgreSQL
- 缓存与调度辅助：Redis
- LLM 接入：通过统一 LLMClient 封装模型 SDK

选择原则：

- 前端强调实时交互和快速迭代
- 后端强调 Agent 编排、调度与状态建模
- 不在 V1 引入额外复杂框架，但要为后续升级保留空间

## 4. 核心运行模型

### 4.1 世界运行方式

世界由“定时计划 + 事件驱动”共同推动。

- 定时计划：角色按日程行动，如上课、吃饭、发动态、找人聊天
- 事件驱动：角色看到消息、被提及、朋友圈互动或导演事件后判断是否响应

### 4.2 角色主循环

角色的标准执行循环为：

1. Observe：读取当前可见上下文
2. Interpret：将事件与上下文转成结构化内部状态
3. Decide：判断是否行动、行动类型、行动目标、是否调整计划
4. Act：执行群聊、私聊、发动态、评论、点赞、改计划等动作
5. Reflect：更新记忆、情绪、关系和计划摘要

### 4.3 关键设计原则

- 角色只能读取自己“应该知道”的信息
- 系统规则负责世界边界和节奏
- 模型负责生成决策与表达，而不是接管全部业务逻辑
- 增强推理仅在关键场景触发，例如重大冲突、计划冲突、导演事件、大幅关系变化

## 5. 扩展性设计

### 5.1 AI 思维方式扩展点

AI 思维方式必须抽象为独立接口，不与具体实现绑定。

建议接口名称：

- ThinkingEngine

V1 默认实现：

- StateDrivenThinkingEngine

后续可扩展实现：

- ReActThinkingEngine
- PlannerExecutorThinkingEngine
- MultiAgentThinkingEngine
- LangGraphThinkingEngine

所有实现统一输出：

- ActionDecision
- DirectorExplanation
- PlanAdjustmentSuggestion

这样业务层只依赖统一契约，不依赖某一种“思维方式”。

### 5.2 用户权限扩展点

用户权限必须策略化设计，避免权限规则写死在业务层。

建议接口名称：

- PermissionPolicy

V1 默认实现：

- MemberDirectorHybridPolicy

后续可扩展实现：

- MemberOnlyPolicy
- DirectorOnlyPolicy
- MultiRolePolicy
- SharedWorldPolicy

权限策略至少控制以下内容：

- 用户可查看哪些记录
- 是否可查看实时私聊
- 是否可注入事件
- 是否可暂停或加速世界
- 是否可查看计划和关系变化

## 6. 模块化架构

推荐按领域拆分后端模块：

- world：世界状态、时钟、事件总线、时间推进
- character：人设、属性、情绪、社交倾向
- relationship：关系图谱与关系变化
- plan：计划、冲突检测、重排
- social：群聊、私聊、朋友圈、互动可见性
- agent_runtime：角色主循环与动作执行
- memory：短期记忆、摘要记忆、反思机制
- director：导演权限、记录查看、事件注入、世界控制
- llm：模型客户端、prompt、结构化输出、路由、重试
- workflow：复杂流程编排接口，预留 LangGraph 接入位
- infra：数据库、Redis、日志、配置

模块边界要求：

- 领域对象和状态归各领域模块
- 复杂流程归 agent_runtime / workflow
- 模型调用只通过 llm 模块进入
- 导演逻辑不直接散落到 social / character 中

## 7. 推荐仓库结构

建议采用前后端分离但同仓库管理的结构：

```text
MutilAgentsRolePlay/
  docs/
  apps/
    web/
  services/
    api/
  packages/
    shared-contracts/
```

其中：

- `apps/web`：前端应用
- `services/api`：后端服务
- `packages/shared-contracts`：前后端共享的 API 契约、事件类型、结构化 schema

后端内部建议结构：

```text
services/api/
  app/
    api/
    world/
    character/
    relationship/
    plan/
    social/
    agent_runtime/
    memory/
    director/
    llm/
    workflow/
    infra/
```

## 8. 关键数据对象

V1 至少需要以下核心对象：

- User
- Character
- CharacterState
- RelationshipSnapshot
- Conversation
- Message
- MomentPost
- PlanItem
- WorldEvent
- ActionDecision
- DirectorExplanation
- WorldUpdate

这些对象应优先定义清楚，再开始搭建接口和数据库。

## 9. API 与交互面板建议

### 9.1 核心页面

- 世界主页
- 群聊页
- 私聊页
- 朋友圈页
- 导演面板

### 9.2 导演面板内容

- 角色状态总览
- 当前计划与计划变更历史
- 关系图谱
- 行动日志
- 聊天记录查看入口
- 世界控制面板

### 9.3 API 建议

- GET /world/state
- GET /conversations
- GET /conversations/{id}/messages
- POST /messages
- GET /moments
- POST /moments
- GET /characters/{id}
- GET /characters/{id}/plan
- GET /director/logs
- GET /director/relationships
- POST /director/events
- POST /director/world-control
- WS /realtime

## 10. 开发阶段建议

### 阶段一：项目脚手架

- 建立仓库结构
- 初始化前端与后端工程
- 搭建基础配置、日志、测试框架
- 定义共享契约与核心数据对象

### 阶段二：世界内核

- 实现世界时钟
- 实现事件总线
- 实现调度器
- 实现世界状态存储

### 阶段三：角色运行与社交闭环

- 实现 CharacterState
- 实现 ThinkingEngine 接口与默认状态机实现
- 实现群聊、私聊、朋友圈链路
- 打通消息触发与计划触发

### 阶段四：导演模式

- 实现 PermissionPolicy 接口与默认导演权限策略
- 实现记录查看与延迟可见规则
- 实现导演事件注入与世界控制
- 实现导演解释展示

### 阶段五：稳定性与调优

- 增加记忆摘要
- 控制消息频率与打扰阈值
- 调整社交欲望与情绪变化规则
- 统计成本与性能

## 11. 测试要求

- 每个领域模块都应有单元测试
- 世界时钟、事件总线、调度器应有集成测试
- ThinkingEngine 与 PermissionPolicy 应有接口级测试
- 社交链路应覆盖群聊、私聊、朋友圈和可见性规则
- 导演模式应覆盖聊天记录查看、延迟规则、事件注入、世界控制
- 对关键场景增加端到端测试，确保多个角色连续运行时行为稳定

## 12. 最终结论

V1 的核心不是把所有高级 Agent 框架都接上，而是先把世界内核、角色状态、社交链路、导演权限和扩展接口做稳。

本项目第一版确定采用：

- Web + 单用户单世界
- Next.js + TypeScript 前端
- Python + FastAPI 后端
- PostgreSQL + Redis + WebSocket
- 状态机 + LLM 驱动的角色思维方式
- 延迟全可见的导演权限模型
- ThinkingEngine 与 PermissionPolicy 双扩展点设计
- 不接 LangChain/LangGraph，但预留未来接入能力

## 13. 当前实现状态

截至当前代码阶段，以下部分已经完成基础实现：

- 仓库结构已建立：`apps/web`、`services/api`、`packages/shared-contracts`
- 前端基础页面已可运行：世界概览页、导演页
- 后端基础接口已可运行：health、world、director、social
- 容器化基础设施已完成：PostgreSQL、Redis、API Docker 化
- 数据库自动建表已接通
- world runtime 已具备：
  - 世界时钟
  - 事件总线
  - 调度器
  - sample world 初始化
  - 启动恢复与持久化
- social 已具备：
  - 默认群聊会话
  - 默认朋友圈会话
  - 私聊会话自动创建
  - 消息持久化读写
- agent runtime 已具备：
  - StateDrivenThinkingEngine
  - 基于任务意图的决策
  - 自治动作执行器
  - 计划任务触发后写入真实聊天消息
  - follow-up task 自动续排

## 14. 当前实际运行流

当前后端的实际执行流如下：

1. 系统启动
2. 初始化数据库表
3. world runtime 创建 sample world 或从数据库恢复
4. social service 确保默认会话存在
5. 调用 `/api/world/advance`
6. 世界时钟推进并找出到期任务
7. 到期任务交给 ThinkingEngine 做决策
8. 自治执行器将动作落入群聊、私聊或朋友圈消息表
9. runtime 写入 action event，并为角色安排下一次计划任务
10. 最新状态再次持久化到数据库

## 15. 当前限制与风险

当前版本已经具备“世界可以自己说话”的能力，但仍有这些明显限制：

- 文本表达仍为模板化内容，不是完整角色生成表达
- 角色只实现了有限动作执行，尚未覆盖评论、点赞、计划改写等完整行为
- director 面板尚未接入真实后端数据
- Redis 尚未真正承担事件分发和调度协作
- world runtime 仍是“内存执行 + 数据库存档”的混合模式
- 关系、计划、朋友圈互动仍未形成完整领域闭环
- 本机测试环境尚未完全标准化，当前存在 Python 依赖环境差异风险

## 16. 当前阶段建议

当前最优先工作不是继续盲目扩功能，而是先完成“核心闭环测试”并修正暴露的问题。

建议测试重点如下：

- world 初始化与数据库恢复
- `/api/world/advance` 对到期任务的处理
- 调度任务到 ThinkingEngine 的决策链路
- 群聊、私聊、朋友圈消息的正确落库
- follow-up task 续排
- 基础 API 的稳定性与响应结构

待这些测试闭环稳定后，再继续扩展更复杂的角色表达、关系系统和导演功能。
