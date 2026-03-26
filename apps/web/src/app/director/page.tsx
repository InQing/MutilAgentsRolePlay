import { fetchDirectorPanel } from "@/lib/api";

const delayedPanels = [
  "查看私聊记录（延迟可见）",
  "查看计划变更历史与关系变化摘要",
  "查看角色最近一次动作的导演解释",
  "注入轻量事件并控制世界节奏"
];

function formatTime(value?: string | null) {
  if (!value) {
    return "暂无时间";
  }

  return new Intl.DateTimeFormat("zh-CN", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export default async function DirectorPage() {
  const panel = await fetchDirectorPanel();

  return (
    <main className="space-y-8">
      <section className="glass p-8">
        <p className="eyebrow">Director Mode</p>
        <h2 className="text-3xl font-semibold text-ink">增强版导演视角</h2>
        <p className="muted mt-4 max-w-3xl text-base leading-7">
          用户既是世界中的一员，也是可观察和轻度干预的导演。第一版采用“延迟全可见”
          策略：群聊和朋友圈实时可见，私聊、计划细节和关系变化默认延迟展示。
        </p>
        {panel ? (
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                World Clock
              </p>
              <p className="mt-3 text-2xl font-semibold text-ink">{formatTime(panel.current_time)}</p>
              <p className="mt-2 text-sm text-slate-600">
                {panel.paused ? "当前已暂停" : "世界正在运行"}，速度倍率 {panel.speed_multiplier}x
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                Pending Tasks
              </p>
              <p className="mt-3 text-2xl font-semibold text-ink">{panel.pending_task_count}</p>
              <p className="mt-2 text-sm text-slate-600">
                当前导演延迟可见窗口 {Math.floor(panel.director_visibility_delay_seconds / 60)} 分钟
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                Runtime Scope
              </p>
              <p className="mt-3 text-2xl font-semibold text-ink">{panel.characters.length} 角色</p>
              <p className="mt-2 text-sm text-slate-600">
                已接入 {panel.conversations.length} 个会话与 {panel.relationships.length} 条关系边
              </p>
            </div>
          </div>
        ) : (
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white/60 px-4 py-4 text-sm text-slate-600">
            导演面板 API 当前不可达，页面先回退到静态说明。启动本地 API 后，这里会展示真实世界状态。
          </div>
        )}
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
          {panel ? (
            <div className="mt-4 space-y-4 text-sm leading-6 text-slate-700">
              <p>导演权限、运行时角色状态、最近事件日志和会话预览已经接入真实后端接口。</p>
              <p>下一步仍然是补齐计划、关系和更细粒度的延迟可见规则，而不是继续停留在静态壳子。</p>
            </div>
          ) : (
            <div className="mt-4 space-y-4 text-sm leading-6 text-slate-700">
              <p>权限策略接口已经在后端骨架中预留，V1 默认策略为 MemberDirectorHybridPolicy。</p>
              <p>启动本地 API 后，这个区域会自动切换为真实导演数据视图。</p>
            </div>
          )}
        </section>
      </section>

      {panel ? (
        <>
          <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <section className="glass p-6">
              <h3 className="text-xl font-semibold text-ink">角色运行快照</h3>
              <div className="mt-4 grid gap-4">
                {panel.characters.map((character) => (
                  <article
                    key={character.id}
                    className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h4 className="text-base font-semibold text-ink">{character.display_name}</h4>
                        <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
                          {character.emotion_state}
                        </p>
                      </div>
                      <div className="text-right text-xs text-slate-500">
                        <p>社交驱动力 {character.social_drive.toFixed(2)}</p>
                        <p>打断阈值 {character.interrupt_threshold.toFixed(2)}</p>
                      </div>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-700">
                      当前计划：{character.current_plan_summary}
                    </p>
                    <p className="mt-3 text-sm text-slate-600">
                      下一任务：
                      {character.next_task_intent
                        ? ` ${character.next_task_intent} · ${formatTime(character.next_task_run_at)}`
                        : " 暂无已排程任务"}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="glass p-6">
              <h3 className="text-xl font-semibold text-ink">最近世界日志</h3>
              <div className="mt-4 space-y-3">
                {panel.recent_logs.map((log) => (
                  <article
                    key={log.event_id}
                    className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                        {log.kind}
                      </p>
                      <p className="text-xs text-slate-500">{formatTime(log.created_at)}</p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-700">{log.summary}</p>
                    {log.director_explanation ? (
                      <p className="mt-2 rounded-xl bg-orange-50 px-3 py-2 text-sm text-orange-900">
                        导演解释：{log.director_explanation}
                      </p>
                    ) : null}
                  </article>
                ))}
              </div>
            </section>
          </section>

          <section className="glass p-6">
            <h3 className="text-xl font-semibold text-ink">会话观察视图</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {panel.conversations.map((conversation) => (
                <article
                  key={conversation.id}
                  className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <h4 className="text-base font-semibold text-ink">{conversation.title}</h4>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                      {conversation.conversation_type}
                    </p>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-700">
                    {conversation.last_message_preview ?? "当前还没有消息。"}
                  </p>
                  <p className="mt-3 text-xs text-slate-500">
                    {conversation.last_message_sender_name
                      ? `最近发言：${conversation.last_message_sender_name} · ${formatTime(conversation.last_message_at)}`
                      : "暂无最近发言"}
                  </p>
                </article>
              ))}
            </div>
          </section>

          <section className="glass p-6">
            <h3 className="text-xl font-semibold text-ink">关系快照</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {panel.relationships.map((relationship) => (
                <article
                  key={`${relationship.source_character_id}-${relationship.target_character_id}`}
                  className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <h4 className="text-base font-semibold text-ink">
                      {relationship.source_display_name} → {relationship.target_display_name}
                    </h4>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                      {relationship.affinity.toFixed(2)}
                    </p>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-700">
                    {relationship.labels.length > 0
                      ? relationship.labels.join(" / ")
                      : "当前还没有显式关系标签。"}
                  </p>
                  <p className="mt-3 text-xs text-slate-500">
                    最近更新时间：{formatTime(relationship.updated_at)}
                  </p>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}
