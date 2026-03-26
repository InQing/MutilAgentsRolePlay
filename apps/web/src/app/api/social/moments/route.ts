import { NextRequest, NextResponse } from "next/server";

import { createMoment } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json(
      { message: "Invalid request body." },
      { status: 400 }
    );
  }

  const message = await createMoment({
    sender_id: String(payload.sender_id ?? "user-001"),
    content: String(payload.content ?? ""),
    mentions: Array.isArray(payload.mentions)
      ? (payload.mentions as string[])
      : [],
    created_at: typeof payload.created_at === "string" ? payload.created_at : undefined
  });

  if (message === null) {
    return NextResponse.json(
      { message: "Create moment failed because the API is unavailable." },
      { status: 503 }
    );
  }

  return NextResponse.json(message);
}
