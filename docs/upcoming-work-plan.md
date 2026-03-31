# 后续执行计划

## 1. 文档用途

本文件不是“愿望清单”，而是下一阶段真实开发的执行文档。

目标：

- 让接手者知道下一步该做什么
- 明确任务顺序、依赖关系和验收标准
- 避免功能扩展时失去当前已建立的架构稳定性

使用方式：

- 开始新阶段开发前，先读本文件
- 每完成一个阶段，应同步更新本文件和 `docs/project-progress.md`
- 如果架构发生变化，也同步更新 `docs/project-context.md`

## 2. 当前判断

当前项目已经完成：

- 最小可用 Web 闭环
- 后端基础架构
- 世界时钟、调度、事件、持久化基础
- 社交消息持久化基础
- 第一版自治动作执行链路
- 轻量本地测试环境
- 30 项后端测试基线
- Ubuntu 云服务器上的 Docker 常驻部署与第一轮手工 smoke check
- Docker/PostgreSQL/Redis 正式一致性联调
- follow-up task 恢复一致性测试
- 自治消息 API 可见性联调
- relationship 规则最小闭环
- plan 持久化最小闭环
- moment comment / like 最小后端闭环
- director 延迟可见最小后端闭环
- director pause / resume / speed 最小控制闭环
- director 前端控制入口、互动展示与统一可见性 helper 最小闭环
- director inject event 最小闭环

当前项目尚未完成：

- 模板化消息升级为角色表达生成
- 导演模式更完整的可见性细则与前端回归校验
- Redis 真正进入调度协作

因此，后续工作不应再回到“搭骨架”，而应围绕三条主线推进：

1. 先升级表达层
2. 并行收尾导演细则
3. 最后做基础设施深化

## 3. 执行总原则

- 不要绕过现有 runtime 主链路新增旁路逻辑
- 不要在 route 层堆业务逻辑
- 不要在功能扩展时破坏当前测试基线
- 每新增重要能力，都应带最小必要测试
- 先完成一条链路的“可运行 + 可测试”，再继续往上叠功能

## 4. 阶段零：基本可运行状态

该阶段已完成。

### 4.1 目标

让项目在轻量本地模式下达到“用户打开页面即可看到真实世界，并可进行最小互动”的状态。

### 4.2 任务

#### 任务 A：世界主页真实化

内容：

- 首页接入 `/api/world/state`
- 展示真实 world clock、active characters、recent events、pending tasks
- 保留项目介绍，但不再只是静态展示

#### 任务 B：世界推进入口

内容：

- 在前端增加“推进世界”入口
- 调用 `/api/world/advance`
- 推进后刷新世界状态

#### 任务 C：最小群聊页

内容：

- 提供群聊页
- 读取默认群聊消息
- 支持发送群聊消息

#### 任务 D：最小朋友圈页

内容：

- 提供朋友圈页
- 读取 moment 流
- 支持发布动态

#### 任务 E：本地运行入口收束

内容：

- 统一本地 API base URL 的使用方式
- 确保轻量模式启动后前端默认可用

### 4.3 阶段结束条件

当以下条件都满足时，阶段零结束：

- 首页已读取真实 world state
- 前端可主动推进世界
- 群聊页可读写
- 朋友圈页可读写
- 轻量模式下前后端联通顺畅

## 5. 阶段一：环境与一致性验证

该阶段已完成。

### 5.1 目标

确认项目在“目标运行环境”下与当前本地 SQLite 轻量模式行为一致。

### 5.2 任务

#### 任务 F：Docker / PostgreSQL / Redis 联调

内容：

- 在具备 Docker 的机器上运行 `scripts/integration/run-docker-consistency-check.ps1` 或 `scripts/integration/run-docker-consistency-check.sh`
- 启动 PostgreSQL 和 Redis
- 用 API 实际跑 world advance 与 social 读写
- 对比 SQLite 模式下的结果是否一致

验收标准：

- world 初始化成功
- API 服务可启动
- `/api/world/state` 正常返回
- `/api/world/advance` 正常推进并写入消息
- `/api/social/conversations` 可正确读到默认会话
- private message 与 moment API 行为与 SQLite 模式一致

阻塞条件：

- 当前已解除，Ubuntu 环境上的正式验证脚本与结果记录已完成

建议执行环境：

- 云服务器
- 安装了 Docker Desktop 的开发机

#### 任务 G：follow-up task 持久化恢复一致性

内容：

