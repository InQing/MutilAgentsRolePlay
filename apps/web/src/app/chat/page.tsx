import type {
  ConversationSummaryContract,
  MessageRecordContract
} from "@mutilagentsroleplay/shared-contracts";

import { GroupChatPanel } from "@/components/group-chat-panel";
import {
  fetchConversationMessages,
  fetchConversations
} from "@/lib/api";

export default async function ChatPage() {
  const conversations = (await fetchConversations()) ?? [];
  const groupConversations = conversations.filter(
    (conversation) => conversation.conversation_type === "group"
  );

  const defaultConversation =
    groupConversations.find((conversation) => conversation.id === "conv-general") ??
    groupConversations[0] ??
    null;

  const initialMessages =
    defaultConversation === null
      ? []
      : ((await fetchConversationMessages(defaultConversation.id)) ?? []);

  return (
    <main className="space-y-8">
      <GroupChatPanel
        initialConversationId={defaultConversation?.id ?? null}
        initialConversations={groupConversations as ConversationSummaryContract[]}
        initialMessages={initialMessages as MessageRecordContract[]}
      />
    </main>
  );
}
