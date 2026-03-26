"use client";

import type { MessageRecordContract } from "@mutilagentsroleplay/shared-contracts";
import { useEffect, useState, useTransition } from "react";

type MomentFeedPanelProps = {
  initialMessages: MessageRecordContract[];
};

const DEFAULT_SENDER_ID = "user-001";

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour12: false,
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export function MomentFeedPanel({ initialMessages }: MomentFeedPanelProps) {
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  function handleRefresh() {
    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const response = await fetch("/api/social/conversations/conv-moments/messages", {
          cache: "no-store"
        });

        if (!response.ok) {
          setFeedback("刷新动态失败，请确认本地 API 已启动。");
          return;
        }

        const nextMessages = (await response.json()) as MessageRecordContract[];
        setMessages(nextMessages);
      })();
    });
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim()) {
      return;
    }

    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const response = await fetch("/api/social/moments", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            sender_id: DEFAULT_SENDER_ID,
            content: draft.trim(),
            mentions: []
          })
        });

        if (!response.ok) {
          setFeedback("发布动态失败，请稍后再试。");
          return;
        }

        const createdMoment = (await response.json()) as MessageRecordContract;
        setMessages((currentMessages) => [...currentMessages, createdMoment]);
        setDraft("");
        setFeedback("新动态已发布到朋友圈。");
      })();
    });
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <section className="glass p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="eyebrow">Moments</p>
            <h2 className="text-2xl font-semibold text-ink">最小朋友圈页</h2>
          </div>
          <button
            className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:text-slate-400"
            disabled={isPending}
            onClick={handleRefresh}
            type="button"
          >
            {isPending ? "刷新中..." : "刷新动态"}
          </button>
        </div>
        <p className="muted mt-4 text-sm leading-6">
          当前页面会直接读取默认朋友圈会话 `conv-moments` 的真实消息流。你可以先查看 AI 的动态，
          再自己发布一条新的 moment，验证这条链路也已经可用。
        </p>

        <div className="mt-6 space-y-4">
          {messages.map((message) => {
            const isUser = message.sender_id === DEFAULT_SENDER_ID;
            return (
              <article
                key={message.id}
                className={`rounded-2xl border px-5 py-4 ${
                  isUser
                    ? "border-emerald-200 bg-emerald-50"
                    : "border-slate-200 bg-white/70"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-ink">
                      {isUser ? "你" : message.sender_id}
                    </p>
                    <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-500">
                      {message.conversation_type}
                    </p>
                  </div>
                  <p className="text-xs text-slate-500">{formatTime(message.created_at)}</p>
                </div>
                <p className="mt-4 text-sm leading-7 text-slate-700">{message.content}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="glass p-6">
        <p className="eyebrow">New Moment</p>
        <h2 className="text-2xl font-semibold text-ink">发布一条新动态</h2>
        <p className="muted mt-4 text-sm leading-6">
          发送身份固定为 `{DEFAULT_SENDER_ID}`。这一步先验证最小动态发布能力，不引入点赞、
          评论和可见性复杂规则。
        </p>

        <form className="mt-6 space-y-3" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-700" htmlFor="moment-draft">
            动态内容
          </label>
          <textarea
            id="moment-draft"
            className="min-h-36 w-full rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-emerald-300"
            onChange={(event) => setDraft(event.target.value)}
            placeholder="输入一条新的朋友圈动态..."
            value={draft}
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-500">发布位置：conv-moments</p>
            <button
              className="rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-300"
              disabled={isPending || !draft.trim()}
              type="submit"
            >
              {isPending ? "发布中..." : "发布动态"}
            </button>
          </div>
          {feedback ? <p className="text-sm text-slate-600">{feedback}</p> : null}
        </form>
      </section>
    </section>
  );
}