- 增加测试，验证 world 重启后 follow-up task 不只是“还在”，而且后续继续执行时行为正确
- 确认恢复后的任务不会重复执行
- 确认恢复后继续 advance 时消息与事件符合预期

验收标准：

- 至少覆盖“advance -> 续排 -> 持久化 -> 重启 -> 再次 advance -> 成功产生新行为”完整链路

#### 任务 H：自治消息的 API 可见性联调

内容：

- 验证自治生成的群聊消息可通过 conversation API 读到
- 验证自治生成的 moment 消息可通过 moment conversation 读到
- 验证私聊链路在 API 层可见且会话不重复

验收标准：

- 同一次自治链路中，写入和读取结果一致
- API 返回结构稳定

### 5.3 阶段结束条件

当以下条件都满足时，阶段一结束：

- Docker/PostgreSQL/Redis 联调完成，或明确记录了环境外部阻塞
- follow-up task 恢复一致性测试完成
- 自治消息 API 可见性联调完成

当前状态：

- 已完成

## 6. 阶段二：持久化与领域补全

在环境一致性确认后进入本阶段。

### 6.1 目标

把当前“能跑”的核心闭环补成“更完整的世界状态模型”。

### 6.2 任务

#### 任务 I：relationship 规则补强

内容：

- 在已有 relationship 持久化基础上补充更明确的变化规则
- 为导演面板和角色决策提供更可靠的数据来源

验收标准：

- 关系数据可以保存和读取
- 角色行动后可触发稳定、可解释的关系变化
- 测试覆盖基本读写

#### 任务 J：plan 持久化

内容：

- 为角色计划建立数据库模型
- 从“任务 payload”提升为“计划对象 + 调度任务”的组合
- 为未来计划调整和计划历史做准备

验收标准：

- 角色计划可落库
- 调度任务可从计划衍生
- 计划可在重启后恢复

当前状态：

- 最小后端闭环已完成

#### 任务 K：moment interaction 能力

内容：

- 朋友圈评论
- 点赞
- 对应事件记录

验收标准：

- 至少完成 comment / like 的最小链路
- 行为可通过 API 查看
- 会写入世界事件

当前状态：

- 最小后端闭环已完成，后续主要补前端可视化与更完整的互动呈现

### 6.3 阶段结束条件

- relationship / plan / moment interaction 都有最小可运行实现
- 持久化和 API 至少打通一条完整读写链路

当前状态：

- 已完成

## 7. 阶段三：角色管理系统

### 7.1 目标

让角色定义从“bootstrap 内置样本”升级为用户可管理、可持久化、可直接驱动 runtime 与后续表达层的正式产品能力。

### 7.2 子阶段 A：角色管理基础闭环

内容：

- 新增角色管理 API：`GET /api/characters`、`PUT /api/characters/{character_id}`
- 新增独立角色页 `/characters`
- 支持编辑现有角色的显示名、角色画像与行为参数
- 保存后立即更新当前 runtime，并同步持久化
- 当 `current_plan_summary` 被修改时，同步更新该角色当前 active plan 的 `summary`

角色画像字段先固定为：

- `identity_and_background`
- `personality`
- `speaking_style`
- `appearance_and_presence`
- `additional_notes`

行为参数字段先固定为：

- `current_plan_summary`
- `emotion_state`
- `social_drive`
- `interrupt_threshold`

验收标准：

- 用户可以在角色页编辑当前世界已有角色
- 更新后 world / director 页面都能读到新角色状态
- 角色画像已进入 `character` 域，不再由表达层临时定义

### 7.3 子阶段 B：角色生命周期 CRUD 扩展

内容：

- 新增角色创建 API：`POST /api/characters`
- 新增角色删除 API：`DELETE /api/characters/{character_id}`
- 创建角色时自动补齐初始 active plan、pending task 与默认关系边
- 删除角色时同步移除 active plan、pending tasks 与相关关系边
- 保留历史消息与历史 world event，不做物理删除
- 在角色页补充“新增角色”和“删除角色”入口

验收标准：

- 新增角色后 world / director 可立即看到新角色
- 删除角色后 world advance 不再调度该角色
- 历史消息与事件仍然可读

### 7.4 阶段结束条件

- 角色定义有独立页面与独立 API
- 角色画像、行为参数、增删改都已经进入正式链路
- 后续表达层与 LLM 接入已有稳定的角色数据来源

## 8. 阶段四：角色表达升级

### 8.1 目标

把当前模板化消息升级为更真实的角色表达，但前提是直接消费 `character` 域中的角色画像与运行态。

### 8.2 任务

#### 任务 L：表达层抽象

