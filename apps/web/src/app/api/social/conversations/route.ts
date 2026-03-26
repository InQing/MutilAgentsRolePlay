import { NextResponse } from "next/server";

import { fetchConversations } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function GET() {
  const conversations = await fetchConversations();

  if (conversations === null) {
    return NextResponse.json(
      { message: "Conversations API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(conversations);
}
