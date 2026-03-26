# 项目进度

## 当前阶段

- 阶段：基础仓库骨架已完成，待进入核心能力实现阶段
- 概要：已完成前端、后端、共享契约与扩展接口的基础搭建，下一步进入世界内核与社交链路实现。

## 最近变更

- 2026-03-25：创建 `docs/project-context.md`，作为项目背景与架构信息的主文档。
- 2026-03-25：创建 `docs/project-progress.md`，作为项目执行过程与进展记录文档。
- 2026-03-25：开始构建项目专用 Codex skill，使 AI 能在工作前读取文档、在完成开发后更新文档。
- 2026-03-26：确定 V1 产品范围为 Web 端、单用户单世界的多 AI 社交模拟。
- 2026-03-26：确定 V1 技术栈为 Next.js + TypeScript 前端，Python + FastAPI 后端，PostgreSQL + Redis + WebSocket。
- 2026-03-26：确定导演模式采用“延迟全可见”，用户可查看 AI 聊天记录，但不展示原始思维链。
- 2026-03-26：确定 AI 运行机制采用“状态机 + LLM 驱动”，并将 ThinkingEngine 设计为可替换扩展点。
- 2026-03-26：确定用户权限通过 PermissionPolicy 进行策略化设计，支持后续扩展与切换。
- 2026-03-26：新增 `docs/v1-solution-and-blueprint.md`，作为 V1 方案与开发蓝图文档。
- 2026-03-26：创建 monorepo 基础结构，包括 `apps/web`、`services/api`、`packages/shared-contracts`。
- 2026-03-26：搭建 Next.js 前端壳子页面，包含世界概览页和导演页基础界面。
- 2026-03-26：搭建 FastAPI 后端骨架，包含 world、director、agent_runtime 等模块与基础路由。
- 2026-03-26：落地 ThinkingEngine、PermissionPolicy、WorkflowRunner、LLMClient 等关键扩展接口。
- 2026-03-26：新增基础测试并完成后端 Python 语法编译校验。
- 2026-03-26：新增 `docker-compose.yml`、API Dockerfile 与 `.env.example`，用于 PostgreSQL、Redis 与 API 的容器化部署。
- 2026-03-26：为后端加入数据库配置、SQLAlchemy/Redis 接入与基础 ORM 模型。
- 2026-03-26：实现世界时钟、事件总线、调度器与 `WorldRuntimeService` 第一版。
- 2026-03-26：新增 `/api/world/advance` 接口，用于推进世界时间并触发到期任务。
- 2026-03-26：新增数据库自动建表初始化逻辑与 world runtime 基础测试。

## 下一步

- 定义数据库表结构与持久化层。
- 将当前内存仓储替换为真实数据库持久化实现。
- 接入真实的角色运行循环与社交消息闭环。
- 将导演面板与后端状态接口正式打通。
- 把 Redis 真正接入事件队列与调度协作链路。
- 在后续开发任务完成后，持续维护这份进度文档。