内容：

- 不要直接在 `AutonomousActionExecutor` 中继续堆模板
- 提取独立表达层或 message generation 层
- 让动作决策与文本表达解耦

验收标准：

- executor 不再直接承载大量文本模板
- 后续可替换为真实 LLM 表达生成

#### 任务 M：角色状态接入表达

内容：

- 角色画像（来自 `character` 域）
- emotion_state
- current_plan_summary
- recent context

验收标准：

- 相同动作类型在不同角色上有明显表达差异

#### 任务 N：LLM 兼容接入

内容：

- 通过 `LLMClient` 接入真实模型
- 表达层保持 provider-agnostic，避免锁死到单一供应商
- 仅替换表达层，不直接改 runtime 主骨架

验收标准：

- 保持现有自治主链路不变
- 新增测试或至少保留 mockable 结构

## 9. 阶段五：导演能力落地

### 9.1 目标

把导演模式从“静态页面 + 权限结构”升级为“真实可观察系统”。

### 8.2 任务

#### 任务 O：导演日志与事件解释

内容：

- 展示真实 world events
- 展示 director explanation

#### 任务 P：延迟可见规则落地

内容：

- 私聊延迟可见
- 计划与关系变化延迟可见

#### 任务 Q：导演控制能力

内容：

- 暂停
- 恢复
- 加速
- 注入事件

### 8.3 阶段结束条件

- director 页面可读取真实后端数据
- 导演权限不再只是结构占位

## 10. 阶段六：基础设施深化

### 10.1 目标

为未来长时间运行和服务器部署做准备。

### 10.2 任务

#### 任务 R：Redis 真正进入链路

内容：

- 事件队列
- 调度协作
- 后续可能的后台 worker

#### 任务 S：runtime 模式升级

内容：

- 从当前“内存执行 + 数据库存档”
- 逐步推进到“更明确的持久化驱动模型”

#### 任务 T：环境标准化

内容：

- 统一本地 / Docker / 服务器运行说明
- 明确 Python / Node / 数据库版本要求

## 11. 推荐开发顺序

当前最推荐的顺序是：

1. 阶段一：环境与一致性验证
2. 阶段二：持久化与领域补全
3. 阶段三：角色管理系统
4. 阶段四：角色表达升级
5. 阶段五：导演能力落地
6. 阶段六：基础设施深化

原因：

- 最小产品闭环已经打通，继续扩功能前应先确认 Docker/PostgreSQL/Redis 行为与本地轻量模式一致
- 如果跳过一致性验证继续做更深领域能力，后续修复成本会更高
- 导演能力、表达层和基础设施深化都更依赖稳定的持久化与恢复基线

## 12. 当前最具体的下一步

如果现在立刻继续开发，建议按以下顺序执行：

1. 先补角色管理系统，把角色画像与行为参数从 bootstrap 数据升级为正式可管理数据
2. 先做角色管理基础闭环：独立角色页、现有角色编辑、立即生效与持久化
3. 紧接着补角色 CRUD：新增角色、删除角色，以及相关 plan / task / relationship 联动
4. 角色管理稳定后，再进入表达层抽象与 LLM 兼容接入
5. 表达层稳定后，再回补导演模式的细化可见性规则与前端回归检查

补充进展：

- 私聊、计划、关系、moment interaction 的统一可见性过滤已落地，当前 director panel 也会对相关 director log 做统一过滤
- pause / resume / speed 与 inject event 的前后端闭环已完成，导演模式已具备最小可观察、可控制、可轻量干预能力
- 但在真正升级表达层之前，角色管理需要先落地，否则 persona、角色画像和运行态仍缺少正式产品入口

当前最建议的新窗口接手顺序：

1. 提供角色管理 API 与角色独立页面
2. 让角色画像、行为参数与 runtime 持久化正式连通
3. 补齐新增角色 / 删除角色的联动逻辑
4. 再进入表达层与 LLM 兼容接入
5. 最后回补导演细则与 Redis / runtime 深化

## 13. 暂不建议做的事情

当前不建议优先做：

- 直接接入 LangGraph
- 直接接入复杂多 Agent 讨论机制
- 大规模重构 runtime 主链路
- 先做复杂前端页面再回头补后端真实数据
- 跳过持久化与恢复验证直接继续扩功能

## 14. 文档维护要求

- 每完成一个阶段，要更新本文件中的“当前最具体的下一步”
- 如果阶段优先级变化，要同步修改本文件
- 如果新增模块或改变架构边界，要同步更新 `docs/project-context.md`
