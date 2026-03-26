import { NextRequest, NextResponse } from "next/server";

import {
  createConversationMessage,
  fetchConversationMessages
} from "@/lib/api";

type RouteContext = {
  params: Promise<{
    conversationId: string;
  }>;
};

export const dynamic = "force-dynamic";

export async function GET(_: NextRequest, context: RouteContext) {
  const { conversationId } = await context.params;
  const messages = await fetchConversationMessages(conversationId);

  if (messages === null) {
    return NextResponse.json(
      { message: "Conversation messages API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(messages);
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { conversationId } = await context.params;

  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json(
      { message: "Invalid request body." },
      { status: 400 }
    );
  }

  const message = await createConversationMessage(conversationId, {
    conversation_id: conversationId,
    conversation_type: (payload.conversation_type as "group" | "private" | "moment") ?? "group",
    sender_id: String(payload.sender_id ?? "user-001"),
    content: String(payload.content ?? ""),
    target_id: payload.target_id as string | null | undefined,
    mentions: Array.isArray(payload.mentions)
      ? (payload.mentions as string[])
      : [],
    created_at: typeof payload.created_at === "string" ? payload.created_at : undefined
  });

  if (message === null) {
    return NextResponse.json(
      { message: "Create message failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(message);
}
