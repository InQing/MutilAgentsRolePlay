"use client";

import type { WorldStateContract } from "@mutilagentsroleplay/shared-contracts";
import { useEffect, useState, useTransition } from "react";

type WorldRuntimePanelProps = {
  initialState: WorldStateContract | null;
};

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(new Date(value));
}

export function WorldRuntimePanel({ initialState }: WorldRuntimePanelProps) {
  const [worldState, setWorldState] = useState(initialState);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (initialState !== null) {
      return;
    }

    let cancelled = false;

    startTransition(() => {
      void (async () => {
        const response = await fetch("/api/world/state", {
          cache: "no-store"
        });

        if (!response.ok || cancelled) {
          return;
        }

        const nextState = (await response.json()) as WorldStateContract;
        setWorldState(nextState);
      })();
    });

    return () => {
      cancelled = true;
    };
  }, [initialState]);

  function handleAdvance(seconds: number) {
    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const response = await fetch("/api/world/advance", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ seconds })
        });

        if (!response.ok) {
          setFeedback("世界推进失败，请确认本地 API 已启动。");
          return;
        }

        const nextState = (await response.json()) as WorldStateContract;
        setWorldState(nextState);
        setFeedback(`已推进 ${Math.floor(seconds / 60)} 分钟，世界状态已刷新。`);
      })();
    });
  }

  if (worldState === null) {
    return (
      <section className="glass p-6">
        <h2 className="text-xl font-semibold text-ink">真实世界状态</h2>
        <div className="mt-4 rounded-2xl border border-dashed border-slate-300 bg-white/60 px-4 py-4 text-sm text-slate-600">
          当前无法读取 world API。请先启动本地后端，再刷新页面。
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <section className="glass grid gap-6 p-6 lg:grid-cols-[1.15fr_0.85fr]">
        <div>
          <p className="eyebrow">Live World</p>
          <h2 className="text-3xl font-semibold text-ink">世界状态已接入真实运行时</h2>
          <p className="muted mt-4 max-w-2xl text-base leading-7">
            当前页面直接读取 world runtime 的真实状态。你可以查看角色、最近事件与待执行任务，
            也可以主动推进世界，让角色继续行动。
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              className="rounded-full bg-orange-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-300"
              disabled={isPending}
              onClick={() => handleAdvance(300)}
              type="button"
            >
              {isPending ? "推进中..." : "推进 5 分钟"}
            </button>
            <button
              className="rounded-full border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400"
              disabled={isPending}
              onClick={() => handleAdvance(900)}
              type="button"
            >
              推进 15 分钟
            </button>
          </div>
          {feedback ? <p className="mt-4 text-sm text-slate-600">{feedback}</p> : null}
        </div>

        <div className="grid gap-4">
          <section className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
              World Clock
            </p>
            <p className="mt-3 text-2xl font-semibold text-ink">{formatTime(worldState.clock.now)}</p>
            <p className="mt-2 text-sm text-slate-600">
              {worldState.clock.paused ? "当前暂停" : "当前运行中"}，速度倍率{" "}
              {worldState.clock.speed_multiplier}x
            </p>
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
              Runtime Summary
            </p>
            <p className="mt-3 text-2xl font-semibold text-ink">
              {worldState.active_characters.length} 角色 / {worldState.pending_tasks.length} 待执行任务
            </p>
            <p className="mt-2 text-sm text-slate-600">世界 ID：{worldState.world_id}</p>
          </section>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="glass p-6">
          <h3 className="text-xl font-semibold text-ink">活跃角色</h3>
          <div className="mt-4 grid gap-4">
            {worldState.active_characters.map((character) => (
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
              </article>
            ))}
          </div>
        </section>

        <section className="space-y-6">
          <section className="glass p-6">
            <h3 className="text-xl font-semibold text-ink">最近事件</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              {worldState.recent_events.map((event) => (
                <li
                  key={event}
                  className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-3"
                >
                  {event}
                </li>
              ))}
            </ul>
          </section>

          <section className="glass p-6">
            <h3 className="text-xl font-semibold text-ink">待执行任务</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              {worldState.pending_tasks.map((task) => (
                <li
                  key={task}
                  className="rounded-2xl border border-slate-200 bg-white/70 px-4 py-3"
                >
                  {task}
                </li>
              ))}
            </ul>
          </section>
        </section>
      </section>
    </section>
  );
}
