import { MomentFeedPanel } from "@/components/moment-feed-panel";
import { fetchConversationMessages } from "@/lib/api";

export default async function MomentsPage() {
  const initialMessages = (await fetchConversationMessages("conv-moments")) ?? [];

  return (
    <main className="space-y-8">
      <MomentFeedPanel initialMessages={initialMessages} />
    </main>
  );
}
