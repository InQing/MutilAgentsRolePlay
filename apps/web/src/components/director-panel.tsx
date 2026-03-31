"use client";

import type { DirectorPanelStateContract } from "@mutilagentsroleplay/shared-contracts";
import { useEffect, useState, useTransition } from "react";

type DirectorPanelProps = {
  initialPanel: DirectorPanelStateContract | null;
};

const delayedPanels = [
  "查看私聊记录（延迟可见）",
  "查看计划变更历史与关系变化摘要",
  "查看朋友圈评论与点赞聚合",
  "暂停、恢复并调整世界节奏"
];

const SPEED_OPTIONS = [0.5, 1, 2, 5];

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

async function fetchPanelFromProxy() {
  const response = await fetch("/api/director/panel", {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("导演面板暂时不可用。");
  }

  return (await response.json()) as DirectorPanelStateContract;
}

export function DirectorPanel({ initialPanel }: DirectorPanelProps) {
  const [panel, setPanel] = useState(initialPanel);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    setPanel(initialPanel);
  }, [initialPanel]);

  useEffect(() => {
    if (initialPanel !== null) {
      return;
    }

    let cancelled = false;
    startTransition(() => {
      void (async () => {
        try {
          const nextPanel = await fetchPanelFromProxy();
          if (!cancelled) {
            setPanel(nextPanel);
          }
        } catch {
          if (!cancelled) {
            setFeedback("导演面板 API 当前不可达，请确认本地后端已启动。");
          }
        }
      })();
    });

    return () => {
      cancelled = true;
    };
  }, [initialPanel]);

  function runPanelAction(
    requestFactory: () => Promise<Response>,
    successMessage: string
  ) {
    setFeedback(null);
    startTransition(() => {
      void (async () => {
        try {
          const response = await requestFactory();
          if (!response.ok) {
            const payload = (await response.json().catch(() => null)) as
              | { message?: string }
              | null;
            throw new Error(payload?.message ?? "导演操作失败，请稍后再试。");
          }

          const nextPanel = (await response.json()) as DirectorPanelStateContract;
          setPanel(nextPanel);
          setFeedback(successMessage);
        } catch (error) {
          const message =
            error instanceof Error ? error.message : "导演操作失败，请稍后再试。";
          setFeedback(message);
        }
      })();
    });
  }

  function handleRefresh() {
    runPanelAction(
      () =>
        fetch("/api/director/panel", {
          cache: "no-store"
        }),
      "导演面板已刷新。"
    );
  }

  function handlePause() {
    runPanelAction(
      () =>
        fetch("/api/director/pause", {
          method: "POST"
        }),
      "世界已暂停，导演面板已刷新。"
    );
  }

  function handleResume() {
    runPanelAction(
      () =>
        fetch("/api/director/resume", {
          method: "POST"
        }),
      "世界已恢复运行，导演面板已刷新。"
    );
  }

  function handleSetSpeed(speedMultiplier: number) {
    runPanelAction(
      () =>
        fetch("/api/director/speed", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            speed_multiplier: speedMultiplier
          })
        }),
      `世界速度已调整为 ${speedMultiplier}x。`
    );
  }

  return (
    <>
      <section className="glass p-8">
        <p className="eyebrow">Director Mode</p>
        <h2 className="text-3xl font-semibold text-ink">增强版导演视角</h2>
        <p className="muted mt-4 max-w-3xl text-base leading-7">
          用户既是世界中的一员，也是可观察和轻度干预的导演。当前页面已接入真实导演控制接口，
          并会按统一延迟规则过滤私聊、计划、关系变化与朋友圈互动。
        </p>
        {panel ? (
          <>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  World Clock
                </p>
                <p className="mt-3 text-2xl font-semibold text-ink">
                  {formatTime(panel.current_time)}
                </p>
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
                  当前导演延迟可见窗口{" "}
                  {Math.floor(panel.director_visibility_delay_seconds / 60)} 分钟
                </p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Runtime Scope
                </p>
                <p className="mt-3 text-2xl font-semibold text-ink">
                  {panel.characters.length} 角色
                </p>
                <p className="mt-2 text-sm text-slate-600">
                  {panel.conversations.length} 个会话 / {panel.relationships.length} 条关系 /{" "}
                  {panel.moment_interactions.length} 条互动
                </p>
              </div>
            </div>

            <section className="mt-6 rounded-[28px] border border-slate-200 bg-white/70 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Director Controls
                  </p>
                  <p className="mt-2 text-sm text-slate-600">
                    当前控制权限：{panel.permissions.can_control_world ? "已启用" : "未启用"}
                  </p>
                </div>
                <button
                  className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400"
                  disabled={isPending}
                  onClick={handleRefresh}
                  type="button"
                >
                  {isPending ? "处理中..." : "刷新面板"}
                </button>
              </div>

              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  className="rounded-full bg-orange-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-300"
                  disabled={isPending || !panel.permissions.can_control_world || panel.paused}
                  onClick={handlePause}
                  type="button"
                >
                  暂停世界
                </button>
                <button
                  className="rounded-full border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400"
                  disabled={isPending || !panel.permissions.can_control_world || !panel.paused}
                  onClick={handleResume}
                  type="button"
                >
                  恢复运行
                </button>
              </div>

              <div className="mt-4 flex flex-wrap gap-3">
                {SPEED_OPTIONS.map((speedOption) => {
                  const isActive = panel.speed_multiplier === speedOption;
                  return (
                    <button
                      key={speedOption}
                      className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                        isActive
                          ? "bg-ink text-white"
                          : "border border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50"
                      } disabled:cursor-not-allowed disabled:border-slate-200 disabled:bg-slate-100 disabled:text-slate-400`}
                      disabled={isPending || !panel.permissions.can_control_world || isActive}
                      onClick={() => handleSetSpeed(speedOption)}
                      type="button"
                    >
                      {speedOption}x
                    </button>
                  );
                })}
              </div>

              {feedback ? <p className="mt-4 text-sm text-slate-600">{feedback}</p> : null}
            </section>
          </>
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
              <p>导演权限、运行时角色状态、最近事件日志、会话预览和朋友圈互动聚合已经接入真实后端接口。</p>
              <p>当前这一版以“控制闭环 + 统一可见性 + 互动展示”为收口，暂不在这里加入 inject event。</p>
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
                        <h4 className="text-base font-semibold text-ink">
                          {character.display_name}
                        </h4>
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
            <h3 className="text-xl font-semibold text-ink">朋友圈互动</h3>
            <div className="mt-4 grid gap-4 lg:grid-cols-2">
              {panel.moment_interactions.length > 0 ? (
                panel.moment_interactions.map((interaction) => (
                  <article
                    key={interaction.id}
                    className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-ink">
                        {interaction.actor_display_name}
                        {interaction.interaction_type === "comment" ? " 评论了" : " 点赞了"}
                        {interaction.target_moment_sender_name
                          ? ` ${interaction.target_moment_sender_name}`
                          : ""}
                        的动态
                      </p>
                      <p className="text-xs text-slate-500">
                        {formatTime(interaction.created_at)}
                      </p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-700">
                      动态内容：{interaction.target_moment_preview}
                    </p>
                    <p className="mt-3 text-sm text-slate-600">
                      {interaction.content ? `互动内容：${interaction.content}` : "互动内容：点赞"}
                    </p>
                  </article>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-white/60 px-4 py-6 text-sm text-slate-600">
                  当前还没有进入导演可见窗口的朋友圈互动。
                </div>
              )}
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
    </>
  );
}
