# 项目进度

## 当前阶段

- 阶段：本地测试任务已完成，待进入 Docker 联调准备与后续功能开发阶段
- 概要：已完成前端预览、后端基础设施、world runtime、持久化恢复、基础 social 落库、自治动作执行，以及本地核心测试闭环。Docker/PostgreSQL/Redis 联调已具备脚本入口，但因本机缺少 Docker 环境尚未执行。

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
- 2026-03-26：新增 world 持久化恢复服务，支持启动时从数据库恢复世界时钟、角色、任务与事件。
- 2026-03-26：新增 conversations / chat_messages ORM 模型与 social service，支持群聊会话和消息基础落库。
- 2026-03-26：新增 `/api/social/conversations` 与消息读写接口，为后续真实社交链路做准备。
- 2026-03-26：安装前端依赖，修正本地共享包引用与 TypeScript 路径配置。
- 2026-03-26：完成前端类型检查与生产构建验证，确认 Next.js 页面可正常构建。
- 2026-03-26：成功启动本地前端开发服务器，当前预览地址为 `http://localhost:3000`。
- 2026-03-26：新增自治动作执行器，将到期调度任务接入 ThinkingEngine 与 social gateway。
- 2026-03-26：实现角色自动发送群聊、私聊、朋友圈消息的第一版执行链路，并将结果写入消息表。
- 2026-03-26：实现角色 follow-up task 续排逻辑，避免世界在首轮任务后停摆。
- 2026-03-26：新增自治执行基础测试，验证计划任务可产出真实聊天消息。
- 2026-03-26：将 `ThinkingEngine` 与调度任务意图打通，支持按任务意图触发群聊发言等自治动作。
- 2026-03-26：新增 private conversation 自动创建逻辑与朋友圈默认会话。
- 2026-03-26：补充当前实现状态文档，明确已完成链路、现存限制与后续任务分解。
- 2026-03-26：新增 `scripts/local/start-light-dev.ps1`、`stop-light-dev.ps1`、`run-backend-tests.ps1`，用于低资源占用的本地开发与测试。
- 2026-03-26：为后端增加 SQLite 轻量本地模式支持，用于在私人电脑上减少资源占用。
- 2026-03-26：修复自治执行测试中的 `MessageRecord.created_at` 默认值问题。
- 2026-03-26：使用 Python 3.12 虚拟环境跑通后端本地测试环境，当前 `8` 项测试全部通过。
- 2026-03-26：新增 API 级测试，覆盖 `/api/world/advance` 与 social conversation/message 链路。
- 2026-03-26：补充测试隔离夹具，解决 SQLite 文件占用与 runtime 单例状态串扰问题。
- 2026-03-26：本地轻量模式下后端测试扩展到 `10` 项，当前全部通过。
- 2026-03-26：新增 SQLite 模式下的 world 持久化恢复测试，验证 world clock、事件与 pending task 可恢复。
- 2026-03-26：新增 social service 测试，覆盖 private conversation 自动创建复用与 moment 消息写入。
- 2026-03-26：本地轻量模式下后端测试扩展到 `13` 项，当前全部通过。
- 2026-03-26：新增 `/api/social/private-messages` 与 `/api/social/moments`，补齐更自然的私聊与朋友圈 API 入口。
- 2026-03-26：新增 API 级私聊与朋友圈测试，覆盖 private conversation 自动建会话与 moment 消息写入默认会话。
- 2026-03-26：修复 social service 在未显式传入 `created_at` 时覆盖默认值的问题。
- 2026-03-26：本地轻量模式下后端测试扩展到 `15` 项，当前全部通过。
- 2026-03-26：新增恢复一致性测试，覆盖 world 重启后消息与 pending task 的一致性。
- 2026-03-26：新增多次 `advance` 稳定性测试，验证自治链路连续运行不会停摆。
- 2026-03-26：修复 world event 恢复顺序不稳定问题，引入显式 `sequence_number` 持久化字段。
- 2026-03-26：新增 Docker/PostgreSQL/Redis 一致性检查脚本 `scripts/integration/run-docker-consistency-check.ps1`。
- 2026-03-26：本地轻量模式下后端测试扩展到 `17` 项，当前全部通过。
- 2026-03-26：尝试执行 Docker/PostgreSQL/Redis 一致性联调，但当前机器 `docker` 不在 PATH 中，测试暂时阻塞于环境条件。

## 下一步

- 测试任务暂时收束，后续优先项为：
  - 在具备 Docker 环境后补做 PostgreSQL/Redis 一致性联调
  - 增加 follow-up task 落库与恢复一致性测试
  - 增加自治生成消息后 API 可见性的联调测试
- 然后继续补充功能：
  - 将剩余内存仓储逐步替换为真实数据库持久化实现
  - 补充关系、计划、朋友圈等领域的数据库模型与持久化逻辑
  - 将当前模板化消息表达升级为更完整的角色表达生成逻辑
  - 补充私聊目标选择、朋友圈互动、计划调整等更完整的自治行为
  - 将导演面板与后端状态接口正式打通
  - 把 Redis 真正接入事件队列与调度协作链路
- 在后续开发任务完成后，持续维护这份进度文档。
