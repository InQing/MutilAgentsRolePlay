import { ScenePanel } from "@/components/scene-panel";
import { WorldRuntimePanel } from "@/components/world-runtime-panel";
import { fetchWorldState } from "@/lib/api";

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

export default async function HomePage() {
  const worldState = await fetchWorldState();

  return (
    <main className="space-y-8">
      <WorldRuntimePanel initialState={worldState} />

      <section className="grid gap-6 lg:grid-cols-2">
        <ScenePanel title="第一版主循环" items={loopItems} />
        <ScenePanel title="扩展性设计" items={extensibilityItems} />
      </section>
    </main>
  );
}
