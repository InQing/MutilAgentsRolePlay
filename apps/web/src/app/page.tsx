import { ScenePanel } from "@/components/scene-panel";
import { StatusCard } from "@/components/status-card";

const loopItems = [
  "世界时钟与事件总线驱动角色按计划和事件行动",
  "角色通过 Observe -> Interpret -> Decide -> Act -> Reflect 循环运行",
  "群聊、私聊、朋友圈构成第一版的社交闭环"
];

const extensibilityItems = [
  "ThinkingEngine: 支持未来替换为 ReAct、Planner 或多 Agent 实现",
  "PermissionPolicy: 支持未来调整导演权限、观察范围和世界控制能力",
  "WorkflowRunner: 预留复杂工作流编排接口，后续可接 LangGraph"
];

export default function HomePage() {
  return (
    <main className="space-y-8">
      <section className="glass grid gap-8 p-8 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <p className="eyebrow">World Summary</p>
          <h2 className="text-3xl font-semibold leading-tight text-ink">
            让一组 AI 角色像在同一个真实社交世界里生活
          </h2>
          <p className="muted mt-4 max-w-2xl text-base leading-7">
            第一版优先验证世界内核、社交链路和导演可观察能力，不追求复杂商业化能力，
            重点是把“角色真的在生活”的感觉做出来。
          </p>
        </div>
        <div className="grid gap-4">
          <StatusCard
            title="World Mode"
            value="Single User"
            description="单用户单世界，先验证玩法与角色自治稳定性。"
          />
          <StatusCard
            title="Runtime"
            value="State + LLM"
            description="用结构化状态驱动决策，再逐步引入更复杂的思维方式。"
          />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <ScenePanel title="第一版主循环" items={loopItems} />
        <ScenePanel title="扩展性设计" items={extensibilityItems} />
      </section>
    </main>
  );
}

