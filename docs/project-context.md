# 项目背景

## 项目概览

- 项目名称：MutilAgentsRolePlay
- 项目目标：从 0 开发一个多 AI 角色扮演与社交模拟项目，核心体验是 AI 自主聊天互动，用户可作为世界成员参与，并以导演视角观察和轻度干预。
- 当前状态：已完成 V1 产品方案、开发蓝图与代码仓库基础骨架搭建，已进入实现准备阶段。

## 产品范围

- 核心使用场景：单用户进入自己的 AI 世界，观察 6-10 个 AI 角色在群聊、私聊、朋友圈中的自主互动，并随时参与其中。
- 目标用户：喜欢 AI 角色扮演、群像社交模拟、观察角色关系演化的用户。
- 约束条件：
  - V1 聚焦 Web 端、单用户单世界。
  - V1 不接入 LangChain/LangGraph，但架构必须预留后续接入复杂工作流编排的能力。
  - “AI 思维方式”与“用户权限”必须做成可替换、可扩展模块。
  - 不向用户展示模型原始思维链，只展示导演可读解释。

## 架构信息

- 前端：Next.js + TypeScript + React + Tailwind CSS
- 后端：Python + FastAPI
- 数据与存储：PostgreSQL + Redis + WebSocket
- 核心架构：
  - 世界内核：世界时钟、事件总线、调度器、状态存储
  - 角色运行循环：Observe -> Interpret -> Decide -> Act -> Reflect
  - 领域模块：world、character、relationship、plan、social、agent_runtime、memory、director、llm、workflow、infra
  - 扩展点：
    - ThinkingEngine：V1 默认 StateDrivenThinkingEngine，后续可替换为 ReAct / Agent / LangGraph 等实现
    - PermissionPolicy：V1 默认 MemberDirectorHybridPolicy，后续可扩展更多权限层级与共享世界模式
- 当前代码骨架：
  - `apps/web`：Next.js 前端壳子与基础页面
  - `services/api`：FastAPI 模块化骨架、世界 runtime 底座、数据库初始化与初始测试
  - `packages/shared-contracts`：前端共享契约定义
- 部署与基础设施：
  - 根目录提供 `docker-compose.yml`，用于启动 PostgreSQL、Redis 和 API 服务
  - API 容器启动时可自动创建基础数据库表结构
- 外部集成：
  - LLM 提供商 SDK 通过统一 LLMClient 接口接入
  - 复杂工作流通过 WorkflowRunner 抽象预留 LangGraph 接入位

## 协作约定

- 在本仓库内开始实质性工作前，先阅读本文件和 `docs/project-progress.md`。
- 进行产品或架构设计时，优先参考 `docs/v1-solution-and-blueprint.md`。
- 当架构、模块边界、技术选型或关键技术决策发生变化时，更新本文件。
- 内容保持简洁、准确、便于长期维护。
