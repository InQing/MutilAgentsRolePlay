const delayedPanels = [
  "查看私聊记录（延迟可见）",
  "查看计划变更历史与关系变化摘要",
  "查看角色最近一次动作的导演解释",
  "注入轻量事件并控制世界节奏"
];

export default function DirectorPage() {
  return (
    <main className="space-y-8">
      <section className="glass p-8">
        <p className="eyebrow">Director Mode</p>
        <h2 className="text-3xl font-semibold text-ink">增强版导演视角</h2>
        <p className="muted mt-4 max-w-3xl text-base leading-7">
          用户既是世界中的一员，也是可观察和轻度干预的导演。第一版采用“延迟全可见”
          策略：群聊和朋友圈实时可见，私聊、计划细节和关系变化默认延迟展示。
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="glass p-6">
          <h3 className="text-xl font-semibold text-ink">导演权限基线</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-700">
            {delayedPanels.map((item) => (
              <li
                key={item}
                className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-3"
              >
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="glass p-6">
          <h3 className="text-xl font-semibold text-ink">当前实现状态</h3>
          <div className="mt-4 space-y-4 text-sm leading-6 text-slate-700">
            <p>权限策略接口已经在后端骨架中预留，V1 默认策略为 MemberDirectorHybridPolicy。</p>
            <p>下一步会把导演事件注入、日志查看与延迟可见规则接入真实世界状态。</p>
          </div>
        </section>
      </section>
    </main>
  );
}

