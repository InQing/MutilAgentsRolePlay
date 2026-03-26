"use client";

import type {
  ConversationSummaryContract,
  MessageRecordContract
} from "@mutilagentsroleplay/shared-contracts";
import { useEffect, useState, useTransition } from "react";

type GroupChatPanelProps = {
  initialConversations: ConversationSummaryContract[];
  initialConversationId: string | null;
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

export function GroupChatPanel({
  initialConversations,
  initialConversationId,
  initialMessages
}: GroupChatPanelProps) {
  const [conversations, setConversations] = useState(initialConversations);
  const [selectedConversationId, setSelectedConversationId] = useState(initialConversationId);
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    setConversations(initialConversations);
  }, [initialConversations]);

  useEffect(() => {
    setSelectedConversationId(initialConversationId);
  }, [initialConversationId]);

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  const selectedConversation =
    conversations.find((conversation) => conversation.id === selectedConversationId) ?? null;

  function handleSelectConversation(conversationId: string) {
    setSelectedConversationId(conversationId);
    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const response = await fetch(`/api/social/conversations/${conversationId}/messages`, {
          cache: "no-store"
        });

        if (!response.ok) {
          setFeedback("读取群聊消息失败，请确认本地 API 已启动。");
          return;
        }

        const nextMessages = (await response.json()) as MessageRecordContract[];
        setMessages(nextMessages);
      })();
    });
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedConversation || !draft.trim()) {
      return;
    }

    setFeedback(null);
    startTransition(() => {
      void (async () => {
        const response = await fetch(
          `/api/social/conversations/${selectedConversation.id}/messages`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              conversation_id: selectedConversation.id,
              conversation_type: selectedConversation.conversation_type,
              sender_id: DEFAULT_SENDER_ID,
              content: draft.trim(),
              mentions: []
            })
          }
        );

        if (!response.ok) {
          setFeedback("发送消息失败，请稍后再试。");
          return;
        }

        const createdMessage = (await response.json()) as MessageRecordContract;
        setMessages((currentMessages) => [...currentMessages, createdMessage]);
        setDraft("");
        setFeedback("消息已发送到当前群聊。");
      })();
    });
  }

  if (conversations.length === 0) {
    return (
      <section className="glass p-6">
        <h2 className="text-xl font-semibold text-ink">最小群聊页</h2>
        <div className="mt-4 rounded-2xl border border-dashed border-slate-300 bg-white/60 px-4 py-4 text-sm text-slate-600">
          当前没有可用的群聊会话。请先确认后端默认会话是否已初始化。
        </div>
      </section>
    );
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <section className="glass p-6">
        <p className="eyebrow">Group Chat</p>
        <h2 className="text-2xl font-semibold text-ink">最小群聊页</h2>
        <p className="muted mt-4 text-sm leading-6">
          当前页面会读取真实 conversation 列表，并默认进入世界群聊。你可以直接发送一条消息，
          验证前后端读写链路已经接通。
        </p>

        <div className="mt-6 space-y-3">
          {conversations.map((conversation) => {
            const active = conversation.id === selectedConversationId;
            return (
              <button
                key={conversation.id}
                className={`w-full rounded-2xl border px-4 py-4 text-left transition ${
                  active
                    ? "border-orange-300 bg-orange-50"
                    : "border-slate-200 bg-white/70 hover:border-slate-300"
                }`}
                disabled={isPending}
                onClick={() => handleSelectConversation(conversation.id)}
                type="button"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-base font-semibold text-ink">{conversation.title}</h3>
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                    {conversation.conversation_type}
                  </p>
                </div>
                <p className="mt-2 text-sm text-slate-600">
                  参与者数：{conversation.participant_ids.length || "默认公开会话"}
                </p>
              </button>
            );
          })}
        </div>
      </section>

      <section className="glass p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="eyebrow">Live Messages</p>
            <h2 className="text-2xl font-semibold text-ink">
              {selectedConversation?.title ?? "当前会话"}
            </h2>
          </div>
          <p className="text-sm text-slate-500">
            发送身份：`{DEFAULT_SENDER_ID}`
          </p>
        </div>

        <div className="mt-6 max-h-[420px] space-y-3 overflow-y-auto pr-2">
          {messages.map((message) => {
            const isUser = message.sender_id === DEFAULT_SENDER_ID;
            return (
              <article
                key={message.id}
                className={`rounded-2xl border px-4 py-4 ${
                  isUser
                    ? "border-orange-200 bg-orange-50"
                    : "border-slate-200 bg-white/70"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-ink">
                    {isUser ? "你" : message.sender_id}
                  </p>
                  <p className="text-xs text-slate-500">{formatTime(message.created_at)}</p>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-700">{message.content}</p>
              </article>
            );
          })}
        </div>

        <form className="mt-6 space-y-3" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-slate-700" htmlFor="chat-draft">
            发送一条群聊消息
          </label>
          <textarea
            id="chat-draft"
            className="min-h-28 w-full rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-orange-300"
            onChange={(event) => setDraft(event.target.value)}
            placeholder="输入一条消息，验证群聊写入链路..."
            value={draft}
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-500">
              当前会话：{selectedConversation?.id ?? "未选择"}
            </p>
            <button
              className="rounded-full bg-orange-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-300"
              disabled={isPending || !draft.trim() || selectedConversation === null}
              type="submit"
            >
              {isPending ? "发送中..." : "发送消息"}
            </button>
          </div>
          {feedback ? <p className="text-sm text-slate-600">{feedback}</p> : null}
        </form>
      </section>
    </section>
  );
}
